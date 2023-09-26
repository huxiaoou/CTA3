import pandas as pd
from factors.factors_cls_base import (CFactorsWithMajorReturn, CFactorsWithInstruVolume, CFactorsWithInstruVolumeAndInstruMember,
                                      CFactorsWithStock, CFactorsWithBasis, CFactorsWithMajorMinorAndMdc)


class CFactorMTM(CFactorsWithMajorReturn):
    def _set_factor_id(self):
        self.factor_id = "MTM"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "major_return"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)
        return -df["major_return"]


class CFactorsSIZE(CFactorsWithInstruVolume):
    def _set_factor_id(self):
        self.factor_id = "SIZE"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        db_reader = self.manager_instru_volume.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "sizeSettle"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)
        return df["sizeSettle"]


class CFactorsOI(CFactorsWithInstruVolume):
    def _set_factor_id(self):
        self.factor_id = "OI"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        db_reader = self.manager_instru_volume.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "oi"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)
        return df["oi"]


class CFactorsRS(CFactorsWithStock):
    def _set_factor_id(self):
        self.factor_id = "RS"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        df = self.manager_stock.get_var_by_instrument(instrument, "in_stock", bgn_date, stp_date)
        return df["in_stock"].fillna(0)


class CFactorsBASIS(CFactorsWithBasis):
    def _set_factor_id(self):
        self.factor_id = "BASIS"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        df = self.manager_basis.get_var_by_instrument(instrument, "basis_rate", bgn_date, stp_date)
        return df["basis_rate"]


class CFactorsTS(CFactorsWithMajorMinorAndMdc):
    @staticmethod
    def cal_roll_return(x: pd.Series, n_prc: str, d_prc: str):
        d_month, n_month = x["d_contract"].split(".")[0][-2:], x["n_contract"].split(".")[0][-2:]
        _dlt_month = int(d_month) - int(n_month)
        _dlt_month = _dlt_month + (12 if _dlt_month <= 0 else 0)
        return (x[n_prc] / x[d_prc] - 1) / _dlt_month * 12

    def _set_factor_id(self):
        self.factor_id = "TS"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        __price_type = "close"
        db_reader = self.manager_major_minor.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "n_contract", "d_contract"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)

        df["n_" + __price_type] = [self.manager_md.get_price_for_contract_at_day(instrument, c, t) for c, t in zip(df["n_contract"], df.index)]
        df["d_" + __price_type] = [self.manager_md.get_price_for_contract_at_day(instrument, c, t) for c, t in zip(df["d_contract"], df.index)]
        df["roll_return"] = df.apply(self.cal_roll_return, args=("n_" + __price_type, "d_" + __price_type), axis=1)
        return df["roll_return"]


class CFactorsLIQUID(CFactorsWithMajorReturn):
    def _set_factor_id(self):
        self.factor_id = "LIQUID"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        db_reader = self.manager_major_return.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "major_return", "amount"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)
        df["liquid"] = df["major_return"].abs() * 1e8 / df["amount"]
        return df["liquid"]


class CFactorsSR(CFactorsWithInstruVolume):
    def _set_factor_id(self):
        self.factor_id = "SR"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        db_reader = self.manager_instru_volume.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "volume", "oi"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)
        df["sr"] = df["volume"] / df["oi"]
        return df["sr"]


class CFactorsHR(CFactorsWithInstruVolume):
    def _set_factor_id(self):
        self.factor_id = "HR"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        db_reader = self.manager_instru_volume.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "volume", "oi"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)
        df["doi"] = (df["oi"] - df["oi"].shift(1)).fillna(0)
        df["hr"] = df["doi"] / df["volume"]
        return df["hr"]


class CFactorsNETOI(CFactorsWithInstruVolumeAndInstruMember):
    def _set_factor_id(self):
        self.factor_id = "NETOI"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        db_reader = self.manager_instru_volume.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "oi"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)
        df["net"] = self._get_net_srs(instrument, bgn_date, stp_date, "lngSum", "srtSum")
        return df["net"] / df["oi"] * 100


class CFactorsNETOIW(CFactorsWithInstruVolumeAndInstruMember):
    def _set_factor_id(self):
        self.factor_id = "NETOIW"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        db_reader = self.manager_instru_volume.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "oi"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)
        df["net"] = self._get_wgt_net_srs(instrument, bgn_date, stp_date, "lngSum", "srtSum")
        return df["net"] / df["oi"] * 100


class CFactorsNETDOI(CFactorsWithInstruVolumeAndInstruMember):
    def _set_factor_id(self):
        self.factor_id = "NETDOI"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        db_reader = self.manager_instru_volume.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "oi"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)
        df["net"] = self._get_net_srs(instrument, bgn_date, stp_date, "lngDlt", "srtDlt")
        return df["net"] / df["oi"] * 100


class CFactorsNETDOIW(CFactorsWithInstruVolumeAndInstruMember):
    def _set_factor_id(self):
        self.factor_id = "NETDOIW"
        return 0

    def _get_instrument_factor_exposure(self, instrument: str, run_mode: str, bgn_date: str, stp_date: str) -> pd.Series:
        db_reader = self.manager_instru_volume.get_db_reader()
        df = db_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "oi"],
            t_using_default_table=False, t_table_name=instrument.replace(".", "_"))
        db_reader.close()
        df.set_index("trade_date", inplace=True)
        df["net"] = self._get_wgt_net_srs(instrument, bgn_date, stp_date, "lngDlt", "srtDlt")
        return -df["net"] / df["oi"] * 100
