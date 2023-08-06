#!/usr/bin/env python3
#
# this is the built-in vehicle model or live-GPS-follower in the
# Mobility Virutal Environment (MoVE)
#
# this vehicle model is configured as a built-in simulation-only vehicle model
# or a live-GPS-follower by specifying zero or a non-zero port number for
# receiving live GPS inputs via udp/ip.
#
# example usage is in the code below or is printed to console upon execution:
#
#     ./main_veh_model.py
#
# main_srt_veh.py is a state machine that operates in runState=1,2,3,4, or 5.
# These runStates correspond to READY, SET, GO, PAUSE, and EXIT states.
#
# runState==1   is the READY state that exercises bi-directional network communications
#               but otherwise loops slowly, waiting, allowing you to get your other
#               hardware and software working for the test.
# runState==2   is the SET state that assigns initial conditions (ICs) in preparation
#               for runState 3. The model ticks quickly in time but sim time is at zero.
# runState==3   is the RUN state where a simple vehicle model is advanced in
#               soft-real-time with a Runge-Kutta 4th order fixed-step ODE integrator.
#               The RUN state advances simulated time at approximately the same rate
#               as wall-clock time without drift. An absolute reference is taken upon
#               entering runState==3 with the epoch time and the fixed-step integrator
#               always advances as fast as required to ensure each successive step
#               keeps the time difference between wall-clock and simulated time near zero.
#               A priority-based behavior scheduler is implemented using a multi-threaded
#               approach so wander(), periodicTurn(), periodicPitch(), stayInBounds(),
#               and avoid() behaviors all have independent triggers and commands.
#               The behavior scheduler selects the highest priority commands from the
#               set of active behaviors similar to Rodney Brooks' subsumption architecture.
# runState==4   is the PAUSE state. All network IO to and from core is still responsive
#               but the RK4 integrator is not called which stops simulation time advance.
# runState==5   is the ALL-EXIT command that triggers exit events in all behavior
#               threads and others, including, eventually, main().
#
# During runStates 2, 3 and 4 the model communicates with core at the communication
# interval, cInt. Setting cInt=0.1 assigns communication interval of 10Hz updates to core.
# The communication interval must be an integer multiple of the integrator stepsize, h.
#
# The general approach is:
# (a) receive runState commands via udp/ip from MoVE core
# (b) take many smaller integration steps within cInt to advance the vehicle state
#     forward in simulated time. Simulated time must advance faster than wall-clock time.
# (c) output time and states every cInt (communication interval) w.r.t. wall-clock time
# (d) once integration to tNew=t+cInt is complete, delay loop time (in wall-clock time)
#     by the time remaining within the communication interval, then write outputs and repeat.
#
#
# vehicle model change log:
# 28 Nov 2021       - added basic v2v functionality in vehicle model and default.cfg config file
# 14 Jun 2020       - added config file section for veh_details: name, type, subtype, ICs
# 28 May 2020       - added goToGate() behavior, v1.07
# 04 Jul 2019       - added followRoute() behavior to v1.05
# 13 Jan 2019       - added config file functionality in preparation for v1.00
# AugSep 2018       - achieved 5-state vehicle model running remotely in screen
#                     launched by parallel-ssh and monitored and managed by core
# 23 Jul 2018, v1.3 - integrated recv() and send_core() methods into VehicleModel class
#                     from ./parallel-ssh/processLauncher.py, processMonitor.py, and udpSender_ALL_EXIT.py
# 18 Jul 2018       - began developing processLauncher.py and myProc3.py with parallel-ssh package
# 18 Jul 2018, v1.2 - re-structured vehicle model into a MyVehicle class with very simple main loop
# 17 Jul 2018, v1.1 - achieved basic vehicle model ticking in soft-real-time with a kinematics
#                     motion model with rk4 integrator and logging to csv text file
# 07 Jul 2018,      - started priority-based behavior scheduler (Rodney Brooks, subsumption architecture)
# 27 May 2018, v1.0 - integrated soft-real-time with rk4 integrator and console output at cInt
# 03 Feb 2018         started with rk4 integrator solving ode's in python
#
# Marc Compere, comperem@gmail.com
# created : 03 Feb 2018
# modified: 02 Jul 2022
#
# --------------------------------------------------------------
# Copyright 2018 - 2022 Marc Compere
#
# This file is part of the Mobility Virtual Environment (MoVE).
# MoVE is open source software licensed under the GNU GPLv3.
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
# --------------------------------------------------------------

