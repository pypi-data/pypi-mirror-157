from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Collection, Dict, List, Optional, Tuple

import numpy
import pandas
from annofabapi.models import TaskPhase
from dataclasses_json import DataClassJsonMixin

import annofabcli
from annofabcli.common.cli import AbstractCommandLineWithoutWebapiInterface, get_json_from_args, get_list_from_args
from annofabcli.common.utils import print_csv
from annofabcli.statistics.visualization.dataframe.project_performance import (
    ProjectPerformance,
    ProjectWorktimePerMonth,
)
from annofabcli.statistics.visualization.model import WorktimeColumn
from annofabcli.statistics.visualization.project_dir import ProjectDir

logger = logging.getLogger(__name__)


@dataclass
class ResultDataframe:
    annotation_productivity: pandas.DataFrame
    inspection_acceptance_productivity: pandas.DataFrame
    quality_with_task_rejected_count: pandas.DataFrame
    quality_with_inspection_comment: pandas.DataFrame

    project_performance: ProjectPerformance
    """プロジェクトごとの生産性と品質"""

    project_actual_worktime: ProjectWorktimePerMonth
    """プロジェクトごとの実績作業時間"""
    project_monitored_worktime: ProjectWorktimePerMonth
    """プロジェクトごとの計測作業時間"""


@dataclass
class ThresholdInfo(DataClassJsonMixin):
    """閾値の情報"""

    threshold_worktime: Optional[float] = None
    """作業時間の閾値。指定した時間以下の作業者は除外する。"""
    threshold_task_count: Optional[int] = None
    """作業したタスク数の閾値。作業したタスク数が指定した数以下作業者は除外する。"""


class PerformanceUnit(Enum):
    """生産性の単位"""

    ANNOTATION_COUNT = "annotation_count"
    INPUT_DATA_COUNT = "input_data_count"


class ProductivityType(Enum):
    """生産性情報の種類"""

    ANNOTATION = "annotation"
    """教師付"""
    INSPECTION_ACCEPTANCE = "inspection_acceptance"
    """検査または受入"""


ThresholdInfoSettings = Dict[Tuple[str, ProductivityType], ThresholdInfo]
"""
閾値の設定情報
key: tuple(ディレクトリ名, 生産性の種類)
value: 閾値情報
"""


