import os
import datetime as dt
import itertools as ittl
import multiprocessing as mp
import pandas as pd
from skyrim.riften import CNAV
from skyrim.whiterun import SetFontGreen
from skyrim.winterhold2 import CPlotLines
from struct_lib.portfolios import get_nav_df


class CEvaluation(object):
    def __init__(self, eval_id: str, simu_ids: list[str],
                 indicators: list[str],
                 simu_save_dir: str, eval_save_dir: str, annual_risk_free_rate: float):
        self.simu_ids = simu_ids
        self.indicators = indicators
        self.simu_save_dir = simu_save_dir
        self.eval_save_dir = eval_save_dir
        self.annual_risk_free_rate = annual_risk_free_rate
        self.eval_id = eval_id

    def __get_portfolio_net_ret(self) -> pd.DataFrame:
        portfolios_net_ret_data = {}
        for simu_id in self.simu_ids:
            nav_df = get_nav_df(simu_id, self.simu_save_dir)
            portfolios_net_ret_data[simu_id] = nav_df["netRet"]
        portfolios_net_ret_df = pd.DataFrame(portfolios_net_ret_data)
        return portfolios_net_ret_df

    def __get_performance_evaluation(self, simu_id: str) -> dict:
        simu_nav_df = get_nav_df(simu_id, self.simu_save_dir)
        nav = CNAV(t_raw_nav_srs=simu_nav_df["netRet"], t_annual_rf_rate=self.annual_risk_free_rate, t_type="RET")
        nav.cal_all_indicators(t_method="linear")
        return nav.to_dict(t_type="eng")

    def _add_args_to(self, res: dict, simu_id: str):
        # res.update(kwargs)
        pass

    def _set_index(self, eval_df: pd.DataFrame):
        # eval_df.set_index(indexes:list[str], inplace=True)
        pass

    def __save(self, res_data: list[dict], printout: bool = False):
        eval_df = pd.DataFrame(res_data)
        self._set_index(eval_df)
        eval_file = f"eval-{self.eval_id}.csv"
        eval_path = os.path.join(self.eval_save_dir, eval_file)
        eval_df[self.indicators].to_csv(eval_path, float_format="%.4f")
        if printout:
            print(eval_df[self.indicators])
        return 0

    def main(self, printout: bool = False):
        res_data = []
        for simu_id in self.simu_ids:
            res = self.__get_performance_evaluation(simu_id)
            self._add_args_to(res, simu_id)
            res_data.append(res)
        self.__save(res_data, printout)
        print(f"... @ {SetFontGreen(f'{dt.datetime.now()}')} nav evaluation for {SetFontGreen(self.eval_id)} calculated")
        return 0

    def plot_nav(self):
        portfolios_net_ret_df = self.__get_portfolio_net_ret()
        portfolios_nav_df = (portfolios_net_ret_df + 1).cumprod()
        artist = CPlotLines(plot_df=portfolios_nav_df, fig_name="portfolios_nav",
                            line_color=["#708090", "#000000", "#4169E1", "#8B0000"], line_style=["--", "--", "--", "-"],
                            fig_save_dir=self.eval_save_dir, xtick_label_size=16, ytick_label_size=16)
        artist.plot()
        return 0

    def plot_nav_by_year(self):
        portfolios_net_ret_df = self.__get_portfolio_net_ret()
        portfolios_net_ret_df["trade_year"] = portfolios_net_ret_df.index.map(lambda _: _[0:4])
        for trade_year, trade_year_df in portfolios_net_ret_df.groupby(by="trade_year"):
            trade_year_ret = trade_year_df.drop("trade_year", axis=1)
            trade_year_nav = (trade_year_ret + 1).cumprod()
            artist = CPlotLines(plot_df=trade_year_nav, fig_name=f"portfolios_nav_{trade_year}",
                                line_color=["#708090", "#000000", "#4169E1", "#8B0000"], line_style=["--", "--", "--", "-"],
                                fig_save_dir=self.eval_save_dir, xtick_label_size=16, ytick_label_size=16)
            artist.plot()
        return 0

    def eval_by_year(self, printout: bool = False):
        summary_data = {simu_id: {} for simu_id in self.simu_ids}
        portfolios_net_ret_df = self.__get_portfolio_net_ret()
        portfolios_net_ret_df["trade_year"] = portfolios_net_ret_df.index.map(lambda _: _[0:4])
        for trade_year, trade_year_df in portfolios_net_ret_df.groupby(by="trade_year"):
            for simu_id in self.simu_ids:
                portfolio_trade_year_ret = trade_year_df[simu_id]
                nav = CNAV(portfolio_trade_year_ret, t_annual_rf_rate=self.annual_risk_free_rate,
                           t_type="RET")
                nav.cal_all_indicators()
                summary_data[simu_id][trade_year] = nav.to_dict(t_type="eng")
        for simu_id, simu_id_data in summary_data.items():
            summary_df = pd.DataFrame.from_dict(simu_id_data, orient="index")
            summary_file = f"eval-portfolios-by-year-{simu_id}.csv"
            summary_path = os.path.join(self.eval_save_dir, summary_file)
            summary_df[self.indicators].to_csv(summary_path, index_label="tradeYear", float_format="%.2f")
            if printout:
                print(summary_df[self.indicators])
        return 0


