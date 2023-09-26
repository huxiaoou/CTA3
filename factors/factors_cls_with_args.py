import datetime as dt
import itertools as ittl
import multiprocessing as mp
import numpy as np
import pandas as pd
from skyrim.whiterun import SetFontGreen
from factors.factors_cls_base import (CFactorsWithMajorReturn, CFactorsWithMajorReturnAndArgWin, CFactorsWithMajorReturnAndMarketReturn,
                                      CFactorsWithMajorReturnAndExchangeRate, CFactorsWithMajorReturnAndMacroEconomic)


def cal_rolling_corr(df: pd.DataFrame, x: str, y: str, rolling_window: int) -> pd.Series:
    df["xy"] = (df[x] * df[y]).rolling(window=rolling_window).mean()
    df["xx"] = (df[x] * df[x]).rolling(window=rolling_window).mean()
    df["yy"] = (df[y] * df[y]).rolling(window=rolling_window).mean()
    df["x"] = df[x].rolling(window=rolling_window).mean()
    df["y"] = df[y].rolling(window=rolling_window).mean()

    df["cov_xy"] = df["xy"] - df["x"] * df["y"]
    df["cov_xx"] = df["xx"] - df["x"] * df["x"]
    df["cov_yy"] = df["yy"] - df["y"] * df["y"]

    df.loc[np.abs(df["cov_xx"]) <= 1e-10, "cov_xx"] = 0
    df.loc[np.abs(df["cov_yy"]) <= 1e-10, "cov_yy"] = 0

    df["sqrt_cov_xx_yy"] = np.sqrt(df["cov_xx"] * df["cov_yy"]).fillna(0)
    s = df[["cov_xy", "sqrt_cov_xx_yy"]].apply(
        lambda z: 0 if z["sqrt_cov_xx_yy"] == 0 else z["cov_xy"] / z["sqrt_cov_xx_yy"], axis=1)
    return s


def cal_rolling_beta(df: pd.DataFrame, x: str, y: str, rolling_window: int) -> pd.Series:
    df["xy"] = (df[x] * df[y]).rolling(window=rolling_window).mean()
    df["xx"] = (df[x] * df[x]).rolling(window=rolling_window).mean()
    df["x"] = df[x].rolling(window=rolling_window).mean()
    df["y"] = df[y].rolling(window=rolling_window).mean()
    df["cov_xy"] = df["xy"] - df["x"] * df["y"]
    df["cov_xx"] = df["xx"] - df["x"] * df["x"]
    s = df["cov_xy"] / df["cov_xx"]
    return s


class CFactorsSKEW(CFactorsWithMajorReturnAndArgWin):
    def _set_factor_id(self):
        self.factor_id = f"SKEW{self.arg_win:03d}"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        self._set_base_date(bgn_date, stp_date)
        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", self.base_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "major_return"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)
        s = -df["major_return"].rolling(window=self.arg_win).skew()
        return self.truncate_series(s, bgn_date)


class CFactorsVOL(CFactorsWithMajorReturnAndArgWin):
    def _set_factor_id(self):
        self.factor_id = f"VOL{self.arg_win:03d}"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        self._set_base_date(bgn_date, stp_date)
        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", self.base_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "major_return"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)
        s = df["major_return"].rolling(window=self.arg_win).std() * np.sqrt(240)
        return self.truncate_series(s, bgn_date)


class CFactorsRVOL(CFactorsWithMajorReturnAndArgWin):
    def _set_factor_id(self):
        self.factor_id = f"RVOL{self.arg_win:03d}"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        self._set_base_date(bgn_date, stp_date)
        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", self.base_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "open", "high", "low", "close"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)
        rho = df["high"] / df["open"] - 1
        rhc = df["high"] / df["close"] - 1
        rlo = df["low"] / df["open"] - 1
        rlc = df["low"] / df["close"] - 1
        s2 = (rho * rhc / 2 + rlo * rlc / 2).rolling(window=self.arg_win).mean()
        s = np.sqrt(240 * s2)
        return self.truncate_series(s, bgn_date)


class CFactorsCV(CFactorsWithMajorReturnAndArgWin):
    def _set_factor_id(self):
        self.factor_id = f"CV{self.arg_win:03d}"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        self._set_base_date(bgn_date, stp_date)
        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", self.base_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "major_return"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)
        sd = df["major_return"].rolling(window=self.arg_win).std()
        mu = df["major_return"].rolling(window=self.arg_win).mean()
        s = sd / mu.abs() / np.sqrt(240)
        return self.truncate_series(s, bgn_date)