class CollectingPerformanceInfo:
    """
    メンバごとの生産性と品質.csv からパフォーマンスの指標となる情報を収集します。

    Args:
        worktime_type: 作業時間の種類
        performance_unit: 生産性の単位
        threshold_info: 閾値の情報
        threshold_infos_per_project: プロジェクトごとの閾値の情報。`threshold_info`より優先される
    """

    def __init__(
        self,
        worktime_type: WorktimeColumn,
        performance_unit: PerformanceUnit,
        threshold_info: ThresholdInfo,
        threshold_infos_per_project: ThresholdInfoSettings,
    ) -> None:
        self.worktime_type = worktime_type
        self.performance_unit = performance_unit
        self.threshold_info = threshold_info
        self.threshold_infos_per_project = threshold_infos_per_project

    def get_threshold_info(self, project_title: str, productivity_type: ProductivityType) -> ThresholdInfo:
        """指定したプロジェクト名に対応する、閾値情報を取得する。"""
        global_info = self.threshold_info
        local_info = self.threshold_infos_per_project.get((project_title, productivity_type))
        if local_info is None:
            return global_info

        worktime = (
            local_info.threshold_worktime
            if local_info.threshold_worktime is not None
            else global_info.threshold_worktime
        )
        task_count = (
            local_info.threshold_task_count
            if local_info.threshold_task_count is not None
            else global_info.threshold_task_count
        )

        return ThresholdInfo(threshold_worktime=worktime, threshold_task_count=task_count)

    def filter_df_with_threshold(self, df, phase: TaskPhase, threshold_info: ThresholdInfo):
        if threshold_info.threshold_worktime is not None:
            df = df[df[(self.worktime_type.value, phase.value)] > threshold_info.threshold_worktime]

        if threshold_info.threshold_task_count is not None:
            df = df[df[("task_count", phase.value)] > threshold_info.threshold_task_count]

        return df

    def join_annotation_productivity(
        self, df: pandas.DataFrame, df_performance: pandas.DataFrame, project_title: str, threshold_info: ThresholdInfo
    ) -> pandas.DataFrame:
        """教師付生産性の指標を抽出してdfにjoinする"""
        phase = TaskPhase.ANNOTATION

        df_joined = df_performance

        df_joined = self.filter_df_with_threshold(df_joined, phase, threshold_info=threshold_info)

        df_tmp = df_joined[[(f"{self.worktime_type.value}/{self.performance_unit.value}", phase.value)]]
        df_tmp.columns = pandas.MultiIndex.from_tuples(
            [(project_title, f"{self.worktime_type.value}/{self.performance_unit.value}__{phase.value}")]
        )
        return df.join(df_tmp)

    def join_inspection_acceptance_productivity(
        self, df: pandas.DataFrame, df_performance: pandas.DataFrame, project_title: str, threshold_info: ThresholdInfo
    ) -> pandas.DataFrame:
        """検査,受入生産性の指標を抽出してdfにjoinする"""

        def _join_inspection():
            phase = TaskPhase.INSPECTION
            if (f"{self.worktime_type.value}/{self.performance_unit.value}", phase.value) not in df_performance.columns:
                return df

            df_joined = df_performance
            df_joined = self.filter_df_with_threshold(df_joined, phase, threshold_info=threshold_info)

            df_tmp = df_joined[[(f"{self.worktime_type.value}/{self.performance_unit.value}", phase.value)]]
            df_tmp.columns = pandas.MultiIndex.from_tuples(
                [(project_title, f"{self.worktime_type.value}/{self.performance_unit.value}__{phase.value}")]
            )

            return df.join(df_tmp)

        def _join_acceptance():
            phase = TaskPhase.ACCEPTANCE
            if (f"{self.worktime_type.value}/{self.performance_unit.value}", phase.value) not in df_performance.columns:
                return df

            df_joined = df_performance
            df_joined = self.filter_df_with_threshold(df_joined, phase, threshold_info=threshold_info)

            df_tmp = df_joined[[(f"{self.worktime_type.value}/{self.performance_unit.value}", phase.value)]]
            df_tmp.columns = pandas.MultiIndex.from_tuples(
                [(project_title, f"{self.worktime_type.value}/{self.performance_unit.value}__{phase.value}")]
            )

            return df.join(df_tmp)

        df = _join_inspection()
        df = _join_acceptance()

        return df

    def join_quality_with_task_rejected_count(
        self, df: pandas.DataFrame, df_performance: pandas.DataFrame, project_title: str, threshold_info: ThresholdInfo
    ) -> pandas.DataFrame:
        """タスクの差し戻し回数を品質の指標にしたDataFrameを生成する。"""
        df_joined = df_performance

        df_joined = self.filter_df_with_threshold(df_joined, phase=TaskPhase.ANNOTATION, threshold_info=threshold_info)

        df_tmp = df_joined[[("rejected_count/task_count", "annotation")]]

        df_tmp.columns = pandas.MultiIndex.from_tuples([(project_title, "rejected_count/task_count")])
        return df.join(df_tmp)

    def join_quality_with_inspection_comment(
        self, df: pandas.DataFrame, df_performance: pandas.DataFrame, project_title: str, threshold_info: ThresholdInfo
    ) -> pandas.DataFrame:
        """検査コメント数を品質の指標にしたDataFrameを生成する。"""

        df_joined = df_performance

        df_joined = self.filter_df_with_threshold(df_joined, phase=TaskPhase.ANNOTATION, threshold_info=threshold_info)

        df_tmp = df_joined[[(f"pointed_out_inspection_comment_count/{self.performance_unit.value}", "annotation")]]

        df_tmp.columns = pandas.MultiIndex.from_tuples(
            [(project_title, f"pointed_out_inspection_comment_count/{self.performance_unit.value}")]
        )
        return df.join(df_tmp)

    def create_rating_df(
        self,
        df_user: pandas.DataFrame,
        target_dir: Path,
    ) -> ResultDataframe:
        """対象ディレクトリから、評価対象の指標になる情報を取得します。"""
        df_annotation_productivity = df_user
        df_inspection_acceptance_productivity = df_user
        df_quality_per_task = df_user
        df_quality_per_annotation = df_user

        project_dir_list: list[ProjectDir] = []
        for p_project_dir in target_dir.iterdir():
            if not p_project_dir.is_dir():
                continue

            project_title = p_project_dir.name
            project_dir = ProjectDir(p_project_dir)
            project_dir_list.append(project_dir)

            try:
                user_performance = project_dir.read_user_performance()
            except Exception:
                logger.warning(f"{project_dir}からメンバごとの生産性と品質を読み込むのに失敗しました。", exc_info=True)
                continue

            df_performance = user_performance.df.copy()
            df_performance.set_index("user_id", inplace=True)

            annotation_threshold_info = self.get_threshold_info(project_title, ProductivityType.ANNOTATION)
            df_annotation_productivity = self.join_annotation_productivity(
                df_annotation_productivity,
                df_performance,
                project_title=project_title,
                threshold_info=annotation_threshold_info,
            )

            df_quality_per_task = self.join_quality_with_task_rejected_count(
                df_quality_per_task,
                df_performance,
                project_title=project_title,
                threshold_info=annotation_threshold_info,
            )
            df_quality_per_annotation = self.join_quality_with_inspection_comment(
                df_quality_per_annotation,
                df_performance,
                project_title=project_title,
                threshold_info=annotation_threshold_info,
            )

            # 閾値が教師付と検査/受入で別れている理由：作業を評価するのに必要な作業時間/タスク数は、教師付作業とは異なるため
            inspection_acceptance_threshold_info = self.get_threshold_info(
                project_title, ProductivityType.INSPECTION_ACCEPTANCE
            )
            df_inspection_acceptance_productivity = self.join_inspection_acceptance_productivity(
                df_inspection_acceptance_productivity,
                df_performance,
                project_title=project_title,
                threshold_info=inspection_acceptance_threshold_info,
            )

        # プロジェクトの生産性と品質のDataFrameを生成する
        project_performance = ProjectPerformance.from_project_dirs(project_dir_list)
        project_actual_worktime = ProjectWorktimePerMonth.from_project_dirs(
            project_dir_list, WorktimeColumn.ACTUAL_WORKTIME_HOUR
        )
        project_monitored_worktime = ProjectWorktimePerMonth.from_project_dirs(
            project_dir_list, WorktimeColumn.MONITORED_WORKTIME_HOUR
        )
        return ResultDataframe(
            annotation_productivity=df_annotation_productivity.reset_index(),
            inspection_acceptance_productivity=df_inspection_acceptance_productivity.reset_index(),
            quality_with_task_rejected_count=df_quality_per_task.reset_index(),
            quality_with_inspection_comment=df_quality_per_annotation.reset_index(),
            project_performance=project_performance,
            project_actual_worktime=project_actual_worktime,
            project_monitored_worktime=project_monitored_worktime,
        )


