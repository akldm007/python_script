#!/usr/bin/python
import sys
import os

#get report
def get_report(report_path):
    if os.path.exists(report_path):
        report=eval(open(report_path).read())
        return report
    else:
        raise Exception("Report file not found!")

#diff dict 

#diff list

if __name__ == '__main__':
    arg1=sys.argv[1]
    arg2=sys.argv[2]
    report1=get_report(arg1)
    report2=get_report(arg2)
    cov_detail1=[]
    cov_detail2=[]
    for a_key in report1.keys():
        if a_key != "detail":
            if report1[a_key]==report2[a_key]:
                pass
            else:
                print "%-20s: %-30s | %-30s"%(a_key,report1[a_key],report2[a_key])
        elif a_key == "detail":
            for a_detail in report1["detail"]:
                cur_tuple=(a_detail["file_name"],a_detail["detail"]["line_found_num"],a_detail["detail"]["line_hit_num"])
                cov_detail1.append(cur_tuple)
            for a_detail in report2["detail"]:
                cur_tuple=(a_detail["file_name"],a_detail["detail"]["line_found_num"],a_detail["detail"]["line_hit_num"])
                cov_detail2.append(cur_tuple)
    print "========================================================"
    print "%-80s: %-10s | %-10s"%("file_name","line_found","line_hit")
    print 
    if len(cov_detail1)>len(cov_detail2):
        print "1 is report %s, 2 is report %s"%(arg1,arg2)
    else:
        cov_detail_tmp=cov_detail1
        cov_detail1=cov_detail2
        cov_detail2=cov_detail_tmp
        print "1 is report %s, 2 is report %s"%(arg2,arg1)
    for a_t1 in cov_detail1:
        found_flag=0
        for a_t2 in cov_detail2:
             if a_t1[0]==a_t2[0]:
                 found_flag=1
                 # if a_t1[1]!=a_t2[1] or a_t1[2]!=a_t2[2]:
                 if a_t1[1]!=a_t2[1]:
                     print "1> %-80s: %-10s | %-10s"%(a_t1[0],a_t1[1],a_t1[2])
                     print "2< %-80s: %-10s | %-10s"%(a_t2[0],a_t2[1],a_t2[2])
                 else:
                     pass
        if found_flag:
            pass
        else:
            print "file %s not in report2"%(a_t1[0])
            print "   %-80s: %-10s | %-10s"%(a_t1[0],a_t1[1],a_t1[2])
