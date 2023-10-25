import pandas as pd
from struct_lib.portfolios import get_lib_struct_signal

from skyrim.falkreath import CManagerLibReader


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


if __name__ == "__main__":
    from config_portfolio import selected_src_signal_ids_raw, selected_src_signal_ids_neu
    from setup_project import signals_hedge_test_dir

    selected_df = display_signal_selected(
        sids=selected_src_signal_ids_raw,
        db_save_dir=signals_hedge_test_dir,
        bgn_date="20231011", stp_date="20231012", instrument="AG.SHF"
    )
    print(selected_df)

    selected_df = display_signal_selected(
        sids=selected_src_signal_ids_neu,
        db_save_dir=signals_hedge_test_dir,
        bgn_date="20231011", stp_date="20231012", instrument="AG.SHF"
    )
    print(selected_df)