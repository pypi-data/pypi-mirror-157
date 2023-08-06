#!/usr/bin/env python3
#
# main_launch_veh_process.py - launches N vehicle processes using parallel-ssh that each
#                             send and receive udp messages with main_core.py.
#
# Individual vehicle model processes are launched using parallel-ssh as individual
# detatched screen processes on a remote (or localhost) machine's ssh server
#
#
# make sure ssh is setup for passwordless login: http://www.linuxproblem.org/art_9.html
# (a) on local machine, ssh-keygen -t rsa (use blank passphrase)
# (b) make .ssh folder on remote machine: ssh b@B mkdir -p .ssh
# (c) move public key to remote machine: cat .ssh/id_rsa.pub | ssh b@B 'cat >> .ssh/authorized_keys'
#
# https://github.com/ParallelSSH/parallel-ssh
#
# Marc Compere, comperem@gmail.com
# created : 18 Jul 2018
# modified: 04 Jul 2022
#
# ---
# Copyright 2018 - 2022 Marc Compere
#
# This file is part of the Mobility Virtual Environment (MoVE).
#
# MoVE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.
#
# MoVE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License version 3 for more details.
#
# A copy of the GNU General Public License is included with MoVE
# in the COPYING file, or see <https://www.gnu.org/licenses/>.
# ---

import os
import sys
import time
import random
import string
from sync_function import sync_vehicle_and_config
sys.path.append(os.path.relpath("../scenario")) # find ../scenario/readConfigFile.py w/o a linux file system symbolic link (when run from ./core)
from readConfigFile import readConfigFile
from pssh.clients import ParallelSSHClient
import code # drop into a python interpreter to debug using: code.interact(local=dict(globals(), **locals()))
import getpass # getpass.getuser()


cmdLineSync=True
n=len(sys.argv)

if n==4 and sys.argv[3]=='--no-sync':
    cmdLineSync=False # skip vehicle model and config file sync'ing if you know you wanna

# this is the normal GUI based execution from the data dashboard display "Launch vehicle processes" button
if n>=3 and sys.argv[1]=='-f':
    # source files, to be copied to runtime folder via ssh/rsync
    #cfgFileSrc = '../scenario/default.cfg' # python's .ini format config file
    cfgFileSrc  = sys.argv[2] # /home/comperem/Google_drive/Compere/technical/lang/python/MoVE/v1.07_dev/scenario/default.cfg
    cfgFileName = os.path.basename( cfgFileSrc ) # default.cfg
    coreSrcBase = os.path.abspath(os.path.dirname(__file__)) # this is where file is located: coreSrcBase=/home/comperem/Google_drive/Compere/technical/lang/python/MoVE/v1.07_dev/core
    print('coreSrcBase: {}'.format( coreSrcBase ))
    print('reading SOURCE scenario config file: {}'.format( cfgFileSrc ))
    cfg, veh_names_builtins, veh_names_live_gps = readConfigFile( cfgFileSrc )

else:
    print('\n')
    print('\t usage  :    ./main_launch_veh_process.py -f myScenario.cfg [--no-sync]\n\n')
    print('\t example:    ./main_launch_veh_process.py -f ../scenario/default.cfg')
    print('\t example:    ./main_launch_veh_process.py -f ../scenario/default.cfg --no-sync\n')
    sys.exit(0)



nVehTot = cfg.nVeh_builtin + cfg.nVeh_live_gps # + nVeh_custom
if nVehTot==0:
    print('ERROR, nVeh_builtin={0}, nVeh_live_gps={0}, zero vehicles specified - redo with at least 1 vehicle or live GPS follower' \
           .format(cfg.nVeh_builtin,cfg.nVeh_live_gps))
    sys.exit(-1)

if (cfg.sync_veh_and_cfg==True and cmdLineSync==True):
    # sync ../veh_model and config files in ../scenario to veh runtime location
    # on remote host (even if it's localhost)
    sync_vehicle_and_config( coreSrcBase, cfg.veh_host_ip , cfg.username , cfg.vehRuntimeDir ) # rsync ../veh_model and config file to target runtime folder on remote machine



# destination, or runtime file locations
vehModelFileName='main_veh_model.py' # MoVE built-in vehicle model (or live-GPS-follower) executable python script, locally or on a remote machine
vehModelFilePath = cfg.vehRuntimeDir + '/veh_model'                # vehModelFilePath = '/tmp/MoVE/veh_model'
vehModelFileFull = vehModelFilePath + '/' + vehModelFileName       # full path to veh model script: vehModelFileFull = '/tmp/MoVE/veh_model/main_veh_model.py'
cfgFileFull      = cfg.vehRuntimeDir + '/scenario/'  + cfgFileName # locate config file: cfgFileFull='/tmp/MoVE/veh_model/../scenario/default.cfg'
output = {} # init dummy dictionary

