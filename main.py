import argparse
import datetime as dt


def parse_args(bgn_dates_options: dict[str, str]):
    args_parser = argparse.ArgumentParser(description="Entry point of this project", formatter_class=argparse.RawTextHelpFormatter)
    args_parser.add_argument("-w", "--switch", type=str, choices=('ir', 'au', 'mr', 'tr', 'trn', 'fe', 'fen', 'ic', 'icn', 'ics', 'icns', 'icc', 'fecor', 'sig', 'simu', 'eval'),
                             help="""use this to decide which parts to run, available options = {
        'ir': instrument return,
        'au': available universe,
        'mr': market return,
        'tr': test return,
        'trn': test return neutral,
        'fe': factors exposure,
        'fen': factors exposure neutral,
        'ic': ic-tests,
        'icn': ic-tests-neutral,
        'ics': ic-tests-summary,
        'icns': ic-tests-neutral-summary,
        'icc': ic-tests-comparison,
        'fecor': factor exposure correlation,
        'sig': signals,
        'simu': simulations,
        'eval': evaluations,
        }""")
    args_parser.add_argument("-m", "--mode", type=str, choices=("o", "a"), help="""run mode, available options = {'o', 'a'}""")
    args_parser.add_argument("-b", "--bgn", type=str, help="""begin date, must be provided if run_mode = 'a' else DO NOT provided.""")
    args_parser.add_argument("-s", "--stp", type=str, help="""stop  date, NOT INCLUDED, must be provided if run_mode = 'o'.""")
    args_parser.add_argument("-f", "--factor", type=str, default="", help="""optional, must be provided if switch = 'factors_exposure', use this to decide which factor""",
                             choices=(
                                 'mtm', 'size', 'oi', 'rs', 'basis', 'ts', 'liquid', 'sr', 'hr', 'netoi', 'netoiw', 'netdoi', 'netdoiw',
                                 'skew', 'vol', 'rvol', 'cv', 'ctp', 'cvp', 'csp', 'beta', 'val', 'cbeta', 'ibeta', 'macd', 'kdj', 'rsi',),
                             )
    args_parser.add_argument("-t", "--type", type=str, default="", choices=('hedge-raw', 'hedge-ma', 'portfolio'),
                             help="""optional, must be provided if switch in ('sig','simu','eval'), use this to decide type of signal/simulation""")
    args_parser.add_argument("-p", "--process", type=int, default=5, help="""number of process to be called when calculating, default = 5""")
    args = args_parser.parse_args()

    _switch = args.switch.upper()
    if _switch in ["ICS", "ICNS", "ICC", "EVAL"]:
        _run_mode = None
    elif _switch in ["IR", "MR", "FECOR"]:
        _run_mode = "O"
    else:
        _run_mode = args.mode.upper()
    _bgn_date, _stp_date = (bgn_dates_options[_switch] if _run_mode in ["O"] else args.bgn), args.stp
    if (_stp_date is None) and (_bgn_date is not None):
        _stp_date = (dt.datetime.strptime(_bgn_date, "%Y%m%d") + dt.timedelta(days=1)).strftime("%Y%m%d")
    _factor = args.factor.upper() if _switch in ["FE"] else None
    _sig_type = args.type.upper() if _switch in ["SIG", "SIMU", "EVAL"] else None
    _proc_num = args.process
    return _switch, _run_mode, _bgn_date, _stp_date, _factor, _sig_type, _proc_num


