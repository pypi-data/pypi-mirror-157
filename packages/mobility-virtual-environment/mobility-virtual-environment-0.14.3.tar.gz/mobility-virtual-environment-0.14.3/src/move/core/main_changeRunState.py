#!/usr/bin/env python3
#
# send a runState command message to N running vehicle models
#
# usage and example are below when len(sys.argv)<5
#
# Marc Compere, comperem@gmail.com
# created : 21 Feb 2017
# modified: 13 Jan 2019
#
# ---
# Copyright 2018, 2019 Marc Compere
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
import msgpack # fast serialize/deserialize of complete python data structures
import socket
sys.path.append(os.path.relpath("../scenario")) # find ../scenario/readConfigFile.py w/o (a) being a package or (b) using linux file system symbolic link
from readConfigFile import readConfigFile

n=len(sys.argv)
if n==4 and sys.argv[1]=='-f':
    print('reading scenario config file: {}'.format(sys.argv[2]))
    cfgFile =      sys.argv[2]
    myCmd   = int( sys.argv[3] )
    #cfgFile = '../scenario/default.cfg' # python's .ini format config file
    cfg, veh_names_builtins, veh_names_live_gps = readConfigFile( cfgFile )
else:
    print('\n')
    print('\t usage  :    ./main_changeRunState.py -f myScenario.cfg runStateCmd\n')
    print('\t example:    ./main_changeRunState.py -f ../scenario/default.cfg 5\n')
    sys.exit(0)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # udp/ip socket
nVehTot = cfg.nVeh_builtin + cfg.nVeh_live_gps # + nVeh_custom

for i in range(nVehTot):
    vid = cfg.vid_base + i
    udp_port_in = vid + cfg.udp_port_base + cfg.udp_port_offset # 'in' is w.r.t. to the vehicle model process (it listens on 'in' port)
    print("sending runStateCmd message to vid=[{0}] at [{1}:{2}]... ".format(vid,cfg.veh_host_ip,udp_port_in), end='')

    #veh_IC_spacing = (5*veh.L_char)
    # nX = (veh.geom.Xmax - veh.geom.Xmin) / veh_IC_spacing # assuming all vehicles are identical
    # nY = (veh.geom.Ymax - veh.geom.Ymin) / veh_IC_spacing
    # for i in range(nX):
    #     Xic = veh.geom.Xmin + (cfg.vid-100)*veh_IC_spacing
    #     for j in range(nY):
    #         Yic = veh.geom.Ymin + (cfg.vid-100)*veh_IC_spacing
    #         psi_ic = random.uniform(-3.14,+3.14)

    # construct a command message dictionary
    payload = [0]*6
    payload[1] = { 'runStateCmd': 1 } # ready?
    payload[2] = { 'runStateCmd': 2 , 'x0': [ 1, 2, 3, 0.4] } # set ICs - runState 2 is the only payload with additional data
    payload[3] = { 'runStateCmd': 3 } # go!
    payload[4] = { 'runStateCmd': 4 } # pause
    payload[5] = { 'runStateCmd': 5 } # all threads exit

    cmd = { 'vid':vid, 'type': 'runStateCmd', 'payload': payload[myCmd] } # this is the command for the os process to exit
    msgpackedCmd = msgpack.packb(cmd) # fast serialize for entire python data structure w/o detailing each field
    nBytes = sock.sendto(msgpackedCmd, (cfg.veh_host_ip,udp_port_in) )
    print('done. sent {0} bytes to vid=[{1}], cmd={2}'.format(nBytes,vid,cmd) )

    time.sleep(0.2) # this reduces peak cpu load for changing many vehicle processes into runState==3 (when the numba @jit causes tick() compilation in myVehicle.py)



print('exiting.')
