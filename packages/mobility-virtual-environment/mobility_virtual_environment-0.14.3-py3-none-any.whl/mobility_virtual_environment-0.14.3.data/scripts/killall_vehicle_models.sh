#!/bin/bash
# kill all vehicle models from the command-line
#
# this shell script is not the normal way to exit vehicles models.
# this is intended only when sending the runState==5 message does not work.
#
# the normal, expected way of stopping vehicle model processes is:
#     ./main_changeRunState.py -f ../scenario/default.cfg 5
#
# Marc Compere, comperem@gmail.com
# created : 19 Jul 2020
# modified: 19 Jul 2020

vm_procs=`ps ax | grep python3 | grep main_veh_model | awk '{print $1}'`

echo 'found these vehicle model process numbers to kill:'
echo ${vm_procs[*]}

for procNum in ${vm_procs[*]}
do
    echo killing $procNum
    kill $procNum
done