if __name__ == "__main__":
    import pandas as pd
    from setup_project import calendar_path, futures_instru_info_path
    from config_project import bgn_dates_in_overwrite_mod, concerned_instruments_universe, sector_classification
    from skyrim.whiterun import CCalendarMonthly, CInstrumentInfoTable

    switch, run_mode, bgn_date, stp_date, factor, sig_type, proc_num = parse_args(bgn_dates_in_overwrite_mod)

    # some shared data
    calendar = CCalendarMonthly(calendar_path)
    instru_into_tab = CInstrumentInfoTable(futures_instru_info_path, t_index_label="windCode", t_type="CSV")
    mother_universe_df = pd.DataFrame({"instrument": concerned_instruments_universe})
    sector_df = pd.DataFrame.from_dict({z: {sector_classification[z]: 1} for z in concerned_instruments_universe}, orient="index").fillna(0)

    #  ----------- CORE -----------
    if switch in ["IR"]:  # "INSTRUMENT RETURN":
        from setup_project import futures_by_instrument_dir, major_return_db_name, instruments_return_dir
        from returns.instrument_return import merge_instru_return

        merge_instru_return(
            bgn_date=bgn_date, stp_date=stp_date,
            futures_by_instrument_dir=futures_by_instrument_dir, major_return_db_name=major_return_db_name,
            instruments_return_dir=instruments_return_dir,
            concerned_instruments_universe=concerned_instruments_universe,
        )
    elif switch in ["AU"]:  # "AVAILABLE UNIVERSE"
        from setup_project import available_universe_dir, futures_by_instrument_dir, major_return_db_name
        from config_project import available_universe_options
        from returns.available_universe import cal_available_universe

        cal_available_universe(
            run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date,
            instruments_universe=concerned_instruments_universe,
            available_universe_options=available_universe_options,
            available_universe_dir=available_universe_dir,
            futures_by_instrument_dir=futures_by_instrument_dir,
            major_return_db_name=major_return_db_name,
            calendar=calendar,
        )
    elif switch in ["MR"]:  # "MARKET RETURN"
        from setup_project import available_universe_dir, instruments_return_dir
        from returns.market_return import cal_market_return

        cal_market_return(
            bgn_date=bgn_date, stp_date=stp_date,
            available_universe_dir=available_universe_dir,
            instruments_return_dir=instruments_return_dir,
            calendar=calendar,
        )
    elif switch in ["TR"]:  # "TEST RETURN"
        from setup_project import instruments_return_dir, test_return_dir
        from returns.test_return import cal_test_return

        cal_test_return(
            run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date,
            instruments_return_dir=instruments_return_dir,
            test_return_dir=test_return_dir,
            calendar=calendar,
        )
    elif switch in ["TRN"]:  # "TEST RETURN NEUTRAL"
        from setup_project import available_universe_dir, test_return_dir
        from returns.test_return_neutral import cal_test_return_neutral

        cal_test_return_neutral(
            run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date,
            instruments_universe=concerned_instruments_universe,
            available_universe_dir=available_universe_dir,
            sector_classification=sector_classification,
            test_return_dir=test_return_dir,
            calendar=calendar,
        )
    elif switch in ["FE"]:
        from setup_project import futures_by_instrument_dir, major_return_db_name, factors_exposure_raw_dir
        from config_factor import factors_settings, factors_transformation_directions
        from factors.factors_cls_with_args import CMpFactorWithArgWin, CMpFactorMACD, CMpFactorKDJ, CMpFactorRSI
        from factors.factors_cls_transformer import CMpTransformer, apply_transformations

        shared_keywords = dict(concerned_instruments_universe=concerned_instruments_universe, factors_exposure_dst_dir=factors_exposure_raw_dir, calendar=calendar)
        raw_factor_bgn_date = bgn_dates_in_overwrite_mod["FEB"] if run_mode in ["O"] else bgn_date
        if factor == "MTM":
            from factors.factors_cls_without_args import CFactorMTM

            agent_factor = CFactorMTM(futures_by_instrument_dir, major_return_db_name, **shared_keywords)
            agent_factor.core(run_mode, raw_factor_bgn_date, stp_date)
            apply_transformations(proc_num=proc_num, factor=factor, transform_types=["SUM", "SHARPE"],
                                  factors_settings=factors_settings, factors_transformation_directions=factors_transformation_directions,
                                  factors_exposure_dir=factors_exposure_raw_dir,
                                  run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date, **shared_keywords)
        elif factor == "SIZE":
            from setup_project import instrument_volume_db_name
            from factors.factors_cls_without_args import CFactorsSIZE

            agent_factor = CFactorsSIZE(futures_by_instrument_dir, instrument_volume_db_name, **shared_keywords)
            agent_factor.core(run_mode, raw_factor_bgn_date, stp_date)
            apply_transformations(proc_num=proc_num, factor=factor, transform_types=["AVER", "BR", "LR"],
                                  factors_settings=factors_settings, factors_transformation_directions=factors_transformation_directions,
                                  factors_exposure_dir=factors_exposure_raw_dir,
                                  run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date, **shared_keywords)
        elif factor == "OI":
            from setup_project import instrument_volume_db_name
            from factors.factors_cls_without_args import CFactorsOI

            agent_factor = CFactorsOI(futures_by_instrument_dir, instrument_volume_db_name, **shared_keywords)
            agent_factor.core(run_mode, raw_factor_bgn_date, stp_date)
            apply_transformations(proc_num=proc_num, factor=factor, transform_types=["BR", "LR"],
                                  factors_settings=factors_settings, factors_transformation_directions=factors_transformation_directions,
                                  factors_exposure_dir=factors_exposure_raw_dir,
                                  run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date, **shared_keywords)
        elif factor == "RS":
            from setup_project import by_instru_fd_dir
            from factors.factors_cls_without_args import CFactorsRS

            agent_factor = CFactorsRS(by_instru_fd_dir, **shared_keywords)
            agent_factor.core(run_mode, raw_factor_bgn_date, stp_date)
            apply_transformations(proc_num=proc_num, factor=factor, transform_types=["BR", "LR"],
                                  factors_settings=factors_settings, factors_transformation_directions=factors_transformation_directions,
                                  factors_exposure_dir=factors_exposure_raw_dir,
                                  run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date, **shared_keywords)
        elif factor == "BASIS":
            from setup_project import by_instru_fd_dir
            from factors.factors_cls_without_args import CFactorsBASIS

            agent_factor = CFactorsBASIS(by_instru_fd_dir, **shared_keywords)
            agent_factor.core(run_mode, raw_factor_bgn_date, stp_date)
            apply_transformations(proc_num=proc_num, factor=factor, transform_types=["AVER", "BD", "LD"],
                                  factors_settings=factors_settings, factors_transformation_directions=factors_transformation_directions,
                                  factors_exposure_dir=factors_exposure_raw_dir,
                                  run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date, **shared_keywords)
        elif factor == "TS":
            from setup_project import major_minor_db_name, by_instru_md_dir
            from factors.factors_cls_without_args import CFactorsTS

            agent_factor = CFactorsTS(futures_by_instrument_dir, major_minor_db_name, by_instru_md_dir, **shared_keywords)
            agent_factor.core(run_mode, raw_factor_bgn_date, stp_date)
            apply_transformations(proc_num=proc_num, factor=factor, transform_types=["AVER", "BD", "LD"],
                                  factors_settings=factors_settings, factors_transformation_directions=factors_transformation_directions,
                                  factors_exposure_dir=factors_exposure_raw_dir,
                                  run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date, **shared_keywords)
        elif factor == "LIQUID":
            from factors.factors_cls_without_args import CFactorsLIQUID

            agent_factor = CFactorsLIQUID(futures_by_instrument_dir, major_return_db_name, **shared_keywords)
            agent_factor.core(run_mode, raw_factor_bgn_date, stp_date)
            apply_transformations(proc_num=proc_num, factor=factor, transform_types=["AVER", "BD", "LD"],
                                  factors_settings=factors_settings, factors_transformation_directions=factors_transformation_directions,
                                  factors_exposure_dir=factors_exposure_raw_dir,
                                  run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date, **shared_keywords)
        elif factor == "SR":
            from setup_project import instrument_volume_db_name
            from factors.factors_cls_without_args import CFactorsSR

            agent_factor = CFactorsSR(futures_by_instrument_dir, instrument_volume_db_name, **shared_keywords)
            agent_factor.core(run_mode, raw_factor_bgn_date, stp_date)
            apply_transformations(proc_num=proc_num, factor=factor, transform_types=["AVER", "BD", "LD"],
                                  factors_settings=factors_settings, factors_transformation_directions=factors_transformation_directions,
                                  factors_exposure_dir=factors_exposure_raw_dir,
                                  run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date, **shared_keywords)
        elif factor == "HR":
            from setup_project import instrument_volume_db_name
            from factors.factors_cls_without_args import CFactorsHR

            agent_factor = CFactorsHR(futures_by_instrument_dir, instrument_volume_db_name, **shared_keywords)
            agent_factor.core(run_mode, raw_factor_bgn_date, stp_date)
            apply_transformations(proc_num=proc_num, factor=factor, transform_types=["AVER", "BD", "LD"],
                                  factors_settings=factors_settings, factors_transformation_directions=factors_transformation_directions,
                                  factors_exposure_dir=factors_exposure_raw_dir,
                                  run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date, **shared_keywords)
        elif factor == "NETOI":
            from setup_project import instrument_volume_db_name, instrument_member_db_name
            from factors.factors_cls_without_args import CFactorsNETOI

            agent_factor = CFactorsNETOI(futures_by_instrument_dir, instrument_volume_db_name, instrument_member_db_name, **shared_keywords)
            agent_factor.core(run_mode, raw_factor_bgn_date, stp_date)
            apply_transformations(proc_num=proc_num, factor=factor, transform_types=["AVER", "BD", "LD"],
                                  factors_settings=factors_settings, factors_transformation_directions=factors_transformation_directions,
                                  factors_exposure_dir=factors_exposure_raw_dir,
                                  run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date, **shared_keywords)
        elif factor == "NETOIW":
            from setup_project import instrument_volume_db_name, instrument_member_db_name
            from factors.factors_cls_without_args import CFactorsNETOIW

            agent_factor = CFactorsNETOIW(futures_by_instrument_dir, instrument_volume_db_name, instrument_member_db_name, **shared_keywords)
            agent_factor.core(run_mode, raw_factor_bgn_date, stp_date)
            apply_transformations(proc_num=proc_num, factor=factor, transform_types=["AVER", "BD", "LD"],
                                  factors_settings=factors_settings, factors_transformation_directions=factors_transformation_directions,
                                  factors_exposure_dir=factors_exposure_raw_dir,
                                  run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date, **shared_keywords)
        elif factor == "NETDOI":
            from setup_project import instrument_volume_db_name, instrument_member_db_name
            from factors.factors_cls_without_args import CFactorsNETDOI

            agent_factor = CFactorsNETDOI(futures_by_instrument_dir, instrument_volume_db_name, instrument_member_db_name, **shared_keywords)
            agent_factor.core(run_mode, raw_factor_bgn_date, stp_date)
            apply_transformations(proc_num=proc_num, factor=factor, transform_types=["AVER", "BD", "LD"],
                                  factors_settings=factors_settings, factors_transformation_directions=factors_transformation_directions,
                                  factors_exposure_dir=factors_exposure_raw_dir,
                                  run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date, **shared_keywords)
        elif factor == "NETDOIW":
            from setup_project import instrument_volume_db_name, instrument_member_db_name
            from factors.factors_cls_without_args import CFactorsNETDOIW

            agent_factor = CFactorsNETDOIW(futures_by_instrument_dir, instrument_volume_db_name, instrument_member_db_name, **shared_keywords)
            agent_factor.core(run_mode, raw_factor_bgn_date, stp_date)
            apply_transformations(proc_num=proc_num, factor=factor, transform_types=["AVER", "BD", "LD"],
                                  factors_settings=factors_settings, factors_transformation_directions=factors_transformation_directions,
                                  factors_exposure_dir=factors_exposure_raw_dir,
                                  run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date, **shared_keywords)
        elif factor in ["SKEW", "VOL", "RVOL", "CV", "CTP", "CVP", "CSP", "VAL"]:
            agent_factor = CMpFactorWithArgWin(proc_num, factor, factors_settings[factor]["H"], run_mode, bgn_date, stp_date)
            agent_factor.mp_cal_factor(futures_by_instrument_dir=futures_by_instrument_dir, major_return_db_name=major_return_db_name, **shared_keywords)
            src_factor_ids = [f"{factor}{_:03d}" for _ in factors_settings[factor]["H"]]
            direction = factors_transformation_directions.get((factor, "LD"), 1)
            agent_transformer = CMpTransformer(proc_num, src_factor_ids, "LD", factors_settings[factor]["LD"], direction, factors_exposure_raw_dir,
                                               run_mode, bgn_date, stp_date, factor)
            agent_transformer.mp_cal_transform(**shared_keywords)
        elif factor == "BETA":
            from setup_project import instruments_return_dir

            agent_factor = CMpFactorWithArgWin(proc_num, factor, factors_settings[factor]["H"], run_mode, bgn_date, stp_date)
            agent_factor.mp_cal_factor(market_return_dir=instruments_return_dir, market_return_file="market_return.csv.gz",
                                       futures_by_instrument_dir=futures_by_instrument_dir, major_return_db_name=major_return_db_name, **shared_keywords)
            src_factor_ids = [f"{factor}{_:03d}" for _ in factors_settings[factor]["H"]]
            direction = factors_transformation_directions.get(("BETA", "LD"), 1)
            agent_transformer = CMpTransformer(proc_num, src_factor_ids, "LD", factors_settings[factor]["LD"], direction, factors_exposure_raw_dir,
                                               run_mode, bgn_date, stp_date, factor)
            agent_transformer.mp_cal_transform(**shared_keywords)
        elif factor == "CBETA":
            from setup_project import forex_dir, exchange_rate_file

            agent_factor = CMpFactorWithArgWin(proc_num, factor, factors_settings[factor]["H"], run_mode, bgn_date, stp_date)
            agent_factor.mp_cal_factor(forex_dir=forex_dir, exchange_rate_file=exchange_rate_file,
                                       futures_by_instrument_dir=futures_by_instrument_dir, major_return_db_name=major_return_db_name, **shared_keywords)

            src_factor_ids = [f"{factor}{_:03d}" for _ in factors_settings[factor]["H"]]
            direction = factors_transformation_directions.get(("CBETA", "LD"), 1)
            agent_transformer = CMpTransformer(proc_num, src_factor_ids, "LD", factors_settings[factor]["LD"], direction, factors_exposure_raw_dir,
                                               run_mode, bgn_date, stp_date, factor)
            agent_transformer.mp_cal_transform(**shared_keywords)
        elif factor == "IBETA":
            from setup_project import macro_economic_dir, cpi_m2_file

            agent_factor = CMpFactorWithArgWin(proc_num, factor, factors_settings[factor]["H"], run_mode, bgn_date, stp_date)
            agent_factor.mp_cal_factor(macro_economic_dir=macro_economic_dir, cpi_m2_file=cpi_m2_file,
                                       futures_by_instrument_dir=futures_by_instrument_dir, major_return_db_name=major_return_db_name, **shared_keywords)

            src_factor_ids = [f"{factor}{_:03d}" for _ in factors_settings[factor]["H"]]
            direction = factors_transformation_directions.get(("IBETA", "LD"), 1)
            agent_transformer = CMpTransformer(proc_num, src_factor_ids, "LD", factors_settings[factor]["LD"], direction, factors_exposure_raw_dir,
                                               run_mode, bgn_date, stp_date, factor)
            agent_transformer.mp_cal_transform(**shared_keywords)
        elif factor == "MACD":
            ewm_bgn_date = bgn_dates_in_overwrite_mod["FEB"]
            agent_factor = CMpFactorMACD(proc_num, factors_settings[factor]["F"], factors_settings[factor]["S"], factors_settings[factor]["ALPHA"],
                                         ewm_bgn_date, run_mode, bgn_date, stp_date)
            agent_factor.mp_cal_factor(futures_by_instrument_dir=futures_by_instrument_dir, major_return_db_name=major_return_db_name, **shared_keywords)
        elif factor == "KDJ":
            ewm_bgn_date = bgn_dates_in_overwrite_mod["FEB"]
            agent_factor = CMpFactorKDJ(proc_num, factors_settings[factor]["N"], ewm_bgn_date, run_mode, bgn_date, stp_date)
            agent_factor.mp_cal_factor(futures_by_instrument_dir=futures_by_instrument_dir, major_return_db_name=major_return_db_name, **shared_keywords)
        elif factor == "RSI":
            ewm_bgn_date = bgn_dates_in_overwrite_mod["FEB"]
            agent_factor = CMpFactorRSI(proc_num, factors_settings[factor]["N"], ewm_bgn_date, run_mode, bgn_date, stp_date)
            agent_factor.mp_cal_factor(futures_by_instrument_dir=futures_by_instrument_dir, major_return_db_name=major_return_db_name, **shared_keywords)
    elif switch in ["FEN"]:
        from config_factor import factors_raw
        from setup_project import available_universe_dir, factors_exposure_raw_dir, factors_exposure_neu_dir
        from factors.factors_neutral import cal_factors_neutral_mp

        cal_factors_neutral_mp(
            proc_num=proc_num, factors=factors_raw,
            run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date,
            mother_universe_df=mother_universe_df, sector_df=sector_df,
            available_universe_dir=available_universe_dir,
            factors_exposure_raw_dir=factors_exposure_raw_dir,
            factors_exposure_neu_dir=factors_exposure_neu_dir,
            calendar=calendar, )
    elif switch in ["IC"]:
        from config_factor import factors_raw
        from setup_project import ic_tests_raw_dir, available_universe_dir, factors_exposure_raw_dir, test_return_dir
        from ic_tests.ic_tests_cls import cal_ic_tests_mp

        cal_ic_tests_mp(
            proc_num=proc_num, factors=factors_raw,
            ic_tests_dir=ic_tests_raw_dir,
            available_universe_dir=available_universe_dir,
            exposure_dir=factors_exposure_raw_dir,
            test_return_dir=test_return_dir,
            calendar=calendar,
            run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date,
            neutral_tag="RAW"
        )
    elif switch in ["ICN"]:
        from config_factor import factors_raw
        from setup_project import ic_tests_neu_dir, available_universe_dir, factors_exposure_neu_dir, test_return_dir
        from ic_tests.ic_tests_cls import cal_ic_tests_mp

        cal_ic_tests_mp(
            proc_num=proc_num, factors=factors_raw,
            ic_tests_dir=ic_tests_neu_dir,
            available_universe_dir=available_universe_dir,
            exposure_dir=factors_exposure_neu_dir,
            test_return_dir=test_return_dir,
            calendar=calendar,
            run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date,
            neutral_tag="NEU",
        )
    elif switch in ["ICS"]:
        from config_factor import factors_raw, factors_classification, factors_group
        from config_portfolio import selected_raw_factors
        from setup_project import ic_tests_raw_dir, ic_tests_summary_dir
        from ic_tests.ic_tests_cls_summary import CICTestsSummary

        agent_summary = CICTestsSummary(
            proc_num=proc_num, ic_tests_dir=ic_tests_raw_dir,
            ic_tests_summary_dir=ic_tests_summary_dir, neutral_tag="RAW",
        )
        agent_summary.get_summary_mp(factors_raw, factors_classification)
        agent_summary.get_cumsum_mp(factors_group, selected_factors_pool=factors_raw)
        agent_summary.plot_selected_factors_cumsum(selected_raw_factors)
    elif switch in ["ICNS"]:
        from config_factor import factors_raw, factors_classification, factors_group
        from config_portfolio import selected_neu_factors
        from setup_project import ic_tests_neu_dir, ic_tests_summary_dir
        from ic_tests.ic_tests_cls_summary import CICTestsSummary

        agent_summary = CICTestsSummary(
            proc_num=proc_num, ic_tests_dir=ic_tests_neu_dir,
            ic_tests_summary_dir=ic_tests_summary_dir, neutral_tag="NEU",
        )
        agent_summary.get_summary_mp(factors_raw, factors_classification)
        agent_summary.get_cumsum_mp(factors_group, selected_factors_pool=factors_raw)
        agent_summary.plot_selected_factors_cumsum(selected_neu_factors)
    elif switch in ["ICC"]:
        from setup_project import ic_tests_summary_dir
        from ic_tests.ic_tests_cls_summary import cal_ic_tests_comparison

        cal_ic_tests_comparison(ic_tests_summary_dir)
    elif switch in ["FECOR"]:
        from setup_project import factors_exposure_raw_dir, factors_exposure_neu_dir, factors_exposure_cor_dir
        from factors.factors_exposure_corr import cal_factors_exposure_corr

        # test_factor_list_l = ["CTP120", "CSP120", "CVP120", "CSP180LD020"]
        # test_factor_list_l = ["MTM", "NETDOIWLD240"]
        test_factor_list_l = ["RSBR020", "RSBR240", "RSLR240"]
        test_factor_list_r = []
        test_neutral_tag = ["RAW", "NEU"][0]

        cal_factors_exposure_corr(
            neutral_tag=test_neutral_tag,
            test_factor_list_l=test_factor_list_l, test_factor_list_r=test_factor_list_r,
            bgn_date=bgn_date, stp_date=stp_date,
            factors_exposure_src_dir=factors_exposure_raw_dir if test_neutral_tag == "RAW" else factors_exposure_neu_dir,
            factors_exposure_corr_dir=factors_exposure_cor_dir,
            calendar=calendar, )
    elif switch in ["SIG"]:
        if sig_type == "HEDGE-RAW":
            from config_factor import factors_raw, factors_neu
            from config_portfolio import uni_props
            from setup_project import available_universe_dir, signals_factor_raw_dir, factors_exposure_raw_dir, factors_exposure_neu_dir
            from signals.signals_cls import cal_signals_hedge_mp

            cal_signals_hedge_mp(proc_num=proc_num, factors=factors_raw, uni_props=uni_props,
                                 available_universe_dir=available_universe_dir, signals_save_dir=signals_factor_raw_dir,
                                 src_factor_dir=factors_exposure_raw_dir, calendar=calendar, tips="signals-raw-hedge",
                                 run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date)
            cal_signals_hedge_mp(proc_num=proc_num, factors=factors_neu, uni_props=uni_props,
                                 available_universe_dir=available_universe_dir, signals_save_dir=signals_factor_raw_dir,
                                 src_factor_dir=factors_exposure_neu_dir, calendar=calendar, tips=f"signals-neu-hedge",
                                 run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date)
        elif sig_type == "HEDGE-MA":
            from config_factor import factors_raw, factors_neu
            from config_portfolio import uni_props, mov_ave_wins
            from setup_project import signals_hedge_test_dir, signals_factor_raw_dir
            from signals.signals_cls import cal_signals_hedge_ma_mp

            cal_signals_hedge_ma_mp(proc_num=proc_num, factors=factors_raw + factors_neu, uni_props=uni_props, mov_ave_wins=mov_ave_wins,
                                    src_signals_save_dir=signals_factor_raw_dir, signals_save_dir=signals_hedge_test_dir, calendar=calendar,
                                    tips="signals-hedge-ma", run_mode=run_mode, bgn_date=bgn_date, stp_date=stp_date)
        elif sig_type == "PORTFOLIO":
            from setup_project import signals_hedge_test_dir, signals_portfolios_dir, simulations_hedge_test_dir, signals_optimized_dir
            from config_factor import factors_classification, factors_raw, factors_neu
            from config_portfolio import selected_src_signal_ids_raw, selected_src_signal_ids_neu, size_raw, size_neu, trn_win, lbd, min_model_days
            from signals.signals_cls_portfolio import CSignalCombineFromOtherSignalsWithFixWeight, CSignalCombineFromOtherSignalsWithDynWeight
            from signals.signals_cls_optimizer import CSignalOptimizerMinUtyCon
            from skyrim.whiterun import SetFontGreen

            print(SetFontGreen(f"... trnWin = {trn_win:>2d}, lbd = {lbd:>6.2f}"))

            # RAW FIX
            signals = CSignalCombineFromOtherSignalsWithFixWeight(
                src_signal_weight={_: 1 / size_raw for _ in selected_src_signal_ids_raw},
                src_signal_ids=selected_src_signal_ids_raw, src_signal_dir=signals_hedge_test_dir, sig_id="RF",
                sig_save_dir=signals_portfolios_dir, calendar=calendar)
            signals.main(run_mode, bgn_date, stp_date)

            # NEU FIX
            signals = CSignalCombineFromOtherSignalsWithFixWeight(
                src_signal_weight={_: 1 / size_neu for _ in selected_src_signal_ids_neu},
                src_signal_ids=selected_src_signal_ids_neu, src_signal_dir=signals_hedge_test_dir, sig_id="NF",
                sig_save_dir=signals_portfolios_dir, calendar=calendar)
            signals.main(run_mode, bgn_date, stp_date)

            # RAW DYN
            optimizer = CSignalOptimizerMinUtyCon(
                save_id="RD", src_signal_ids=selected_src_signal_ids_raw,
                weight_bounds=(1 / size_raw / 2, 2 / size_raw), total_pos_lim=(0, 1), maxiter=10000, tol=1e-8,
                trn_win=trn_win, min_model_days=min_model_days, lbd=lbd,
                simu_test_dir=simulations_hedge_test_dir, optimized_dir=signals_optimized_dir,
                calendar=calendar)
            optimizer.main(run_mode, bgn_date, stp_date)  # only works on the last trade date of each month
            optimizer.plot_optimized_weight(reduced=True)
            signal_weight_df = optimizer.get_signal_weight(run_mode, bgn_date, stp_date)
            signals = CSignalCombineFromOtherSignalsWithDynWeight(
                src_signal_weight=signal_weight_df,
                src_signal_ids=selected_src_signal_ids_raw, src_signal_dir=signals_hedge_test_dir, sig_id="RD",
                sig_save_dir=signals_portfolios_dir, calendar=calendar)
            signals.main(run_mode, bgn_date, stp_date)

            # NEU DYN
            optimizer = CSignalOptimizerMinUtyCon(
                save_id="ND", src_signal_ids=selected_src_signal_ids_neu,
                weight_bounds=(1 / size_neu / 2, 2 / size_neu), total_pos_lim=(0, 1), maxiter=10000, tol=1e-8,
                trn_win=trn_win, min_model_days=min_model_days, lbd=lbd,
                simu_test_dir=simulations_hedge_test_dir, optimized_dir=signals_optimized_dir,
                calendar=calendar)
            optimizer.main(run_mode, bgn_date, stp_date)  # only works on the last trade date of each month
            optimizer.plot_optimized_weight(reduced=True)
            signal_weight_df = optimizer.get_signal_weight(run_mode, bgn_date, stp_date)
            signals = CSignalCombineFromOtherSignalsWithDynWeight(
                src_signal_weight=signal_weight_df,
                src_signal_ids=selected_src_signal_ids_neu, src_signal_dir=signals_hedge_test_dir, sig_id="ND",
                sig_save_dir=signals_portfolios_dir, calendar=calendar)
            signals.main(run_mode, bgn_date, stp_date)
    elif switch in ["SIMU"]:
        from simulations.simulation_cls import cal_simulations_mp
        from setup_project import futures_by_instrument_dir, major_return_db_name

        if sig_type == "HEDGE-MA":
            import itertools as ittl
            from setup_project import signals_hedge_test_dir, simulations_hedge_test_dir
            from config_factor import factors_raw, factors_neu
            from config_portfolio import uni_props, mov_ave_wins, cost_rate_hedge_test

            sig_ids = [f"{sid}_UHP{int(uni_prop * 10):02d}_MA{mov_ave_win:02d}"
                       for sid, uni_prop, mov_ave_win in ittl.product(factors_raw + factors_neu, uni_props, mov_ave_wins)]
            cal_simulations_mp(
                proc_num=proc_num,
                sig_ids=sig_ids, run_mode=run_mode, test_bgn_date=bgn_date, test_stp_date=stp_date,
                cost_rate=cost_rate_hedge_test, test_universe=concerned_instruments_universe,
                signals_dir=signals_hedge_test_dir, simulations_dir=simulations_hedge_test_dir,
                futures_by_instrument_dir=futures_by_instrument_dir, major_return_db_name=major_return_db_name,
                calendar=calendar, tips="Simulation for hedge-test factors with MA"
            )

        elif sig_type == "PORTFOLIO":
            from setup_project import signals_portfolios_dir, simulations_portfolios_dir
            from config_portfolio import test_portfolio_ids, cost_rate_portfolios
            from skyrim.whiterun import SetFontGreen

            print(f"... simu bgn_date = {SetFontGreen(bgn_date)}")
            cal_simulations_mp(
                proc_num=proc_num,
                sig_ids=test_portfolio_ids, run_mode=run_mode, test_bgn_date=bgn_date, test_stp_date=stp_date,
                cost_rate=cost_rate_portfolios, test_universe=concerned_instruments_universe,
                signals_dir=signals_portfolios_dir, simulations_dir=simulations_portfolios_dir,
                futures_by_instrument_dir=futures_by_instrument_dir, major_return_db_name=major_return_db_name,
                calendar=calendar, tips="Simulation for portfolios"
            )
    elif switch in ["EVAL"]:
        from config_portfolio import risk_free_rate, performance_indicators, test_portfolio_ids

        if sig_type == "HEDGE-MA":
            from setup_project import simulations_hedge_test_dir, evaluations_hedge_test_dir
            from config_factor import factors_raw, factors_neu, factors_classification
            from config_portfolio import uni_props, mov_ave_wins, selected_raw_factors_and_uni_prop_ma, selected_neu_factors_and_uni_prop_ma
            from simulations.evaluations_cls import eval_hedge_ma_mp, concat_eval_ma_results, plot_selected_factors_and_uni_prop_ma

            eval_hedge_ma_mp(proc_num=proc_num,
                             factors=factors_raw, factors_neutral=factors_neu, uni_props=uni_props, mov_ave_wins=mov_ave_wins,
                             factors_classification=factors_classification,
                             indicators=performance_indicators,
                             simu_save_dir=simulations_hedge_test_dir,
                             eval_save_dir=evaluations_hedge_test_dir,
                             annual_risk_free_rate=risk_free_rate
                             )
            concat_eval_ma_results(uni_props, mov_ave_wins, evaluations_hedge_test_dir)
            plot_selected_factors_and_uni_prop_ma(selected_raw_factors_and_uni_prop_ma, "RAW", simulations_hedge_test_dir, evaluations_hedge_test_dir)
            plot_selected_factors_and_uni_prop_ma(selected_neu_factors_and_uni_prop_ma, "NEU", simulations_hedge_test_dir, evaluations_hedge_test_dir)

        elif sig_type == "PORTFOLIO":
            from setup_project import simulations_portfolios_dir, evaluations_portfolios_dir
            from simulations.evaluations_cls import CEvaluationPortfolio

            evaluator = CEvaluationPortfolio(
                eval_id="portfolios", simu_ids=test_portfolio_ids,
                indicators=performance_indicators, simu_save_dir=simulations_portfolios_dir,
                eval_save_dir=evaluations_portfolios_dir, annual_risk_free_rate=0,
            )
            evaluator.main(True)
            evaluator.eval_by_year()
            evaluator.plot_nav()
            evaluator.plot_nav_by_year()
    else:
        pass