class CEvaluationWithFactorClass(CEvaluation):
    def __init__(self, factors_classification: dict[str, str], **kwargs):
        super().__init__(**kwargs)
        self.factors_classification = factors_classification

    def _add_args_to(self, res: dict, simu_id: str):
        factor = simu_id.split("_")[0]
        factor_class = self.factors_classification[factor]
        res.update({"factor": factor, "factor_class": factor_class})
        return 0

    def _set_index(self, eval_df: pd.DataFrame):
        eval_df.set_index(["factor", "factor_class"], inplace=True)
        return 0


class CEvaluationPortfolio(CEvaluation):
    def _add_args_to(self, res: dict, simu_id: str):
        res.update({"portfolio": simu_id})
        return 0

    def _set_index(self, eval_df: pd.DataFrame):
        eval_df.set_index(["portfolio"], inplace=True)
        return 0


def eval_hedge_ma_mp(proc_num: int, factors: list[str], factors_neutral: list[str], uni_props: tuple[float], mov_ave_wins: tuple[int], **kwargs):
    t0 = dt.datetime.now()
    pool = mp.Pool(processes=proc_num)
    for (fs, fid), uni_prop, mov_ave_win in ittl.product([(factors, "raw"), (factors_neutral, "neu")], uni_props, mov_ave_wins):
        uni_prop_lbl = f"UHP{int(uni_prop * 10):02d}"
        ma_lbl = f"MA{mov_ave_win:02d}"
        eval_id = f"factors_{fid}_{uni_prop_lbl}_{ma_lbl}"
        simu_ids = [f"{_}_{uni_prop_lbl}_{ma_lbl}" for _ in fs]
        agent_eval = CEvaluationWithFactorClass(eval_id=eval_id, simu_ids=simu_ids, **kwargs)
        pool.apply_async(agent_eval.main)
    pool.close()
    pool.join()
    t1 = dt.datetime.now()
    print(f"... {SetFontGreen('Summary for Hedge Test')} calculated")
    print(f"... total time consuming:{SetFontGreen(f'{(t1 - t0).total_seconds():.2f}')} seconds")
    return 0


def concat_eval_results(uni_props: tuple[float], eval_save_dir: str):
    raw_dfs, neu_dfs = [], []
    for uni_prop in uni_props:
        uni_prop_lbl = f"UHP{int(uni_prop * 10):02d}"
        sub_eval_raw_file = f"eval-factors_raw_{uni_prop_lbl}.csv"
        sub_eval_neu_file = f"eval-factors_neu_{uni_prop_lbl}.csv"
        sub_eval_raw_path = os.path.join(eval_save_dir, sub_eval_raw_file)
        sub_eval_neu_path = os.path.join(eval_save_dir, sub_eval_neu_file)
        sub_eval_raw_df = pd.read_csv(sub_eval_raw_path)
        sub_eval_neu_df = pd.read_csv(sub_eval_neu_path)
        sub_eval_raw_df["uni_prop"] = uni_prop
        sub_eval_neu_df["uni_prop"] = uni_prop
        raw_dfs.append(sub_eval_raw_df)
        neu_dfs.append(sub_eval_neu_df)

    raw_df_concat = pd.concat(raw_dfs, axis=0, ignore_index=True).sort_values(by=["factor", "sharpe_ratio"], ascending=[True, False])
    neu_df_concat = pd.concat(neu_dfs, axis=0, ignore_index=True).sort_values(by=["factor", "sharpe_ratio"], ascending=[True, False])
    raw_concat_file = os.path.join(eval_save_dir, "eval-factors_raw-concat.csv")
    neu_concat_file = os.path.join(eval_save_dir, "eval-factors_neu-concat.csv")
    raw_df_concat.to_csv(raw_concat_file, index=False, float_format="%.2f")
    neu_df_concat.to_csv(neu_concat_file, index=False, float_format="%.2f")
    return 0


