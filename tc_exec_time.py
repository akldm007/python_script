#!/remote/asepw_archive2/grid/tools/asepython/pythonMini/asepython/python/bin/python
import sys
import os
import re
import pdb
os.environ['SYBASE']='/remote/aseqa_archive2/asecepheus/linuxamd64_smp/release'
os.environ['SYBASE_OCS']='OCS-16_0'
os.environ["LD_LIBRARY_PATH"]=os.environ["LD_LIBRARY_PATH"]+":/remote/aseqa_archive2/asecepheus/linuxamd64_smp/release/OCS-16_0/lib"
sys.path.append('/remote/aseqa_archive2/asecepheus/linuxamd64_smp/release/OCS-16_0/python/python26_64r/lib')
import sybpydb
import math

tc_name=sys.argv[1]
def exec_cmd(sql):
    conn = sybpydb.connect(user='tamqa',password='only4qa',servername="PDSQTS1")
    cur=conn.cursor()
    cur.execute(sql)
    result=cur.fetchall()
    cur.close()
    conn.close()
    return result

get_id_sql="select tc_id from tlib_test_cases where tc_name=\"%s\""%(tc_name)

try:
    tc_id=exec_cmd(get_id_sql)[0][0]
    # print tc_id
except:
    raise ValueError("'{0}' is not a valide test case name!".format(tc_name))

sql="""select exec_time from tlib_test_results where tc_id=%s and tc_status='suc'"""%(tc_id)

try:
    result=exec_cmd(sql)
except:
    raise Exception("No result!")

exec_time_list=map(lambda x:x[0], result)
# print exec_time_list
sum_time=0
count=0
for exec_time in exec_time_list:
    if exec_time:
        sum_time+=int(exec_time)
        count+=1
if count:
    average=int(math.ceil(float(sum_time/count)))
else:
    raise Exception("No result!")

if exec_time_list>3:
    print (sorted(exec_time_list)[0],average,sorted(exec_time_list)[-1])
else:
    print (average,average,average)
