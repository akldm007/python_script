#!/bin/bash

export NO_PROXY=10.172.217.34,*.sap.corp,*.mo.sap.corp,localhost,127.0.0.1,mo-*,*.sjc.sap.corp,10.173.0.195,10.173.3.54,lnxsdcc1,lnxsdcc1.oak.sap.corp
export no_proxy=10.172.217.34,*.sap.corp,*.mo.sap.corp,localhost,127.0.0.1,mo-*,*.sjc.sap.corp,10.173.0.195,10.173.3.54,lnxsdcc1,lnxsdcc1.oak.sap.corp
export HTTP_PROXY=http://proxy.oak.sap.corp:8080
export HTTPS_PROXY=http://proxy.oak.sap.corp:8080
# echo "==> `date +%T`"
if [ $HOSTNAME == "lnxsdcc1" ]
    then
        /usr/bin/python /usr/u/demingli/python_script/log_result $@
else
        /remote/aseqa_archive3/xud/python/tia/bin/python /usr/u/demingli/python_script/log_result $@
fi
# echo "==> `date +%T`"

