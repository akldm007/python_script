#!/remote/asepw_archive2/grid/tools/asepython/pythonMini/asepython/python/bin/python

import sys
import os
import pdb
import subprocess
import datetime
os.environ['SYBASE']='/remote/aseqa_archive2/asecepheus/linuxamd64_smp/release'
os.environ['SYBASE_OCS']='OCS-16_0'
sys.path.append('/remote/aseqa_archive2/asecepheus/linuxamd64_smp/release/OCS-16_0/python/python26_64r/lib')
import sybpydb

def exec_cmd(sql):
    conn = sybpydb.connect(user='qts_user',password='ujes228o',servername="PDSQTS1")
    cur=conn.cursor()
    cur.execute(sql)
    result=cur.fetchall()
    cur.close()
    conn.close()
    return result

branch_name=sys.argv[1]
url="http://10.173.3.54/tsm/cov_archive/?list=1"
get_cc_list_cmd="curl -s \"%s\""%(url)
cc_list=eval(os.popen(get_cc_list_cmd).read())
for a_list in cc_list["branch"]:
    if a_list["branch_name"]==branch_name:
        latest_report_time=a_list["archive_list"][0]["report_name"].split("_")[1]

if len(latest_report_time)==8:
    # print latest_report_time
    pass
else:
    print "Time format is not right"
    sys.exit(1)

year=int(latest_report_time[0:4])
month=int(latest_report_time[4:6])
day=int(latest_report_time[6:8])
report_time=datetime.datetime(year,month,day)
timedelta=datetime.timedelta(days=7)
hist_time=report_time-timedelta
if len(str(hist_time.month))==1:
    hist_time_month="0"+str(hist_time.month)
else:
    hist_time_month=str(hist_time.month)
if len(str(hist_time.day))==1:
    hist_time_day="0"+str(hist_time.day)
else:
    hist_time_day=str(hist_time.day)
hist_time_str=str(hist_time.year)+hist_time_month+hist_time_day
# begin time of asecoronamig
if branch_name=="ase160sp02plx":
    hist_time_str="20160801"
else:
    hist_time_str="20160620"
# hist_time_str="20160801"

# pdb.set_trace()
view_tag=branch_name+"\_%"
get_latest_cset_sql="select cset_name from qts_db..e2_cset where view_tag like \"%s\" escape '\\' and date_closed > \"%s\""%(view_tag,hist_time_str)
# print get_latest_cset_sql

latest_cset=exec_cmd(get_latest_cset_sql)

latest_cset_list=map(lambda x:x[0], latest_cset)
cset_list=",".join(latest_cset_list)
print cset_list

