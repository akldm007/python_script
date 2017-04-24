#!/usr/bin/env python
import re
from sys import argv
import os

def show_result(line_start, line_end=None):
    if line_end is None:
        print line_start
    else:
        print "%d-%d" % (line_start, line_end)

def parse_lines(content):
    line_no = 0
    line_start = False
    comment_start = False
    start_line_no = 0;
    for line in content.split('\n'):
        line_no += 1
        if not line_start and not comment_start:
            if re.match(r'#\s*include',line) is not None:
                # print "//include found"
                # show_result(line_no)
                pass
            elif re.match(r'^\s*/\*.*\*/',line) is not None or re.match(r'^//',line) is not None:
                # print "//comment found."
                # show_result(line_no)
                pass
            elif re.match(r'^\s*$', line):
                # print "//empty line"
                # show_result(line_no)
                pass
            elif re.match(r'^\s*.*[;\}]\s*(/\*.*)?\s*$', line) or re.match(r'^\s*\w.*\{\s*(/\*.*)?\s*$',line):
                # show_result(line_no)
                if re.search(r'/\*.*\s*$', line) is not None:
                    comment_start = True
            elif re.match(r'^\s*/\*',line) is not None and re.search(r'[^;}]\s*\*/\s*$', line) is None:
                # print "//comment started"
                pass
                comment_start = True
                # start_line_no = line_no
            # elif re.match(r'^\s*\w+.*[^;]\s*/\*.*\s*$', line) is not None:
            #     show_result(line_no)
            elif re.match(r'^\s*\w+.*[^;]\s*(/\*.*)?\s*$', line) is not None:
                # print "//code line started"
                line_start = True
                start_line_no = line_no
            else:
                # show_result(line_no)
                pass
        else:
            if line_start:
                if re.search(r'\s*[;{}]\s*(/\*.*\*/)?\s*$',line) is not None:
                    # print "//block code found"
                    # show_result(start_line_no, line_no)
                    cur_list=[]
                    # show_result(start_line_no, line_no)
                    for line_number in range(start_line_no,line_no+1):
                        cur_list.append(line_number)
                    return_list.append(cur_list)
                    line_start = False
                else:
                    continue
            if comment_start:
                if re.search(r'\s*\*/\s*$',line) is not None:
                    # print "//block comment found"
                    # show_result(start_line_no, line_no)
                    comment_start = False
                else:
                    continue

if __name__ == "__main__":
    if len(argv) == 1:
        exit("Usage:%s <source_file>" % os.path.basename(argv[0]))
    src_file = argv[1]
    if os.path.exists(src_file):
        return_list=[]
        parse_lines(open(src_file).read())
        print return_list
    else:
        # print "Source '%s' does not exist!" % src_file
        raise Exception("Source '%s' does not exist!" % src_file)
