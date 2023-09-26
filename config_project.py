# begin date for argument bgn in main.py
bgn_dates_in_overwrite_mod = {
    "IR": "20120101",  # instrument_return
    "AU": "20120301",  # available_universe
    "MR": "20120301",  # market_return
    "TR": "20120301",  # test_return
    "TRN": "20120301",  # test_return_neutral

    "FEB": "20120101",  # factor_exposure basic
    "FE": "20130101",  # factor_exposure
    "FEN": "20130101",  # factor_exposure_neutral

    "IC": "20140701",  # ic-test
    "ICN": "20140701",  # ic-test-neutral
    "FECOR": "20140701",  # factors correlation

    "SIG": "20140701",  # signals
    "SIMU": "20140701",  # signals
}

# universe
concerned_instruments_universe = [
    "AU.SHF",
    "AG.SHF",
    "CU.SHF",
    "AL.SHF",
    "PB.SHF",
    "ZN.SHF",
    "SN.SHF",
    "NI.SHF",
    "SS.SHF",
    "RB.SHF",
    "HC.SHF",
    "J.DCE",
    "JM.DCE",
    "I.DCE",
    "FG.CZC",
    "SA.CZC",
    "UR.CZC",
    "ZC.CZC",
    "SF.CZC",
    "SM.CZC",
    "Y.DCE",
    "P.DCE",
    "OI.CZC",
    "M.DCE",
    "RM.CZC",
    "A.DCE",
    "RU.SHF",
    "BU.SHF",
    "FU.SHF",
    "L.DCE",
    "V.DCE",
    "PP.DCE",
    "EG.DCE",
    "EB.DCE",
    "PG.DCE",
    "TA.CZC",
    "MA.CZC",
    "SP.SHF",
    "CF.CZC",
    "CY.CZC",
    "SR.CZC",
    "C.DCE",
    "CS.DCE",
    "JD.DCE",
    "LH.DCE",
    "AP.CZC",
    "CJ.CZC",
]
ciu_size = len(concerned_instruments_universe)  # should be 47

# sector
sectors = ["AUAG", "METAL", "BLACK", "OIL", "CHEM", "MISC"]  # 6
sector_classification = {
    "AU.SHF": "AUAG",
    "AG.SHF": "AUAG",
    "CU.SHF": "METAL",
    "AL.SHF": "METAL",
    "PB.SHF": "METAL",
    "ZN.SHF": "METAL",
    "SN.SHF": "METAL",
    "NI.SHF": "METAL",
    "SS.SHF": "METAL",
    "RB.SHF": "BLACK",
    "HC.SHF": "BLACK",
    "J.DCE": "BLACK",
    "JM.DCE": "BLACK",
    "I.DCE": "BLACK",
    "FG.CZC": "BLACK",
    "SA.CZC": "BLACK",
    "UR.CZC": "BLACK",
    "ZC.CZC": "BLACK",
    "SF.CZC": "BLACK",
    "SM.CZC": "BLACK",
    "Y.DCE": "OIL",
    "P.DCE": "OIL",
    "OI.CZC": "OIL",
    "M.DCE": "OIL",
    "RM.CZC": "OIL",
    "A.DCE": "OIL",
    "RU.SHF": "CHEM",
    "BU.SHF": "CHEM",
    "FU.SHF": "CHEM",
    "L.DCE": "CHEM",
    "V.DCE": "CHEM",
    "PP.DCE": "CHEM",
    "EG.DCE": "CHEM",
    "EB.DCE": "CHEM",
    "PG.DCE": "CHEM",
    "TA.CZC": "CHEM",
    "MA.CZC": "CHEM",
    "SP.SHF": "CHEM",
    "CF.CZC": "MISC",
    "CY.CZC": "MISC",
    "SR.CZC": "MISC",
    "C.DCE": "MISC",
    "CS.DCE": "MISC",
    "LH.DCE": "MISC",
    "JD.DCE": "MISC",
    "AP.CZC": "MISC",
    "CJ.CZC": "MISC",
}

# available universe
available_universe_options = {
    "rolling_window": 20,
    "amount_threshold": 5,
}
