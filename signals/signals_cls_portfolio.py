import pandas as pd
from signals.signals_cls import CSignalReader
from struct_lib.portfolios import get_signal_lib_struct
from skyrim.falkreath import CManagerLibReader


class CSignalCombineFromOtherSignals(CSignalReader):
    def __init__(self, src_signal_ids: list, src_signal_dir: str, sig_id: str, **kwargs):
        self.src_signal_ids = src_signal_ids
        self.src_signal_dir = src_signal_dir
        super().__init__(sig_id=sig_id, **kwargs)
        self.src_signals_dfs: dict[str, pd.DataFrame] = {}

    def _load_src_signals(self, bgn_date: str, stp_date: str):
        for src_signal_id in self.src_signal_ids:
            src_sig_struct = get_signal_lib_struct(src_signal_id)
            src_sig_lib_reader = CManagerLibReader(self.src_signal_dir, src_sig_struct.m_lib_name)
            src_sig_lib_reader.set_default(src_sig_struct.m_tab.m_table_name)
            src_sig_df = src_sig_lib_reader.read_by_conditions(t_conditions=[
                ("trade_date", ">=", bgn_date),
                ("trade_date", "<", stp_date),
            ], t_value_columns=["trade_date", "instrument", "value"])
            src_pivot_df = pd.pivot_table(data=src_sig_df, index="trade_date", columns="instrument", values="value")
            self.src_signals_dfs[src_signal_id] = src_pivot_df.fillna(0)
        return 0

    @staticmethod
    def normalize_final_weight(df: pd.DataFrame) -> pd.DataFrame:
        wgt_abs_sum = df.abs().sum(axis=1)
        return df.div(wgt_abs_sum, axis=0).fillna(0)


class CSignalCombineFromOtherSignalsWithFixWeight(CSignalCombineFromOtherSignals):
    def __init__(self, src_signal_weight: dict[str, float], **kwargs):
        self.src_signal_weight = src_signal_weight
        super().__init__(**kwargs)

    def _get_update_df(self, run_mode: str, bgn_date: str, stp_date: str) -> pd.DataFrame:
        self._load_src_signals(bgn_date, stp_date)
        sum_weight_df = pd.DataFrame()
        for src_signal_id in self.src_signal_ids:
            sig_df = self.src_signals_dfs[src_signal_id]
            sig_wgt = self.src_signal_weight[src_signal_id]  # type = scalar
            sum_weight_df = sum_weight_df.add(sig_df * sig_wgt, fill_value=0)
        sum_weight_df_norm = self.normalize_final_weight(sum_weight_df)
        update_df = sum_weight_df_norm.stack(dropna=False).reset_index()
        return update_df


class CSignalCombineFromOtherSignalsWithDynWeight(CSignalCombineFromOtherSignals):
    def __init__(self, src_signal_weight: pd.DataFrame, **kwargs):
        """

        :param src_signal_weight: a DataFrame, with index = trade_date, columns = src signals, value = signal weight,
                                  ie, each row of this DataFrame is a weight
        :param kwargs:
        """
        self.src_signal_weight = src_signal_weight
        super().__init__(**kwargs)

    def _get_update_df(self, run_mode: str, bgn_date: str, stp_date: str) -> pd.DataFrame:
        self._load_src_signals(bgn_date, stp_date)
        filter_dates = (self.src_signal_weight.index >= bgn_date) & (self.src_signal_weight.index < stp_date)
        selected_weight_df = self.src_signal_weight.loc[filter_dates]

        sum_weight_df = pd.DataFrame()
        for src_signal_id in self.src_signal_ids:
            sig_df = self.src_signals_dfs[src_signal_id]
            try:
                sig_wgt = selected_weight_df[src_signal_id]  # type = pd.Series
            except KeyError:
                sig_wgt = 0  # type = int
            dlt_wgt = sig_df.multiply(sig_wgt, axis=0).fillna(0)
            sum_weight_df = sum_weight_df.add(dlt_wgt, fill_value=0)
        sum_weight_df_norm = self.normalize_final_weight(sum_weight_df)
        update_df = sum_weight_df_norm.stack(dropna=False).reset_index()
        return update_df
