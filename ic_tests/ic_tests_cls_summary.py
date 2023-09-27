import os
import datetime as dt
import multiprocessing as mp
import sqlite3
import numpy as np
import pandas as pd
from struct_lib.returns_and_exposure import get_lib_struct_ic_test
from skyrim.whiterun import SetFontGreen
from skyrim.falkreath import CLib1Tab1, CManagerLibReader
from skyrim.winterhold import plot_lines


class CICTestsSummary(object):
    def __init__(self, proc_num: int, ic_tests_dir: str, ic_tests_summary_dir: str, neutral_tag: str):
        self.ic_tests_dir = ic_tests_dir
        self.ic_tests_summary_dir = ic_tests_summary_dir
        self.neutral_tag = neutral_tag
        self.proc_num = proc_num

    def _get_ic_test_struct(self, factor: str) -> CLib1Tab1:
        if self.neutral_tag.upper() == "RAW":
            return get_lib_struct_ic_test(factor)
        elif self.neutral_tag.upper() == "NEU":
            return get_lib_struct_ic_test(f"{factor}_neu")
        else:
            pass

    def _get_summary_file_id(self) -> str:
        return f"ic_statistics-{self.neutral_tag}"

    def _get_cumsum_file_id(self, factor_class: str) -> str:
        return f"ic_cumsum-{self.neutral_tag}-{factor_class}"

    def _get_selected_factors_cumsum_ic_id(self) -> str:
        return f"ic_selected_factors-{self.neutral_tag}"

    def __get_ic_test_data(self, factor: str) -> pd.DataFrame:
        ic_test_lib_struct = self._get_ic_test_struct(factor)
        ic_test_lib = CManagerLibReader(t_db_name=ic_test_lib_struct.m_lib_name, t_db_save_dir=self.ic_tests_dir)
        ic_test_lib.set_default(ic_test_lib_struct.m_tab.m_table_name)
        ic_df = ic_test_lib.read(t_value_columns=["trade_date", "value"]).set_index("trade_date")
        ic_test_lib.close()
        ic_df.rename(mapper={"value": "ic"}, axis=1, inplace=True)
        return ic_df

    @staticmethod
    def __get_factor_statistics(factor: str, factor_sub_class: str, factor_class: str, ic_df: pd.DataFrame) -> dict[str, float | int]:
        __days_per_year = 240
        obs = len(ic_df)
        mu = ic_df["ic"].mean()
        sd = ic_df["ic"].std()
        icir = mu / sd * np.sqrt(__days_per_year)
        ic_q000 = np.percentile(ic_df["ic"], q=0)
        ic_q025 = np.percentile(ic_df["ic"], q=25)
        ic_q050 = np.percentile(ic_df["ic"], q=50)
        ic_q075 = np.percentile(ic_df["ic"], q=75)
        ic_q100 = np.percentile(ic_df["ic"], q=100)
        return {
            "factor": factor,
            "subClass": factor_sub_class,
            "class": factor_class,
            "obs": obs,
            "ICMean": mu,
            "ICStd": sd,
            "ICIR": icir,
            "qI": ic_q000,
            "qII": ic_q025,
            "qIII": ic_q050,
            "qIV": ic_q075,
            "qV": ic_q100,
        }

    def _get_factor_summary(self, arg_comb: tuple[str, str, str]) -> dict:
        factor, factor_subclass, factor_class = arg_comb
        try:
            ic_df = self.__get_ic_test_data(factor)
            res = self.__get_factor_statistics(factor, factor_subclass, factor_class, ic_df)
            return res
        except sqlite3.OperationalError:
            print(arg_comb)
            return {}

    def get_summary_mp(self, factors: tuple[str], factors_classification: dict[str, tuple[str, str]]):
        t0 = dt.datetime.now()
        arg_combs = [(factor, *factors_classification[factor]) for factor in factors]
        pool = mp.Pool(processes=self.proc_num)
        statistics = pool.map(self._get_factor_summary, arg_combs)
        pool.close()
        pool.join()

        statistics_df = pd.DataFrame(statistics).sort_values(["class", "factor"], ascending=True)
        statistics_file = self._get_summary_file_id() + ".csv"
        statistics_path = os.path.join(self.ic_tests_summary_dir, statistics_file)
        statistics_df.to_csv(statistics_path, index=False, float_format="%.4f")
        t1 = dt.datetime.now()
        print(f"... {SetFontGreen('IC-tests summary')} calculated")
        print(f"... total time consuming:{SetFontGreen(f'{(t1 - t0).total_seconds():.2f}')} seconds")
        return 0

    def _get_factor_cumsum(self, factor_class: str, factors: tuple[str], selected_factors_pool: list[str]):
        ic_cumsum_data = {}
        for factor in factors:
            if factor in selected_factors_pool:
                ic_df = self.__get_ic_test_data(factor)
                ic_cumsum_data[factor] = ic_df["ic"].cumsum()
        if ic_cumsum_data:
            ic_cumsum_df = pd.DataFrame(ic_cumsum_data)
            plot_lines(
                t_plot_df=ic_cumsum_df, t_fig_name=self._get_cumsum_file_id(factor_class),
                t_save_dir=self.ic_tests_summary_dir, t_colormap="jet",
            )
            ic_cumsum_file = self._get_cumsum_file_id(factor_class) + ".csv"
            ic_cumsum_path = os.path.join(self.ic_tests_summary_dir, ic_cumsum_file)
            ic_cumsum_df.to_csv(ic_cumsum_path, index_label="trade_date", float_format="%.6f")
        return 0

    def get_cumsum_mp(self, factors_group: dict[str, list[str]], selected_factors_pool: list[str]):
        t0 = dt.datetime.now()
        pool = mp.Pool(processes=self.proc_num)
        for factor_class, factors in factors_group.items():
            pool.apply_async(self._get_factor_cumsum, args=(factor_class, factors, selected_factors_pool))
        pool.close()
        pool.join()
        t1 = dt.datetime.now()
        print(f"... {SetFontGreen('IC-tests plot cumsum for all factors by class')} calculated")
        print(f"... total time consuming:{SetFontGreen(f'{(t1 - t0).total_seconds():.2f}')} seconds")
        return 0

    def plot_selected_factors_cumsum(self, factors: tuple[str]):
        ic_cumsum_data = {}
        for factor in factors:
            ic_df = self.__get_ic_test_data(factor)
            ic_cumsum_data[factor] = ic_df["ic"].cumsum()
        ic_cumsum_df = pd.DataFrame(ic_cumsum_data)
        plot_lines(
            t_plot_df=ic_cumsum_df, t_fig_name=self._get_selected_factors_cumsum_ic_id(),
            t_save_dir=self.ic_tests_summary_dir, t_colormap="jet",
        )
        ic_cumsum_file = self._get_selected_factors_cumsum_ic_id() + ".csv"
        ic_cumsum_path = os.path.join(self.ic_tests_summary_dir, ic_cumsum_file)
        ic_cumsum_df.to_csv(ic_cumsum_path, index_label="trade_date", float_format="%.6f")
        print(f"... {SetFontGreen('IC-tests plot cumsum for selected factors')}")
        return 0


