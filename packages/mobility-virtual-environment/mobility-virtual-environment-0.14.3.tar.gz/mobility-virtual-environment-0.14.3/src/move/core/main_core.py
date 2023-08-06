#!/usr/bin/env python3
#
# main_core.py - central executable for communicating with N vehicles over udp
#
# the primary goals of main_core.py are to:
# (1) listen to all incoming messages from each of the N vehicles, some of which
#     may be live GPS followers. This happens in the aggregator thread.
#     The aggregator thread assembles all incoming vehicle state update messages
#     into a single State struct. The State struct represents the current
#     snapshot of the entire set of N vehicle states (pos, vel, behavior, health).
# (2) periodically poll the State vector to check for vehicle-to-vecicle distances
#     that could be problematic. This is an order N^2 problem which can take
#     significant cpu time, especially above N=100 vehicles.
#     This is a naive implementation checking all distances at each poll of State.
# (3) send collision warning messages back to certain vehicles, especially those
#     whose inter-vehicle distance drops below a threshold and the distance rate
#     is sufficiently negative.
# (4) log all traffic to a .csv file
#
#
#
# Benchmarking results from udp message send and receive rate using select()
# windows:
#   sent 100000 udp packets in 13.368475914 seconds, rate=7480.28(pkts/sec)
#   received 100000 udp packets in 13.366605520248413 seconds, rate=7481.330981790023(pkts/sec)
#
# linux:
#   sent 100000 udp packets in 0.42529797554 seconds, rate=235129.26(pkts/sec)
#   received 100000 udp packets in 0.4251558780670166 seconds, rate=235207.85001174832(pkts/sec)
#
# Marc Compere, comperem@gmail.com
# created : 21 Feb 2017
# modified: 02 Jul 2022
#
# ---
# Copyright 2018 - 2020 Marc Compere
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
from datetime import datetime
import socket
import msgpack # fast serialize/deserialize of complete python data structures: sudo pip3 install msgpack-python
import msgpack_numpy as m # msgpack for numpy objects: sudo pip3 install msgpack-numpy
import select
import queue
import threading
import logging
from all_vehicles import All_vehicles
from core_udp_io import core_udp_io
sys.path.append(os.path.relpath("../scenario")) # find ../scenario/readConfigFile.py w/o a linux file system symbolic link (when run from ./core)
from readConfigFile import readConfigFile

n=len(sys.argv)
if n==3 and sys.argv[1]=='-f':
    print('reading scenario config file: {}'.format(sys.argv[2]))
    cfgFile =      sys.argv[2]
    #cfgFile = '../scenario/default.cfg' # python's .ini format config file
    print('cfgFile={}'.format(cfgFile))
    cfg, veh_names_builtins, veh_names_live_gps = readConfigFile( cfgFile, -1 )
    print("avoidBySteer behavior     {0}".format(cfg.behaviorCfg['avoidBySteer']))
    
else:
    print('\n')
    print('\t usage  :    ./main_core.py -f myScenario.cfg\n')
    print('\t example:    ./main_core.py -f ../scenario/default.cfg\n')
    sys.exit(0)

cfg.nVehTot = cfg.nVeh_builtin + cfg.nVeh_live_gps # + nVeh_custom


debug=cfg.debug # (0/1/2/3) more or less console output (0=none, 3=tons)

cfg.udp_ip_in          = "0.0.0.0" # listen for vehicle updates from any ip (keep separate from cfg.core_host_ip b/c you always want to listen from anyone 0.0.0.0)
cfg.tStart          = time.time() # seconds since Jan 01, 1970

cfg.runStateDesc = ['']*6 # 1-based text strings for each runState, entry [0] unusused
cfg.runStateDesc[1] = '=== READY ==='
cfg.runStateDesc[2] = '===  SET  ==='
cfg.runStateDesc[3] = '===  GO   ==='
cfg.runStateDesc[4] = '=== PAUSE ==='
cfg.runStateDesc[5] = '=== EXIT  ==='


e            = threading.Event() # for signaling graceful exit() to all threads
eDataPollReq = threading.Event() # for data consumer to tell producer to send new data
qState       = queue.Queue() # for sharing State between aggregatoro() and poll_state()
qVehCmd      = queue.Queue() # queue for sending vehicles commands from poll_state() to udp_io.send()
                             # for example: AVOID messages and testMgr commands: READY, SET, GO, PAUSE, STOP

if cfg.logfile==1:
    tNowFname  = datetime.now()
    myStr      = tNowFname.strftime('%Y_%m_%d__%H_%M_%S') # strftime() = string format time: str='2018_07_24__18_18_40'
    cfg.fname  = '{0}/{1}_core_State.csv'.format(cfg.logfile_loc_core,myStr)
    cfg.fd     = open(cfg.fname,'a') # open for subsequent appending --> see all_vehicles.py | poll_state()
    logging.debug('\t{0}: logging to: {1}'.format(sys.argv[0],cfg.fname))
    # for logfile details, see all_vehicles.py | if (self.firstVehMsg==True)
else:
    cfg.fd=-1
    cfg.csv=-1
    logging.debug('{0}: no logging configured.'.format(sys.argv[0]))


# instantiate udp listener sockets on N udp ports
udp_io = core_udp_io(cfg, qVehCmd, debug) # core_udp_io() is in core_udp_io.py

# start listener thread for receiving state updates from all vehicles ( aggregator() is in core_udp_io.py )
t = threading.Thread( name='aggregator', target=udp_io.aggregator , args=(udp_io.sockets, cfg, e, eDataPollReq, qState, debug))
t.start()

# start sender thread for sending messages back to the vehicles ( send() is in core_udp_io.py )
t = threading.Thread( name='send', target=udp_io.send , args=(e, qVehCmd, debug))
t.start()

# instantiate an all_veh struct for computing vehicle-to-vehicle distances
all_veh = All_vehicles( cfg, debug ) # All_vehicles() is in all_vehicles.py

# start the poll_state() thread checking on the State vector periodically with all_veh.checkDistVel() ( poll_state() is in all_vehicles.py )
t = threading.Thread( name='poll_state', target=all_veh.poll_state , args=(e,eDataPollReq,qState,qVehCmd,cfg))
t.start()



try:
    time.sleep(3600*24*365)
except KeyboardInterrupt:
    logging.debug('caught KeyboardInterrupt, exiting!')
    e.set()


# all-stop and exit
e.set()
logging.debug('t={0}: {1} exiting.'.format(time.time(), sys.argv[0]))
