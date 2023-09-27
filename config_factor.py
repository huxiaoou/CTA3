import itertools


def gen_factor_series(factor: str, factor_setting: dict, append_raw: bool) -> list[tuple[str, str, str]]:
    res = [(factor, "V", factor)] if append_raw else []  # V = vanilla
    for k, v in factor_setting.items():
        res += [(f"{factor}{k}{_:03d}", k, factor) for _ in v]
    return res


def gen_factor_series_H_LD(factor: str, factor_setting: dict) -> list[tuple[str, str, str]]:
    res = []
    for h in factor_setting["H"]:
        res.append((f"{factor}{h:03d}", "H", factor))
        for ld in factor_setting["LD"]:
            res.append((f"{factor}{h:03d}LD{ld:03d}", "LD", factor))
    return res


# --- factor settings ---
wins_aver = (10,)  # (10, 20, 60, 120, 180, 240)
wins_break = (10,)  # (10, 20, 60, 120, 180, 240)
wins_lag = (20,)  # (20, 60, 240)
wins_lag_month = (24,)  # (24, 66, 250)
wins_full_term = (10,)  # (10, 20, 60, 120, 180, 240)
wins_quad_term = (60,)  # (60, 120, 180, 240)
factors_settings = {
    "MTM": {"S": (240,), "SP": wins_aver},

    "SIZE": {"A": wins_aver, "BR": (10,), "LR": wins_lag},
    "OI": {"BR": wins_break, "LR": wins_lag},
    "RS": {"BR": (10, 20, 240), "LR": (20, 240)},

    "BASIS": {"A": (60, 120), "BD": wins_break, "LD": wins_lag},
    "TS": {"A": (60, 120, 180), "BD": wins_break, "LD": (240,)},
    "LIQUID": {"A": wins_aver, "BD": (10, 180), "LD": wins_lag},
    "SR": {"A": wins_aver, "BD": (180,), "LD": (240,)},
    "HR": {"A": (60,), "BD": wins_break, "LD": wins_lag},
    "NETOI": {"A": wins_aver, "BD": wins_break, "LD": wins_lag},
    "NETOIW": {"A": wins_aver, "BD": wins_break, "LD": wins_lag},
    "NETDOI": {"A": (240,), "BD": (20,), "LD": wins_lag},
    "NETDOIW": {"A": (20,), "BD": (180,), "LD": wins_lag},

    "SKEW": {"H": (10, 120, 180), "LD": (20, 60)},
    "VOL": {"H": (20,), "LD": wins_lag},
    "RVOL": {"H": (60,), "LD": wins_lag},
    "CV": {"H": wins_full_term, "LD": wins_lag},

    "CTP": {"H": (120, 180, 240), "LD": (20, 60)},
    "CVP": {"H": (120, 180), "LD": (20, 60)},
    "CSP": {"H": (120, 180), "LD": (20,)},
    "BETA": {"H": (20,) + wins_quad_term, "LD": wins_lag},

    "VAL": {"H": wins_quad_term, "LD": wins_lag},
    "CBETA": {"H": wins_quad_term, "LD": wins_lag},
    "IBETA": {"H": (240,), "LD": (24, 250)},

    "MACD": {"F": (10,), "S": (20,), "ALPHA": (0.2,)},
    "KDJ": {"N": (10, 20)},
    "RSI": {"N": (10, 20)},
}

factors_transformation_directions = {
    ("MTM", "S"): -1,
    ("MTM", "SP"): -1,
    ("SIZE", "BR"): -1,
    ("SIZE", "LR"): -1,
    ("RS", "BR"): -1,
    ("RS", "LR"): -1,
    ("RVOL", "LD"): -1,
}

factors_mtm = gen_factor_series("MTM", factors_settings["MTM"], True)
factors_size = gen_factor_series("SIZE", factors_settings["SIZE"], True)
factors_oi = gen_factor_series("OI", factors_settings["OI"], True)
factors_rs = gen_factor_series("RS", factors_settings["RS"], True)
factors_basis = gen_factor_series("BASIS", factors_settings["BASIS"], True)
factors_ts = gen_factor_series("TS", factors_settings["TS"], True)
factors_liquid = gen_factor_series("LIQUID", factors_settings["LIQUID"], True)
factors_sr = gen_factor_series("SR", factors_settings["SR"], True)
factors_hr = gen_factor_series("HR", factors_settings["HR"], True)
factors_netoi = gen_factor_series("NETOI", factors_settings["NETOI"], True)
factors_netoiw = gen_factor_series("NETOIW", factors_settings["NETOIW"], True)
factors_netdoi = gen_factor_series("NETDOI", factors_settings["NETDOI"], True)
factors_netdoiw = gen_factor_series("NETDOIW", factors_settings["NETDOIW"], True)