def to_rank(series: pandas.Series) -> pandas.Series:
    quantile = list(series.quantile([0.25, 0.5, 0.75]))

    def _to_point(value):
        if numpy.isnan(value):
            return numpy.nan
        elif value < quantile[0]:
            return "A"
        elif quantile[0] <= value < quantile[1]:
            return "B"
        elif quantile[1] <= value < quantile[2]:
            return "C"
        elif quantile[2] <= value:
            return "D"
        else:
            return numpy.nan

    if len([v for v in series if not numpy.isnan(v)]) >= 4:
        return series.map(_to_point)
    else:
        return pandas.Series([numpy.nan] * len(series))


def to_deviation(series: pandas.Series, threshold_deviation_user_count: Optional[int] = None) -> pandas.Series:
    if series.count() == 0 or (
        threshold_deviation_user_count is not None and series.count() <= threshold_deviation_user_count
    ):
        return pandas.Series([numpy.nan] * len(series))
    else:
        std = series.std(ddof=0)
        mean = series.mean()
        if std != 0.0:
            return series.map(lambda x: (x - mean) / std * 10 + 50)
        else:
            return series.map(lambda x: 50 if not numpy.isnan(x) else numpy.nan)


def create_rank_df(df: pandas.DataFrame, *, user_ids: Optional[Collection[str]] = None) -> pandas.DataFrame:
    df_rank = df.copy()
    for col in df.columns[3:]:
        df_rank[col] = to_rank(df[col])

    if user_ids is not None:
        return df_rank[df_rank[("user_id", "")].isin(user_ids)]
    else:
        return df_rank


