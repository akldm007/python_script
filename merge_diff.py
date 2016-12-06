#!/usr/bin/python

import re
import pdb

def merge_diff(diff_all,diff_pull):
    for a_diff_pull in diff_pull:
        str_diff_all="\n".join(diff_all)
        a_diff_pull_content=" ".join(a_diff_pull.split(" ")[1:])
        if a_diff_pull_content:
            exp="\d+\s"+re.escape(a_diff_pull_content)
            # print exp
            if re.findall(exp,str_diff_all):
                #if len(re.findall(exp,str_diff_all))>1:
                #    pass
                #else:
                #    match_line=re.findall(exp,str_diff_all)[0]
                #    try:
                #        diff_all.remove(match_line)
                #    except:
                #        pass
                #        # print "remove pull content %s failed"%(a_diff_pull_content)
                match_line=re.findall(exp,str_diff_all)[0]
                try:
                    diff_all.remove(match_line)
                except:
                    pass
    return diff_all

diff_all=['529 imrh = imrv->imrv_hdrp;','565 imrh = imrv->imrv_hdrp;']
diff_pull=['529 imrh = imrv->imrv_hdrp;','565 imrh = imrv->imrv_hdrp;']

print merge_diff(diff_all,diff_pull)
