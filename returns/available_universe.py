import datetime as dt
import pandas as pd
from struct_lib.returns_and_exposure import get_lib_struct_available_universe
from skyrim.whiterun import CCalendar, SetFontGreen, SetFontRed
from skyrim.falkreath import CManagerLibReader, CManagerLibWriter


def get_available_universe_by_date(x: pd.Series, ret_df: pd.DataFrame, amt_df: pd.DataFrame, res: []):
    trade_date = x.name  # x is a Series like this: pd.Series({"CU.SHF":True, "CY.CZC":False}, name="20120104")
    available_universe_df = pd.DataFrame({
        "return": ret_df.loc[trade_date, x],
        "amount": amt_df.loc[trade_date, x],
    })
    available_universe_df["trade_date"] = trade_date
    res.append(available_universe_df)
    return 0


def cal_available_universe(
        run_mode: str, bgn_date: str, stp_date: str,
        instruments_universe: list[str],
        available_universe_options: dict[str, int | float],
        available_universe_dir: str,
        futures_by_instrument_dir: str, major_return_db_name: str,
        calendar: CCalendar):
    t0 = dt.datetime.now()
    _wanyuan, _yiyuan = 1e4, 1e8
    rolling_win, amt_threshold = available_universe_options["rolling_window"], available_universe_options["amount_threshold"]

    # set dates
    iter_dates = calendar.get_iter_list(bgn_date, stp_date, True)
    base_date = calendar.get_next_date(iter_dates[0], -rolling_win + 1)

    # --- initialize lib
    available_universe_lib_structure = get_lib_struct_available_universe()
    available_universe_lib = CManagerLibWriter(t_db_name=available_universe_lib_structure.m_lib_name, t_db_save_dir=available_universe_dir)
    available_universe_lib.initialize_table(t_table=available_universe_lib_structure.m_tab, t_remove_existence=run_mode in ["O"])
    dst_lib_is_continuous = available_universe_lib.check_continuity(append_date=bgn_date, t_calendar=calendar) if run_mode in ["A"] else 0
    if dst_lib_is_continuous == 0:
        # --- load all amount and return data
        amt_ma_data_for_available = {}
        amt_data, return_data = {}, {}
        major_return_db_reader = CManagerLibReader(futures_by_instrument_dir, major_return_db_name)
        for instrument in instruments_universe:
            major_return_df = major_return_db_reader.read_by_conditions(t_conditions=[
                ("trade_date", ">=", base_date),
                ("trade_date", "<", stp_date),
            ], t_value_columns=["trade_date", "amount", "major_return"],
                t_using_default_table=False, t_table_name=instrument.replace(".", "_")
            ).set_index("trade_date")
            amt_ma_data_for_available[instrument] = major_return_df["amount"].rolling(window=rolling_win).mean() * _wanyuan / _yiyuan
            amt_data[instrument] = major_return_df["amount"] * _wanyuan / _yiyuan
            return_data[instrument] = major_return_df["major_return"]

        # --- reorganize and save
        amt_ma_df_for_available = pd.DataFrame(amt_ma_data_for_available)
        amt_df, return_df = pd.DataFrame(amt_data), pd.DataFrame(return_data)
        filter_df: pd.DataFrame = amt_ma_df_for_available >= amt_threshold
        filter_df = filter_df.loc[filter_df.index >= bgn_date]
        res = []
        filter_df.apply(get_available_universe_by_date, args=(return_df, amt_df, res), axis=1)
        update_df = pd.concat(res).reset_index().set_index("trade_date").sort_index(ascending=True)
        available_universe_lib.update(t_update_df=update_df, t_using_index=True)

        print(f"... {SetFontGreen('available universe')} are calculated")
        print("... total time consuming: {:.2f} seconds".format((dt.datetime.now() - t0).total_seconds()))
    else:
        print(f"... {SetFontGreen('available universe')} {SetFontRed('FAILED')} to update")
    available_universe_lib.close()
    return 0
