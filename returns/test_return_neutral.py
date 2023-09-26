import datetime as dt
import numpy as np
import pandas as pd
from struct_lib.returns_and_exposure import get_lib_struct_available_universe, get_lib_struct_test_return
from factors.factors_shared import neutralize_by_sector
from skyrim.falkreath import CManagerLibReader, CManagerLibWriterByDate
from skyrim.whiterun import CCalendar, SetFontGreen, SetFontRed


def cal_test_return_neutral(
        run_mode: str, bgn_date: str, stp_date: str | None,
        instruments_universe: list[str],
        available_universe_dir,
        sector_classification: dict[str, str],
        test_return_dir: str,
        calendar: CCalendar,
):
    _weight_id = "amount"

    # --- available universe
    available_universe_lib_structure = get_lib_struct_available_universe()
    available_universe_lib = CManagerLibReader(t_db_name=available_universe_lib_structure.m_lib_name, t_db_save_dir=available_universe_dir)
    available_universe_lib.set_default(available_universe_lib_structure.m_tab.m_table_name)

    # --- mother universe
    mother_universe_df = pd.DataFrame({"instrument": instruments_universe})

    # --- sector df
    sector_df = pd.DataFrame.from_dict({z: {sector_classification[z]: 1} for z in instruments_universe}, orient="index").fillna(0)

    # --- test return library
    test_return_lib_structure = get_lib_struct_test_return("test_return")
    test_return_lib = CManagerLibReader(t_db_name=test_return_lib_structure.m_lib_name, t_db_save_dir=test_return_dir)
    test_return_lib.set_default(test_return_lib_structure.m_tab.m_table_name)

    # --- test return neutral library
    test_return_neutral_lib_structure = get_lib_struct_test_return(f"test_return_neu")
    test_return_neutral_lib = CManagerLibWriterByDate(t_db_name=test_return_neutral_lib_structure.m_lib_name, t_db_save_dir=test_return_dir)
    test_return_neutral_lib.initialize_table(t_table=test_return_neutral_lib_structure.m_tab, t_remove_existence=run_mode in ["O"])
    dst_lib_is_continuous = test_return_neutral_lib.check_continuity(append_date=bgn_date, t_calendar=calendar) if run_mode in ["A"] else 0
    if dst_lib_is_continuous == 0:
        for trade_date in calendar.get_iter_list(t_bgn_date=bgn_date, t_stp_date=stp_date, t_ascending=True):
            test_return_df = test_return_lib.read_by_date(
                t_trade_date=trade_date,
                t_value_columns=["instrument", "value"]
            )
            if len(test_return_df) == 0:
                print(f"... Warning! trade_date = {trade_date} Not enough test return")
                continue
            weight_df = available_universe_lib.read_by_date(
                t_trade_date=trade_date,
                t_value_columns=["instrument", _weight_id]
            )
            if len(weight_df) == 0:
                print(f"... Warning! trade_date = {trade_date} Not enough weight data")
                continue

            input_df = mother_universe_df.merge(
                right=weight_df, on=["instrument"], how="inner").merge(
                right=test_return_df, on=["instrument"], how="inner").set_index("instrument")
            input_df[_weight_id] = np.sqrt(input_df[_weight_id])
            test_return_neutral_srs = neutralize_by_sector(
                t_raw_data=input_df["value"],
                t_sector_df=sector_df,
                t_weight=input_df[_weight_id]
            )
            test_return_neutral_lib.update_by_date(
                t_date=trade_date,
                t_update_df=pd.DataFrame({"value": test_return_neutral_srs}),
                t_using_index=True
            )
        print(f"... @ {dt.datetime.now()} {SetFontGreen('test return neutral')} updated")
    else:
        print(f"... {SetFontGreen('test return neutral')} {SetFontRed('FAILED')} to update")

    test_return_lib.close()
    test_return_neutral_lib.close()
    available_universe_lib.close()
    return 0