import os # for sys.path.append()
import sys
import time
from datetime import datetime
import numpy as np
import random
import logging
import threading # needed only for monitoring all threads exiting
from myVehicle import MyVehicle
from veh_udp_io import Veh_udp_io
from readConfigFile import readConfigFile # <-- note: readConfigFile module located here b/c of veh_udp_io.py and v2v.py (in myVehicle.py)
from route_init import route_init
from missionStateSequencer import MissionState
import code # drop into a python interpreter to debug using: code.interact(local=dict(globals(), **locals()))
from math import atan2 # for yaw initial conditions with a route; from 1st waypoint to 2nd
import utm
from ast import literal_eval # literal_eval() for converting strings into proper dicts
import pprint


n=len(sys.argv)
startUpRunStateGoal=1 # default runState on startup (keep this at 1 unless a headless startup script should launch into a running vehicle)
if n==7 and sys.argv[1]=='-f':
    startUpRunStateGoal = int(sys.argv[6]) # make this 3 for GO; this only gets set when run with an additional commnnd-line argument
    print('assigned auto-advance startUpRunStateGoal={}'.format(startUpRunStateGoal))

if n>=6 and sys.argv[1]=='-f':
    print('using scenario config file: {}'.format(sys.argv[2]))
    #cfgFile = '../scenario/default.cfg' # python's .ini format config file
    cfgFile =      sys.argv[2]
else:
    print('\n')
    print('\t usage  :    ./main_veh_model.py -f myScenario.cfg vid udp_port_gps name\n')
    print('\t example:    ./main_veh_model.py -f ../scenario/default.cfg 100   0  myModel     (for a simple built-in vehicle model)')
    print('\t example:    ./main_veh_model.py -f ../scenario/default.cfg 103 9103 speedracer  (put a live-GPS-follower listening for GPS on udp port 9103 (udp_port_base_gps+vid)\n')
    sys.exit(0)