def create_deviation_df(
    df: pandas.DataFrame,
    *,
    threshold_deviation_user_count: Optional[int] = None,
    user_ids: Optional[Collection[str]] = None,
) -> pandas.DataFrame:
    """偏差値が格納されたDataFrameを返す。

    Args:
        df (pandas.DataFrame):
        threshold_deviation_user_count: プロジェクト内の作業者がしきい値以下であれば、偏差値を算出しない。
        user_ids (Optional[Set[str]], optional): 指定してあればuser_idで絞り込む

    Returns:
        pandas.DataFrame: [description]
    """
    df_rank = df.copy()
    user_columns = df.columns[0:3]
    project_columns = df.columns[3:]
    for col in project_columns:
        df_rank[col] = to_deviation(df[col], threshold_deviation_user_count)

    df_rank["mean_of_deviation"] = df_rank[project_columns].mean(axis=1)
    df_rank["count_of_project"] = df_rank[project_columns].count(axis=1)
    df = df_rank[list(user_columns) + [("mean_of_deviation", ""), ("count_of_project", "")] + list(project_columns)]
    if user_ids is not None:
        return df[df[("user_id", "")].isin(user_ids)]
    else:
        return df


def create_basic_statistics_df(df: pandas.DataFrame) -> pandas.DataFrame:
    df_stat = df.describe().T
    return df_stat


def create_user_df(target_dir: Path) -> pandas.DataFrame:
    """
    "メンバごとの生産性と品質.csv"から、ユーザのDataFrameを作成する。

    Args:
        target_dir:

    Returns:
        ユーザのDataFrame. columnは("username", ""), ("biography", "") , indexが"user_id"

    """
    all_user_list: List[Dict[str, Any]] = []
    for p_project_dir in target_dir.iterdir():
        if not p_project_dir.is_dir():
            continue

        project_dir = ProjectDir(p_project_dir)

        try:
            user_performance = project_dir.read_user_performance()
        except Exception:
            logger.warning(f"{project_dir}からメンバごとの生産性と品質を読み込むのに失敗しました。", exc_info=True)
            continue

        tmp_df_user = user_performance.df[[("user_id", ""), ("username", ""), ("biography", "")]].copy()
        all_user_list.extend(tmp_df_user.to_dict("records"))

    index = pandas.MultiIndex.from_tuples([("user_id", ""), ("username", ""), ("biography", "")])
    df_user = pandas.DataFrame(all_user_list, columns=index)
    df_user.drop_duplicates(inplace=True)
    return df_user.sort_values("user_id").set_index("user_id")


class WritingCsv:
    def __init__(
        self, threshold_deviation_user_count: Optional[int] = None, user_ids: Optional[Collection[str]] = None
    ) -> None:
        self.threshold_deviation_user_count = threshold_deviation_user_count
        self.user_ids = user_ids

    def write(self, df: pandas.DataFrame, csv_basename: str, output_dir: Path):

        print_csv(df, str(output_dir / f"{csv_basename}.csv"))

        # 偏差値のCSVを出力
        print_csv(
            create_deviation_df(
                df, threshold_deviation_user_count=self.threshold_deviation_user_count, user_ids=self.user_ids
            ),
            str(output_dir / f"{csv_basename}_deviation.csv"),
        )

        # A,B,C,DでランクされたCSVを出力
        print_csv(
            create_rank_df(df, user_ids=self.user_ids),
            str(output_dir / f"{csv_basename}_rank.csv"),
        )

        # プロジェクトごとのサマリを出力
        print_csv(
            create_basic_statistics_df(df),
            str(output_dir / f"{csv_basename}_summary.csv"),
            to_csv_kwargs={"index": True},
        )


