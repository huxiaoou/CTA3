"""
Created by huxo
Initialized @ 14:10, 2023/09/26
=========================================
This project is mainly about:
0.  calculate factors of futures
"""

import os
import sys
import json
import platform

# platform confirmation
this_platform = platform.system().upper()
if this_platform == "WINDOWS":
    with open("/Deploy/config3.json", "r", encoding="utf-8") as j:
        global_config = json.load(j)
elif this_platform == "LINUX":
    with open("/home/huxo/Deploy/config3.json", "r", encoding="utf-8") as j:
        global_config = json.load(j)
else:
    print("... this platform is {}.".format(this_platform))
    print("... it is not a recognized platform, please check again.")
    sys.exit()

deploy_dir = global_config["deploy_dir"][this_platform]
project_data_root_dir = os.path.join(deploy_dir, "Data")

# --- calendar
calendar_dir = os.path.join(project_data_root_dir, global_config["calendar"]["dir"])
calendar_path = os.path.join(calendar_dir, global_config["calendar"]["file"])

# --- futures data
futures_dir = os.path.join(project_data_root_dir, global_config["futures"]["dir"])
futures_instru_info_path = os.path.join(futures_dir, global_config["futures"]["instrument_info_file"])
futures_by_date_dir = os.path.join(futures_dir, global_config["futures"]["by_date"]["dir"])
futures_by_instrument_dir = os.path.join(futures_dir, global_config["futures"]["by_instrument"]["dir"])
with open(os.path.join(futures_dir, global_config["futures"]["db_struct_file"]), "r", encoding="utf-8") as j:
    db_structs = json.load(j)
futures_md_wds_db_name = global_config["futures"]["md"]["wds_db"]
futures_md_tsdb_db_name = global_config["futures"]["md"]["tsdb_db"]
futures_cm01_db_name = global_config["futures"]["md"]["cm01_db"]
futures_em01_db_name = global_config["futures"]["md"]["em01_db"]
futures_positions_c_db_name = global_config["futures"]["positions"]["c_db"]
futures_positions_e_db_name = global_config["futures"]["positions"]["e_db"]
futures_fundamental_db_name = global_config["futures"]["fundamental"]["db"]

# marco economic
macro_economic_dir = os.path.join(project_data_root_dir, global_config["macro"]["dir"])
cpi_m2_file = global_config["macro"]["cpi_m2_file"]

# forex
forex_dir = os.path.join(project_data_root_dir, global_config["forex"]["dir"])
exchange_rate_file = global_config["forex"]["exchange_rate_file"]

# --- by instrument
by_instru_md_dir = os.path.join(futures_by_instrument_dir, global_config["futures"]["by_instrument"]["md"]["dir"])
by_instru_fd_dir = os.path.join(futures_by_instrument_dir, global_config["futures"]["by_instrument"]["fd"]["dir"])
major_minor_db_name = global_config["futures"]["by_instrument"]["major_minor_db"]
major_return_db_name = global_config["futures"]["by_instrument"]["major_return_db"]
instrument_volume_db_name = global_config["futures"]["by_instrument"]["instrument_volume_db"]
instrument_member_db_name = global_config["futures"]["by_instrument"]["instrument_member_db"]

# --- projects data
for_projects_dir = os.path.join(project_data_root_dir, global_config["forProjects"]["dir"])
deploy_cta_data_dir = os.path.join(for_projects_dir, global_config["forProjects"]["cta"]["dir"])

# library
instruments_return_dir = os.path.join(deploy_cta_data_dir, "instruments_return")
available_universe_dir = os.path.join(deploy_cta_data_dir, "available_universe")
test_return_dir = os.path.join(deploy_cta_data_dir, "test_return")
factors_exposure_dir = os.path.join(deploy_cta_data_dir, "factors_exposure")
factors_exposure_raw_dir = os.path.join(factors_exposure_dir, "raw")
factors_exposure_neu_dir = os.path.join(factors_exposure_dir, "neu")
factors_exposure_cor_dir = os.path.join(factors_exposure_dir, "cor")
ic_tests_dir = os.path.join(deploy_cta_data_dir, "ic_tests")
ic_tests_raw_dir = os.path.join(ic_tests_dir, "raw")
ic_tests_neu_dir = os.path.join(ic_tests_dir, "neu")
ic_tests_summary_dir = os.path.join(ic_tests_dir, "summary")

# portfolio
signals_dir = os.path.join(deploy_cta_data_dir, "signals")
signals_factor_raw_dir = os.path.join(signals_dir, "factor_raw")
signals_hedge_test_dir = os.path.join(signals_dir, "hedge_test")
signals_portfolios_dir = os.path.join(signals_dir, "portfolios")
signals_optimized_dir = os.path.join(signals_dir, "optimized")

simulations_dir = os.path.join(deploy_cta_data_dir, "simulations")
simulations_hedge_test_dir = os.path.join(simulations_dir, "hedge_test")
simulations_portfolios_dir = os.path.join(simulations_dir, "portfolios")

evaluations_dir = os.path.join(deploy_cta_data_dir, "evaluations")
evaluations_hedge_test_dir = os.path.join(evaluations_dir, "hedge_test")
evaluations_portfolios_dir = os.path.join(evaluations_dir, "portfolios")

if __name__ == "__main__":
    from skyrim.winterhold import check_and_mkdir

    check_and_mkdir(deploy_cta_data_dir)
    check_and_mkdir(instruments_return_dir)
    check_and_mkdir(available_universe_dir)
    check_and_mkdir(test_return_dir)
    check_and_mkdir(factors_exposure_dir)
    check_and_mkdir(factors_exposure_neu_dir)
    check_and_mkdir(factors_exposure_raw_dir)
    check_and_mkdir(factors_exposure_cor_dir)
    check_and_mkdir(ic_tests_dir)
    check_and_mkdir(ic_tests_raw_dir)
    check_and_mkdir(ic_tests_neu_dir)
    check_and_mkdir(ic_tests_summary_dir)

    check_and_mkdir(signals_dir)
    check_and_mkdir(signals_factor_raw_dir)
    check_and_mkdir(signals_hedge_test_dir)
    check_and_mkdir(signals_portfolios_dir)
    check_and_mkdir(signals_optimized_dir)
    check_and_mkdir(simulations_dir)
    check_and_mkdir(simulations_hedge_test_dir)
    check_and_mkdir(simulations_portfolios_dir)
    check_and_mkdir(evaluations_dir)
    check_and_mkdir(evaluations_hedge_test_dir)
    check_and_mkdir(evaluations_portfolios_dir)

    print("... directory system for this project has been established.")
