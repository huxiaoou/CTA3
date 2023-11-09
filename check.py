import pandas as pd
from struct_lib.portfolios import get_lib_struct_signal, get_lib_struct_signal_optimized
from skyrim.falkreath import CManagerLibReader
from skyrim.whiterun import CCalendarMonthly, SetFontGreen, SetFontYellow


def display_signal_selected(sids: list[str], db_save_dir: str,
                            bgn_date: str, stp_date: str, instrument: str) -> pd.DataFrame:
    dfs_list = []
    for sid in sids:
        sig_lib_struct = get_lib_struct_signal(sid)
        sig_lib_reader = CManagerLibReader(db_save_dir, sig_lib_struct.m_lib_name)
        sig_lib_reader.set_default(sig_lib_struct.m_tab.m_table_name)
        df = sig_lib_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
            ("instrument", "=", instrument),
        ], t_value_columns=["trade_date", "instrument", "value"])
        df["sid"] = sid
        dfs_list.append(df)
    res = pd.concat(dfs_list, axis=0, ignore_index=True)
    return res


def validate_dynamic_portfolio_weight(check_ids: tuple[list[str], str], trade_date: str,
                                      src_signal_db_save_dir: str, optimized_dir: str,
                                      portfolio_db_save_dir: str, calendar: CCalendarMonthly):
    selected_src_ids, short_id = check_ids
    src_data = {}
    for src_fac_id in selected_src_ids:
        sig_lib_struct = get_lib_struct_signal(src_fac_id)
        sig_lib_reader = CManagerLibReader(src_signal_db_save_dir, sig_lib_struct.m_lib_name)
        sig_lib_reader.set_default(sig_lib_struct.m_tab.m_table_name)
        df = sig_lib_reader.read_by_date(t_trade_date=trade_date, t_value_columns=["instrument", "value"]).set_index("instrument")
        src_data[src_fac_id] = df["value"]
    src_df = pd.DataFrame(src_data).fillna(0)

    trade_month = trade_date[0:6]
    trade_month_last_date = calendar.get_last_date_of_month(trade_month)
    if trade_date == trade_month_last_date:
        optimized_weight_date = trade_date
    else:
        optimized_weight_date = calendar.get_last_date_of_month(calendar.get_next_month(trade_month, -1))
    optimized_weight_lib_struct = get_lib_struct_signal_optimized(short_id)
    optimized_weight_lib_reader = CManagerLibReader(optimized_dir, optimized_weight_lib_struct.m_lib_name)
    optimized_weight_lib_reader.set_default(optimized_weight_lib_struct.m_tab.m_table_name)
    weight_df = optimized_weight_lib_reader.read_by_date(t_trade_date=optimized_weight_date, t_value_columns=["signal", "value"]).set_index("signal")

    validate_weight = src_df @ weight_df
    validate_weight["value"] = validate_weight["value"] / validate_weight["value"].abs().sum()

    portfolio_lib_struct = get_lib_struct_signal(short_id)
    portfolio_lib_reader = CManagerLibReader(portfolio_db_save_dir, portfolio_lib_struct.m_lib_name)
    portfolio_lib_reader.set_default(optimized_weight_lib_struct.m_tab.m_table_name)
    portfolio_weight = portfolio_lib_reader.read_by_date(t_trade_date=trade_date, t_value_columns=["instrument", "value"]).set_index("instrument")

    check_df = pd.DataFrame({"portfolio": portfolio_weight["value"], "validate": validate_weight["value"]}).fillna(0)
    check_df["diff"] = check_df["portfolio"] - check_df["validate"]
    diff_abs_sum = check_df["diff"].abs().sum()
    if check_df.empty:
        print(f"... there is no data available for {SetFontYellow(trade_date)}. This may happen because {SetFontYellow(trade_date)} is not a trade_date, please check again.")
    else:
        if diff_abs_sum > 1e-10:
            pd.set_option("display.width", 0)
            pd.set_option("display.float_format", "{:.6f}".format)
            print(f"... some differences are found for portfolio-{SetFontYellow(short_id)} @ {SetFontYellow(trade_date)}")
            print(f"shape of source    signal = {src_df.shape}")
            print(f"shape of optimized weight = {weight_df.shape}")
            print(trade_date, optimized_weight_date)
            print(check_df)
            print(check_df.abs().sum())
        else:
            print(f"... No errors are found for portfolio-{SetFontGreen(short_id)} @ signal date = {SetFontGreen(trade_date)}")
    return 0
