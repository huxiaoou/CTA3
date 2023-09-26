import datetime as dt
import multiprocessing as mp
import numpy as np
import pandas as pd
from struct_lib.returns_and_exposure import get_lib_struct_factor_exposure, get_lib_struct_available_universe
from factors.factors_shared import transform_dist, neutralize_by_sector
from skyrim.whiterun import SetFontGreen, CCalendar
from skyrim.falkreath import CManagerLibReader, CManagerLibWriter


def neutralize_one_factor_one_day(
        df: pd.DataFrame, mother_df: pd.DataFrame,
        weight_id: str, sector_df: pd.DataFrame) -> pd.Series:
    xdf = pd.merge(left=mother_df, right=df, on="instrument", how="inner").set_index("instrument")
    xdf["value_norm"] = transform_dist(t_exposure_srs=xdf["value"])
    xdf["rel_wgt"] = np.sqrt(xdf[weight_id])
    factor_neutral_srs = neutralize_by_sector(
        t_raw_data=xdf["value_norm"],
        t_sector_df=sector_df,
        t_weight=xdf["rel_wgt"]
    )
    return factor_neutral_srs


def neutralize_one_factor(src_factor: str,
                          run_mode: str, bgn_date: str, stp_date: str,
                          mother_universe_df: pd.DataFrame, sector_df: pd.DataFrame,
                          available_universe_dir: str,
                          factors_exposure_raw_dir: str,
                          factors_exposure_neu_dir: str,
                          calendar: CCalendar, ):
    # --- factor neutral library
    factor_neutral_lib_struct = get_lib_struct_factor_exposure(f"{src_factor}_NEU")
    factor_neutral_lib = CManagerLibWriter(t_db_name=factor_neutral_lib_struct.m_lib_name, t_db_save_dir=factors_exposure_neu_dir)
    factor_neutral_lib.initialize_table(t_table=factor_neutral_lib_struct.m_tab, t_remove_existence=run_mode in ["O"])
    is_continuous = factor_neutral_lib.check_continuity(append_date=bgn_date, t_calendar=calendar) if run_mode in ["A"] else 0
    if is_continuous == 0:
        __weight_id = "amount"

        # --- available universe
        available_universe_lib_struct = get_lib_struct_available_universe()
        available_universe_lib = CManagerLibReader(t_db_name=available_universe_lib_struct.m_lib_name, t_db_save_dir=available_universe_dir)
        available_universe_lib.set_default(available_universe_lib_struct.m_tab.m_table_name)

        # --- src factor library
        src_factor_lib_struct = get_lib_struct_factor_exposure(src_factor)
        src_factor_lib = CManagerLibReader(t_db_name=src_factor_lib_struct.m_lib_name, t_db_save_dir=factors_exposure_raw_dir)
        src_factor_lib.set_default(src_factor_lib_struct.m_tab.m_table_name)

        factor_df = src_factor_lib.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "instrument", "value"])
        src_factor_lib.close()

        weight_df = available_universe_lib.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "instrument", __weight_id])
        available_universe_lib.close()

        input_df = pd.merge(left=factor_df, right=weight_df, on=["trade_date", "instrument"], how="inner")
        input_df.dropna(axis=0, subset=["value"], inplace=True)
        res_agg = input_df.groupby(by="trade_date", group_keys=True).apply(
            neutralize_one_factor_one_day, mother_df=mother_universe_df,
            weight_id=__weight_id, sector_df=sector_df,
        )

        # type of res_agg may vary according to the result:
        # if length of each day(i.e. number of instruments) is the same, it will be a DataFrame(this happens when only a few days are calculated)
        # otherwise it would be a DataFrame(this happens when all days in history are calculated)
        if type(res_agg) == pd.Series:
            update_df = res_agg.reset_index()
        elif type(res_agg) == pd.DataFrame:
            update_df = res_agg.stack(dropna=False).reset_index()
        else:
            print("... Wrong type of result when calculate factors neutral.")
            print("... The result is neither a pd.Series nor a pd.DataFrame.")
            update_df = pd.DataFrame()

        factor_neutral_lib.update(t_update_df=update_df, t_using_index=False)
    factor_neutral_lib.close()
    return 0


def cal_factors_neutral_mp(proc_num: int, factors: list[str], **kwargs):
    t0 = dt.datetime.now()
    pool = mp.Pool(processes=proc_num)
    for f in factors:
        pool.apply_async(neutralize_one_factor, args=(f,), kwds=kwargs)
    pool.close()
    pool.join()
    t1 = dt.datetime.now()
    print(f"... factors {SetFontGreen('NEUTRALIZATION')} calculated")
    print(f"... total time consuming: {SetFontGreen(f'{(t1 - t0).total_seconds():.2f}')} seconds")
    return 0
