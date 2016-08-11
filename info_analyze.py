#!/usr/bin/python

import os
import re
import sys
import math 
import pdb

info_file = sys.argv[1]

branch_name = sys.argv[2]
ts_name = info_file.split('/')[-1].split('.')[0].split('__')[0]
#print ts_name
model = sys.argv[3]
get_ts_id_cmd = "curl -s \"http://10.173.3.54/tsm/ts_info/get_ts_id/?branch_name=%s&ts_name=%s\""%(branch_name,ts_name)
#pdb.set_trace()
#get_ts_id_cmd = "curl -s \"http://10.173.3.54:8888/ts_info/get_ts_id/?branch_name=%s&ts_name=%s\""%(branch_name,ts_name)
try:
        tasks=eval(os.popen(get_ts_id_cmd).read())
        ts_id = tasks['ts_id']
        view_id = tasks['view_id']
except:
	ts_id = 0
	view_id = 0

info_content = open(info_file).read()

list_index_SF = []

list_index_end_of_record = []

for each_SF in re.finditer("SF:\S+\n", info_content):

    list_index_SF.append(each_SF.start())
#    print each_SF.start() 
#    print "\n"

#print list_index_SF
#
#print "\n"

for each_end_of_record in re.finditer("end_of_record\n", info_content):

    list_index_end_of_record.append(each_end_of_record.end())
#    print each_end_of_record.end()
#    print "\n"
if len(list_index_SF) != len(list_index_end_of_record):

    print "Warning: Dismatch, some record may be lost!"

    if len(list_index_SF) > len(list_index_end_of_record):

        record_amount = len(list_index_SF) 
	
    else:

	record_amount = len(list_index_end_of_record)

else:

    record_amount = len(list_index_SF)

SF_list = []
dict_record = {}

for i in range(0,record_amount):
#    pdb.set_trace()
    if re.search("SF:/calm/svr/(\S+)\n", info_content[list_index_SF[i]:list_index_end_of_record[i]]):
	exp = """SF:/calm/svr/(\S+)\n"""
	#cur_SF = "/calm/svr/"+re.search(exp, info_content[list_index_SF[i]:list_index_end_of_record[i]]).group(1)
	cur_SF = re.search(exp, info_content[list_index_SF[i]:list_index_end_of_record[i]]).group(1)
	if cur_SF in SF_list:
	    dict_record[cur_SF]=dict_record[cur_SF]+info_content[list_index_SF[i]:list_index_end_of_record[i]]
	else:
	    dict_record[cur_SF]=info_content[list_index_SF[i]:list_index_end_of_record[i]]
	    SF_list.append(cur_SF)

#print dict_record
#print "\n"
#print SF_list
for cur_SF in dict_record.keys():
#    pdb.set_trace()
    cur_record=dict_record[cur_SF]
#    if cur_record.count('ext/'):
#	break
#func coverage
    dict_cur_FDA={}
    cur_FNF=0
    cur_FNFDA=[]
    cur_FNH=0
    cur_FNHDA=[]
    list_cur_FDA=[]
    for cur_FDA in re.finditer("FNDA:(\d+),(\S+)\n",cur_record):
       	if cur_FDA.group(2) in list_cur_FDA:
       	    if int(cur_FDA.group(1)):
       	        dict_cur_FDA[cur_FDA.group(2)]=cur_FDA.group(1)
       	else:
       	    dict_cur_FDA[cur_FDA.group(2)]=cur_FDA.group(1)
       	    list_cur_FDA.append(cur_FDA)
	    
    for a_FDA in dict_cur_FDA.keys():
	if int(dict_cur_FDA[a_FDA]):
	    cur_FNH=cur_FNH+1	
	    cur_FNHDA.append(a_FDA)
	cur_FNFDA.append(a_FDA)
	cur_FNF=cur_FNF+1
	
	
