from skyrim.falkreath import CLib1Tab1, CTable


def get_lib_struct_available_universe() -> CLib1Tab1:
    return CLib1Tab1(
        t_lib_name="available_universe.db",
        t_tab=CTable({
            "table_name": "available_universe",
            "primary_keys": {"trade_date": "TEXT", "instrument": "TEXT"},
            "value_columns": {"return": "REAL", "amount": "REAL"}
        })
    )


def get_lib_struct_test_return(tr_id: str) -> CLib1Tab1:
    """

    :param tr_id: ("test_return", "test_return_neu")
    :return:
    """
    return CLib1Tab1(
        t_lib_name=f"{tr_id}.db",
        t_tab=CTable({
            "table_name": tr_id,
            "primary_keys": {"trade_date": "TEXT", "instrument": "TEXT"},
            "value_columns": {"value": "REAL"},
        })
    )


def get_lib_struct_factor_exposure(factor: str) -> CLib1Tab1:
    """

    :param factor: ("BASISA147", "BASISA147_NEU")
    :return:
    """
    return CLib1Tab1(
        t_lib_name=f"{factor}.db",
        t_tab=CTable({
            "table_name": factor,
            "primary_keys": {"trade_date": "TEXT", "instrument": "TEXT"},
            "value_columns": {"value": "REAL"},
        })
    )


def get_lib_struct_ic_test(factor: str) -> CLib1Tab1:
    """

    :param factor: ("BASISA147", "BASISA147_NEU")
    :return:
    """
    return CLib1Tab1(
        t_lib_name=f"ic-{factor}.db",
        t_tab=CTable({
            "table_name": factor,
            "primary_keys": {"trade_date": "TEXT"},
            "value_columns": {"value": "REAL"},
        })
    )
