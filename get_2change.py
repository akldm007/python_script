#!/usr/bin/env python

import os
import sys
import pdb
import subprocess
import redis

create_time=sys.argv[1]
close_time=sys.argv[2]
file_list=sys.argv[3]
def sys_cmd(cmd):
    ret=subprocess.call(cmd,shell=True,stdout=open('/dev/null','w'),stderr=subprocess.STDOUT)
    if ret:
        raise SyntaxError("Exec cmd "+cmd+" fail")
    return ret

def redis_con():
    #redis on lnxsdcc1.oak.sap.corp
    pool = redis.ConnectionPool(host='10.172.217.34', port=6379, db=2)
    r = redis.Redis(connection_pool=pool)
    return r

for a_file in file_list.split(","):
    org_tmp_file="/remote/aseqa_archive3/code_coverage/scrum_tmp/org"+a_file.replace("/","_")
    if os.path.exists(org_tmp_file):
	sys_cmd("rm -f "+org_tmp_file)
    #freeze
    sys_cmd("/usr/u/codeadm/bin/freeze "+create_time)
    #write file 
    try:
        org_file_content=open(a_file).read() 
    except:
	org_file_content=""
    org_file=open(org_tmp_file, 'w')
    org_file.write(org_file_content)
    org_file.close()
    #unfreeze
    sys_cmd("/usr/u/codeadm/bin/unfreeze")

for a_file in file_list.split(","):
    cur_tmp_file="/remote/aseqa_archive3/code_coverage/scrum_tmp/cur"+a_file.replace("/","_")
    if os.path.exists(cur_tmp_file):
	sys_cmd("rm -f "+cur_tmp_file)
    #freeze
    sys_cmd("/usr/u/codeadm/bin/freeze "+close_time)
    #write file
    try:
        cur_file_content=open(a_file).read()
    except:
	cur_file_content=""
    cur_file=open(cur_tmp_file, 'w')
    cur_file.write(cur_file_content)
    cur_file.close()
    r=redis_con()
    r.set(a_file,cur_file_content)
    #unfreeze 
    sys_cmd("/usr/u/codeadm/bin/unfreeze")

result=[]
for a_file in file_list.split(","):
    org_tmp_file="/remote/aseqa_archive3/code_coverage/scrum_tmp/org"+a_file.replace("/","_")
    cur_tmp_file="/remote/aseqa_archive3/code_coverage/scrum_tmp/cur"+a_file.replace("/","_")
    #ct diff 
    cur_result={}
    cur_result["file_name"]=a_file
    cur_result["change_info"]=os.popen("ct diff "+org_tmp_file+" "+cur_tmp_file).read()
    result.append(cur_result)
    sys_cmd("rm -f "+org_tmp_file+" "+cur_tmp_file)
print result
    
