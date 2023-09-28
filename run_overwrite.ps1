Write-Host "Run me to overwrite all data"
$stp_date = Read-Host -Prompt "Please input the stop date, which is NOT INCLUDED, format = [YYYYMMDD]"
$proc_num = 5

python main.py -p $proc_num -w ir       -s $stp_date
python main.py -p $proc_num -w au  -m o -s $stp_date
python main.py -p $proc_num -w mr       -s $stp_date
python main.py -p $proc_num -w tr  -m o -s $stp_date
python main.py -p $proc_num -w trn -m o -s $stp_date

# factor exposure
python main.py -p $proc_num -w fe  -m o -s $stp_date -f mtm
python main.py -p $proc_num -w fe  -m o -s $stp_date -f size
python main.py -p $proc_num -w fe  -m o -s $stp_date -f rs
python main.py -p $proc_num -w fe  -m o -s $stp_date -f basis
python main.py -p $proc_num -w fe  -m o -s $stp_date -f ts
python main.py -p $proc_num -w fe  -m o -s $stp_date -f liquid
python main.py -p $proc_num -w fe  -m o -s $stp_date -f sr
python main.py -p $proc_num -w fe  -m o -s $stp_date -f hr
python main.py -p $proc_num -w fe  -m o -s $stp_date -f netdoi
python main.py -p $proc_num -w fe  -m o -s $stp_date -f netdoiw
python main.py -p $proc_num -w fe  -m o -s $stp_date -f skew
python main.py -p $proc_num -w fe  -m o -s $stp_date -f vol
python main.py -p $proc_num -w fe  -m o -s $stp_date -f rvol
python main.py -p $proc_num -w fe  -m o -s $stp_date -f ctp
python main.py -p $proc_num -w fe  -m o -s $stp_date -f cvp
python main.py -p $proc_num -w fe  -m o -s $stp_date -f csp
python main.py -p $proc_num -w fe  -m o -s $stp_date -f beta
python main.py -p $proc_num -w fe  -m o -s $stp_date -f ibeta

# factors neutral
python main.py -p $proc_num -w fen -m o -s $stp_date

# ic tests and ic tests neutral
python main.py -p $proc_num -w ic  -m o -s $stp_date
python main.py -p $proc_num -w icn -m o -s $stp_date
python main.py -p $proc_num -w ics
python main.py -p $proc_num -w icns
python main.py -p $proc_num -w icc

# hedge test
python main.py -p $proc_num -w sig  -t hedge-raw -m o -s $stp_date
python main.py -p $proc_num -w sig  -t hedge-ma  -m o -s $stp_date
python main.py -p $proc_num -w simu -t hedge-ma  -m o -s $stp_date
python main.py -p $proc_num -w eval -t hedge-ma

# portfolios
python main.py -p $proc_num -w sig  -t portfolio -m o -s $stp_date
python main.py -p $proc_num -w simu -t portfolio -m o -s $stp_date
python main.py -p $proc_num -w eval -t portfolio
