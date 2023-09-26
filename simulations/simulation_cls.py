import os
import datetime as dt
import multiprocessing as mp
import pandas as pd
from factors.factors_cls_base import CDbByInstrument
from signals.signals_cls import CSignalReader
from skyrim.whiterun import CCalendar, SetFontGreen


class CSimulation(object):
    def __init__(self, signal: CSignalReader, test_bgn_date: str, test_stp_date: str,
                 cost_rate: float, test_universe: list[str],
                 manager_major_return: CDbByInstrument,
                 simu_save_dir: str, calendar: CCalendar
                 ):
        self.cost_rate = cost_rate
        self.test_universe = test_universe
        self.calendar = calendar
        self.simu_id = signal.get_id()
        self.simu_save_dir = simu_save_dir

        self.__init_dates(test_bgn_date, test_stp_date)
        self.__init_instru_ret(manager_major_return)
        self.__init_signals(signal)

    def __init_dates(self, test_bgn_date: str, test_stp_date: str):
        __test_lag, __test_window = 1, 1
        self.test_bgn_date, self.test_stp_date = test_bgn_date, test_stp_date
        self.iter_test_dates = self.calendar.get_iter_list(self.test_bgn_date, self.test_stp_date, True)
        self.sig_bgn_date = self.calendar.get_next_date(self.iter_test_dates[0], -__test_window - __test_lag)
        self.sig_stp_date = self.iter_test_dates[-1]
        self.sig_dates = self.calendar.get_iter_list(self.sig_bgn_date, self.sig_stp_date, True)
        return 0

    def __init_instru_ret(self, manager_major_return: CDbByInstrument):
        instru_ret_data = {}
        ret_db_reader = manager_major_return.get_db_reader()
        for instrument in self.test_universe:
            ret_df = ret_db_reader.read_by_conditions(t_conditions=[
                ("trade_date", ">=", self.test_bgn_date),
                ("trade_date", "<", self.test_stp_date),
            ], t_value_columns=["trade_date", "major_return"],
                t_table_name=instrument.replace(".", "_"), t_using_default_table=False)
            ret_df.set_index("trade_date", inplace=True)
            instru_ret_data[instrument] = ret_df["major_return"]
        ret_db_reader.close()
        self.instru_ret_df = pd.DataFrame(instru_ret_data).fillna(0)
        return 0

    def __init_signals(self, signal: CSignalReader):
        raw_sig_df = signal.get_signal_data(self.sig_bgn_date, self.sig_stp_date)
        raw_sig_df.rename(mapper={"trade_date": "sig_date"}, axis=1, inplace=True)
        self.sig_df = pd.pivot_table(data=raw_sig_df, index="sig_date", columns="instrument", values="value").fillna(0)
        for instrument in self.test_universe:  # this may happen in append mode when there is only a few days between bgn_date and stp_date
            if instrument not in self.sig_df.columns:
                self.sig_df[instrument] = 0.0
        return 0

    def main(self):
        bridge_dates_ret_df = pd.DataFrame({"trade_date": self.iter_test_dates, "sig_date": self.sig_dates[:-1]})
        bridge_dates_fee_df = pd.DataFrame({"trade_date": self.iter_test_dates, "sig_date": self.sig_dates[1:]})
        wgt_ret_df = pd.merge(left=bridge_dates_ret_df, right=self.sig_df, on="sig_date", how="left")
        wgt_dlt_df = pd.merge(left=bridge_dates_fee_df, right=self.sig_df - self.sig_df.shift(1), on="sig_date", how="left")
        wgt_ret_df = wgt_ret_df.set_index("trade_date").drop(axis=1, labels="sig_date")
        wgt_dlt_df = wgt_dlt_df.set_index("trade_date").drop(axis=1, labels="sig_date")

        if self.instru_ret_df.shape == wgt_ret_df.shape:
            xdf: pd.DataFrame = wgt_ret_df * self.instru_ret_df
            nav_df = pd.DataFrame({
                "rawRet": xdf.sum(axis=1),
                "dltWgt": wgt_dlt_df.abs().sum(axis=1),
            })
            nav_df["fee"] = nav_df["dltWgt"] * self.cost_rate
            nav_df["netRet"] = nav_df["rawRet"] - nav_df["fee"]
            nav_df["nav"] = (nav_df["netRet"] + 1).cumprod()

            nav_file = f"nav-{self.simu_id}.csv.gz"
            nav_path = os.path.join(self.simu_save_dir, nav_file)
            nav_df.to_csv(nav_path, float_format="%.8f")
        return 0


def cal_simulations_mp(proc_num: int,
                       sig_ids: list[str], test_bgn_date: str, test_stp_date: str,
                       cost_rate: float, test_universe: list[str],
                       signals_dir: str, simulations_dir: str,
                       futures_by_instrument_dir: str, major_return_db_name: str,
                       calendar: CCalendar,
                       tips: str):
    t0 = dt.datetime.now()
    pool = mp.Pool(processes=proc_num)
    for sig_id in sig_ids:
        signal = CSignalReader(sig_id=sig_id, sig_save_dir=signals_dir, calendar=calendar)
        simu = CSimulation(signal=signal, test_bgn_date=test_bgn_date, test_stp_date=test_stp_date,
                           cost_rate=cost_rate, test_universe=test_universe,
                           manager_major_return=CDbByInstrument(futures_by_instrument_dir, major_return_db_name),
                           simu_save_dir=simulations_dir,
                           calendar=calendar)
        pool.apply_async(simu.main)
    pool.close()
    pool.join()
    t1 = dt.datetime.now()
    print(f"... {SetFontGreen(tips)} calculated")
    print(f"... total time consuming: {SetFontGreen(f'{(t1 - t0).total_seconds():.2f}')} seconds")
    return 0
