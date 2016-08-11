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

#get cset list
cset_list=sys.argv[1]

def get_affected_info(content):
    return_list=[]
    for check_type in ["change","delete","insert"]:
        if check_type=="change":
            exp="-+\[(?:changed)\s(?:\S+)\]-+\|-+\[.*\s(\S+)\]-+\n"
        elif check_type=="delete":
            exp="-+\[(?:deleted)\s(?:\S+)\]-+\|-+\[.*\s(\S+)\]-+\n"
        elif check_type=="insert":
            exp="-+\[(?:after)\s(?:\S+)\]-+\|-+\[(?:inserted)\s(\S+)\]-+\n"
        affected_row=re.findall(exp,content)
        if affected_row:
            file_affected_info={}
            list_affected_row=[]
            ###To use the row as one list, un-comments the following line
            for rows in affected_row:
                if rows.count("-"):
                    begin_num=rows.split("-")[0]
                    eng_num=rows.split("-")[1]
                    row=range(int(begin_num),int(eng_num)+1)
                    list_affected_row.extend(row)
                else:
                    row=int(rows)
                    list_affected_row.extend([row])
            file_affected_info["row"]=list_affected_row
            #file_affected_info["row"]=affected_row
            file_affected_info["change_type"]=check_type
            return_list.append(file_affected_info)
    return return_list

def exec_cmd(sql):
    conn = sybpydb.connect(user='qts_user',password='ujes228o',servername="PDSQTS1")
    cur=conn.cursor()
    cur.execute(sql)
    result=cur.fetchall()
    cur.close()
    conn.close()
    return result

close_time_list=[]
all_affect_file_list=[]
branch_list=[]
condition=""
for a_cset in cset_list.split(",")[0:-1]:
    condition+="cset_name=\"%s\" or "%(a_cset)
condition+="cset_name=\"%s\""%(cset_list.split(",")[-1])
#print condition
create_time_sql="select date_created from qts_db..e2_cset where %s order by date_created"%(condition)     
create_time_list=exec_cmd(create_time_sql) 
close_time_sql="select date_closed from qts_db..e2_cset where %s order by date_closed desc"%(condition)
close_time_list=exec_cmd(close_time_sql)
#print create_time_list
#print close_time_list
affected_file_sql="select file_name from  qts_db..e2_members where cset_id in (select cset_id from qts_db..e2_cset where %s)"%(condition)
affected_file=exec_cmd(affected_file_sql)
branch_list_sql="select view_tag from qts_db..e2_cset where %s"%(condition)
branch_list=exec_cmd(branch_list_sql)

all_affect_file_list=[]
for an_affected_file in affected_file:
    if an_affected_file[0] in all_affect_file_list:
        pass
    else:
	all_affect_file_list.append(an_affected_file[0])

all_branch_list=[]
for a_branch in branch_list:
    cur_branch_name=a_branch[0].split("_")[0]
    if cur_branch_name in all_branch_list:
        pass
    else:
        all_branch_list.append(cur_branch_name)

if len(all_branch_list)>1:
    print """{"code": 1, "msg":"These csets are in mult-branch, Please make sure all the csets are in the same branch"}"""
    sys.exit(1)
else:
    branch_name=all_branch_list[0]
    view_name=branch_name+"_demingli_vu"
    cspec=branch_name+".csp"

##################Time##################
if create_time_list:
    earliest_create_time=create_time_list[0][0].strftime('%d-%b-%Y.%H:%M')
if close_time_list:
    if (None,) in close_time_list:
	latest_close_time=datetime.datetime.now().strftime('%d-%b-%Y.%H:%M')
    else:
	#latest_close_time=close_time_list[0][0].strftime('%d-%b-%Y.%H:%M')
	latest_close_time=(close_time_list[0][0]+datetime.timedelta(minutes=1)).strftime('%d-%b-%Y.%H:%M')

#print earliest_create_time
#print latest_close_time
##################affect file list##################

server_code_list=[]
tcf_list=[]
testset_list=[]
for a_file in all_affect_file_list:
    if a_file.endswith('.c') or a_file.endswith('.cpp') or a_file.endswith('.h') or a_file.endswith('.hpp'):
	server_code_list.append(a_file)
    elif re.search("(?:/qtst/testsets/)(\S+)",a_file):
	cur_set=re.search("(?:/qtst/testsets/)(\S+)",a_file).group(1)
	testset_list.append(cur_set.split("/")[-1])
    elif a_file.endswith('.tcf'):
	tcf_list.append(a_file)

#print server_code_list
#pdb.set_trace()

#################server code######################
file_list=",".join(server_code_list)
get_info_cmd="ssh demingli@lnxsdcc1.oak.sap.corp /usr/u/demingli/code_coverage/get_file_list_change.sh "+view_name+" "+cspec+" "+earliest_create_time+" "+latest_close_time+" "+file_list+" 2>/dev/null"
#print get_info_cmd
all_file_info=os.popen(get_info_cmd).read()

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
	        file_affected_info["change_info"]=get_affected_info(a_file_info["change_info"])
	        server_affected_list.append(file_affected_info)
else:
    print """{"code": 1, "msg":"No server code change is detected"}"""
    sys.exit(1)

#print server_affected_list
return_dict={}
return_dict["branch_name"]=branch_name
return_dict["earliest_create_time"]=earliest_create_time
return_dict["latest_close_time"]=latest_close_time
return_dict["server_code_change_list"]=server_affected_list
print return_dict	
#################test code########################