client = ParallelSSHClient( [cfg.veh_host_ip] ) # client API: https://parallel-ssh.readthedocs.io/en/latest/native_parallel.html


# to index vehicle names from the config file, convert the .keys() method output into a list:
names_gps      = list( veh_names_live_gps.values() )
names_builtins = list( veh_names_builtins.values() )


print('constructing and launching parallel-ssh commands for {} vehicle models:'.format(nVehTot))
for i in range(nVehTot):
    
    ith_vid = i+cfg.vid_base # assign vid (vehicle ID) for the i'th parallel-ssh process
    
    # read cfg file for each vehicle's cfg.name only!
    cfgVid, _, __ = readConfigFile( cfgFileSrc, ith_vid )
    #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
    
    # - the first nVeh_builtin vehicles will have GPS listener ports=0 (udp_port_gps==0)
    #   indicating they are a built-in vehicle models
    # - all remainin vehicles must be live-GPS-followers, so their listener ports are non-zero and
    #   assigned as [udp_port_base_gps+i] for each subsequent live-GPS-follower vehicle model
    if i<cfg.nVeh_builtin:
        screen_name = str(ith_vid)
        udp_port_gps=0 # 0->indicates to veh model process it is a standard built-in veh model (not a live-GPS-follower)
        ith_vid_str  = str(ith_vid)
        if hasattr(cfgVid,'name'): # if a name is assigned from cfg file [veh_types] section, use it
            ith_name     = cfgVid.name
        elif i<len(names_builtins): # otherwise, assign a name from [veh_names_builtins]
            ith_name = names_builtins[i] # use as many names as are in the config file
        else: # otherwise, make up a name
            ith_name = 'sim_'.join(random.sample( string.ascii_lowercase*3, 3 )) # literally make up a name from 3 random characters
    else:
        screen_name  = str(ith_vid) + "_live_gps"
        udp_port_gps = ith_vid + cfg.udp_port_base_gps # this vehicle ID will listen for live GPS input on this port
        ith_vid_str  = str(ith_vid) + "_live_gps"
        j=i+cfg.nVeh_builtin # j shifts the i'th vehicle to pull names from the builtin vehicle names
        if hasattr(cfgVid,'name'): # if a name is assigned from cfg file [veh_types] section, use it
            ith_name     = cfgVid.name
        elif j<len(names_gps): # otherwise, assign a name from [veh_names_live_gps]
            ith_name = names_gps[j] # use as many names as are in the config file
        else: # otherwise, make up a name
            ith_name = 'live_'.join(random.sample( string.ascii_lowercase*3, 3 )) # literally make up a name from 3 random characters
    
    # construct a bash command line to run a detached screen process with the vehicle model or live-GPS-follower
    if cfg.log_level>1:
        # capture console output in /tmp/debug*.txt
        ith_cmd = 'screen -dm -S vid{0} bash -c "cd {1} ; {2} -f {3} {4} {5} {6} > /tmp/debug_{7}.txt   2>&1"' \
                  .format(screen_name, vehModelFilePath, vehModelFileFull, cfgFileFull, ith_vid, udp_port_gps, ith_name, ith_vid_str)
    else:
        ith_cmd = 'screen -dm -S vid{0}          cd {1} ; {2} -f {3} {4} {5} {6}' \
                  .format(screen_name, vehModelFilePath, vehModelFileFull, cfgFileFull, ith_vid, udp_port_gps, ith_name)
    
    print( '\tlaunching vehicle {0} of {1}, vid={2}, name={3} with: [ {4} ] on: [{5}]'.format(i+1,nVehTot,ith_vid,ith_name,ith_cmd,cfg.veh_host_ip) )
    
    # launch the i'th vehicle command to the operating system (a vehicle model process in a detached screen)
    # e.g. ith_cmd = 'screen -dm -S vid100 bash -c "/tmp/MoVE/veh_model/main_veh_model.py -f /tmp/MoVE/veh_model/../scenario/default.cfg 100 0 > /tmp/debug_100.txt   2>&1"'
    #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
    output[i] = client.run_command( ith_cmd )
    
    # get the detached screen's exit code to make sure it ran correctly
    client.join(output[i]) # .join gets exit codes after command completion; does not block other commands running in parallel
    
    for host_output in output[i]:
        print("\tprocess [%s] exit code: %s" % (host_output.host, host_output.exit_code))
        for line in host_output.stdout:
            print("\tprocess [%s] stdout   : %s" % (host_output.host, line))
            
    time.sleep(0.2) # this reduces peak cpu load for starting many vehicle processes
    
print('done.', flush=True)