factors_skew = gen_factor_series_H_LD("SKEW", factors_settings["SKEW"])
factors_vol = gen_factor_series_H_LD("VOL", factors_settings["VOL"])
factors_rvol = gen_factor_series_H_LD("RVOL", factors_settings["RVOL"])
factors_cv = gen_factor_series_H_LD("CV", factors_settings["CV"])
factors_ctp = gen_factor_series_H_LD("CTP", factors_settings["CTP"])
factors_cvp = gen_factor_series_H_LD("CVP", factors_settings["CVP"])
factors_csp = gen_factor_series_H_LD("CSP", factors_settings["CSP"])
factors_beta = gen_factor_series_H_LD("BETA", factors_settings["BETA"])
factors_val = gen_factor_series_H_LD("VAL", factors_settings["VAL"])
factors_cbeta = gen_factor_series_H_LD("CBETA", factors_settings["CBETA"])
factors_ibeta = gen_factor_series_H_LD("IBETA", factors_settings["IBETA"])

factors_macd = [(f"MACDF{f:03d}S{s:03d}A{int(100 * a):03d}", "MACD", "MACD")
                for f, s, a in itertools.product(factors_settings["MACD"]["F"], factors_settings["MACD"]["S"], factors_settings["MACD"]["ALPHA"])]
factors_kdj = [(f"KDJ{n:03d}", "KDJ", "KDJ") for n in factors_settings["KDJ"]["N"]]
factors_rsi = [(f"RSI{n:03d}", "RSI", "RSI") for n in factors_settings["RSI"]["N"]]

factors: list[tuple[str, str, str]] = factors_mtm + factors_size + factors_oi + factors_rs + \
                                      factors_basis + factors_ts + factors_liquid + factors_sr + factors_hr + \
                                      factors_netoi + factors_netoiw + factors_netdoi + factors_netdoiw + \
                                      factors_skew + factors_vol + factors_rvol + factors_cv + \
                                      factors_ctp + factors_cvp + factors_csp + factors_beta + \
                                      factors_val + factors_cbeta + factors_ibeta + \
                                      factors_macd + factors_kdj + factors_rsi
factors_selected = factors_mtm + factors_size + factors_rs + \
                   factors_basis + factors_ts + factors_liquid + factors_sr + factors_hr + \
                   factors_netdoi + factors_netdoiw + \
                   factors_skew + factors_vol + factors_rvol + \
                   factors_ctp + factors_cvp + factors_csp + factors_beta + \
                   factors_ibeta

factors_classification: dict[str, tuple[str, str]] = {f: (sc, c) for f, sc, c in factors}

factors_group: dict[str, list[str]] = {
    "MTM": [f for f, sc, c in factors_mtm],
    "SIZE": [f for f, sc, c in factors_size],
    "OI": [f for f, sc, c in factors_oi],
    "RS": [f for f, sc, c in factors_rs],
    "BASIS": [f for f, sc, c in factors_basis],
    "TS": [f for f, sc, c in factors_ts],
    "LIQUID": [f for f, sc, c in factors_liquid],
    "SR": [f for f, sc, c in factors_sr],
    "HR": [f for f, sc, c in factors_hr],
    "NETOI": [f for f, sc, c in factors_netoi],
    "NETOIW": [f for f, sc, c in factors_netoiw],
    "NETDOI": [f for f, sc, c in factors_netdoi],
    "NETDOIW": [f for f, sc, c in factors_netdoiw],
    "SKEW": [f for f, sc, c in factors_skew],
    "VOL": [f for f, sc, c in factors_vol],
    "RVOL": [f for f, sc, c in factors_rvol],
    "CV": [f for f, sc, c in factors_cv],
    "CTP": [f for f, sc, c in factors_ctp],
    "CVP": [f for f, sc, c in factors_cvp],
    "CSP": [f for f, sc, c in factors_csp],
    "BETA": [f for f, sc, c in factors_beta],
    "VAL": [f for f, sc, c in factors_val],
    "CBETA": [f for f, sc, c in factors_cbeta],
    "IBETA": [f for f, sc, c in factors_ibeta],
    "MACD": [f for f, sc, c in factors_macd],
    "KDJ": [f for f, sc, c in factors_kdj],
    "RSI": [f for f, sc, c in factors_rsi],
}

factors_raw = [f for f, sc, c in factors_selected]
factors_neu = [f"{f}_NEU" for f, sc, c in factors_selected]

if __name__ == "__main__":
    s = 0
    for g, fs in factors_group.items():
        print(f"number of {g:>8s} = {len(fs):>3d}")
        s += len(fs)
    print(f"      number of factors group          = {len(factors_group):>3d}")
    print(f"Sum   number of factors group          = {s:>3d}")
    print(f"Total number of factors classification = {len(factors_classification):>3d}")
    print(f"Total number of factors                = {len(factors):>3d}")  # 106
    print(f"Total number of factors selected       = {len(factors_selected):>3d}")  # 84
    print(f"Total number of factors raw            = {len(factors_raw):>3d}")  # 84
    print(f"Total number of factors neu            = {len(factors_neu):>3d}")  # 84
