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

formatter = "%(asctime)s:%(name)s:%(levelname)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, format=formatter)
logger = logging.getLogger(__name__)

start_time=sys.argv[1]
end_time=sys.argv[2]
branch_name=sys.argv[3]
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
    # print "relevant_cset %s"%(",".join(relevant_cset_list))

pull_view_tag=branch_name+"\_merge%"
get_pull_cset_sql="select cset_name from qts_db..e2_cset where date_created > \"%s\" and date_closed < \"%s\" and view_tag like \"%s\" escape '\\'"%(start_time,end_time,pull_view_tag)
# print get_pull_cset_sql
pull_cset=exec_cmd(get_pull_cset_sql)
if pull_cset:
    pull_cset_list=map(lambda x:x[0], pull_cset)
    # print "pull_cset %s"%(",".join(pull_cset_list))
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
# print testset_list

all_pull_affect_file_list=get_affected_file_list(pull_cset_list)
pull_affect_file_list=filter(lambda x:x in all_affect_file_list, all_pull_affect_file_list)

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
    file_list=",".join(server_code_list)
    wfile=open("/remote/aseqa_archive3/code_coverage/scrum_tmp/file_list", 'w')
    wfile.write(file_list)
    wfile.close()
    #get_info_cmd="ssh demingli@lnxsdcc1.oak.sap.corp /usr/u/demingli/code_coverage/get_file_list_change2.sh "+view_name+" "+cspec+" "+earliest_create_time+" "+latest_close_time+" "+file_list+" 2>/dev/null"
    get_info_cmd="ssh demingli@hpcblade5.oak.sap.corp /usr/u/demingli/code_coverage/get_file_list_change2.sh "+view_name+" "+cspec+" "+earliest_create_time+" "+latest_close_time+" "+"/remote/aseqa_archive3/code_coverage/scrum_tmp/file_list"+" 2>/dev/null"
    # print get_info_cmd
    all_file_info=os.popen(get_info_cmd).read()
    # pdb.set_trace()
    if all_file_info:
        all_file_info=eval(all_file_info)
    else:
        print """{"code": 1, "msg":"Files are identical"}"""
        sys.exit(1) 
    server_affected_list=[]
    if len(server_code_list):
        for a_server_code in server_code_list:
            file_affected_info={}
            for a_file_info in all_file_info:
                if a_file_info["file_name"]==a_server_code:
                    file_affected_info["file_name"]=a_server_code
                    file_affected_info["code_type"]="server"
                    file_affected_info["change_info"]=parse_diff(a_file_info["change_info"])
                    server_affected_list.append(file_affected_info)
    else:
        print """{"code": 1, "msg":"No server code change is detected"}"""
        sys.exit(1)
    return server_affected_list

def merge_diff(diff_all,diff_pull):
    str_diff_all="\n".join(diff_all)
    for a_diff_pull in diff_pull:
        a_diff_pull_content=" ".join(a_diff_pull.split(" ")[1:])
        if a_diff_pull_content:
            exp="\d+\s"+re.escape(a_diff_pull_content)
            # print exp
            if re.findall(exp,str_diff_all):
                if len(re.findall(exp,str_diff_all))>1:
                    pass
                else:
                    match_line=re.findall(exp,str_diff_all)[0]
                    diff_all.remove(match_line)
                    # print "remove pull content %s"%(a_diff_pull_content)
    return diff_all
        
if pull_cset:
    relevant_change_content=get_change_content(relevant_cset_list)
    for a_pull_cset in pull_cset_list:
        pull_change_content=get_change_content([a_pull_cset])
        for i,a_change in enumerate(relevant_change_content):
            file_name=a_change["file_name"]
            for a_pull_change in pull_change_content:
                 if a_pull_change["file_name"]==file_name:
                      # print "file name: %s"%(file_name)
                      relevant_change_content[i]["change_info"]=merge_diff(a_change["change_info"],a_pull_change["change_info"])
    print relevant_change_content
     
else:
    print get_change_content(relevant_cset_list)
