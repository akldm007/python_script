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
f_end_time=sys.argv[2]
end_time=f_end_time.replace("."," ")
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
            ele = "%d %s"%(line_cnt,line.lstrip('> \t'))
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
get_relevant_cset_sql="select cset_name from qts_db..e2_cset where date_created > \"%s\" and date_closed <= \"%s\" and view_tag like \"%s\" escape '\\'"%(start_time,end_time,view_tag)
# print get_relevant_cset_sql
relevant_cset=exec_cmd(get_relevant_cset_sql)
if relevant_cset:
    relevant_cset_list=map(lambda x:x[0], relevant_cset)
    # print "relevant_cset %s"%(",".join(relevant_cset_list))
else:
    relevant_cset_list=[]

pull_view_tag=branch_name+"\_merge%"
get_pull_cset_sql="select cset_name from qts_db..e2_cset where date_created > \"%s\" and date_closed <= \"%s\" and view_tag like \"%s\" escape '\\'"%(start_time,end_time,pull_view_tag)
# print get_pull_cset_sql
pull_cset=exec_cmd(get_pull_cset_sql)
if pull_cset:
    pull_cset_list=map(lambda x:x[0], pull_cset)
    # print "pull_cset %s"%(",".join(pull_cset_list))
else:
    pull_cset_list=[]
    # pass
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

def get_csetinfo(file_name):
    return_info_list=[]
    if file_name.startswith('/calm/svr/'):
        file_condition="%"+file_name+"%"
        select_sql="select a.cset_name,c.email from qts_db..e2_cset as a inner join qts_db..e2_members as b on a.date_created > \"%s\" and a.date_closed <= \"%s\" and a.view_tag like \"%s\" escape '\\' and a.cset_id in (select b.cset_id from qts_db..e2_members where b.file_name like \"%s\") inner join qts_db..users as c on b.userid=c.userid and not (c.userid=13162)"%(start_time,end_time,view_tag,file_condition) 
        try:
            select_results=exec_cmd(select_sql)
            if select_results:
                for a_result in select_results:
                    cur_csetinfo_dict={}
                    cur_csetinfo_dict["cset_name"]=a_result[0]
                    cur_csetinfo_dict["user_id"]=a_result[1]
                    return_info_list.append(cur_csetinfo_dict)
        except:
            return []
    return return_info_list

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
    file_list_name="/remote/aseqa_archive3/code_coverage/scrum_tmp/"+branch_name+"_file_list_"+time_tag
    wfile=open(file_list_name, 'w')
    wfile.write(file_list)
    wfile.close()
    #get_info_cmd="ssh demingli@lnxsdcc1.oak.sap.corp /usr/u/demingli/code_coverage/get_file_list_change2.sh "+view_name+" "+cspec+" "+earliest_create_time+" "+latest_close_time+" "+file_list+" 2>/dev/null"
    get_info_cmd="ssh demingli@lnxsdcc2.sjc.sap.corp /usr/u/demingli/code_coverage/get_file_list_change2.sh "+view_name+" "+cspec+" "+earliest_create_time+" "+latest_close_time+" "+branch_name+" "+file_list_name+" 2>/dev/null"
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
                    # remove to the final loop
                    #if file_affected_info["change_info"]:
                    #    file_affected_info["cset_info"]=get_csetinfo(a_server_code)
                    #else:
                    #    file_affected_info["cset_info"]=[]
                    server_affected_list.append(file_affected_info)
    else:
        print """{"code": 1, "msg":"No server code change is detected"}"""
        sys.exit(1)
    return server_affected_list

def merge_diff(diff_all,diff_pull):
    for a_diff_pull in diff_pull:
        str_diff_all="\n".join(diff_all)
        a_diff_pull_content=" ".join(a_diff_pull.split(" ")[1:])
        if a_diff_pull_content:
            exp="^\d+\s"+re.escape(a_diff_pull_content)+"$"
            # print exp
            if re.findall(exp,str_diff_all,re.M):
                #if find many matchs, do nothing
                #if len(re.findall(exp,str_diff_all))>1:
                #    pass
                #else:
                #    match_line=re.findall(exp,str_diff_all)[0]
                #    try:
                #        diff_all.remove(match_line)
                #    except:
                #        pass
                #        # print "remove pull content %s failed"%(a_diff_pull_content)
                match_line=re.findall(exp,str_diff_all,re.M)[0]
                try:
                    diff_all.remove(match_line)
                except:
                    pass
                #if match_line.endswith("/*") or match_line.endswith("*/") or match_line.endswith("{") or match_line.endswith("}"):
                #    pass
                #else:
                #    try:
                #        diff_all.remove(match_line)
                #    except:
                #        pass
        #remove all null raw
    for a_diff_all in diff_all:
        a_diff_all_content=" ".join(a_diff_all.split(" ")[1:])
        if a_diff_all_content:
            if a_diff_all_content=="/*" or a_diff_all_content=="*/" or a_diff_all_content=="**" or a_diff_all_content=="{" or a_diff_all_content=="}":
                match_line=a_diff_all.split(" ")[0]+" "+a_diff_all_content
                try:
                    diff_all.remove(match_line)
                except:
                    pass
            else:
                pass
        else:
            match_line=a_diff_all.split(" ")[0]+" "
            try:
                diff_all.remove(match_line)
            except:
                pass
                # print "remove null content %s failed"%(match_line)
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
    # print relevant_change_content
    new_code=relevant_change_content
else:
    new_code=get_change_content(relevant_cset_list)

change_content=new_code
# remove pure pull file from change_content
file_list_name="/remote/aseqa_archive3/code_coverage/scrum_tmp/"+branch_name+"_file_list_"+time_tag
get_list_cmd="ssh demingli@lnxsdcc2.sjc.sap.corp /usr/u/demingli/code_coverage/get_pure_pull_list.sh "+view_name+" "+cspec+" "+start_time+" "+f_end_time+" "+branch_name+" "+file_list_name+" 2>/dev/null"
return_file_info=os.popen(get_list_cmd).read()
if return_file_info:
    return_dict=eval(return_file_info)
    pure_pull_list=return_dict["pure_pull_list"]
    file_blocks_list=return_dict["file_blocks_list"]
else:
    pure_pull_list=[]
    file_blocks_list=[]

if pure_pull_list:
    for i,a_change in enumerate(change_content):
        file_name=a_change["file_name"]
        if file_name in pure_pull_list:
            # remove element which is in pure pull list
            change_content[i]["change_info"]=[]
        else:
            pass

for i,a_change in enumerate(change_content):
    # add cset info
    file_name=a_change["file_name"]
    if change_content[i]["change_info"]:
        change_content[i]["cset_info"]=get_csetinfo(file_name)
    else:
        change_content[i]["cset_info"]=[]
    # add file blocks info
    for a_file_block_info in file_blocks_list:
        if file_name==a_file_block_info["file_name"]:
            change_content[i]["blocks_info"]=a_file_block_info["blocks_info"]
    if change_content[i].has_key("blocks_info"):
        pass
    else:
        change_content[i]["blocks_info"]=[]

new_code=change_content
new_code_file="/remote/aseqa_archive3/code_coverage/scrum_tmp/"+branch_name+"_new_code_"+time_tag
wfile=open(new_code_file, 'w')
wfile.write(str(new_code))
wfile.close()
print new_code
