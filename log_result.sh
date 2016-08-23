#!/bin/bash
if [ $HOSTNAME == "lnxsdcc1" ]
    then
        /usr/bin/python /usr/u/demingli/python_script/log_result $@
else
        /remote/aseqa_archive3/xud/python/tia/bin/python /usr/u/demingli/python_script/log_result $@
fi

