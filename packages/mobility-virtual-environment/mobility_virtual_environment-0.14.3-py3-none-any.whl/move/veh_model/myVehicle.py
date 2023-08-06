# a class for initializing and advancing an ODE-based vehicle model in time
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

import time
import sys
import threading
import queue
import numpy as np
#from scipy import io
from datetime import datetime # filename string
from math import sqrt,floor,isinf
from collections import deque
import logging
import utm


from srt import srt # pull in srt() from srt.py in same dir
from behaviors import Behaviors # from behavior_scheduler.py in same dir
from veh_util import rk4_single_step, f, myRem, update_window, simple_moving_average # pull in fcns from veh_util.py in same dir
import code # drop into a python interpreter to debug using: code.interact(local=dict(globals(), **locals()))
from v2v import V2V # bring in vehicle-to-vehicle messaging class

#from numba import jit # for making tick() faster

class Geom:
    """ a geometry description for the stayInBounds() behavior """
    def __init__(self):
        self.type = 'stayIn' # options: stayIn or stayOut
        # stay in this square
        self.Xmax = +1.0 # (m) UTM coordinates w.r.t. origin
        self.Xmin = -1.0 # (m)
        self.Ymax = +1.0 # (m)
        self.Ymin = -1.0 # (m)
        self.cg_X = (self.Xmax + self.Xmin)/2.0 # (m)
        self.cg_Y = (self.Ymax + self.Ymin)/2.0 # (m)