if __name__ == "__main__":
    
    # these command line arguments are set by parallel-ssh upon execution and define
    # this vehicle process' unique identity and role as a builtin model or live-GPS-follower
    vid              =   int( sys.argv[3] ) # vid == vehicle identifier for this vehicle process, assigned by main_launch_veh_process.py
    
    # now we know which specific vehicle we are: vid
    cfg, veh_names_builtins, veh_names_live_gps = readConfigFile( cfgFile, vid ) # readConfigFile.py is in ../scenario but should be visible here via symbolic link
    cfg.udp_port_gps =   int( sys.argv[4] )       # udp port for live-GPS-inputs (if ==0, this is a built-in vehicle model, if >0, it's a GPS follower)
    cfg.name         =        sys.argv[5]         # this vehicle's name from command line; assigned by main_launch_veh_process.py
    cfg.runState     =                [1]         # initial runstate; valid range is: [1 5], *keep* as mutable *list* for class visibility
    cfg.runStatePrev =                [0]         # placed in cfg. for behavior accessibility; note: keep as mutable list for modification in the class
    
    
    # ------------------ vehicle init -------------------
    tStart = time.time()
    localLogFlag=0
    if cfg.log_level>=1:
        localLogFlag=1 # (0/1) write and append a .csv file every cInt?
    
    # this veh instance can be a dynamic model with behaviors, or a simpler live-GPS-follower - both interact with Core
    cfg.live_gps_follower = False
    if (cfg.udp_port_gps != 0): cfg.live_gps_follower=True
    
    hInt = 1 # (s) heartbeat interval during runState==1 (ready) only
    dt = hInt # (s) runState loop interval; when runState==1, heartbeat at 1Hz; for runStates=2,3,4, dt=cInt
    timeout = 0.5 # periodically loop to catch the graceful exit signal, e.is_set()
    startUp = True # for auto-advancing runState to 'GO' on an embedded device that wakes up and starts reporting
    
    
    
    # ------------------ route init -------------------
    cfg = route_init(cfg) # populate with cfg.routeCfg ; the route_init() function is in routes_functions.py in ./veh_model directory
    
    # init the vehicle object, launch v2v and behavior threads
    #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
    veh = MyVehicle(cfg, localLogFlag)
    # code note: to stop behaviors while debugging: veh.e.set(), udp_io.e.set()
    #veh.tf=10.0 # (s)
    
    veh.v2v.v2vPrtFlag=False #True # (True/False) print v2v console updates?
    
    # ---------- MissionState() init for simulated vehicles only -----------
    if (cfg.live_gps_follower == False):
        #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
        mState = MissionState(cfg,veh) # create the missionState object; start misson state sequencer thread    
        
    # ----------------- route origin adjustment ----------------
    # if there's a route and if it was originally specified in lat/lon pairs,
    # then it was converted to utm coordinates which means it's probably a series of giant numbers
    # --> it needs the vehicle origin subtracted which is pulled from the scenario config file
    #
    # if the route was specified as a simple set of XY coordinates, then no origin adjustment is necessary
    #
    if (cfg.behaviorCfg['followRoute']>0) and hasattr(cfg.route,'originalUnits') and cfg.route.originalUnits == 'decimal_degrees':
        # - adjust (X,Y) from route to be w.r.t. the origin in the config file
        # - offset route (X,Y) coords here to keep route file a stand-alone test script (so it doesn't have to read the scenario config file)
        for i in range(cfg.route.N):
            cfg.route.X[i] = cfg.route.X[i] - veh.X_origin
            cfg.route.Y[i] = cfg.route.Y[i] - veh.Y_origin
            logging.debug('\torigin-adjusted waypoint i={0:<4}, (X,Y,Z) = ( {1:8.3f}, {2:8.3f}, {3:8.3f} )(m),  dist={4:8.1f}(m),   speed={5:6.1f}(m/s)'.format( i,cfg.route.X[i],cfg.route.Y[i],cfg.route.Z[i],cfg.route.S[i],cfg.route.spd_mps[i] ))
    
    # ------------------ udp i/o init -------------------
    # this launches 2 processes: recv_core, udp_console_update
    udp_io = Veh_udp_io(cfg, veh) # udp_io has visibility to this sinble veh object and behaviors
    #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
    # code note: to stop behaviors while debugging: veh.e.set(), udp_io.e.set()
    
    # runState definitions:
    #   runState == 1 --> ready : veh model process running and sending udp heartneats at 1Hz
    #   runState == 2 --> set   : assign initial conditions on veh, payload, fuel, battery; send udp out at cInt (perhaps 10Hz)
    #   runState == 3 --> GO!   : advance the vehicle model in soft-real-time; allow vehicle mobility
    #   runState == 4 --> pause : pause vehicle dynamics; send output messages at cInt (faster than 1Hz)
    #   runState == 5 --> exit  : stop veh model process, stop logging, all threads exit
    #
    # runState processing loop is around the vehicle model soft-real-time and integration loops
    try:
        while udp_io.e.is_set() is False: # flag to exit
            
            udp_io.eRunState.wait(dt) # nominal loop rate is either hInt or cInt (heartbeat or communication intervals)
            
            # change runState when a queue indicates a new udp runstate message has been received
            if udp_io.eRunState.is_set() is True:
                payload = udp_io.qRunState.get(block=True,timeout=timeout) # Queue.get(block=True, timeout=None), timeout is for catching the thread exit signal, e.is_set()
                veh.runStatePrev = veh.runState[0] # capture last runState
                veh.runState[0] = payload['runStateCmd'] # assign runState from runStateCmd just received; note: this is the only way runState can change.. except (veh.t<veh.tf) below and during pause/resume, all of which is in main_veh_model.py; all others read-only runState
                logging.debug('')
                logging.debug('[{0}]: assigning veh.runState={1} or {2}, formerly={3}'.format( datetime.now().strftime('%c') ,veh.runState[0], veh.runStateDesc[veh.runState[0]], veh.runStatePrev))
                logging.debug('')
                udp_io.eRunState.clear()
                #veh.deqGoToPoint.append( [ runState, runStatePrev ] ) # inform goToPoint() behavior (once) that runState just changed
                
                # note: if queue times out, add try-except clause with continue (but it should never timeout)
            
            # this if-statement is for a vehicle model launching automatically on a device (like a Raspberry Pi) that wakes up and starts reporting
            if (startUp==True) and (veh.runState[0]<startUpRunStateGoal):
                veh.runStatePrev = veh.runState[0] # capture last runState
                veh.runState[0] = veh.runState[0] + 1
                logging.debug('auto-advanced runState by +1: runStatePrev={0}, runState={1}'.format(veh.runStatePrev,veh.runState[0]))
                #veh.deqGoToPoint.append( [ runState, runStatePrev ] ) # inform goToPoint() behavior that runState just changed
                # if this gets to runState==GO, then stop auto-advance (assumption is we want this particular model to startup and go right to runState==3 "GO"
                if veh.runState[0]>=3:
                    startUp=False
            
            # ----------------------------------------------------------------------
            #                              parse runState
            # ----------------------------------------------------------------------
            if veh.runState[0] == 1: # "ready" - send udp messages out at 1Hz
                logging.debug('[{0}]: ========================= READY =========================, dt={1}(s)'.format( datetime.now().strftime('%c') ,dt))
                if dt != hInt:
                    dt=hInt # set loop interval to hInt, the heartbeat interval (say, 1Hz)
                    logging.debug('[{0}]: assigning ready heartbeat interval, hInt={1}(s)'.format( datetime.now().strftime('%c') ,dt))
                if cfg.live_gps_follower==True:
                    veh.gather_live_gps_inputs() # get latest UTM coordinates from GPS lat/lon; cannot block; veh.tick() controls loop rate with srt()
                else:
                    veh.gather_behavior_inputs() # update v2vState and veh model behavior inputs; cannot block
                veh.gather_outputs( udp_io.recvCnt, udp_io.sendCnt, udp_io.errorCnt ) # update veh.vehData
                udp_io.send_core( veh.vehData ) # send MoVE core a vehicle state update
                veh.veh_console_update() # local console output + logging to /tmp
            
            
            if veh.runState[0]==2: # "set" or reset
                # assign initial conditions for this (the vid'th) vehicle
                logging.debug('[{0}]: ========================= SET =========================, dt={1}(s)'.format( datetime.now().strftime('%c') ,dt))
                if dt != cfg.cInt:
                    dt=cfg.cInt # set loop interval to cInt, the communication interval (say, 10Hz)
                    logging.debug('[{0}]: assigning veh communication interval, cInt={1}(s)'.format( datetime.now().strftime('%c') ,dt))
                
                if veh.t != veh.t0:
                    # assign nominal ICs as a grid-pattern inside the bounding box geometry
                    # todo: get ICs assigned in a config file for core and have core send over ICs at runStateCmd=='set'
                    kth_vehicle = cfg.vid-cfg.vid_base # this is the k'th vehicle, zero-based
                    Xic = veh.geom.Xmin # start at min X and min Y corner
                    Yic = veh.geom.Ymin
                    Zic = cfg.IC_elev # (m)
                    psi_ic = 0.0 # (rad)
                    if cfg.debug>1: print('kth_vehicle={}'.format(kth_vehicle))
                    if cfg.debug>1: print('veh.geom.Xmin={0}, veh.geom.Xmax={1}'.format(veh.geom.Xmin, veh.geom.Xmax))
                    if cfg.debug>1: print('veh.geom.Ymin={0}, veh.geom.Ymax={1}'.format(veh.geom.Ymin, veh.geom.Ymax))
                    
                    #IC_sel=1 # 1-> straight down the X-axis; 2->square pattern for N vehicles, 3->collision scenario for 2 vehicles
                    
                    # if there's a route specified, it takes priority (for now, 'goTo' and 'startAt' are identical, meaning 'startAt')
                    if hasattr(cfg,'routeCfg') and ('startOption' in cfg.routeCfg): # 2nd term is evaluated only if first is True
                        #todo: implement 'goTo' option separately from 'startAt'
                        #      currently, they're both ideintical (meaning startAt)
                        cfg.IC_sel=-1 # invalidate all other IC_sel options below
                        # place vehicle at first waypoint and orient it toward the second
                        cfg.route.i = cfg.routeCfg['startingWaypoint'] # current waypoint is startingWaypoint (which is 1-based)
                        
                        # initial position is first waypoint's XY pair
                        Xic = cfg.route.X[ cfg.route.i-1 ] # (m) XYZ in cartesian terrain-fixed, or inertial frame, +X-axis is to the East, or right on the page
                        Yic = cfg.route.Y[ cfg.route.i-1 ] # (m) note: the -1 is b/c python is 0-based (waypoint #1 is element zero)
                        Zic = cfg.route.Z[ cfg.route.i-1 ] # (m)
                        
                        dX = cfg.route.X[ cfg.route.i ] - cfg.route.X[ cfg.route.i-1 ] # (m) X-component of vector pointing from 1st waypoint to 2nd waypoint (tip-tail)
                        dY = cfg.route.Y[ cfg.route.i ] - cfg.route.Y[ cfg.route.i-1 ] # (m)
                        psi_ic = atan2( dY , dX ) # (rad) 4-quadrant arc-tangent provides orientation from 1st waypoint to 2nd waypoint
                        logging.debug('assigning ICs to first waypoint: (X,Y,Z) = ( {0:8.3f}, {1:8.3f}, {2:8.3f} )(m),  psi_ic={3:8.1f}(rad)'.format( Xic,Yic,Zic, psi_ic ))
                    
                    veh_IC_spacing = (10*veh.L_char) # used for deltaX and deltaY
                    i=0 # X-spacing counter
                    j=0 # Y-spacing counter
                    if cfg.IC_sel == 1: # straight down the X-axis, errbody line up down da X-axis
                        for k in range( kth_vehicle+1 ):
                            Xic    = 0.0 + k*veh_IC_spacing
                            psi_ic = cfg.randFlag*random.uniform(-3.14,+3.14) # (rad) ...but face different directions if randFlag==1
                        Yic = 0.0 # (m)
                        
                    
                    if cfg.IC_sel == 2: # grid pattern within geom extents
                        for k in range( kth_vehicle+1 ):
                            Xic = veh.geom.Xmin + i*veh_IC_spacing
                            if Xic > veh.geom.Xmax:
                                i = 0  # re-zero X spacing counter (go back to zero along X-axis)
                                j += 1 # increase Y counter        (start 1 row higher on Y-axis)
                                Xic = veh.geom.Xmin
                            Yic = veh.geom.Ymin + j*veh_IC_spacing
                            i+=1
                        
                        if cfg.debug>1: print('i={0}, j={1}, (Xic,Yic)=({2},{3})'.format(i,j,Xic,Yic))
                        #Zic = cfg.randFlag*random.uniform(10,100) # (m) initial height
                        Zic    = cfg.IC_elev # (m) initial height
                        psi_ic = cfg.randFlag*random.uniform(-3.14,+3.14)
                    
                    if cfg.IC_sel == 3: # side-swipe collision avoidance for N=2
                        Zic = cfg.IC_elev
                        if cfg.vid==101: # 2-veh IC test for collision avoidance
                            Xic    = 0.0
                            Yic    = 20.0
                            psi_ic = -0.4636
                        else:
                            Xic    = 0.0
                            Yic    = 0.0
                            psi_ic = 0.0
                            
                    if cfg.IC_sel == 4: # side-swipe collision avoidance for N=2
                        Zic = cfg.IC_elev
                        if cfg.vid==101: # 2-veh IC test for collision avoidance
                            Xic    = -30.0
                            Yic    =   0.0
                            psi_ic =   0.0
                        else:
                            Xic    = 0.0
                            Yic    = 0.0
                            psi_ic = 0.0
                    
                    if cfg.IC_sel == 5: # config file found IC_latlon entry (see readConfigFile.py | veh_details[] section)
                        Xic     = cfg.Xic        # (m) from config file
                        Yic     = cfg.Yic        # (m) from config file
                        Zic     = cfg.IC_elev    # (m) from config file
                        psi_ic  = cfg.IC_yaw_rad # (m) from config file
                    
                    if cfg.IC_sel == 6: # config file found IC_latlon entry (see readConfigFile.py | veh_details[] section)
                        Xic     = random.uniform( cfg.boundary_Xmin , cfg.boundary_Xmax )
                        Yic     = random.uniform( cfg.boundary_Ymin , cfg.boundary_Ymax )
                        Zic     = 0.0 # (m) above sea level
                        psi_ic  = random.uniform( 0.0 , 2*3.14 ) # (rad) orientation initial condition
                    
                    veh.x = np.array([Xic, Yic, Zic, psi_ic]) # ode IC's [ X, Y, Z, psi ]
                    veh.t = veh.t0
                    logging.debug('[{0}]: assigning veh initial conditions, t={1}(s), pos={2}'.format( datetime.now().strftime('%c') ,veh.t,veh.x))
                    
                if cfg.live_gps_follower==True:
                    veh.gather_live_gps_inputs() # get latest UTM coordinates from GPS lat/lon; cannot block; veh.tick() controls loop rate with srt()
                else:
                    veh.gather_behavior_inputs() # update v2vState and veh model behavior inputs; cannot block
                veh.gather_outputs( udp_io.recvCnt, udp_io.sendCnt, udp_io.errorCnt ) # update veh.vehData
                udp_io.send_core( veh.vehData ) # send MoVE core a vehicle state update
                veh.veh_console_update() # local console output + logging to /tmp
                
            if veh.runState[0]==3: # "go!"
                # tick the model; send update messages at cInt
                # =========================================
                # tick the model in soft-real-time
                logging.debug('[{0}]: entering ========================= GO =========================, dt={1}(s)'.format( datetime.now().strftime('%c') ,dt))
                veh.elapsedErr = 0.0      # zero-out internal soft-real-time variables
                veh.elapsedErrAccum = 0.0
                if veh.runStatePrev==2: # came from 'set'
                    veh.tStart = time.time() # start time is now time
                    veh.tNow   = veh.tStart
                    veh.srtCnt = 0 # start from veh.t=0 again
                if veh.runStatePrev==4: # came from 'pause'
                    veh.tStart = time.time() - veh.t # restart at now minus how long it previously ran so resumes from same time as paused
                    veh.tNow   = veh.tStart          # set tNow=tStart to make elapsedErr=0.0 in srt.py
                
                while ( veh.t<veh.tf and veh.runState[0]==3):
                    
                    #if udp_io.e.is_set()         is True: break  # are we all exiting?
                    if udp_io.eRunState.is_set() is True: break  # exit while-loop if udp_io received a runState command
                    
                    if cfg.live_gps_follower==True:
                        veh.gather_live_gps_inputs() # get latest UTM coordinates from GPS lat/lon; cannot block; veh.tick() controls loop rate with srt()
                    else:
                        veh.gather_behavior_inputs() # update v2vState and veh model behavior inputs from prioritize(); cannot block; veh.tick() controls loop rate with srt()
                    
                    veh.tick() # advance vehicle model states in time; srt() regulates loop rate to cInt
                    
                    veh.gather_outputs( udp_io.recvCnt, udp_io.sendCnt, udp_io.errorCnt ) # update veh.vehData in preparation for udp output message
                    
                    udp_io.send_core( veh.vehData ) # send MoVE core a vehicle state update
                    
                    veh.veh_console_update() # local console output + logging to /tmp
                
                if (veh.t >= veh.tf):
                    logging.debug('[{0}]: reached t>=tFinal, exiting. veh.runState={1}'.format( datetime.now().strftime('%c') ,veh.runState[0]))
                    veh.runState[0] = 2 # all done. continue running but go back to 'ready'
                # =========================================
            
            if veh.runState[0]==4: # "pause"
                logging.debug('[{0}]: entering ========================= PAUSE =========================, dt={1}(s)'.format( datetime.now().strftime('%c') ,dt))
                # pause the motion; continue sending update messages at cInt
                if dt != cfg.cInt:
                    dt=cfg.cInt # set loop interval to cInt, the communication interval (say, 10Hz)
                    logging.debug('[{0}]: assigning veh communication interval, cInt={1}(s)'.format( datetime.now().strftime('%c') ,dt))
                
                if cfg.live_gps_follower==True:
                    veh.gather_live_gps_inputs() # get latest UTM coordinates from GPS lat/lon; cannot block; veh.tick() controls loop rate with srt()
                else:
                    veh.gather_behavior_inputs() # update v2vState and veh model behavior inputs from prioritize(); cannot block; veh.tick() controls loop rate with srt()
                # skip tick() while paused
                veh.gather_outputs( udp_io.recvCnt, udp_io.sendCnt, udp_io.errorCnt ) # update veh.vehData
                udp_io.send_core( veh.vehData ) # send MoVE core a vehicle state update
                veh.veh_console_update() # local console output + logging to /tmp
                veh.runStatePrev = veh.runState[0]
                
            if veh.runState[0]==5: # "exit"
                logging.debug('exiting all threads')
                udp_io.e.set() # exit udp_io threads
                veh.exit()     # exit myVehicle, v2v, and behavior threads
    
    except KeyboardInterrupt:
        logging.debug('caught KeyboardInterrupt, exiting.')
        udp_io.e.set() # tell udp_io threads to exit
        veh.exit()     # exit myVehicle, v2v, and behavior threads
    
    
    # monitoring the thread exit process
    main_thread = threading.main_thread()
    while len(threading.enumerate())>1:
        for t in threading.enumerate():
            if t is main_thread:
                continue
            logging.debug('{0} threads still remaining, including: {1}'.format( len(threading.enumerate()), t.getName() ))
        
        time.sleep(1)
    
    logging.debug('[{0}]: exiting veh model, veh.runState={1}'.format( datetime.now().strftime('%c') ,veh.runState[0]))








