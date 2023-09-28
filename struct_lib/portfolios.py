import pandas as pd
from skyrim.falkreath import CLib1Tab1, CTable
from skyrim.falkreath import CManagerLibReader, CManagerLibWriter


def get_signal_lib_struct(signal: str) -> CLib1Tab1:
    return CLib1Tab1(
        t_lib_name=f"{signal}.db",
        t_tab=CTable({
            "table_name": signal,
            "primary_keys": {"trade_date": "TEXT", "instrument": "TEXT"},
            "value_columns": {"value": "REAL"},
        })
    )


def get_signal_optimized_lib_struct(opt_id: str) -> CLib1Tab1:
    return CLib1Tab1(
        t_lib_name=f"{opt_id}.db",
        t_tab=CTable({
            "table_name": opt_id,
            "primary_keys": {"trade_date": "TEXT", "signal": "TEXT"},
            "value_columns": {"value": "REAL"},
        })
    )


def get_nav_lib_struct(signal_id: str) -> CLib1Tab1:
    return CLib1Tab1(
        t_lib_name=f"nav-{signal_id}.db",
        t_tab=CTable({
            "table_name": signal_id,
            "primary_keys": {"trade_date": "TEXT"},
            "value_columns": {"rawREt": "REAL", "dltWgt": "REAL", "fee": "REAL",
                              "netREt": "REAL", "nav": "REAL"},
        })
    )


def get_nav_lib_reader(simu_id: str, simu_save_dir: str) -> CManagerLibReader:
    nav_lib_struct = get_nav_lib_struct(simu_id)
    nav_lib_reader = CManagerLibReader(simu_save_dir, nav_lib_struct.m_lib_name)
    nav_lib_reader.set_default(nav_lib_struct.m_tab.m_table_name)
    return nav_lib_reader


def get_nav_lib_writer(simu_id: str, simu_save_dir: str, run_mode: str) -> CManagerLibWriter:
    nav_lib_struct = get_nav_lib_struct(simu_id)
    nav_lib_writer = CManagerLibWriter(simu_save_dir, nav_lib_struct.m_lib_name)
    nav_lib_writer.initialize_table(nav_lib_struct.m_tab, run_mode in ["O"])
    return nav_lib_writer


def get_nav_df(simu_id: str, simu_save_dir: str) -> pd.DataFrame:
    nav_lib_reader = get_nav_lib_reader(simu_id, simu_save_dir)
    simu_nav_df = nav_lib_reader.read(["trade_date", "rawRet", "dltWgt", "fee", "netRet", "nav"])
    nav_lib_reader.close()
    simu_nav_df.set_index("trade_date", inplace=True)
    return simu_nav_df