class CFactorsCTP(CFactorsWithMajorReturnAndArgWin):
    def _set_factor_id(self):
        self.factor_id = f"CTP{self.arg_win:03d}"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        self._set_base_date(bgn_date, stp_date)
        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", self.base_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "volume", "oi", "instru_idx"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)

        df["aver_oi"] = df["oi"].rolling(window=2).mean()
        df["turnover"] = df["volume"] / df["aver_oi"]
        x, y = "turnover", "instru_idx"
        s = -cal_rolling_corr(df=df, x=x, y=y, rolling_window=self.arg_win)
        return self.truncate_series(s, bgn_date)


class CFactorsCVP(CFactorsWithMajorReturnAndArgWin):
    def _set_factor_id(self):
        self.factor_id = f"CVP{self.arg_win:03d}"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        self._set_base_date(bgn_date, stp_date)
        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", self.base_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "volume", "instru_idx"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)

        x, y = "volume", "instru_idx"
        s = -cal_rolling_corr(df=df, x=x, y=y, rolling_window=self.arg_win)
        return self.truncate_series(s, bgn_date)


class CFactorsCSP(CFactorsWithMajorReturnAndArgWin):
    def _set_factor_id(self):
        self.factor_id = f"CSP{self.arg_win:03d}"
        return 0

    def _set_base_date(self, bgn_date: str, stp_date: str):
        iter_dates = self.calendar.get_iter_list(bgn_date, stp_date, True)
        self.base_date = self.calendar.get_next_date(iter_dates[0], -self.arg_win - self._near_short_term + 1)
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        self._set_base_date(bgn_date, stp_date)
        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", self.base_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "major_return", "instru_idx"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)

        df["sigma"] = df["major_return"].rolling(window=self._near_short_term).std()
        x, y = "sigma", "instru_idx"
        s = -cal_rolling_corr(df=df, x=x, y=y, rolling_window=self.arg_win)
        return self.truncate_series(s, bgn_date)


class CFactorsVAL(CFactorsWithMajorReturnAndArgWin):
    def _set_factor_id(self):
        self.factor_id = f"VAL{self.arg_win:03d}"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        self._set_base_date(bgn_date, stp_date)
        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", self.base_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "close"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)

        df["near"] = df["close"].rolling(window=self._near_short_term).mean()
        df["hist"] = df["close"].rolling(window=self.arg_win).mean()
        s = df["near"] / df["hist"] - 1
        return self.truncate_series(s, bgn_date)


class CFactorsBETA(CFactorsWithMajorReturnAndMarketReturn):
    def _set_factor_id(self):
        self.factor_id = f"BETA{self.arg_win:03d}"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        self._set_base_date(bgn_date, stp_date)
        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", self.base_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "major_return"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)

        df["market"] = self.manager_market_return.df["market"]
        s = cal_rolling_beta(df, x="market", y="major_return", rolling_window=self.arg_win)
        return self.truncate_series(s, bgn_date)


class CFactorsCBETA(CFactorsWithMajorReturnAndExchangeRate):
    def _set_factor_id(self):
        self.factor_id = f"CBETA{self.arg_win:03d}"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        self._set_base_date(bgn_date, stp_date)
        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", self.base_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "major_return"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)

        df["exchange"] = self.manager_exchange_rate.df["pct_chg"].fillna(0) / 100
        s = cal_rolling_beta(df, x="exchange", y="major_return", rolling_window=self.arg_win)
        return self.truncate_series(s, bgn_date)


class CFactorsIBETA(CFactorsWithMajorReturnAndMacroEconomic):
    def _set_factor_id(self):
        self.factor_id = f"IBETA{self.arg_win:03d}"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        iter_dates = self.calendar.get_iter_list(bgn_date, stp_date, True)
        bgn_last_month = self.calendar.get_latest_month_from_trade_date(iter_dates[0])
        end_last_month = self.calendar.get_latest_month_from_trade_date(iter_dates[-1])

        arg_win_month = int(self.arg_win / 20)
        base_month = self.calendar.get_next_month(bgn_last_month, -arg_win_month)
        self.base_date = base_month + "01"

        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", self.base_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "major_return"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)

        df["trade_month"] = df.index.map(lambda _: _[0:6])
        month_ret_df = df[["trade_month", "major_return"]].groupby(by="trade_month").apply(lambda z: np.prod(1 + z) - 1)
        filter_month = (month_ret_df.index >= base_month) & (month_ret_df.index < end_last_month)
        selected_month_ret_df: pd.DataFrame = month_ret_df.loc[filter_month].copy()
        selected_month_ret_df["cpi"] = self.manager_macro_economic.df["cpi_rate"] / 100
        selected_month_ret_df["cpi_diff"] = (self.manager_macro_economic.df["cpi_rate"] - self.manager_macro_economic.df["cpi_rate"].shift(1)) / 100
        ms = cal_rolling_beta(selected_month_ret_df, x="cpi_diff", y="major_return", rolling_window=arg_win_month)
        ms = pd.concat([ms, pd.Series({end_last_month: np.nan, iter_dates[-1][0:6]: np.nan})])
        ms_shift = ms.shift(2)
        df = df.merge(right=pd.DataFrame({"cbeta": ms_shift}), left_on="trade_month", right_index=True, how="left")
        s = df["cbeta"]
        return self.truncate_series(s, bgn_date)


