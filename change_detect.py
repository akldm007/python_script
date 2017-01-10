#!/remote/asepw_archive2/grid/tools/asepython/pythonMini/asepython/python/bin/python
import sys
import os
import re
import pdb
import subprocess
import time
import datetime
os.environ['SYBASE']='/remote/aseqa_archive2/asecepheus/linuxamd64_smp/release'
os.environ['SYBASE_OCS']='OCS-16_0'
sys.path.append('/remote/aseqa_archive2/asecepheus/linuxamd64_smp/release/OCS-16_0/python/python26_64r/lib')
import sybpydb
import logging
import datetime

now=datetime.datetime.now()
time_tag=now.strftime("%Y-%m-%d-%H-%M-%S")

start_time=sys.argv[1]
end_time=sys.argv[2]
branch_name=sys.argv[3]


formatter = "%(asctime)s:%(name)s:%(levelname)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, format=formatter)
logger = logging.getLogger(__name__)

INSERT='I'
CHANGE='C'

def exec_cmd(sql):
    conn = sybpydb.connect(user='qts_user',password='ujes228o',servername="PDSQTS1")
    cur=conn.cursor()
    cur.execute(sql)
    result=cur.fetchall()
    cur.close()
    conn.close()
    return result

view_tag=branch_name+"\_%"
get_relevant_cset_sql="select cset_name from qts_db..e2_cset where date_created > \"%s\" and date_closed <= \"%s\" and view_tag like \"%s\" escape '\\'"%(start_time,end_time,view_tag)
relevant_cset=exec_cmd(get_relevant_cset_sql)
if relevant_cset:
    relevant_cset_list=map(lambda x:x[0], relevant_cset)
else:
    relevant_cset_list=[]
    # print "relevant_cset %s"%(",".join(relevant_cset_list))

pull_view_tag=branch_name+"\_merge%"
get_pull_cset_sql="select cset_name from qts_db..e2_cset where date_created > \"%s\" and date_closed <= \"%s\" and view_tag like \"%s\" escape '\\'"%(start_time,end_time,pull_view_tag)
# print get_pull_cset_sql
pull_cset=exec_cmd(get_pull_cset_sql)
if pull_cset:
    pull_cset_list=map(lambda x:x[0], pull_cset)
    # print "pull_cset %s"%(",".join(pull_cset_list))
else:
    pull_cset_list=[]
    # print "no pull_cset"

def get_affected_file_list(cset_list):
    if not cset_list:
        return []
    cset_list=",".join(cset_list)
    condition=""
    for a_cset in cset_list.split(",")[0:-1]:
        condition+="cset_name=\"%s\" or "%(a_cset)
    condition+="cset_name=\"%s\""%(cset_list.split(",")[-1])
    affected_file_sql="select file_name from  qts_db..e2_members where cset_id in (select cset_id from qts_db..e2_cset where %s)"%(condition)
    # print affected_file_sql
    affected_file=exec_cmd(affected_file_sql)

    all_affect_file_list=[]
    for an_affected_file in affected_file:
        if an_affected_file[0] in all_affect_file_list:
            pass
        else:
            all_affect_file_list.append(an_affected_file[0])
    return all_affect_file_list

all_affect_file_list=get_affected_file_list(relevant_cset_list)
server_code_list=filter(lambda x:x.endswith('.c') or x.endswith('.cpp') or x.endswith('.h') or x.endswith('.hpp'),all_affect_file_list)
testset_list=[]
for a_file in all_affect_file_list:
    if re.search("(?:/qtst/testsets/)(\S+)",a_file):
        cur_set=re.search("(?:/qtst/testsets/)(\S+)",a_file).group(1)
        testset_list.append(cur_set.split("/")[-1])
view_name=branch_name+"_demingli_vu"
cspec=branch_name+".csp"
# print testset_list

if pull_cset_list:
    all_pull_affect_file_list=get_affected_file_list(pull_cset_list)
    pull_affect_file_list=filter(lambda x:x in all_affect_file_list, all_pull_affect_file_list)
else:
    pass

def get_change_content(cset_list):
    if not cset_list:
        return []
    condition=""
    if len(cset_list)==1:
        condition+="cset_name=\"%s\""%(cset_list[0])
    else:
        cset_list=",".join(cset_list)
        if len(cset_list.split(","))>1:
            for a_cset in cset_list.split(",")[0:-1]:
                condition+="cset_name=\"%s\" or "%(a_cset)
            condition+="cset_name=\"%s\""%(cset_list.split(",")[-1])
        else:
            condition+="cset_name=\"%s\""%(cset_list.split(",")[-1])
    create_time_sql="select date_created from qts_db..e2_cset where %s order by date_created"%(condition)
    # print create_time_sql
    create_time_list=exec_cmd(create_time_sql)
    close_time_sql="select date_closed from qts_db..e2_cset where %s order by date_closed desc"%(condition)
    # print close_time_sql
    close_time_list=exec_cmd(close_time_sql)
    if create_time_list:
        earliest_create_time=create_time_list[0][0].strftime('%d-%b-%Y.%H:%M')
    if close_time_list:
        if (None,) in close_time_list:
            latest_close_time=datetime.datetime.now().strftime('%d-%b-%Y.%H:%M')
        else:
            #latest_close_time=close_time_list[0][0].strftime('%d-%b-%Y.%H:%M')
            # delay 1 min let the check in work
            latest_close_time=(close_time_list[0][0]+datetime.timedelta(minutes=1)).strftime('%d-%b-%Y.%H:%M')
    server_affected_list=[]
    if len(server_code_list):
        return server_code_list
    else:
        return None

if relevant_cset_list:
    print get_change_content(relevant_cset_list)
    sys.exit(0)
else:
    print """{"code": 1, "msg":"No server code change is detected"}"""
    sys.exit(1)
