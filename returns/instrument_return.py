import os
import datetime as dt
import pandas as pd
from skyrim.whiterun import SetFontGreen
from skyrim.falkreath import CManagerLibReader


def merge_instru_return(
        bgn_date: str, stp_date: str,
        futures_by_instrument_dir, major_return_db_name: str,
        instruments_return_dir: str,
        concerned_instruments_universe: list[str]):
    major_return_db_reader = CManagerLibReader(futures_by_instrument_dir, major_return_db_name)

    major_return_data = {}
    for instrument in concerned_instruments_universe:
        major_return_df = major_return_db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "major_return"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_")
        ).set_index("trade_date")
        major_return_data[instrument] = major_return_df["major_return"]
    major_return_db_reader.close()

    return_df = pd.DataFrame(major_return_data)
    return_file = "instruments_return.csv.gz"
    return_path = os.path.join(instruments_return_dir, return_file)
    return_df.to_csv(return_path, float_format="%.10f")
    print(return_df)
    print("... @ {} {} calculated".format(dt.datetime.now(), SetFontGreen("instrument major return")))
    return 0