class CMpFactorWithArgWin(object):
    def __init__(self, proc_num: int, factor_type: str, arg_wins: tuple[int], run_mode: str, bgn_date: str, stp_date: str):
        self.proc_num = proc_num
        self.factor_type = factor_type.upper()
        self.arg_wins = arg_wins
        self.run_mode = run_mode
        self.bgn_date = bgn_date
        self.stp_date = stp_date

    def mp_cal_factor(self, **kwargs):
        t0 = dt.datetime.now()
        pool = mp.Pool(processes=self.proc_num)
        for arg_win in self.arg_wins:
            if self.factor_type == "SKEW":
                transformer = CFactorsSKEW(arg_win=arg_win, **kwargs)
            elif self.factor_type == "VOL":
                transformer = CFactorsVOL(arg_win=arg_win, **kwargs)
            elif self.factor_type == "RVOL":
                transformer = CFactorsRVOL(arg_win=arg_win, **kwargs)
            elif self.factor_type == "CV":
                transformer = CFactorsCV(arg_win=arg_win, **kwargs)
            elif self.factor_type == "CTP":
                transformer = CFactorsCTP(arg_win=arg_win, **kwargs)
            elif self.factor_type == "CVP":
                transformer = CFactorsCVP(arg_win=arg_win, **kwargs)
            elif self.factor_type == "CSP":
                transformer = CFactorsCSP(arg_win=arg_win, **kwargs)
            elif self.factor_type == "BETA":
                transformer = CFactorsBETA(arg_win=arg_win, **kwargs)
            elif self.factor_type == "VAL":
                transformer = CFactorsVAL(arg_win=arg_win, **kwargs)
            elif self.factor_type == "CBETA":
                transformer = CFactorsCBETA(arg_win=arg_win, **kwargs)
            elif self.factor_type == "IBETA":
                transformer = CFactorsIBETA(arg_win=arg_win, **kwargs)
            else:
                transformer = None
            if transformer is not None:
                pool.apply_async(transformer.core, args=(self.run_mode, self.bgn_date, self.stp_date))
        pool.close()
        pool.join()
        t1 = dt.datetime.now()
        print(f"... raw factor {SetFontGreen(self.factor_type)} generated")
        print(f"... total time consuming: {SetFontGreen(f'{(t1 - t0).total_seconds():.2f}')} seconds")
        return 0


class CFactorsMACD(CFactorsWithMajorReturn):
    def __init__(self, fast: int, slow: int, alpha: float, ewm_bgn_date: str, **kwargs):
        super().__init__(**kwargs)
        self.fast = fast
        self.slow = slow
        self.alpha = alpha
        self.ewm_bgn_date = ewm_bgn_date

    def _set_factor_id(self):
        self.factor_id = f"MACDF{self.fast:03d}S{self.slow:03d}A{int(100 * self.alpha):03d}"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", self.ewm_bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "instru_idx"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)

        df["emaFast"] = df["instru_idx"].ewm(span=self.fast, adjust=False).mean()
        df["emaSlow"] = df["instru_idx"].ewm(span=self.slow, adjust=False).mean()
        df["diff"] = (df["emaFast"] / df["emaSlow"] - 1) * 100
        s = df["diff"].ewm(alpha=self.alpha, adjust=False).mean()
        return self.truncate_series(s, bgn_date)


class CFactorsKDJ(CFactorsWithMajorReturn):
    def __init__(self, n: int, ewm_bgn_date: str, **kwargs):
        super().__init__(**kwargs)
        self.n = n
        self.ewm_bgn_date = ewm_bgn_date

    def _set_factor_id(self):
        self.factor_id = f"KDJ{self.n:03d}"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", self.ewm_bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "highC", "lowC", "closeC"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)

        df["Ln"] = df["lowC"].rolling(window=self.n).min()
        df["Hn"] = df["highC"].rolling(window=self.n).max()
        df["rsv"] = (df["closeC"] - df["Ln"]) / (df["Hn"] - df["Ln"]) * 100
        df["k"] = df["rsv"].ewm(alpha=1 / 3, adjust=False).mean()
        df["d"] = df["k"].ewm(alpha=1 / 3, adjust=False).mean()
        s = df["k"] * 3 - df["d"] * 2
        return -self.truncate_series(s, bgn_date)