class MyVehicle:
    """A class defining a single MoVE built-in vehicle with behaviors or a simpler live-GPS-follower with no behaviors"""
    
    # =======================================================================================
    #                                      init()
    # =======================================================================================
    # initialize simulation parameters, initial conditions, behaviors, and logging
    def __init__(self,cfg,localLogFlag):
        
        logging.debug("communication interval for console output = [ {0:0.6f} ](sec)".format(cfg.cInt) )
        
        clkRes = time.get_clock_info('time').resolution
        logging.debug("OS                     [ {0} \t]"          .format(sys.platform) )
        logging.debug("clock resolution       [ {0:0.10f} \t](s)" .format(clkRes) )
        logging.debug("veh model ODE stepsize [ {0:0.6f} \t](s)"  .format(cfg.h) )
        logging.debug("communication interval [ {0:0.6f} \t](s)"  .format(cfg.cInt) )
        
        self.vid                 = cfg.vid     # vid == unique vehicle identifier (assigned in main_launch_veh_process.py)
        self.name                = cfg.name    # informal name for this vehicle instance (comes from config file via main_launch_veh_process.py)
        self.vehType             = cfg.vehType
        self.vehSubType          = cfg.vehSubType
        self.behaviorCfg         = cfg.behaviorCfg
        
        # ---- srt() variables -----
        self.srtCnt=0
        self.srtMargin=0.0
        self.srtOutput = 0 # (0/1/2) 0->none, 1-> some, 2->lots    (keep at none and use debug instead)
        self.elapsedErr=0.0
        self.elapsedErrAccum=0.0
        self.tStart=time.time() # seconds since Jan 1, 1970 00:00:00; a massive number, e.g. 1517836676.8555398
        self.tNow = self.tStart
        logging.debug("Start: {0}, tStart: {1}(s)".format(time.ctime(),self.tStart) )
        
        self.srtMarginAvg=0
        self.srtMarginHistory = deque([]) # double-ended que keeps history for a simple moving average filter
        self.elapsedErrAvg=0
        self.elapsedErrHistory = deque([])
        self.srtFilterWindowN = 50 # set to about 5/self.cINt
        
        self.e     = threading.Event() # for signaling exit to all threads simultaneously (veh, beh, and v2v objects)
        
        # ====== start vehicle-to-vehicle messaging subsystem for simulated vehicles only ======
        self.v2vState={} # init empty v2vState for veh class only (v2v class inits it's own v2vState)
        self.v2v = V2V(self.vid,cfg,self.e) # start vehicle-to-vehicle communications threads
        
        
        # BEGIN: ================== vehicle model setup ===================
        # setup time, states, integration stepsize and state ICs
        self.t0 = 0.0 # t0 always stays 0.0
        self.tf = float('inf') # (s) final time of 'inf' means simulate indefinitely
        #self.tf=2.0 # (s)
        #dt=tf-t0
        # set nominal initial conditions; new ICs can come in via runState==2 message
        self.x0 = np.array([0.0, 0.0, cfg.IC_elev, 0.0]) # ode IC's [ X, Y, Z, psi ]
        self.u = [0.0, 0.0, 0.0, 0.0] # 4 inputs, [steer, v_x, pitch, v_z] in [(rad), (m/s), (rad), (m/s)]
        self.xdot = f( self.t0, self.x0, self.u ) # xdot = [ v_XY[0], v_XY[1], v_Z, psiDot] rates in global SAE XYZ
        
        class myClass:
            pass # simple class for holding positions in XYZ UTM coordinates in (m) and also lat-lon-elev in decimal degrees
        self.pos = myClass() # pos and vel classes are used like C style structs to hold named data values
        self.pos.X     = 0.0 # (m) X-position in inertial XYZ frame, origin is at this UTM zone's origin
        self.pos.Y     = 0.0 # (m) Y-position in XYZ
        self.pos.Z     = 0.0 # (m) Z-position in XYZ (or elevation when used with lat/lon)
        #self.pos.phi   = 0.0 # (rad) roll angle about SAE +x axis in body-fixed forward direction, out the vehicle front or nose
        #self.pos.theta = 0.0 # (rad) pitch angle about SAE +y axis out passenger side window
        self.pos.psi   = 0.0 # (rad) yaw angle about SAE +z axis, positive is down, out the body-fixed floor
        self.pos.hdg   = 0.0 # (rad) heading, course-over-ground (identical to psi for simple kinematic vehicle model; different for live-gps-follower when course is available)
        self.pos.lat   = 0.0 # (dec deg) live-GPS-follower converts to UTM to get X,Y; built-in veh model converts XY to lat/lon
        self.pos.lon   = 0.0 # (dec deg) both have both: both veh types (built-in sim vs. live-GPS-follower) have both XYZ and lat/lon/elev position units
        
        self.vel = myClass() # class for holding vel data
        self.vel.Xd       = 0.0 # (m/s) X-rate in inertial XYZ frame
        self.vel.Yd       = 0.0 # (m/s) Y-rate in XYZ
        self.vel.Zd       = 0.0 # (m/s) Z-rate in XYZ
        #self.pos.phiDot   = 0.0 # (rad/s) roll-rate about SAE +x axis in body-fixed forward direction, out the vehicle front or nose
        #self.pos.thetaDot = 0.0 # (rad/s) pitch-rate about SAE +y axis out passenger side window
        self.vel.psiDot   = 0.0 # (rad/s) heading rate, psi-dot
        self.vel.spd_mps  = 0.0    # (m/s) speed from GPS, converted from knots to m/s (use with pos.psi which is true course over ground for live-GPS-follower)
        
        self.detectMsg = myClass() # create a simple detection-and-reporting data structure to store last-seen time and coordinates for a vehicle or object in a search-and-report behavior
        self.detectMsg.objId       = 0 # whatever you're looking for (e.g. a specific vid)
        self.detectMsg.lastSeen    = 0 # (s) timestamp from last-seen detection
        self.detectMsg.lastLoc_X   = 0 # (m) location from last-seem detection
        self.detectMsg.lastLoc_Y   = 0 # (m)
        self.detectMsg.lastLoc_Z   = 0 # (m)
        self.detectMsg.lastLoc_lat = 0 # (m)
        self.detectMsg.lastLoc_lon = 0 # (m)
        
        self.live_gps_follower = cfg.live_gps_follower
        self.X_origin    = cfg.X_origin # (m)
        self.Y_origin    = cfg.Y_origin # (m)
        self.UTM_zone    = cfg.UTM_zone
        self.UTM_latBand = cfg.UTM_latBand
        
        logging.debug('Origin in lat/lon coords: (lat_origin,lon_origin)=( {0} , {1} ) (decimal degrees)'.format( cfg.lat_origin , cfg.lon_origin ))
        logging.debug('Origin in UTM XYZ coords: ( X_origin , Y_origin )=( {0} , {1} ) (m) in UTM zone={2}, UTM latBand={3}'.format( self.X_origin , self.Y_origin, self.UTM_zone, self.UTM_latBand ))
        
        self.t=-1 # uninitialized time; self.t is set when runState==2
        self.x=self.x0
        
        self.randFlag=cfg.randFlag   # (0/1) use random numbers? (flag to turn all on or off)
        self.h=cfg.h       # numerical integration stepsize, typically 10ms, or 5ms or 1ms. Tune to suit vehicle model dynamics and cpu load
        self.cInt=cfg.cInt # communication interval for veh model inputs and outputs - not the same as integration stepsize
        self.n=round( floor( self.cInt/self.h ) ,14 ) # take n steps of a fixed-step Runge-Kutta 4th order integrator every cInt
        self.localLogFlag=localLogFlag # logfile on /tmp wherever the i'th model is running?
        self.vehData = {} # see gather_outputs() for vehicle data updates every cInt
        
        self.L_char = cfg.L_char # (m) characteristic vehicle length; from config file
        self.v_max  = cfg.v_max # (m/s) nominal vehicle max speed
        self.integCnt=0
        self.debug=cfg.debug # (0/1/2/3) 0->none, 1->some, 2->more, 3->lots PRIORITIZE console output
        self.runState        = cfg.runState # reference to runState from main loop; recall: this is a *mutable* list for class and main visibility
        self.runStatePrev    = cfg.runStatePrev
        self.runStateDesc    = ['']*6 # runStates are 1-based text strings; entry [0] unusused
        self.runStateDesc[1] = '=== READY ==='
        self.runStateDesc[2] = '===  SET  ==='
        self.runStateDesc[3] = '===  GO   ==='
        self.runStateDesc[4] = '=== PAUSE ==='
        self.runStateDesc[5] = '=== EXIT  ==='
        
        # default mission command metrics all vehicles send to all others in v2v messaging; these are sent with or without any config file [missionCommands]
        self.missionState         = -1      # missionState is defined in the config file and is an integer
        self.missionAction        = 'none'  # missionAction is the missionCommand action associated with this missionState
        self.missionPctComplete   = 0.0     # fractional percent complete on interval, [0 1]
        self.missionProgress      = -1      # missionProgress is a floating point number equal to: missionState + pctComplete. each action is completed when missionProgress=missionState+1 (or when pctComplete=1.0)
        self.missionLastCmdTime   = datetime.now().strftime('%c') # last time a command was changed
        self.missionStatus        = 'readyWait'
        self.missionCounter       = 1  # counter for every state change; note: this will be different from missionCommands list if there are any 'goToMissionState' loop-arounds
        # END: ================== vehicle model setup ===================
        
        
        # BEGIN: ============= vehicle-to-vehicle communication setup ==============
        
        # END  : ============= vehicle-to-vehicle communication setup ==============
        
        # ============== BEGIN: Behavior scheduler init ==============
        self.geom  = Geom() # the vehicle gets it's boundaries from the config file (and stayInBounds() behavior must be enabled)
        self.geom.Xmax = cfg.boundary_Xmax
        self.geom.Xmin = cfg.boundary_Xmin
        self.geom.Ymax = cfg.boundary_Ymax
        self.geom.Ymin = cfg.boundary_Ymin
        
        
        if (self.behaviorCfg['followRoute']>0): # is followRoute() enabled?
            if hasattr(cfg,'route'):
                self.route = cfg.route
                self.route.spd_mps_i = 0 # need these three route attributes before ICs are set, during runState==1
                self.route.i         = -1 # this gets re-assigned in main_veh_model.py during 'set' when initial conditions are applied
                #self.route.lap       = -1 # this is already set in route_init.py which is called before myVehicle which calls behaviors (here)
            else:
                print("error: followRoute() behavior enabled, but no route defined, exiting")
                exit(-1) # if these behaviors are turned on (globally or individually) there must be gates defined --> see config file
        
        if (self.behaviorCfg['goToPoint']>0): # is goToPoint() enabled?
            if hasattr(cfg,'points'):
                self.points = cfg.points
            else:
                print("error: goToPoint() behavior enabled, but no points defined, exiting")
                exit(-1) # if goToPoint() is enabled there must be points defined --> see config file)
        
        if (self.behaviorCfg['goToGate']>0): # is goToGate() enabled?
            if hasattr(cfg,'gates'):
                self.gates = cfg.gates
            else:
                print("error: goToGate() behavior enabled, but no gates defined, exiting")
                exit(-1) # if goToGate() is enabled there must be gates defined --> see config file)
        
        # if no routes or gates, populate with -1's
        #if (self.behaviorCfg['followRoute']==0) and (self.behaviorCfg['goToGate']==0): # behaviorCfg is a dictionary of behavior priorities; zero means disabled, or turned off
        self.waypoint_status = {'waypoint':-1, 'lap':-1, 'spd_mps':-1}
        
        
        self.gps_unixTime =  0 # only updates when live_gps_follower==True
        self.batt_stat    = -1 # all vehicles report batt_stat within sensorData (simulated and live-gps-followers)
        self.sensorData   = {} # ensure all vehicles have a sensorData dictionary (simulated vehicles and live-gps-followers)
        
        if self.live_gps_follower==True:
            # live GPS follower process has no behaviors, no command queue, and no avoidance queue
            self.bIdCmd       = self.vid            # vid assignment currently unused except to indicate not-uninitialized
            self.bIdName      = 'live_gps_follower' # live-GPS-follower
            self.bIdProgress  = -1                  # live-GPS-follower progress has little meaning but needs a number
            self.qLiveGps     = queue.Queue()       # que for messaging from udp_io.recv_gps() and the gather_live_gps_inputs() method
        else:
            # vehicle model (not a live GPS follower)
            # note: Queue's are a thread-safe FIFO way of passing messages
            self.qCmdVeh   = queue.Queue() # queue for prioritize() to send winning commands to the vehicle
            self.qBehInfo  = queue.Queue() # queue for prioritize() to send behavior updates; all messages are sent in parity with with self.qCmdVeh()
            self.qVeh2beh  = queue.Queue() # queue to tell all behaviors the current and previous runState (used to detect when ICs are set)
            self.qAvoid    = queue.Queue() # que for messaging from udp_io.recv() and the avoid() behavior
            self.qDetect   = queue.Queue() # que for detectAndReport() behavior
            self.qRoute    = queue.Queue() # que for followRoute() behavior to convey current waypoint and lap to core
            self.qGate     = queue.Queue() # que for goToGate() behavior to convey current gate num and lap to core
            self.qPoint    = queue.Queue() # que for goToPoint() behavior to convey current point num and lap to core
            
            # mission-enabled behaviors must decide who they listen to: (a) 'nextPoint' or (b) 'nextGate' or (c) missionStateSequencer() ?
            self.usingMissionCommands  = cfg.usingMissionCommands # this is assigned in readConfigFile.py, if (vid>0)
            #self.deqGoToPoint         = deque(maxlen=1)   # for runState to be transmitted to goToPoint() behavior
            #self.deqMissionCmdSeq     = deque(maxlen=1)   # for transmitting mission actions to mission-enabled behavior threads
            self.goToPointCmd          = deque(maxlen=1)   # for missionStateSequencer() to send points to goToPoint() behavior
            self.goToPointDone         = threading.Event() # for goToPoint() behavior to tell missionStateSequencer() it reached the point
            
            self.bIdCmd      = -1            # commanded behavior, uninitialized
            self.bIdName     = 'no behavior' # current behavior name
            self.bIdProgress = 0.0           # current behavior progress, [0 1]
            
            self.beh = Behaviors( cfg, self.qCmdVeh, self.qBehInfo, self.e, self.debug ) # instantiate a Behaviors() object
            
            # behaviors are launched in startBehaviors(), which is given a myVehicle object
            # so avoid(), detect(), and followRoute() behaviors can communicate to and from Core
            self.beh.startBehaviors( self ) # a myVehicle object is passed in
        #                                                            #
        # =============== END: Behavior scheduler init ===============
        
        # open local logfile on /tmp where process runs
        logging.debug('vehicle localLogFlag={0}'.format(self.localLogFlag))
        tNowFname=datetime.now()
        myStr=tNowFname.strftime('%Y_%m_%d__%H_%M_%S') # strftime() = string format time: str='2018_07_24__18_18_40'
        self.fname_log_veh_prefix='{0}/{1}_vid_{2}'.format(cfg.logfile_loc_veh,myStr,self.vid) # everything except the .csv
        if (self.localLogFlag>0):
            self.fname_log_veh='{0}.csv'.format(self.fname_log_veh_prefix)
            # /tmp/2021_07_20__19_06_43_vid_104.csv
            logging.debug('vehicle localLogFlag={0}, opening vehicle data log file: {1}'.format(self.localLogFlag,self.fname_log_veh))
            self.fd_log_veh=open(self.fname_log_veh,'a') # open vehicle model log file for subsequent appending
            # note: sensorData log file is created in veh_udp_io.py | recv_gps() thread
            
            # if this vehicle model will receive udp messages with GPS info and possibly custom sensor data, make sure it all gets logged to a separate file
            if self.live_gps_follower==True:
                self.gps        = {} # initialize empty dictionary for incoming udp messages to live-gps-follower vehicle
            
        if ( myRem(self.n) > 0):
            print("error: non-integer number of steps with this combination of h and dt, exiting")
            #h=round( dt/(floor(nSteps)) ,14)
            exit(-1) # re-compute an h to achieve an integer number of steps only if this case arises
        # ------------------
        
        
        
        
    # =======================================================================================
    #                                   gather_behavior_inputs()
    # =======================================================================================
    #
    # gather_behavior_inputs() is called during runState=={1,2,3,4}
    #
    def gather_behavior_inputs(self):
        
        # get latest and greatest v2vState from v2v network model
        self.v2v.v2vState = self.v2v.v2vUpdateFromNetwork(self.v2v.v2vState) # check for new inbound data from multicast receiver
        
        # retrieve all new commands from prioritize()'ed behaviors every cInt;
        # the last one remains if multuple queue items were added during the last communication interval
        while self.qCmdVeh.qsize()>0:
            self.u  = self.qCmdVeh.get(block=False)  # get current prioritize()'ed commands: [ steer, v_x, pitch ]
            behInfo = self.qBehInfo.get(block=False) # get behavior ID and name from: behaviors.py, bottom of prioritize()
            self.bIdCmd      = behInfo[0] # current behavior ID command from prioritize()
            self.bIdName     = behInfo[1] # commanded behavior name
            self.bIdProgress = behInfo[2] # progress of current behavior, [0 1]
    
    
    
    # =======================================================================================
    #                                   gather_live_gps_inputs()
    # =======================================================================================
    # method for gathering live-GPS-inputs and converting to XYZ coords to ensure
    # consistent pos and vel data between XYZ UTM coordinates and lat/lon in decimal degrees
    #
    # gather_live_gps_inputs() is called during runState=={1,2,3,4} ONLY if this is a live-GPS-follower
    #
    def gather_live_gps_inputs(self):
        
        newData=0 # (0/1) local flag
        
        # retrieve all new commands from live-GPS-listener thread
        # the last one remains if multuple queue items were added during the last communication interval
        while self.qLiveGps.qsize()>0:
            newData=1
            # received and separate this from recv_gps() in veh_udp_io.py: {'gps':gps, 'sensorData':sensorData}
            msg = self.qLiveGps.get(block=False) # get behavior ID and name from: behaviors.py, bottom of prioritize()
            self.gps        = msg['gps']
            self.sensorData = msg['sensorData']
            #logging.debug("\n\n\t{0}: len(msg)={1}, sys.getsizeof(msg)={2}, sensorData keys={3}, msg={4}\n".format(self.vid,len(msg),sys.getsizeof(msg),self.sensorData.keys(), msg))
        
        if newData>0:
            # convert (lat,lon) in decimal degrees to meters in a UTM (zone , latitude band)
            (X,Y,zone,latBand) = utm.from_latlon( self.gps['lat'] , self.gps['lon'] )
            if self.debug>1: logging.debug(' ')
            if self.debug>1:
                for k,v in self.gps.items():
                    logging.debug('{0}={1}'.format(k,v))
                logging.debug('-----------------')
                for k,v in self.sensorData.items():
                    logging.debug('{0}={1}'.format(k,v))
            
            #print('\n\n\tgps_unixTime={0}, self.t0={1}\n\n'.format(gps_unixTime,self.t0))
            self.gps_unixTime = self.gps['unixTime']
            self.pos.lat      = self.gps['lat'] # (decimal degrees) latitude from a real device sending position to this vehicle model via udp
            self.pos.lon      = self.gps['lon'] # (decimal degrees) longitude
            self.pos.X        = X - self.X_origin # (m) X-location in this UTM zone from a real lat/lon pair converted by python utm library
            self.pos.Y        = Y - self.Y_origin # (m) Y-location in this UTM zone from a real lat/lon pair converted by python utm library
            self.pos.Z        = self.gps['alt_m'] # (m) height as reported by a real GPS device, see: live_gps_follower_decoding.py
            self.pos.hdg      = self.gps['true_course'] # (deg) true course over ground as reported by a real GPS device, see: live_gps_follower_decoding.py
            self.pos.psi      = self.gps['psi'] # (deg) vehicle yaw angle; identical to heading - correct this if IMU yaw angle is avaialble
            self.vel.spd_mps  = self.gps['spd_mps'] # (m/s) GPS speed as reported by a real GPS device, note: this is used in collision calculation in Core, all_vehicles.py, checkDistVel()
            self.batt_stat    = -2 # -2 distinguishes this from -1 in live_gps_follower.py | live_gps_follower_decoding()
            if hasattr(self.sensorData,'batt_stat'):
                self.batt_stat = self.sensorData['batt_stat'] # update battery SOC from (cellular or xbee) device sending GPS position
           
    # =======================================================================================
    #                                      tick()
    # =======================================================================================
    # advance the model forward N integration steps to the next communication interval, cInt
    #
    # tick() is only called duging runState==3
    #
    # basic functions:
    #     - srt: soft-real-time delay just the right amount so sim time advances with wall-clock time
    #     - update vehicle model inputs, u
    #     - advance the model N integration steps with constant input, u, to the next communication interval
    #     - generate console output
    #     - record t,x,u to logfile
    #
    #@jit # numba works but consumes much memory for >=300 veh models
    def tick(self):
        
        # soft-real-time delay so surrounding while-loop ticks along at cInt (s), the communication interval
        [self.tNow, self.srtCnt, self.srtMargin, self.elapsedErr, self.elapsedErrAccum] = srt( self.tStart, self.tNow, self.cInt, self.srtCnt, self.elapsedErrAccum, self.srtOutput ) # (0/1) console output?
        
        if self.live_gps_follower==True:
            # live-GPS-follower uses soft-real-time elapsed time
            self.t = self.tNow - self.tStart # live gps followers must maintain sim time, t, as elapsed time (not unix time)
            #logging.debug('tick(), self.t={0}, selt.tNow={1}, self.t0={2}'.format(self.t,self.tNow,self.t0))
        else:
            # advance vehicle dynamics forward by n steps to t=t+cInt for output at the next communication interval
            for i in range(1,self.n+1):
                tNew, xNew = rk4_single_step(f, self.t, self.x, self.u, self.h) # integrate from t to t+dt, dt=stepsize h
                self.t = round(tNew,12)    # floating point arithmetic has inherent limitations. read more
                self.x = np.round(xNew,14) # here https://docs.python.org/3/tutorial/floatingpoint.html#tut-fp-issues
                self.integCnt += 1
                
            # this particular model has rates in xdot, so update xdot=f(t,x,u) before updating vel
            self.xdot = f( self.t, self.x, self.u ) # xdot = [ v_XY[0], v_XY[1], v_Z, psiDot] rates in global SAE XYZ
            
            
        # --> this point has the latest and greatest built-in simulated vehicle states
        #     right after n integration steps
        # --> pos and vel are updated every communication interval, cInt
        # --> all code (in main() while loop) between here and the srt() function call above
        #     is timed by the soft-real-time srt() delay to achieve wall-clock time
        #
        # --> main sends pos and vel info out with udp_io.send_core() right after veh.tick()
        
        
    # =======================================================================================
    #                                   gather_outputs()
    # =======================================================================================
    # method returning a python dictionary with all relevant vehicle data for this cInt update
    #
    # gather_outputs() is called during runState=={1,2,3,4}
    #
    def gather_outputs( self, recvCnt, sendCnt, errorCnt ):
        
        # populate pos and vel with consistent GPS lat/lon values from newly updated state vector, x, from tick()
        if self.live_gps_follower==True:
            # do nothing b/c the lat/lon-to-UTM coordinate converion was performed in gather_live_gps_inputs()
            #self.waypoint_status = {'waypoint':-1, 'lap':0, 'spd_mps':0}
            pass
        else:
            # update pos and vel from latest and greatest state vector: x = [ X, Y, Z, psi ] cap XYZ is in global coords; psi w.r.t. +X
            self.pos.X      = self.x[0] # (m) x = [ X, Y, Z, psi], note: these are numpy arrays
            self.pos.Y      = self.x[1] # (m)
            self.pos.Z      = self.x[2] # (m)
            self.pos.psi    = self.x[3] # (rad)
            self.pos.hdg    = self.pos.psi*(180/3.1415926) # (deg) duplicate of psi until veh model captures difference btwn psi and heading

            # convert to lat/lon (in decimal degrees) from XYZ vehicle coordinates in meters
            if (self.debug>1): logging.debug('self.X_origin={0}, self.Y_origin={1}'.format(self.X_origin,self.Y_origin))
            if (self.debug>1): logging.debug('self.pos.X   ={0}, self.pos.Y   ={1}'.format(self.pos.X,self.pos.Y))
            (lat, lon) = utm.to_latlon( (self.X_origin+self.pos.X) , (self.Y_origin+self.pos.Y) , self.UTM_zone, self.UTM_latBand)
            self.pos.lat = lat
            self.pos.lon = lon

            # the virtual vehicle models need these rates to integrate from t to t+dt
            self.vel.Xd      = self.xdot[0] # (m/s) xdot = [ v_XY[0], v_XY[1], v_Z, psiDot] (see veh_util.py)
            self.vel.Yd      = self.xdot[1] # (m/s)
            self.vel.Zd      = self.xdot[2] # (m/s)
            self.vel.psiDot  = self.xdot[3] # (m/s)
            self.vel.spd_mps = sqrt( pow(self.vel.Xd,2) + pow(self.vel.Yd,2) + pow(self.vel.Zd,2) ) # (m/s) this is used in collision calculation in Core, all_vehicles.py, checkDistVel()
            
            self.sensorData['mac']       = self.vid       # simulated vehicles have no mac address, but sensorData needs it
            self.sensorData['batt_stat'] = self.batt_stat # this will be -1 for simulated vehicles unless changed elsewhere
            
            # update waypoint_status for waypoint routes or gates
            if (self.behaviorCfg['followRoute']>0):
                # empty this queue because number of sends since last gather_outputs() message to MoVE Core is variable
                while not self.qRoute.empty():
                    self.route.i, self.route.lap, self.route.spd_mps_i = self.qRoute.get() # see followRoute() thread in behaviors.py
                self.waypoint_status = {'waypoint':self.route.i, 'lap':self.route.lap, 'spd_mps':self.route.spd_mps_i}
                #logging.debug('\n\n\twaypoint_status={0}\n'.format(self.waypoint_status))
            
            # if both goToPoint() and followRoute() are enabled, one takes priority - make sure config file specifies which has priority!
            if (self.behaviorCfg['goToPoint']>0) and (self.behaviorCfg['goToPoint'] > self.behaviorCfg['followRoute']):
                # empty this queue because number of sends since last gather_outputs() message to MoVE Core is variable
                while not self.qPoint.empty():
                    self.points.current_point, self.points.lap, self.vel.spd_mps = self.qPoint.get() # see goToGate() thread in behaviors.py
                self.waypoint_status = {'waypoint':self.points.current_point, 'lap':self.points.lap, 'spd_mps':self.vel.spd_mps} # routes have no speed associated with them, so use veh speed
                #logging.debug('\n\n\twaypoint_status={0}\n'.format(self.waypoint_status))
            
            # if both goToGate() and followRoute() are enabled, one takes priority - make sure config file specifies which has priority!
            if (self.behaviorCfg['goToGate']>0) and (self.behaviorCfg['goToGate'] > self.behaviorCfg['followRoute']):
                # empty this queue because number of sends since last gather_outputs() message to MoVE Core is variable
                while not self.qGate.empty():
                    self.gates.current_gate, self.gates.lap, self.vel.spd_mps = self.qGate.get() # see goToGate() thread in behaviors.py
                self.waypoint_status = {'waypoint':self.gates.current_gate, 'lap':self.gates.lap, 'spd_mps':self.vel.spd_mps} # routes have no speed associated with them, so use veh speed
                #logging.debug('\n\n\twaypoint_status={0}\n'.format(self.waypoint_status))
            
            
            # ===================== v2v outbound update to all other vehicles =====================
            # update self's v2v multicast recv counter for next v2v send
            if len(self.v2v._v2vUdpRecvDeq)>0:
                self.v2v.v2vMcastCntRecd = self.v2v._v2vUdpRecvDeq.pop() # get the only item on the deque from v2v multicast receiver thread: multicast recv counter
            
            # update self's v2v multicast send counter for next v2v send
            if len(self.v2v._v2vUdpSendDeq)>0:
                self.v2v.v2vMcastCntSent = self.v2v._v2vUdpSendDeq.pop() # get the only item on the deque from v2v multicast sender thread: multicast send counter
            
            # create the data dictionary for an outbound v2v message from this particular vehicle to all others
            v2vData = { 'vid':self.vid, 'v2vMcastCntSent':self.v2v.v2vMcastCntSent, 'v2vMcastCntRecd':self.v2v.v2vMcastCntRecd,
                        'posX':self.pos.X, 'posY':self.pos.Y, 'posZ':self.pos.Z, 'tNowVeh':time.time(), 'stale':False,
                        'missionAction':self.missionAction, 'missionState':self.missionState, 'missionPctComplete':self.missionPctComplete,
                        'missionProgress':self.missionProgress, 'missionLastCmdTime':self.missionLastCmdTime, 'missionStatus':self.missionStatus,
                        'missionCounter':self.missionCounter }
            self.v2v.v2vUpdateToNetwork( time.time(), v2vData ) # broadcast this vehicle's data to everyone listening
            # ===================== ========================================== =====================
            
        # vehData object gets sent out via udp_io.send_core() every cInt
        # all fields in vehData show up in MoVE Core
        #print('self.pos={0}'.format(self.pos.__dict__))
        self.vehData = {    'vid'                : self.vid,                # vehicle ID is assigned at process launch in core (./processLauncher.py)
                            'vehName'            : self.name,               # informal name assigned from config file via main_launch_veh_process.py
                            'vehType'            : self.vehType,            # floating point vehicle type designator
                            'vehSubType'         : self.vehSubType,         # floating point vehicle subType designator
                            'runState'           : self.runState[0],        # current runState is on [1 5]; reference as *mutable* list for class and main visibility
                            'msg_cnt_in'         : recvCnt,                 # udp commands received inbound by vehicle from core
                            'msg_cnt_out'        : sendCnt,                 # udp messages sent outbound from vehicle to core
                            'msg_errorCnt'       : errorCnt,                # udp sendto() exception counter in Veh_udp_io::send_core(), veh_udp_io.py
                            'srt_margin_avg'     : self.srtMarginAvg,       # filtered soft-real-time margin = 100*sleepTime/cInt
                            'srt_err_avg'        : self.elapsedErrAvg,      # filtered elapsed time error
                            't'                  : self.t,                  # (s) this vehicle's sim time
                            'gps_unixTime'       : self.gps_unixTime,       # (s) unixtime from incoming gps messages (only updates when live_gps_follower==True)
                            'pos'                : self.pos.__dict__,       # (m) position in global SAE XYZ coords, plus psi (rad) w.r.t. +X
                            'vel'                : self.vel.__dict__,       # (m/s) vel in global SAE XYZ coords,    plus pdiDot (rad/s)
                            'detectMsg'          : self.detectMsg.__dict__, # detection information populated by detectAndReport() behavior in behaviors.py
                            'waypoint_status'    : self.waypoint_status,    # dict with updates from followRoute() OR goToGate() behaviors: [current waypoint/gate, lap/gate_cnt, speed_mps]
                            'u'                  : self.u,                  # the current control inputs (from behaviors or real operator)
                            'bIdCmd'             : self.bIdCmd,             # current commanded behavior from Behaviors::prioritize()
                            'bIdName'            : self.bIdName,            # current behavior name commanding the vehicle
                            'bIdProgress'        : self.bIdProgress,        # behavior progress, [0 1]
                            'missionAction'      : self.missionAction,      # missionAction like 'waitElapsed' or 'goToPoint'
                            'missionState'       : self.missionState,       # missionState is an integer like 1, 10 or 100 from the config file's [missionCommands]
                            'missionPctComplete' : self.missionPctComplete, # [0 1]
                            'missionProgress'    : self.missionProgress,    # progress indicator = missionState + pctComplete
                            'missionLastCmdTime' : self.missionLastCmdTime, # last wall clock time the mission commander issued a command
                            'missionStatus'      : self.missionStatus,      # mission commander's status: 'readyWait', 'active', or 'complete'
                            'missionCounter'     : self.missionCounter,     # counter for all separate mission commands ('goToMissionState' can cause lops which means counter can be higher than all [missionCommands] rows)
                            'L_char'             : self.L_char,             # characteristic vehicle length
                            'sensorData'         : self.sensorData }        # sensorData dictionary for live-gps-followers or simulated vehicles (both)
        
        
    # =======================================================================================
    #                                 veh_console_update()
    # =======================================================================================
    # - console updates occur at the communication interval, cInt
    # - send vehicle-specific information to the command line console for status monitoring
    # - optionally log to file
    def veh_console_update(self):
        if (self.debug>0):
            
            # simple moving average for the two performance metrics indicating soft-real-time process health
            # sma, y = simple_moving_average(sma, y, x[i], n)
            self.srtMarginAvg , self.srtMarginHistory  = simple_moving_average(self.srtMarginAvg , self.srtMarginHistory ,self.srtMargin , self.srtFilterWindowN)
            self.elapsedErrAvg, self.elapsedErrHistory = simple_moving_average(self.elapsedErrAvg, self.elapsedErrHistory,self.elapsedErr, self.srtFilterWindowN)
            
            str  = 'runState={0}, '.format(self.runStateDesc[ self.runState[0] ])
            str += 'behavior={0:<14s}, '.format(self.bIdName)
            str += 'srt margin={0:6.2f}(%), '.format(self.srtMarginAvg)
            str += 'pace err={0:6.3f}(s), '.format(self.elapsedErrAvg)
            str += 't={0:12.2f}(s), pos=['.format(self.t)
            np.set_printoptions(precision=4)
            
            #code.interact(local=dict(globals(), **locals())) # to stop thread outputs, run as live_gps_follower and make dt=200 udp_console_update() in veh_udp_io.py
            # dir(self.pos)  is a list --> ['X', 'Y', 'Z', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'lat', 'lon', 'psi']
            # vars(self.pos) is a dict --> {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'psi': 0.0, 'lat': 0.0, 'lon': 0.0}
            #
            #print('\t\t\tstr={0}'.format(str))
            #print('\t\t\tvars(self.pos).items()={0}'.format( vars(self.pos).items() ))
            for key,val in vars(self.pos).items():
                if key=='psi':
                    val=(180.0/3.14159)*val # convert psi (rad) to degrees for comparison to dashboard display
                str += '{0}={1:6.6f}, '.format(key,val)
            str += ']'
            
            if (self.debug>1):
                str += ', vel=['
                for key,val in vars(self.vel).items():
                    str += '{0}={1:6.2f}, '.format(key,val)
                str += ']'
                
            if (self.debug>=1): # u is a simple list
                str += ', u=[steer,spd,pitch]={0}'.format(self.u)
            
            logging.debug(str)
            
            #print('-------------------------------------')
            #logging.debug('%i threads alive', threading.active_count())
            #if( self.live_gps_follower==False ):
            #    print('qCmdVeh.qsize()={0}, qBehInfo.qsize()={1}'.format( self.qCmdVeh.qsize(), self.qBehInfo.qsize() ) )
            
            sys.stdout.flush()
            
        if (self.localLogFlag>0):
            self.log_locally()
            
            
    # =======================================================================================
    #                                 log_locally()
    # =======================================================================================
    # write a csv text file in /tmp on local machine where the i'th vehicle model is running
    # t,pos,vel,u are all numpy arrays
    def log_locally( self ):
        
        myStr = '{0}, '     .format(self.vid)                  + \
                '{0}, '     .format(self.name)                 + \
                '{0}, '     .format(self.vehType)              + \
                '{0}, '     .format(self.runState[0])          + \
                '{0}, '     .format(self.bIdCmd)               + \
                '{0:0.6f}, '.format(time.time())               + \
                '{0}, '     .format(self.srtCnt)               + \
                '{0:0.6f}, '.format(round(self.srtMargin,3))   + \
                '{0:0.6f}, '.format(round(self.elapsedErr,3))  + \
                '   '                                          + \
                '{0:0.6f},    '.format(self.t)                 + \
                '{0:0.6f},    '.format(self.gps_unixTime)      + \
                '{0}, '.format(self.batt_stat)                 + \
                ', '.join('{0}'.format(v) for k,v in vars(self.pos).items())       + \
                ',    ' + \
                ', '.join('{0}'.format(v) for k,v in vars(self.vel).items())       + \
                ',    ' + \
                ', '.join('{0}'.format(v) for k,v in vars(self.detectMsg).items()) + \
                ',    ' + \
                ', '.join(str(v) for v in self.u)             + '\n'
        
        try:
            self.fd_log_veh.write( myStr ) # append to the log file
            self.fd_log_veh.flush()
        except ValueError as err:
            logging.debug('log_locally(): logfile file error for vehicle data!  {}'.format(err))
            logging.debug('t={0}: exiting.'.format(datetime.now().strftime('%c')))
            exit(-1)
        
        
        
        
    # =======================================================================================
    #                                      exit()
    # =======================================================================================
    # set Event flag to stop all behavior threads, close veh log file, and exit gracefully
    def exit(self):
        
        # execution only gets here when t==tf
        if (self.localLogFlag>0):
            logging.debug('closing vehicle model log file [{}]'.format(self.fname_log_veh))
            self.fd_log_veh.close()
        
        print('\n\n\n veh.exit(): sending v2v and veh exit events\n\n\n')
        self.v2v.e.set()  # tell v2v threads to exit
        self.e.set() # all Veh() threads exit when e.is_set()
        
        logging.debug("veh() class exiting  : {0}, srtCnt={1}, integCnt={2}".format(time.ctime(), self.srtCnt, self.integCnt) )
