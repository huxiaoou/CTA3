"""
Created by huxo
Initialized @ 13:16, 2023/9/1
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
    with open("/Deploy/config.json", "r") as j:
        global_config = json.load(j)
elif this_platform == "LINUX":
    with open("/home/huxo/Deploy/config.json", "r") as j:
        global_config = json.load(j)
else:
    print("... this platform is {}.".format(this_platform))
    print("... it is not a recognized platform, please check again.")
    sys.exit()

deploy_dir = global_config["deploy_dir"][this_platform]
project_data_root_dir = os.path.join(deploy_dir, "Data")

# --- calendar
calendar_dir = os.path.join(project_data_root_dir, global_config["calendar"]["calendar_save_dir"])
calendar_path = os.path.join(calendar_dir, global_config["calendar"]["calendar_save_file"])

# --- futures data
futures_dir = os.path.join(project_data_root_dir, global_config["futures"]["futures_save_dir"])
futures_shared_info_path = os.path.join(futures_dir, global_config["futures"]["futures_shared_info_file"])
instrument_info_path = os.path.join(futures_dir, global_config["futures"]["futures_instrument_info_file"])

futures_md_dir = os.path.join(futures_dir, global_config["futures"]["md_dir"])
futures_md_structure_path = os.path.join(futures_md_dir, global_config["futures"]["md_structure_file"])
futures_md_db_name = global_config["futures"]["md_db_name"]

futures_fundamental_dir = os.path.join(futures_dir, global_config["futures"]["fundamental_dir"])
futures_fundamental_structure_path = os.path.join(futures_fundamental_dir, global_config["futures"]["fundamental_structure_file"])
futures_fundamental_db_name = global_config["futures"]["fundamental_db_name"]

futures_by_instrument_dir = os.path.join(futures_dir, global_config["futures"]["by_instrument_dir"])
md_by_instru_dir = os.path.join(futures_by_instrument_dir, global_config["futures"]["md_by_instru_dir"])
fundamental_by_instru_dir = os.path.join(futures_by_instrument_dir, global_config["futures"]["fundamental_by_instru_dir"])
major_minor_db_name = global_config["futures"]["major_minor_db"]
major_return_db_name = global_config["futures"]["major_return_db"]
instrument_volume_db_name = global_config["futures"]["instrument_volume_db"]
instrument_member_db_name = global_config["futures"]["instrument_member_db"]

# marco economic
macro_economic_dir = os.path.join(project_data_root_dir, global_config["macro"]["macro_dir"])
cpi_m2_file = global_config["macro"]["cpi_m2_file"]

# forex
forex_dir = os.path.join(project_data_root_dir, global_config["forex"]["forex_dir"])
exchange_rate_file = global_config["forex"]["exchange_rate_file"]

# --- projects data
research_data_root_dir = "/ProjectsData"
research_project_name = os.getcwd().split("\\")[-1]
research_project_data_dir = os.path.join(research_data_root_dir, research_project_name)
factors_library_dir = research_project_data_dir
portfolio_dir = research_project_data_dir

# factors_library_dir = os.path.join(futures_dir, global_config["futures"]["cta_dir"])
# portfolio_dir = os.path.join(futures_dir, global_config["futures"]["cta_dir"])

# library
instruments_return_dir = os.path.join(factors_library_dir, "instruments_return")
available_universe_dir = os.path.join(factors_library_dir, "available_universe")
test_return_dir = os.path.join(factors_library_dir, "test_return")
factors_exposure_dir = os.path.join(factors_library_dir, "factors_exposure")
factors_exposure_raw_dir = os.path.join(factors_exposure_dir, "raw")
factors_exposure_neu_dir = os.path.join(factors_exposure_dir, "neu")
factors_exposure_cor_dir = os.path.join(factors_exposure_dir, "cor")
ic_tests_dir = os.path.join(factors_library_dir, "ic_tests")
ic_tests_raw_dir = os.path.join(ic_tests_dir, "raw")
ic_tests_neu_dir = os.path.join(ic_tests_dir, "neu")
ic_tests_summary_dir = os.path.join(ic_tests_dir, "summary")

# portfolio
signals_dir = os.path.join(portfolio_dir, "signals")
signals_factor_raw_dir = os.path.join(signals_dir, "factor_raw")
signals_hedge_test_dir = os.path.join(signals_dir, "hedge_test")
signals_portfolios_dir = os.path.join(signals_dir, "portfolios")
signals_optimized_dir = os.path.join(signals_dir, "optimized")

simulations_dir = os.path.join(portfolio_dir, "simulations")
simulations_hedge_test_dir = os.path.join(simulations_dir, "hedge_test")
simulations_portfolios_dir = os.path.join(simulations_dir, "portfolios")

evaluations_dir = os.path.join(portfolio_dir, "evaluations")
evaluations_hedge_test_dir = os.path.join(evaluations_dir, "hedge_test")
evaluations_portfolios_dir = os.path.join(evaluations_dir, "portfolios")

if __name__ == "__main__":
    from skyrim.winterhold import check_and_mkdir

    check_and_mkdir(research_project_data_dir)

    check_and_mkdir(factors_library_dir)
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

    check_and_mkdir(portfolio_dir)
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
