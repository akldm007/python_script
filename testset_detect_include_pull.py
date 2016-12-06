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

def parse_diff(ct_diff_output):
    '''
    Pass ct diff output to formatted list:
    [(line_no, action, content),(line_no, action, content)...]
    Args:
        ct_diff_output:
    Returns:
    '''
    # pdb.set_trace()
    # logger.debug("Parse diff %s ..." % ct_diff_output)
    rslt = []
    do_capture = False
    line_cnt = 0
    change_type = ""
    for line in ct_diff_output.split("\n")[0:-1]:
        #line = line.strip('\n')

        if re.match(r'-----\[', line) is None and do_capture:
            if change_type == CHANGE and re.match(r'>', line) is None: # capture new version only
                continue
            # ele = "%d %s %s"%(line_cnt, change_type, line.strip('> \t'))
            ele = "%d %s"%(line_cnt,line.strip('> \t'))
            line_cnt+=1
            rslt.append(ele)
            continue

        m = re.match(r'-----\[.* inserted (\d+)(-\d+)?\]-----',line)
        if m is not None:
            change_type = INSERT
            do_capture = True
            line_cnt = int(m.group(1))
            continue

        m = re.match(r'-----\[.* changed to (\d+)(-\d+)?\]-----', line)
        if m is not None:
            change_type = CHANGE
            do_capture = True
            line_cnt = int(m.group(1))
            continue

        do_capture = False

    # logger.debug(rslt)
    return rslt

view_tag=branch_name+"\_%"
get_relevant_cset_sql="select cset_name from qts_db..e2_cset where date_created > \"%s\" and date_closed < \"%s\" and view_tag like \"%s\" escape '\\'"%(start_time,end_time,view_tag)
relevant_cset=exec_cmd(get_relevant_cset_sql)
if relevant_cset:
    relevant_cset_list=map(lambda x:x[0], relevant_cset)
    # print "relevant_cset %s"%(" ".join(relevant_cset_list))

pull_view_tag=branch_name+"\_merge%"
get_pull_cset_sql="select cset_name from qts_db..e2_cset where date_created > \"%s\" and date_closed < \"%s\" and view_tag like \"%s\" escape '\\'"%(start_time,end_time,pull_view_tag)
# print get_pull_cset_sql
pull_cset=exec_cmd(get_pull_cset_sql)
if pull_cset:
    pull_cset_list=map(lambda x:x[0], pull_cset)
    # print "pull_cset %s"%(",".join(pull_cset_list))
    #for a_pull_cset in pull_cset_list:
    #    if a_pull_cset in relevant_cset_list:
    #        relevant_cset_list.remove(a_pull_cset)
else:
    pass
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
print testset_list