class WritePerformanceRatingCsv(AbstractCommandLineWithoutWebapiInterface):
    @staticmethod
    def get_threshold_infos_per_project(dict_threshold_settings: Optional[dict[str, Any]]) -> ThresholdInfoSettings:
        if dict_threshold_settings is None:
            return {}

        result = {}
        for dirname, infos in dict_threshold_settings.items():
            for str_productivity_type, info in infos.items():
                productivity_type = ProductivityType(str_productivity_type)
                threshold_info = ThresholdInfo.from_dict(info)
                result[(dirname, productivity_type)] = threshold_info
        return result

    def main(self) -> None:
        args = self.args

        target_dir: Path = args.dir
        user_id_list = get_list_from_args(args.user_id) if args.user_id is not None else None
        df_user = create_user_df(target_dir)

        dict_threshold_settings = get_json_from_args(args.threshold_settings)
        threshold_infos_per_project = self.get_threshold_infos_per_project(dict_threshold_settings)

        performance_unit = PerformanceUnit(args.performance_unit)
        result = CollectingPerformanceInfo(
            worktime_type=WorktimeColumn.ACTUAL_WORKTIME_HOUR,
            performance_unit=performance_unit,
            threshold_info=ThresholdInfo(
                threshold_worktime=args.threshold_worktime,
                threshold_task_count=args.threshold_task_count,
            ),
            threshold_infos_per_project=threshold_infos_per_project,
        ).create_rating_df(
            df_user,
            target_dir,
        )

        output_dir: Path = args.output_dir

        obj = WritingCsv(threshold_deviation_user_count=args.threshold_deviation_user_count, user_ids=user_id_list)

        # 教師付生産性に関するファイルを出力
        obj.write(
            result.annotation_productivity,
            csv_basename="annotation_productivity",
            output_dir=output_dir / "annotation_productivity",
        )
        # 検査/受入生産性に関するファイルを出力
        obj.write(
            result.inspection_acceptance_productivity,
            csv_basename="inspection_acceptance_productivity",
            output_dir=output_dir / "inspection_acceptance_productivity",
        )
        # タスクの差し戻し回数を品質の指標にしたファイルを出力
        obj.write(
            result.quality_with_task_rejected_count,
            csv_basename="annotation_quality_task_rejected_count",
            output_dir=output_dir / "annotation_quality_task_rejected_count",
        )
        # 検査コメント数を品質の指標にしたファイルを出力
        obj.write(
            result.quality_with_inspection_comment,
            csv_basename="annotation_quality_inspection_comment",
            output_dir=output_dir / "annotation_quality_inspection_comment",
        )

        result.project_performance.to_csv(output_dir / "プロジェクごとの生産性と品質.csv")
        result.project_actual_worktime.to_csv(output_dir / "プロジェクごとの毎月の実績作業時間.csv")
        result.project_monitored_worktime.to_csv(output_dir / "プロジェクごとの毎月の計測作業時間.csv")


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--dir",
        type=Path,
        required=True,
        help=f"プロジェクトディレクトリが存在するディレクトリを指定してください。",
    )

    parser.add_argument(
        "-u",
        "--user_id",
        type=str,
        nargs="+",
        help="評価対象のユーザのuser_idを指定してください。" " ``file://`` を先頭に付けると、user_idの一覧が記載されたファイルを指定できます。",
    )

    parser.add_argument(
        "--performance_unit",
        type=str,
        choices=[e.value for e in PerformanceUnit],
        default=PerformanceUnit.ANNOTATION_COUNT.value,
        help="評価指標の単位",
    )

    parser.add_argument(
        "--threshold_worktime",
        type=int,
        help="作業時間の閾値。指定した時間以下の作業者は除外する。",
    )
    parser.add_argument(
        "--threshold_task_count",
        type=int,
        help="作業したタスク数の閾値。作業したタスク数が指定した数以下作業者は除外する。 ",
    )
    parser.add_argument(
        "--threshold_deviation_user_count",
        type=int,
        default=3,
        help="偏差値を出す際、プロジェクト内の作業者がしきい値以下であれば、偏差値を算出しない。",
    )

    THRESHOLD_SETTINGS_SAMPLE = {
        "dirname1": {"annotation": {"threshold_worktime": 20}},
        "dirname2": {"inspection_acceptance": {"threshold_task_count": 5}},
    }  # noqa: E501
    parser.add_argument(
        "--threshold_settings",
        type=str,
        help="JSON形式で、ディレクトリ名ごとに閾値を指定してください。\n" f"(ex) ``{THRESHOLD_SETTINGS_SAMPLE}``",
    )

    parser.add_argument("-o", "--output_dir", required=True, type=Path, help="出力ディレクトリ")

    parser.set_defaults(subcommand_func=main)


def main(args):
    WritePerformanceRatingCsv(args).main()


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None):
    subcommand_name = "write_performance_rating_csv"
    subcommand_help = "プロジェクトごとユーザごとにパフォーマンスを評価できる複数のCSVを出力します。"
    description = "プロジェクトごとユーザごとにパフォーマンスを評価できる複数のCSVを出力します。"
    parser = annofabcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=description)
    parse_args(parser)
    return parser