#line coverage
    dict_cur_DA={}
    cur_LF=0
    cur_LFDA=[]
    cur_LH=0
    cur_LHDA=[]
    list_cur_DA=[]
    for cur_DA in re.finditer("DA:(\d+),(\d+)\n",cur_record):
       	if cur_DA.group(1) in list_cur_DA:
       	    if int(cur_DA.group(2)):
       	        dict_cur_DA[cur_DA.group(1)]=cur_DA.group(2)
       	else:
       	    dict_cur_DA[cur_DA.group(1)]=cur_DA.group(2)
       	    list_cur_DA.append(cur_DA)
	    
    for a_DA in dict_cur_DA.keys():
	if int(dict_cur_DA[a_DA]):
	    cur_LH=cur_LH+1	
	    cur_LHDA.append(a_DA)
	cur_LFDA.append(a_DA)
        cur_LF=cur_LF+1

#cov
    if int(cur_FNH)==0:
	cur_FCOV=0
    else:
	cur_FCOV='%.2f%%'%(float(cur_FNH)/float(cur_FNF)*100)
    if int(cur_LH)==0:
	cur_LCOV=0    
    else:
	cur_LCOV = '%.2f%%'%(float(cur_LH)/float(cur_LF)*100)
#generate sql

#    pdb.set_trace()
    print "UPDATE ts_info_code_coverage_feature set FNF=%d,LF=%d where file_name=\'%s\';\n"%(int(cur_FNF),int(cur_LF),'/calm/svr/'+cur_SF)
    if (int(cur_FNH)==0 and int(cur_LH)==0): 
	pass
    else:
	list_LHDA=[]
        for i in cur_LHDA:
            list_LHDA.append(int(i))
        list_LHDA.sort()
        cur_LHDA=''.join(str(list_LHDA)[1:-1])

	list_LFDA=[]
        for j in cur_LFDA:
            list_LFDA.append(int(j))
        list_LFDA.sort()
        cur_LFDA=''.join(str(list_LFDA)[1:-1])

	cur_FNFDA=(',').join(cur_FNFDA)
	cur_FNHDA=(',').join(cur_FNHDA)
	if model == 'replace':
	    print "REPLACE INTO ts_info_code_coverage_record VALUES('',%d,%d,\'%s\',%d,%d,\'%s\',%d,%d,\'%s\',\'%s\',\'%s\',\'%s\',\'%s\');\n"%(view_id,ts_id,cur_SF,int(cur_FNF),int(cur_FNH),cur_FCOV,int(cur_LF),int(cur_LH),cur_LCOV,cur_LHDA,cur_LFDA,cur_FNHDA,cur_FNFDA)
	elif model == 'ignore':
	    print "INSERT IGNORE INTO ts_info_code_coverage_record VALUES('',%d,%d,\'%s\',%d,%d,\'%s\',%d,%d,\'%s\',\'%s\',\'%s\',\'%s\',\'%s\');\n"%(view_id,ts_id,cur_SF,int(cur_FNF),int(cur_FNH),cur_FCOV,int(cur_LF),int(cur_LH),cur_LCOV,cur_LHDA,cur_LFDA,cur_FNHDA,cur_FNFDA)
	else:
	    print "INSERT INTO ts_info_code_coverage_record VALUES('',%d,%d,\'%s\',%d,%d,\'%s\',%d,%d,\'%s\',\'%s\',\'%s\',\'%s\',\'%s\');\n"%(view_id,ts_id,cur_SF,int(cur_FNF),int(cur_FNH),cur_FCOV,int(cur_LF),int(cur_LH),cur_LCOV,cur_LHDA,cur_LFDA,cur_FNHDA,cur_FNFDA)
	#print "INSERT INTO ts_info_code_coverage_record VALUES(%d,\'%s\',%d,%d,\'%s\',%d,%d,\'%s\');\n"%(ts_id,cur_SF,int(cur_FNF),int(cur_FNH),cur_FCOV,int(cur_LF),int(cur_LH),cur_LCOV)
#       # print cur_SF,cur_FNF,cur_FNH,cur_LF,cur_LH
	    
	        	