def cal_ic_tests_comparison(ic_tests_summary_dir: str):
    pd.set_option("display.float_format", "{:.4f}".format)
    pd.set_option("display.width", 0)
    pd.set_option("display.max_rows", 1000)

    statistics_file = "ic_statistics-RAW.csv"
    statistics_path = os.path.join(ic_tests_summary_dir, statistics_file)
    statistics_df = pd.read_csv(statistics_path)
    statistics_df = statistics_df[["class", "factor", "ICMean", "ICStd", "ICIR"]]

    statistics_neutral_file = f"ic_statistics-NEU.csv"
    statistics_neutral_path = os.path.join(ic_tests_summary_dir, statistics_neutral_file)
    statistics_neutral_df = pd.read_csv(statistics_neutral_path)
    statistics_neutral_df = statistics_neutral_df[["class", "factor", "ICMean", "ICStd", "ICIR"]]

    comparison_df = pd.merge(
        left=statistics_df, right=statistics_neutral_df,
        on=["class", "factor"],
        how="outer", suffixes=("", "(SEC-NEU)")
    )
    comparison_file = "ic_statistics-comparison.csv"
    comparison_path = os.path.join(ic_tests_summary_dir, comparison_file)
    comparison_df.to_csv(comparison_path, index=False, float_format="%.4f")

    print(comparison_df)
    return 0
