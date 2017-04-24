#!/usr/bin/env python

#test
import os
import sys
import pdb
import subprocess
import redis
import re

testset_file=sys.argv[1]
journal_file=sys.argv[2]
if os.path.exists(journal_file) and os.path.exists(testset_file):
    pass
else:
    print "Testset or journal file doesn't exist"
    print "Usage sumj.py testset journal"

def redis_con():
    #redis on lnxsdcc1.oak.sap.corp
    pool = redis.ConnectionPool(host='10.172.217.34', port=6379, db=3)
    r = redis.Redis(connection_pool=pool)
    return r

def sys_cmd(cmd):
    ret=subprocess.call(cmd,shell=True,stdout=open('/dev/null','w'),stderr=subprocess.STDOUT)
    return ret

def gen_tcf_list(testset_file):
    testset_content_list=open(testset_file).readlines()
    return_tcf_list=[]
    for a_tcf in testset_content_list:
	#print a_tcf
	if re.match("#.*",a_tcf) or re.match("\s*\n",a_tcf):
	    continue
	else:
            tcf_name=a_tcf.split("{")[0]
	    tcf_no=re.split("{|}",a_tcf)[1].split(",")
	    cur_tcf_no_list=[]
	    for a_number in tcf_no:
	        if a_number.count("-"):
	    	    cur_begin_no=a_number.split("-")[0]
	    	    cur_end_no=a_number.split("-")[-1]
	    	    cur_tcf_no_list.extend(range(int(cur_begin_no),int(cur_end_no)+1))
	        else:
		    #print "a_number %s"%(a_number)
	    	    cur_tcf_no_list.append(a_number)
	cur_tcf_list=map(lambda x:tcf_name+"{"+str(x)+"}",cur_tcf_no_list)
	return_tcf_list.append(cur_tcf_list)
    return return_tcf_list
		
tcf_list=[]
for a_list in gen_tcf_list(testset_file):
    tcf_list.extend(a_list)
journal_content=open(journal_file).read()
exp_tcf='(.*\.tcf{\S+}):\s(\S+)'
exp_py="\|.*\|\s(\S+)\s+\| configDefault \|\n\|.*\|.*\|.*\|\n\|.*\|.*\|.*\|\n(?:.*\n)?\|.*\|.*\|\s+(\S+) \|"
#print "%-100s    %-20s"%("Tcf_name","Status")
for cur_exp in [exp_tcf,exp_py]:
    for a_tcf_status in re.findall(cur_exp,journal_content):
        tcf_name=a_tcf_status[0].split("|")[-1]
	tcf_status=a_tcf_status[1]  
	#print "%-100s    %-20s"%(tcf_name,tcf_status)
	if tcf_status=="PASS" or tcf_status=="UNTESTED":
	    try:
	        tcf_list.remove(tcf_name)
	    except:
		pass
#print tcf_list
print "\n".join(tcf_list)