class CFactorsRSI(CFactorsWithMajorReturn):
    def __init__(self, n: int, ewm_bgn_date: str, **kwargs):
        super().__init__(**kwargs)
        self.n = n
        self.ewm_bgn_date = ewm_bgn_date

    def _set_factor_id(self):
        self.factor_id = f"RSI{self.n:03d}"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", self.ewm_bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "openC", "closeC"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)

        df["d"] = df["closeC"] - df["openC"]
        df["sign"] = [1 if z >= 0 else 0 for z in df["d"]]
        df["posN"] = df["sign"].rolling(self.n).sum()
        df["negN"] = self.n - df["posN"]
        df["posSum"] = (df["d"] * df["sign"]).rolling(self.n).sum()
        df["negSum"] = (-df["d"] * (1 - df["sign"])).rolling(self.n).sum()
        df["avgU"] = (df["posSum"] / df["posN"]).fillna(0)
        df["avgD"] = (df["negSum"] / df["negN"]).fillna(0)
        s = df["avgD"] / (df["avgU"] + df["avgD"])
        return self.truncate_series(s, bgn_date)


class CMpFactorMACD(object):
    def __init__(self, proc_num: int, fasts: tuple[int], slows: tuple[int], alphas: tuple[float], ewm_bgn_date: str,
                 run_mode: str, bgn_date: str, stp_date: str):
        self.proc_num = proc_num
        self.fasts = fasts
        self.slows = slows
        self.alphas = alphas
        self.ewm_bgn_date = ewm_bgn_date
        self.run_mode = run_mode
        self.bgn_date = bgn_date
        self.stp_date = stp_date

    def mp_cal_factor(self, **kwargs):
        t0 = dt.datetime.now()
        pool = mp.Pool(processes=self.proc_num)
        for (fast, slow, alpha) in ittl.product(self.fasts, self.slows, self.alphas):
            transformer = CFactorsMACD(fast, slow, alpha, self.ewm_bgn_date, **kwargs)
            pool.apply_async(transformer.core, args=(self.run_mode, self.bgn_date, self.stp_date))
        pool.close()
        pool.join()
        t1 = dt.datetime.now()
        print(f"... raw factor {SetFontGreen('MACD')} generated")
        print(f"... total time consuming: {SetFontGreen(f'{(t1 - t0).total_seconds():.2f}')} seconds")
        return 0


class CMpFactorKDJ(object):
    def __init__(self, proc_num: int, ns: tuple[int], ewm_bgn_date: str,
                 run_mode: str, bgn_date: str, stp_date: str):
        self.proc_num = proc_num
        self.ns = ns
        self.ewm_bgn_date = ewm_bgn_date
        self.run_mode = run_mode
        self.bgn_date = bgn_date
        self.stp_date = stp_date

    def mp_cal_factor(self, **kwargs):
        t0 = dt.datetime.now()
        pool = mp.Pool(processes=self.proc_num)
        for n in self.ns:
            transformer = CFactorsKDJ(n, self.ewm_bgn_date, **kwargs)
            pool.apply_async(transformer.core, args=(self.run_mode, self.bgn_date, self.stp_date))
        pool.close()
        pool.join()
        t1 = dt.datetime.now()
        print(f"... raw factor {SetFontGreen('KDJ')} generated")
        print(f"... total time consuming: {SetFontGreen(f'{(t1 - t0).total_seconds():.2f}')} seconds")
        return 0


class CMpFactorRSI(object):
    def __init__(self, proc_num: int, ns: tuple[int], ewm_bgn_date: str,
                 run_mode: str, bgn_date: str, stp_date: str):
        self.proc_num = proc_num
        self.ns = ns
        self.ewm_bgn_date = ewm_bgn_date
        self.run_mode = run_mode
        self.bgn_date = bgn_date
        self.stp_date = stp_date

    def mp_cal_factor(self, **kwargs):
        t0 = dt.datetime.now()
        pool = mp.Pool(processes=self.proc_num)
        for n in self.ns:
            transformer = CFactorsRSI(n, self.ewm_bgn_date, **kwargs)
            pool.apply_async(transformer.core, args=(self.run_mode, self.bgn_date, self.stp_date))
        pool.close()
        pool.join()
        t1 = dt.datetime.now()
        print(f"... raw factor {SetFontGreen('RSI')} generated")
        print(f"... total time consuming: {SetFontGreen(f'{(t1 - t0).total_seconds():.2f}')} seconds")
        return 0
