from skyrim.falkreath import CLib1Tab1, CTable


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
