import os
import datetime as dt
import pandas as pd
from struct_lib.returns_and_exposure import get_lib_struct_test_return
from skyrim.falkreath import CManagerLibWriter
from skyrim.whiterun import CCalendar, SetFontGreen, SetFontRed


def cal_test_return(run_mode: str, bgn_date: str, stp_date: str | None,
                    instruments_return_dir: str,
                    test_return_dir: str,
                    calendar: CCalendar):
    # load raw return
    raw_return_file = "instruments_return.csv.gz"
    raw_return_path = os.path.join(instruments_return_dir, raw_return_file)
    raw_return_df = pd.read_csv(raw_return_path, dtype={"trade_date": str}).set_index("trade_date")
    filter_dates = (raw_return_df.index >= bgn_date) & (raw_return_df.index < stp_date)
    raw_return_df = raw_return_df.loc[filter_dates]
    update_df = raw_return_df.stack().reset_index(level=1)

    # --- initialize lib
    test_return_lib_structure = get_lib_struct_test_return("test_return")
    test_return_lib = CManagerLibWriter(t_db_name=test_return_lib_structure.m_lib_name, t_db_save_dir=test_return_dir)
    test_return_lib.initialize_table(t_table=test_return_lib_structure.m_tab, t_remove_existence=run_mode in ["O"])
    dst_lib_is_continuous = test_return_lib.check_continuity(append_date=bgn_date, t_calendar=calendar) if run_mode in ["A"] else 0
    if dst_lib_is_continuous == 0:
        test_return_lib.update(t_update_df=update_df, t_using_index=True)
        print(f"... @ {dt.datetime.now()} {SetFontGreen('test return')} updated")
    else:
        print(f"... {SetFontGreen('test return')} {SetFontRed('FAILED')} to update")
    test_return_lib.close()
    return 0
