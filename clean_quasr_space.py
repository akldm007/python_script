#!/remote/aseqa_archive3/xud/python/tia/bin/python
import os
import sys
import subprocess
import re
import pdb

machine_name=sys.argv[1]

#get quasrspace
get_quasrspace_cmd="quasr_rsm show device -m %s -type file | grep file | gawk '{print $NF}'"%(machine_name)

quasrspaces=subprocess.check_output(get_quasrspace_cmd,shell=True).split()

#get session id from each quasrspace
session_list=[]
for a_quasrspace in quasrspaces:
    # ls_cmd="ls %s"%(a_quasrspace)
    # sub_dir=subprocess.check_output(ls_cmd,shell=True).split()
    sub_dir=[d for d in os.listdir(a_quasrspace)]
    if sub_dir:
        for a_dir in sub_dir:
            cur_dir=a_quasrspace+"/"+a_dir
            if os.path.isdir(cur_dir):
                if re.search("[a-z]+(\d+)",a_dir):
                    cur_s_id=re.search("[a-z]+(\d+)",a_dir).group(1)
                    check_cmd="quasr_rsm show session -session_id %d | wc -l"%(int(cur_s_id))
                    rsm_result=subprocess.check_output(check_cmd,shell=True)
                    # if cur_result>3, means session exist in rsm
                    if int(rsm_result)>3:
                        pass
                    else:
                        ps_cmd="ps -ef | grep %d | grep -E \"dataserver|diagserver|repserver|backupserver\" | grep -v grep | gawk '{print $2}'"%(int(cur_s_id))
                        ps_result=subprocess.check_output(ps_cmd,shell=True)
                        if ps_result:
                            pid_list=ps_result.split()
                            for a_pid in pid_list:
                                kill_cmd="sudo kill %d"%(int(a_pid))
                                print kill_cmd
                                # os.popen(kill_cmd)
                        else:
                            print "No process of session %d"%(int(cur_s_id))
                        print "%s is useless"%(cur_dir)
                        rm_cmd="rm -r %s"%(cur_dir)
                        # os.popen(rm_cmd)
            else:
                pass
#if session not exist, clean quasrspace, clean progress
