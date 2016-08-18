#!/usr/bin/env python

import os
import sys
import pdb
import subprocess
import redis
import re
import time
import argparse


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
    #print testset_content_list
    return_tcf_list=[]
    for a_tcf in testset_content_list:
        #print a_tcf
        if re.match("#.*",a_tcf) or re.match("\s*\n",a_tcf) or a_tcf.find("{")==-1:
            continue
        else:
            #use short path
            tcf_name=a_tcf.split("/")[-1].split("{")[0]
            #use long path
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
                

#print time.localtime()
def log_redis(workdir):
    for a_sub_workdir in sub_workdir_list:
        if a_sub_workdir:
            cur_dir=workdir+a_sub_workdir+"/"
            ts_name=a_sub_workdir.split("__")[0]
            #print ts_name
            testset_file=cur_dir+a_sub_workdir.split("__")[0]
            hkey=workdir+a_sub_workdir.split("__")[0]
            r=redis_con()
            r.zadd(workdir,hkey,0)
            tcf_list=[]
            for a_list in gen_tcf_list(testset_file):
                tcf_list.extend(a_list)
            #tcf_list=gen_tcf_list(testset_file)[0]
            map(lambda x:r.hmset(hkey,{"ts_status":"init",x:"init"}),tcf_list)
            #pdb.set_trace()
            #print tcf_list
            journal_file=workdir+"/"+"journal"
            if os.path.exists(journal_file):
                r.hmset(hkey,{"ts_status":"running"})
            else:
                journal_file=cur_dir+"result."+a_sub_workdir.split("__")[0]+"/"+"journal.exec*"
                #print journal_file
                #pdb.set_trace()
                if sys_cmd("head "+journal_file):
                    r.hmset(hkey,{"ts_status":"fail"})
                else:
                    r.hmset(hkey,{"ts_status":"suc"})
                    for a_status in ["PASS","FAIL","UNTESTED","UNRESOLVED"]:
                        grep_cmd="grep %s %s | grep tcf"%(a_status,journal_file)
                        if subprocess.call(grep_cmd,shell=True,stdout=open('/dev/null','w'),stderr=subprocess.STDOUT):
                            pass
                        else:
                            match_content=subprocess.check_output(grep_cmd,shell=True)        
                            for a_match in match_content.split("\n"):
                                if a_match:
                                    cur_match=a_match.split("|")[-1]
                                    #print "cur_match: %s"%(cur_match)
                                    cur_tcf_name=cur_match.split(":")[0]
                                    cur_tcf_status=cur_match.split(":")[1].split()[0].strip()
                                    r.hmset(hkey,{cur_tcf_name:cur_tcf_status})
                                else:
                                    pass

#print time.localtime()
def gen_report(log_key,*testset):
    r=redis_con()
    if testset:
        testset=log_key+testset[0]
        testset_list=[testset]
    else:
        testset_list=r.zrevrange(log_key,0,-1)
    #print "testset_list=%s"%(testset_list)
    for a_testset in testset_list:
        testset_name=a_testset.split("/")[-1] 
        cur_tcf_list=r.hkeys(a_testset)
        pass_tcf_list=[]
        fail_tcf_list=[]
        unres_tcf_list=[]
        untest_tcf_list=[]
        notrun_tcf_list=[]
        for a_tcf in cur_tcf_list:
            if a_tcf=="ts_status":
                cur_ts_status=r.hget(a_testset,a_tcf)
            else:
                cur_tcf_status=r.hget(a_testset,a_tcf)
                if cur_tcf_status=="PASS" or cur_tcf_status=="Ok":
                    pass_tcf_list.append(a_tcf)
                elif cur_tcf_status=="FAIL" or cur_tcf_status=="ERROR":
                    fail_tcf_list.append(a_tcf)
                elif cur_tcf_status=="UNRESOLVED":
                    unres_tcf_list.append(a_tcf)
                elif cur_tcf_status=="UNTESTED":
                    untest_tcf_list.append(a_tcf)
                else:
                    notrun_tcf_list.append(a_tcf)
        cur_report="Testset:%-40s    PASS:%-5d FAIL:%-5d UNRESOLVED:%-5d UNTESTED:%-5d NOT_RUN:%-5d"%(testset_name,len(pass_tcf_list),len(fail_tcf_list),len(unres_tcf_list),len(untest_tcf_list),len(notrun_tcf_list))
        print cur_report

def gen_rerun(log_key,testset):
    #pdb.set_trace()
    r=redis_con()
    hkey=log_key+testset
    cur_tcf_list=r.hkeys(hkey)
    tcf_list=[]
    for a_tcf in cur_tcf_list:
        if a_tcf=="ts_status":
            pass
        else:
            tcf_list.append(a_tcf)
            cur_tcf_status=r.hget(hkey,a_tcf)
            if cur_tcf_status=="PASS" or cur_tcf_status=="UNTESTED":
                tcf_list.remove(a_tcf)
    rerun_ts="\n".join(tcf_list)
    return rerun_ts

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-log_only",action="store_true",help="log the result only")
    parser.add_argument("-gen_report",action="store_true",help="generate the report")
    parser.add_argument("-gen_rerun_ts",action="store_true",help="generate the rerun testset")
    parser.add_argument("-workdir",help="grid work dir")
    parser.add_argument("-testset",help="testset name")
    args=parser.parse_args()
    
    workdir=args.workdir
    testset=args.testset
    
    sub_workdir_list=subprocess.check_output("ls "+workdir,shell=True).split("\n")
    #print sub_workdir_list
    log_key=workdir
    if args.log_only:
        log_redis(log_key)
    elif args.gen_report:
        if testset:
            gen_report(log_key,testset)    
        else:
            gen_report(log_key)
    elif args.gen_rerun_ts:
        print gen_rerun(log_key,testset)
        
    
