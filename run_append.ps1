Write-Host "Run me to append new data"
$append_date = Read-Host -Prompt "Please input the append date, which is usually the LAST trade date, format = [YYYYMMDD]"
$append_date_dt = [Datetime]::ParseExact($append_date, "yyyyMMdd", $null)
$stp_date = Get-Date $append_date_dt.AddDays(1) -Format "yyyyMMdd"
$proc_num = 5

python main.py -p $proc_num -w ir       -s $stp_date
python main.py -p $proc_num -w au  -m a -b $append_date
python main.py -p $proc_num -w mr       -s $stp_date
python main.py -p $proc_num -w tr  -m a -b $append_date
python main.py -p $proc_num -w trn -m a -b $append_date

# factor exposure
python main.py -p $proc_num -w fe  -m a -b $append_date -f mtm
python main.py -p $proc_num -w fe  -m a -b $append_date -f size
python main.py -p $proc_num -w fe  -m a -b $append_date -f rs
python main.py -p $proc_num -w fe  -m a -b $append_date -f basis
python main.py -p $proc_num -w fe  -m a -b $append_date -f ts
python main.py -p $proc_num -w fe  -m a -b $append_date -f liquid
python main.py -p $proc_num -w fe  -m a -b $append_date -f sr
python main.py -p $proc_num -w fe  -m a -b $append_date -f hr
python main.py -p $proc_num -w fe  -m a -b $append_date -f netdoi
python main.py -p $proc_num -w fe  -m a -b $append_date -f netdoiw
python main.py -p $proc_num -w fe  -m a -b $append_date -f skew
python main.py -p $proc_num -w fe  -m a -b $append_date -f vol
python main.py -p $proc_num -w fe  -m a -b $append_date -f rvol
python main.py -p $proc_num -w fe  -m a -b $append_date -f ctp
python main.py -p $proc_num -w fe  -m a -b $append_date -f cvp
python main.py -p $proc_num -w fe  -m a -b $append_date -f csp
python main.py -p $proc_num -w fe  -m a -b $append_date -f beta
python main.py -p $proc_num -w fe  -m a -b $append_date -f ibeta

# factors neutral
python main.py -p $proc_num -w fen -m a -b $append_date

# ic tests and ic tests neutral
python main.py -p $proc_num -w ic  -m a -b $append_date
python main.py -p $proc_num -w icn -m a -b $append_date
python main.py -p $proc_num -w ics
python main.py -p $proc_num -w icns
python main.py -p $proc_num -w icc

# hedge test
python main.py -p $proc_num -w sig  -t hedge-raw -m a -b $append_date
python main.py -p $proc_num -w sig  -t hedge-ma  -m a -b $append_date
python main.py -p $proc_num -w simu -t hedge-ma  -m a -b $append_date
python main.py -p $proc_num -w eval -t hedge-ma

# portfolios
python main.py -p $proc_num -w sig  -t portfolio -m a -b $append_date
python main.py -p $proc_num -w simu -t portfolio -m a -b $append_date
python main.py -p $proc_num -w eval -t portfolio
