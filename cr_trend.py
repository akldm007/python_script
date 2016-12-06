#!/remote/aseqa_archive3/sean/asepython/python/bin/python
import sys
import os
import re
import pdb
import subprocess
import time
import datetime
os.environ['SYBASE']='/remote/aseqa_archive3/sean/cc_ase_rl/release'
os.environ['SYBASE_OCS']='OCS-16_0'
sys.path.append('/remote/aseqa_archive3/sean/cc_ase_rl/release/OCS-16_0/python/python26_64r/lib')
import sybpydb
import logging

branch_name=sys.argv[1]
formatter = "%(asctime)s:%(name)s:%(levelname)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, format=formatter)
logger = logging.getLogger(__name__)

def exec_cmd(sql):
    conn = sybpydb.connect(user='qts_user',password='ujes228o',servername="PDSQTS1")
    cur=conn.cursor()
    cur.execute(sql)
    result=cur.fetchall()
    cur.close()
    conn.close()
    return result

def trans_week(dt):
    week=str(dt.isocalendar()[0])+str(dt.isocalendar()[1])
    return week


view_tag=branch_name+"\_%"
res_opened_dict={}
res_closed_dict={}
get_res_sql="select bug_id,resolution_no,res_status,creation_ts,fix_ts from qts_db..sy_resolution where branch =\"%s\" and (priority=\"1\" or priority=\"0\") order by creation_ts"%(branch_name)
print get_res_sql
get_res_info=exec_cmd(get_res_sql)
pdb.set_trace()
for a_result in get_res_info:
    cur_dict={}
    cur_dict["cr_res"]="%d-%d"%(a_result[0],a_result[1])
    cur_opened=trans_week(a_result[3])
    try:
        cur_closed=trans_week(a_result[4])
    except:
        pass
    if cur_opened in res_opened_dict.keys():
        res_opened_dict[cur_opened]+=1
    else:
        res_opened_dict[cur_opened]=1
    if cur_closed in res_closed_dict.keys():
        res_closed_dict[cur_closed]+=1
    else:
        res_closed_dict[cur_closed]=1

print res_opened_dict
print res_closed_dict

first_week=trans_week(get_res_info[0][3])
last_week=trans_week(datetime.datetime.now())