def concat_eval_ma_results(uni_props: tuple[float], mov_ave_wins: tuple[int], eval_save_dir: str):
    raw_dfs, neu_dfs = [], []
    for uni_prop, mov_ave_win in ittl.product(uni_props, mov_ave_wins):
        uni_prop_lbl = f"UHP{int(uni_prop * 10):02d}"
        ma_lbl = f"MA{mov_ave_win:02d}"
        sub_eval_raw_file = f"eval-factors_raw_{uni_prop_lbl}_{ma_lbl}.csv"
        sub_eval_neu_file = f"eval-factors_neu_{uni_prop_lbl}_{ma_lbl}.csv"
        sub_eval_raw_path = os.path.join(eval_save_dir, sub_eval_raw_file)
        sub_eval_neu_path = os.path.join(eval_save_dir, sub_eval_neu_file)
        sub_eval_raw_df = pd.read_csv(sub_eval_raw_path)
        sub_eval_neu_df = pd.read_csv(sub_eval_neu_path)
        sub_eval_raw_df["uni_prop"] = uni_prop
        sub_eval_neu_df["uni_prop"] = uni_prop
        sub_eval_raw_df["mov_ave_win"] = mov_ave_win
        sub_eval_neu_df["mov_ave_win"] = mov_ave_win
        raw_dfs.append(sub_eval_raw_df)
        neu_dfs.append(sub_eval_neu_df)

    raw_df_concat = pd.concat(raw_dfs, axis=0, ignore_index=True).sort_values(by=["factor", "sharpe_ratio"], ascending=[True, False])
    neu_df_concat = pd.concat(neu_dfs, axis=0, ignore_index=True).sort_values(by=["factor", "sharpe_ratio"], ascending=[True, False])
    raw_concat_file = os.path.join(eval_save_dir, "eval-factors_raw-concat.csv")
    neu_concat_file = os.path.join(eval_save_dir, "eval-factors_neu-concat.csv")
    raw_df_concat.to_csv(raw_concat_file, index=False, float_format="%.2f")
    neu_df_concat.to_csv(neu_concat_file, index=False, float_format="%.2f")
    return 0


def plot_selected_factors_and_uni_prop_ma(
        selected_factors_and_uni_prop_ma: tuple[tuple], neutral_tag: str,
        simu_save_dir: str, eval_save_dir: str):
    nav_data, ret_data = {}, {}
    for factor, uni_prop, mov_ave_win in selected_factors_and_uni_prop_ma:
        uni_prop_lbl = f"UHP{int(uni_prop * 10):02d}"
        ma_lbl = f"MA{mov_ave_win:02d}"
        if neutral_tag == "RAW":
            simu_id = f"{factor}_{uni_prop_lbl}_{ma_lbl}"
        else:
            simu_id = f"{factor}_NEU_{uni_prop_lbl}_{ma_lbl}"
        simu_nav_df = get_nav_df(simu_id, simu_save_dir)
        nav_data[simu_id] = simu_nav_df["nav"]
        ret_data[simu_id] = simu_nav_df["netRet"]
    nav_df, ret_df = pd.DataFrame(nav_data), pd.DataFrame(ret_data)

    # plot all
    artist = CPlotLines(plot_df=nav_df, fig_name=f"selected-factors_and_uni_prop_ma-{neutral_tag}-nav",
                        line_style=["-"] * 6 + ["-."] * 6 + ["--"] * 6,
                        fig_save_dir=eval_save_dir, xtick_label_size=16, ytick_label_size=16)
    artist.plot()

    # plot by year
    ret_df["trade_year"] = ret_df.index.map(lambda z: z[0:4])
    for trade_year, trade_year_ret_df in ret_df.groupby(by="trade_year"):
        trade_year_nav_df = (trade_year_ret_df.drop(labels="trade_year", axis=1) + 1).cumprod()
        artist = CPlotLines(plot_df=trade_year_nav_df, fig_name=f"selected-factors_and_uni_prop_ma-{neutral_tag}-nav-{trade_year}",
                            line_style=["-"] * 6 + ["-."] * 6 + ["--"] * 6,
                            fig_save_dir=eval_save_dir, xtick_label_size=16, ytick_label_size=16)
        artist.plot()

    print(f"... @ {dt.datetime.now()} selected factors and uni-prop for {SetFontGreen(neutral_tag)} plotted")
    return 0
