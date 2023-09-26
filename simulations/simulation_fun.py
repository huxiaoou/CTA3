import os
import datetime as dt
import itertools as ittl
import multiprocessing as mp
from skyrim.whiterun import CCalendar, CInstrumentInfoTable
from skyrim.riverwood2 import CManagerMarketData, CManagerSignalOpt, CPortfolio
from skyrim.winterhold import remove_files_in_the_dir, check_and_mkdir
from skyrim.falkreath import CLib1Tab1


def simulation_single_factor(
        signal_id: str, hold_period_n: int, start_delay: int,
        calendar_path: str, instrument_info_path: str,
        md_by_instru_dir: str, major_minor_dir: str, available_universe_dir: str,
        sig_dir: str, dst_dir: str,
        database_structure: dict[str, CLib1Tab1],
        test_universe: list[str], test_bgn_date: str, test_stp_date: str,
        cost_reservation: float, cost_rate: float, init_premium: float,
        skip_if_exist: bool
):
    # --- pid
    port_id = "{}.HPN{:03d}.D{:02d}".format(signal_id, hold_period_n, start_delay)
    nav_file = "{}.nav.daily.csv.gz".format(port_id)
    nav_path = os.path.join(dst_dir, port_id, nav_file)
    if skip_if_exist and os.path.exists(nav_path):
        return 0

    # --- tips
    t0 = dt.datetime.now()
    print("| {} | {:>60s} | calculating ... |".format(t0, port_id))

    # --- directory check
    dir_pid = os.path.join(dst_dir, port_id)
    dir_pid_trades = os.path.join(dir_pid, "trades")
    dir_pid_positions = os.path.join(dir_pid, "positions")
    check_and_mkdir(dir_pid)
    check_and_mkdir(dir_pid_trades)
    check_and_mkdir(dir_pid_positions)
    remove_files_in_the_dir(dir_pid_trades)
    remove_files_in_the_dir(dir_pid_positions)

    # 3 - load calendar and hist dates list
    trade_calendar = CCalendar(calendar_path)

    # 4 - load aux data
    instrument_info = CInstrumentInfoTable(t_path=instrument_info_path, t_index_label="windCode", t_type="CSV")
    manager_md = CManagerMarketData(t_mother_universe=test_universe, t_dir_market_data=md_by_instru_dir, t_dir_major_data=major_minor_dir)
    manager_signal = CManagerSignalOpt(
        t_mother_universe=test_universe, t_available_universe_dir=available_universe_dir,
        t_database_structure=database_structure,
        t_factors_by_tm_dir=sig_dir, t_factor_lbl=signal_id,
        t_mgr_md=manager_md,
        t_is_trend_follow=True, t_print_details=False
    )

    # 5 - simulation main loop
    simu_portfolio = CPortfolio(
        t_pid=port_id,
        t_init_cash=init_premium, t_cost_reservation=cost_reservation, t_cost_rate=cost_rate,
        t_dir_pid=dir_pid, t_dir_pid_trades=dir_pid_trades, t_dir_pid_positions=dir_pid_positions,
        t_save_details=False
    )
    simu_portfolio.main_loop(
        t_simu_bgn_date=test_bgn_date, t_simu_stp_date=test_stp_date, t_start_delay=start_delay, t_hold_period_n=hold_period_n,
        t_trade_calendar=trade_calendar, t_instru_info=instrument_info, t_mgr_signal=manager_signal, t_mgr_md=manager_md
    )

    # --- end tips
    t1 = dt.datetime.now()
    print("| {} | {:>60s} | calculated  ... | time consuming = {:>6.2f} seconds |".format(t1, port_id, (t1 - t0).total_seconds()))
    return 0


def cal_simulations_mp(
        proc_num: int,
        signal_ids: list[str], test_windows: list[int],
        **kwargs):
    t0 = dt.datetime.now()
    pool = mp.Pool(processes=proc_num)
    for signal_id, test_window in ittl.product(signal_ids, test_windows):
        for start_delay in range(test_window):
            pool.apply_async(simulation_single_factor, args=(signal_id, test_window, start_delay), kwds=kwargs)
    pool.close()
    pool.join()
    t1 = dt.datetime.now()
    print("... total time consuming: {:.2f} seconds".format((t1 - t0).total_seconds()))
    return 0
