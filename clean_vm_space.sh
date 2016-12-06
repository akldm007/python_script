#!/usr/bin/bash

for a_mo in mo-47c0681f3 mo-7281826b8 mo-2e6a306f9 mo-5d4d1d3fe mo-bacf8a849 mo-afacf2ce2 mo-4b0ed0bcf mo-9ce1c6567 mo-a15ab0928
# for a_mo in mo-47c0681f3 mo-7281826b8 mo-2e6a306f9 mo-5d4d1d3fe mo-bacf8a849 mo-afacf2ce2 mo-4b0ed0bcf mo-a15ab0928
    do
        host_name=$a_mo".mo.sap.corp"
        /bin/ping -c1 -W1 $a_mo &> /dev/null
        ping=$?
        if [ "$ping" -eq 0 ]
            then
                ssh -o StrictHostKeyChecking=no -o BatchMode=yes $host_name ls &> /dev/null
                ssh_able=$?
                if  [ "$ssh_able" -eq 0 ]
                    then
                        cmd="/usr/u/demingli/python_script/clean_quasr_space.py "$a_mo
                        echo $cmd
                        ssh -o StrictHostKeyChecking=no $host_name $cmd
                else
                    echo "$a_mo ssh failed"
                fi
        else
            echo "$a_mo is down"
        fi
    done
