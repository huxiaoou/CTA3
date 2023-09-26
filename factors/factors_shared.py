import numpy as np
import pandas as pd
import scipy.stats as sps
from itertools import product


def transform_dist(t_exposure_srs: pd.Series):
    """

    :param t_exposure_srs:
    :return: remap an array of any distribution to the union distribution
    """

    return sps.norm.ppf(t_exposure_srs.rank() / (len(t_exposure_srs) + 1))


def neutralize_by_sector(t_raw_data: pd.Series, t_sector_df: pd.DataFrame, t_weight=None):
    """

    :param t_raw_data: A pd.Series with length = N. Its value could be exposure or return.
    :param t_sector_df: A 0-1 matrix with size = (M, K). And M >=N, make sure that index of
                        t_raw_data is a subset of the index of t_sector_df before call this
                        function.
                        Element[m, k] = 1 if Instruments[m] is in Sector[k] else 0.
    :param t_weight: A pd.Series with length = N1 >= N, make sure that index of t_raw_data
                     is a subset of the index of t_weight. Each element means relative weight
                     of corresponding instrument when regression.
    :return:
    """
    n = len(t_raw_data)
    idx = t_raw_data.index
    if t_weight is None:
        _w: np.ndarray = np.ones(n) / n
    else:
        _w: np.ndarray = t_weight[idx].values

    _w = np.diag(_w)  # It is allowed that sum of _w may not equal 1
    _x: np.ndarray = t_sector_df.loc[idx].values
    _y: np.ndarray = t_raw_data.values

    xw = _x.T.dot(_w)
    xwx_inv = np.linalg.inv(xw.dot(_x))
    xwy = xw.dot(_y)
    b = xwx_inv.dot(xwy)  # b = [XWX]^{-1}[XWY]
    _r = _y - _x.dot(b)  # r = Y - bX
    return pd.Series(data=_r, index=idx)


if __name__ == "__main__":
    print("---- TEST EXAMPLE 0")
    sector_classification = {
        "CU.SHF": "METAL",
        "AL.SHF": "METAL",
        "ZN.SHF": "METAL",
        "A.DCE": "OIL",
        "M.DCE": "OIL",
        "Y.DCE": "OIL",
        "P.DCE": "OIL",
        "MA.CZC": "CHEM",
        "TA.CZC": "CHEM",
        "PP.DCE": "CHEM",
    }

    sector_df = pd.DataFrame.from_dict({z: {sector_classification[z]: 1} for z in sector_classification}, orient="index").fillna(0)
    print(sector_df)

    raw_factor = pd.Series({
        "CU.SHF": 10,
        "ZN.SHF": 8,
        "Y.DCE": 3,
        "P.DCE": 0,
        "MA.CZC": -2,
        "TA.CZC": -4,
    })

    weight = pd.Series({
        "Y.DCE": 2,
        "P.DCE": 1,
        "MA.CZC": 1,
        "TA.CZC": 1,
        "CU.SHF": 1,
        "ZN.SHF": 2,
    })

    new_factor = neutralize_by_sector(
        t_raw_data=raw_factor,
        t_sector_df=sector_df,
        t_weight=weight,
    )

    df = pd.DataFrame({
        "OLD": raw_factor,
        "WGT": weight,
        "NEW": new_factor,
    }).loc[raw_factor.index]

    print(df)

    # ---- TEST EXAMPLE 1
    print("---- TEST EXAMPLE 1")
    df = pd.DataFrame({
        "sector": ["I1", "I1", "I2", "I2"],
        "I1": [1, 1, 0, 0],
        "I2": [0, 0, 1, 1],
        "raw_factor": [100, 80, 32, 8],
        "raw_return": [24, 6, 45, 15],
        "ave_factor_by_sec": [90, 90, 20, 20],
        "ave_return_by_sec": [15, 15, 30, 30],
    }, index=["S1", "S2", "S3", "S4"])
    df.index.name = "资产"
    df["neu_factor"] = neutralize_by_sector(t_raw_data=df["raw_factor"], t_sector_df=df[["I1", "I2"]], t_weight=None)
    df["neu_return"] = neutralize_by_sector(t_raw_data=df["raw_return"], t_sector_df=df[["I1", "I2"]], t_weight=None)

    # wgt_srs = pd.Series({"S1": 1, "S2": 1, "S3": 2, "S4": 3})
    # df["neu_factor"] = neutralize_by_sector(t_raw_data=df["raw_factor"], t_sector_df=df[["I1", "I2"]], t_weight=wgt_srs)
    # df["neu_return"] = neutralize_by_sector(t_raw_data=df["raw_return"], t_sector_df=df[["I1", "I2"]], t_weight=wgt_srs)

    pd.set_option("display.width", 0)
    print(df)

    for x, y in product(["raw_factor", "neu_factor", "I1", "I2"], ["raw_return", "neu_return"]):
        r = df[[x, y]].corr().loc[x, y]
        # print("Corr({:4s},{:4s}) = {:>9.4f}".format(x, y, r))
        print("{} & {} & {:>.3f}\\\\".format(x, y, r))
