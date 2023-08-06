#!/usr/bin/env python3
#
# usage:
#    ./behaviors.py
#
# adapted from: threading_g_priority_based_scheduler.py
#
# Marc Compere, comperem@gmail.com
# created : 07 Jul 2018
# modified: 26 Jun 2022
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

import random
import threading
import time
from datetime import datetime
import queue
import numpy as np
import logging
from math import sin,cos,atan2,pi,copysign,sqrt,tanh
import code # drop into a python interpreter to debug using: code.interact(local=locals())
from collections import deque
from veh_util import compute_perpendicular_angle_to_line_in_space # for navigating through gates

sign = lambda x: x and (1, -1)[x<0] # from: https://stackoverflow.com/a/16726462/7621907

logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-14s) %(message)s',
)

class Behaviors:
    """A class for subsumption architecture behaviors to control a vehicle model            """
    """    these behaviors provide vehicle operator, driver, pilot or pedestrian commands   """
    """    to make the vehicle or pedestrian model zoom around                              """
    
    def __init__(self,cfg,qCmdVeh,qBehInfo,e,debug):
        
        self.behaviorCfg  = cfg.behaviorCfg  # straight from readConfigFile.py, e.g. self.behaviorCfg = {'wander': 1, 'periodicTurn': 2, 'periodicPitch': '0', 'stayInBounds': 12, 'avoid': 10, 'detectAndReport': '0', 'followRoute': '0'}
        self.qBehavior    = queue.Queue()    # queue for all behavior threads to send commands to prioritize()
        self.qCmdVeh      = qCmdVeh          # queue for prioritize() to send the selected commands to the vehicle
        self.qBehInfo     = qBehInfo         # a que for behavior info maintained in exact parity with qCmdVeh
        self.e            = e                # for signaling exit to all Behavior threads
        self.debug        = debug
        self.runState     = cfg.runState     # this should bring runState and runStatePrev visibility to every beh thread; recall: this is a *mutable* list for class and main visibility
        self.runStatePrev = cfg.runStatePrev
        
        self.detectThreshold      = cfg.detectThreshold
        self.pctCompleteGoToPoint = 0.0      # used by behaviors | goToPoint() and missionStateSequencer() to update pctComplete
        goToPointActive           = True     # used by behaviors | goToPoint() and missionStateSequencer() to indicate action complete
        
        # migrate behaviorCfg dictionary to 2 lists: behaviors and priority
        self.behaviors = [0]*len(self.behaviorCfg) # init two lists for behavior names and priority
        self.priority  = [0]*len(self.behaviorCfg)
        self.bId       = [0]*len(self.behaviorCfg)
        for i,(beh,pri) in enumerate( self.behaviorCfg.items() ):
            self.behaviors[i]= 'self.'+beh # behavior name must match method definition here in behaviors.py
            self.priority[i] = pri # behavior priority
            self.bId[i]      = i   # behavior ID for prioritize()
        
        # ------------------ points init -------------------
        #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
        if hasattr(cfg,'points') and hasattr(cfg.points,'IC_pt') and len(cfg.points.points)>0:
            self.points          = cfg.points
            logging.debug('detected points!')
            for k,v in self.points.points.items():
                logging.debug('\t{0}={1}'.format(k,v))
            logging.debug('points.IC_pt={0}'.format(self.points.IC_pt))
            logging.debug('points.lap={0}'.format(self.points.lap))
        
        # ------------------ gates init -------------------
        #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
        if hasattr(cfg,'gates') and hasattr(cfg.gates,'firstGate') and len(cfg.gates.gates)>0:
            self.gates          = cfg.gates
            logging.debug('detected gates!')
            for k,v in self.gates.gates.items():
                logging.debug('\t{0}={1}'.format(k,v))
            logging.debug('gates.firstGate={0}'.format(self.gates.firstGate))
            logging.debug('gates.lap={0}'.format(self.gates.lap))
        
        # ----------- BEGIN: route configuration -------------
        # bring in the route objects if this particular vehicle happened to be configured to follow a waypoint route
        if hasattr(cfg,'routeCfg'): # a route must have been configured in the .ini file and assigned early in main_veh_model.py's __main__
            self.routeCfg = cfg.routeCfg # assign Behavior's self.route to config file route discovered in cfg file for this particular vehicle
            #logging.debug('vid={0} using routeCfg: {1}'.format(cfg.vid, cfg.routeCfg.__dict__))
        
        if hasattr(cfg,'route'): # a route must have been configured in the .ini file and assigned early in main_veh_model.py's __main__
            self.route = cfg.route # assign Behavior's self.route to config file route discovered in cfg file for this particular vehicle
            #logging.debug('vid={0} using route: {1}'.format(cfg.vid, cfg.route.__dict__))
        else:
            self.behaviorCfg['followRoute'] = 0 # confirm followRoute() not started; no need to run followRoute() if there's no route specified for this vehicle
            logging.debug('vid={0} has no route; not starting followRoute() behavior'.format(cfg.vid))
        # ----------- END: route configuration -------------
        
        
        # summarize which behaviors to start
        logging.debug('[{0}]: configured behaviors for {0}'.format( datetime.now().strftime('%c') , cfg.vid))
        for behName,priority in self.behaviorCfg.items():
            toStart = (priority>0)
            logging.debug("\tself.behaviorCfg: behavior name: {0:20s},   priority: {1:20d},   will start? {2:3d}".format(behName,priority,toStart))
                
    # =======================================================================================
    #                                   startBehaviors()
    # =======================================================================================
    # avoid starting threads in __init__ so two separate mains can use
    # these methods:   main_srt_veh.py (vehicle model)   and   behavior_scheduler.py (for testing)
    def startBehaviors(self,veh):
        
        # start behavior and prioritize() thread
        bStartedCnt=0
        logging.debug(' ')
        for i, behName in enumerate( self.behaviors ):
            if (self.priority[i]>0): # if this behavior should be enabled...
                logging.debug('\t[{0}]: starting behavior thread bId={1} : {2:20s} with priority {3}'.format( datetime.now().strftime('%c') , self.bId[i], behName, self.priority[i]))
                self.th = threading.Thread(name=behName, \
                                     target=eval(self.behaviors[i]), \
                                     args=(self.bId[i], behName, self.priority[i], veh, self.debug))
                #code.interact(local=locals())
                self.th.start()
                bStartedCnt+=1
        logging.debug(' ')
        
        logging.debug('[{0}]: started [{1}] behaviors out of [{2}] possible'.format( datetime.now().strftime('%c') , bStartedCnt,len(self.behaviors) ))
        
        # start prioritize() thread
        self.p = threading.Thread(name='PRIORITIZE', target=self.prioritize,args=() )
        self.p.start()
        
        logging.debug('N vehicle and behavior threads: {}'.format( threading.active_count() ))
    
    
    # -----------------------------------------------------------------
    #                        prioritize()
    # -----------------------------------------------------------------
    # prioritize() -  finds highest priority process and sends those commands to the vehicle
    #
    # this is the decision making function from Rodney Brook's 1986 subsumption architecture
    # - any behavior (or other) thread can place a message in the queue to request consideration: qBehavior
    # - if message length is 2, this means disable that behavior (or put your hand down)
    # - otherwise:
    #   - update steer, speed, pitch command from this particular behavior
    #   - update the processEnable[] list with the bId'th priority array, priority[bId]
    #   - find highest priority behavior in current processEnable[] array - this is the most important process at this iteration
    #   - if no other higher priority process is currently running,
    #     copy the highest priority behavior's steer,speed,pitch cmd to vehicle model
    # - to dynamically change behavior priority on the fly, change priority[bId]
    def prioritize(self):
        tStart = time.time()
        behaviors = self.behaviors
        priority  = self.priority
        qBehavior = self.qBehavior
        qCmdVeh   = self.qCmdVeh
        qBehInfo  = self.qBehInfo
        debug     = self.debug
        name      = threading.currentThread().getName()
        dt        = 0.5 # (s) loop periodically to catch the all-exit signal from main, e.is_set()
        
        nBehaviors      = len(behaviors) # 3-behaviors + avoid(); ensure behaviors[] is proper length
        processEnable   = [0]*nBehaviors # init a list of all zeros, one for each thread; lists are mutable
        processProgress = [0]*nBehaviors # processProgress is reported here by all behaviors for missionStateSequencer(), but is not used in the prioritize() selection method 
        
        # vehCmd == [steer, speed, pitch]
        vehCmd = [[0]*4 for i in range(nBehaviors)] # initial vehCmd matrix is 3xnBehaviors, [steer, spd, pitch, v_z]_i for each behavior
        
        while self.e.is_set() is False:
            
            # blocking queue.get() controls loop iteration, but periodic timeout catches graceful exit signal, e.is_set()
            try:
                # did any behaviors raise their hand for prioritized consideration to command the vehicle?
                msg = qBehavior.get(block=True,timeout=dt) # Queue.get(block=True, timeout=None), timeout is for catching the thread exit signal, e.is_set()
            except queue.Empty:
                #logging.error("queue.Empty() timeout")
                continue # "continues with the next cycle of the nearest enclosing loop"  (which is 'while self.e.is_set() is False')
            
            # ------------------------------------------------------
            # parse message, update processEnable and vehCmd arrays
            #
            # message: [ bId , steer , speed, pitch, v_z, pctComplete ]
            bId=msg[0] # what behavior just sent a message?
            if (debug>0): logging.debug('recvd msg from bId={0} [{1}], msg=[{2}]'.format(bId,behaviors[bId],msg))
            
            # a behavior message length of 2 means the behavior just said "I'm done and putting my hand down" 
            if len(msg)==2:
                processEnable[bId]=0 # disable this behavior
                if (debug>0): logging.debug('DISable bId={} [{}]'.format(bId,behaviors[bId]))
            else:
                # assign steer , speed, pitch for this row of the behavior table - it's not clear if this will get used yet
                vehCmd[bId][0]       = msg[1] # steer cmd for the bId'th behavior
                vehCmd[bId][1]       = msg[2] # speed cmd for the bId'th behavior
                vehCmd[bId][2]       = msg[3] # pitch cmd for the bId'th behavior
                vehCmd[bId][3]       = msg[4] # v_z   cmd for the bId'th behavior
                processProgress[bId] = msg[5] # [0 1], update this process' progress
                processEnable[bId]   = priority[bId] # enable this behavior ID (bId) in the table
                if (debug>0): logging.debug('ENable  bId={} [{}]'.format(bId,self.behaviors[bId]))
            
            # ------------------------------------------------------
            # find which process has highest priority and assign it's outputs to the vehicle command
            
            highestPriorityProcess = max(processEnable) # determine highest priority process in the processEnable[] list
            
            bIdCmd = processEnable.index( highestPriorityProcess ) # returns 0-based index of highest priority process
            
            # this situation is when a middle-priority process requests enabling but is not selected because a higher priority behavior is active
            if (priority[bId]<priority[bIdCmd]):
                # the behavior that raised it's hand got rejected b/c current behavior has greater priority
                # note: this case occurs when a lower priority behavior raises *or* lowers it's hand
                if (debug>0): logging.debug('[{0}], other behavior activity ignored, not high enough priority: bId:{1} [{2}], priority:[{3}]'.format( datetime.now().strftime('%c') , bId, behaviors[bId], priority[bId]) )
                if (debug>0): logging.debug('[{0}], keeping current behavior: bId={1} [{2}], priority:[{3}]'.format( datetime.now().strftime('%c') , bIdCmd, behaviors[bIdCmd], priority[bIdCmd]) )
            
            # assign actuator commands from the highest priority process just determined, bIdCmd
            else:
                # send highest priority process commands to the vehicle
                vehCmdOut = vehCmd[bIdCmd]
                qCmdVeh.put(vehCmdOut) # send vehicle model driver cmds: [ steer, v_x, pitch ]  in myVehicle.py | gather_inputs()
                qBehInfo.put( ( bIdCmd, behaviors[bIdCmd], processProgress[bIdCmd] ) ) # behavior ID, bIdName, and bIdProgress sent to myVehicle.py | gather_inputs()
                
                bIdName=behaviors[bIdCmd]
                steerSpdPitch='steer={0:6.2f}, spd={1:6.2f}, pitch={2:6.2f}'.format(vehCmdOut[0], vehCmdOut[1], vehCmdOut[2])
                myStr='[{0}], bId={1:d}, behavior [{2:15s}], {3:s} assigned to vehicle:          [{4:15s}]'.format( datetime.now().strftime('%c') , bIdCmd, bIdName, steerSpdPitch, bIdName)
                if (debug>0): logging.debug( myStr )
                
        logging.debug('[{0}]: exiting.'.format( datetime.now().strftime('%c') ))



    # --------------------------------------------------------------
    #                  behavior: wander()
    # --------------------------------------------------------------
    # wander process: wake up once, tell prioritize() 'go forward'; thread does not stay alive
    def wander(self,bId,behName,priority,veh,debug):
        logging.debug('\t\t[{0}]: bId={1} [{2}], priority={3}'.format( datetime.now().strftime('%c') ,bId,behName,priority))
        
        #spd = 3.1415926/10.0 # (m/s) vehicle nominal wander speed
        spd = 5 #2.0 # (m/s) vehicle nominal wander speed
        #spd = 2.236 # (m/s) wander speed to hit vid 100 (vid=101 should go faster at psi_ic=-0.4636)
        self.qBehavior.put( [ bId , 0.0 , spd, 0.0, 0.0, 0.0 ]) # enable with these cmds: [ bId , steer , speed, pitch, v_z, progress ]
        
    # --------------------------------------------------------------
    #                  behavior: periodicTurn()
    # --------------------------------------------------------------
    # periodic turn: every 10 secs, turn a bit
    def periodicTurn(self,bId,behName,priority,veh,debug):
        logging.debug('\t\t[{0}]: bId={1} [{2}], priority={3}'.format( datetime.now().strftime('%c') ,bId,behName,priority))
        e=veh.e
        randFlag=veh.randFlag # (0/1) use random numbers?
        
        dtDormant = 20 + randFlag*random.uniform(0.0,20.0) # (s) behavior dormant period (not turning)
        #spd       = 2.2 # (m/s) speed while turning
        dtTurn    = 2.0 # (s) turn duration when randFlag==0
        turn      = 0.5 # (rad) nominal turn is positive, or right-hand turn when randFlag==0
        while e.is_set() is False:
            e.wait(dtDormant) # (sec) behavior is dormant for this duration; e.wait() is an interruptable sleep() with independent timers despite using the same event, e
            
            if randFlag>0:
                dtTurn = 1 + randFlag*random.uniform(0.0,4.0) # (s) turn duration
                turn = (randFlag | 1)*random.uniform(-0.5,+0.5) # uniformly distributed random number
            
            if (debug>1): logging.debug('{0:s}, bId={1:d}, pri={2:d}: turn={3:f}'.format(behName, bId, priority, turn))
            
            # enable with these cmds: [ bId , steer , speed, pitch, progress ]
            self.qBehavior.put( [ bId , turn , 0.8*veh.vel.spd_mps, 0.0, 0.0, 0.0 ] ) # use spd or veh.vel.spd_mps
            
            #time.sleep(dtTurn) # (sec) duration to turn
            e.wait(dtTurn) # (sec) duration to turn; interruptable sleep()
            
            self.qBehavior.put( [ bId , 0 ] ) # disable with [bId, 0]
        
        logging.debug('[{0}]: bId={1} [{2}], exiting.'.format( datetime.now().strftime('%c') ,bId,behName))



    # --------------------------------------------------------------
    #                  behavior: periodicPitch()
    # --------------------------------------------------------------
    # periodic pitch: every 15 secs, go up or down a bit
    def periodicPitch(self,bId,behName,priority,veh,debug):
        e=veh.e
        randFlag=veh.randFlag # (0/1) use random numbers?
        
        logging.debug('\t\t[{0}]: bId={1} [{2}], priority={3}'.format( datetime.now().strftime('%c') ,bId,behName,priority))
        dt = 10 + randFlag*random.uniform(0.0,5.0) # (s) intermittency period
        dtPitch = 2 + randFlag*random.uniform(-1.0,2.0) # (s) climb or dive duration
        spd = 3; # (m/s) speed while turning
        pitch = 0.5 # positive is up
        minHeight = 10  # (m) stay at least this high above the ground
        maxHeight = 100 # (m) stay at least this high above the ground
        while e.is_set() is False:
            
            e.wait(dt) # (sec) behavior is dormant for this duration; e.wait() is an interruptable sleep() with independent timers despite using the same event, e
            
            if randFlag>0:
                pitch = randFlag*random.uniform(-0.5,+0.5) # uniformly distributed random number
            
            if veh.pos.Z < minHeight:
                # too low, go up
                pitch = +0.1 # (rad)
            if veh.pos.Z > maxHeight:
                # too high, go down
                pitch = -0.1 # (rad)
            
            if (debug>1): logging.debug('{0:s}, bId={1:d}, pri={2:d}: pitch={3:f}'.format(behName, bId, priority, pitch))
            
            # enable with these cmds: [ bId , steer , speed, pitch, progress ]
            self.qBehavior.put( [ bId , 0.0 , 0.8*veh.vel.spd_mps, pitch, 0.0, 0.0 ] ) # use spd or veh.vel.spd_mps
            
            #time.sleep(dtPitch) # (sec) duration to turn
            e.wait(dtPitch) # (sec) duration to pitch; interruptable sleep()
            
            self.qBehavior.put( [ bId , 0 ] ) # disable with [bId, 0]
            
        logging.debug('[{0}]: bId={1} [{2}], exiting.'.format( datetime.now().strftime('%c') ,bId,behName))



    # --------------------------------------------------------------
    #                  behavior: circleInPlace()
    # --------------------------------------------------------------
    # *UNTESTED* circle in place: meant for fixed-wing aerial vehciles, fly large circles of radius, R_turn, until told otherwise
    def circleInPlace(self,bId,behName,priority,veh,debug):
        e=veh.e
        randFlag=veh.randFlag # (0/1) use random numbers?
        
        logging.debug('\t\t[{0}]: bId={1} [{2}], priority={3}'.format( datetime.now().strftime('%c') ,bId,behName,priority))
        dt = 1 # (s) loop evaluation period
        R_turn = 10 # (m)
        while e.is_set() is False:
            
            e.wait(dt) # (sec) behavior is dormant for this duration; e.wait() is an interruptable sleep() with independent timers despite using the same event, e
            
            steer = veh.L_char / R_turn; # (rad) delta = L/R
            if (debug>1): logging.debug('{0:s}, bId={1:d}, pri={2:d}: pitch={3:f}'.format(behName, bId, priority, pitch))
            
            # enable with these cmds: [ bId , steer , speed, pitch, progress ]
            self.qBehavior.put( [ bId , steer , veh.vel.spd_mps, 0.0, 0.0, 0.0 ] ) # [ bId , steer , speed, pitch, v_z, progress ]
            
            #self.qBehavior.put( [ bId , 0 ] ) # disable with [bId, 0]
            
        logging.debug('[{0}]: bId={1} [{2}], exiting.'.format( datetime.now().strftime('%c') ,bId,behName))


    # --------------------------------------------------------------
    #                  behavior: stayInBounds()
    # --------------------------------------------------------------
    # stayInBounds: if vehicle exceeds bondaries, turn until back inside
    def stayInBounds(self,bId,behName,priority,veh,debug):
        logging.debug('\t\t[{0}]: bId={1} [{2}], priority={3}'.format( datetime.now().strftime('%c') ,bId,behName,priority))
        e=veh.e
        geom=veh.geom
        geom_center = np.array([ geom.cg_X , geom.cg_Y , 0.0 ])
        
        steer_max = 35*np.pi/180.0 # (rad) set lock-to-lock max steer limit of 35deg, from ME620 Adv. Veh. Dyn. (~0.6rad)
        k_steer = 1.5 # pure-pursuit steering gain, chosen in Simulink, ME620 Advanced Vehicle Dynamics
        
        dt = 1 # (s) out-of-bounds evaluation period
        spd = 2; # (m/s) speed while turning
        remainingTime = -1 # (s)
        while e.is_set() is False:
            
            e.wait(dt) # (sec) behavior is dormant for this duration; e.wait() is an interruptable sleep() with independent timers despite using the same event, e
            
            # are we out of bounds?
            Xout = (veh.pos.X > geom.Xmax) or (veh.pos.X < geom.Xmin) # is veh out of bounds in X-dir?
            Yout = (veh.pos.Y > geom.Ymax) or (veh.pos.Y < geom.Ymin) # is veh out of bounds in Y-dir?
            
            # while out-of-bounds, steer back towards the rectangular geometry's centroid
            if (Xout==True) or (Yout==True) or (remainingTime>0):
                # yep, we're out of bounds... or we've been out of bounds and we're still returning to boundary centroid
                if (remainingTime<=0):
                    getBackInThereTimer = 5 # (s) duration for get-back-in-there behavior to execute once it's gone out-of-bounds
                    tStartForTimer = time.time() # (s) seconds since the epoch (a giant number)
                    remainingTime = tStartForTimer - time.time() + getBackInThereTimer # (s) duration to keep steering back towards the interior
                else:
                    remainingTime = tStartForTimer - time.time() + getBackInThereTimer # (s) duration to keep steering back towards the interior
                
                #determine which way to turn
                #dt = veh.cInt # provide higher frequency dynamic steering input matching veh.pos update rate
                
                # compute steer angle to bring the vehicle back in-bounds, which means
                # inside the rectangle defined by geom in MyVehicle class init: [Xmin Xmax Ymin Ymax])
                #
                # for steering control law diagram and equations
                # see: p.4 of 03_Compere_handwritten_notes_Path_Nav_Control_Lecture_1_of_2_14_Oct_2016.pdf
                veh_g = np.array([ veh.pos.X, veh.pos.Y, veh.pos.Z ])
                r_gc  = geom_center - veh_g # vector from veh cg to geometry gentroid; tip minus tail
                
                psi_c = atan2( r_gc[1] , r_gc[0] ) # (rad) heading angle from vehicle to geometry centroid
                psi_veh = veh.pos.psi                # (rad) current vehicle heading, which could be large from multiple turns (i.e. >> +/- 2pi)
                
                psi_err_raw = psi_c - psi_veh # (rad) heading error; this could be a large number, way beyond +/- pi
                
                # unwrap such that psi_err is on [-pi  +pi]
                # credit: Mike Fair, Nov 2004
                spsi = sin(psi_err_raw)
                cpsi = cos(psi_err_raw)
                # psi_err is in body-fixed frame on inteval [-pi +pi] - this essentially says, turn left or turn right
                psi_err = atan2(spsi,cpsi) # (rad) heading error w.r.t. vehicle x-axis, atan2() returns [-pi  +pi]
                
                steer_raw = k_steer*psi_err # (rad) steering gain for path following (even tho this is a stationary point)
                steer = np.clip( steer_raw , -steer_max, +steer_max) # (rad) impose max steer angle, clip is numpy's saturation function
                #logging.debug('[{0}]: steer_max={1}, steer_raw={2}, steer={3}'.format( datetime.now().strftime('%c') ,steer_max,steer_raw,steer))
                
                if (debug>1): logging.debug('{0:s}, bId={1:d}, pri={2:d}: steer={3:f}'.format(behName, bId, priority, steer))
                
                # enable with these cmds: [ bId , steer , speed, pitch, progress ]
                self.qBehavior.put( [ bId , steer , spd, 0.0, 0.0, 0.0 ] ) # [ bId , steer , speed, pitch, v_z, progress ]
                
            else: # we're in-bounds again
                self.qBehavior.put( [ bId , 0 ] ) # disable this behavior with [bId, 0]
                dt = 1 # (s) go back to slower polling while no longer computing a dynamic steering input
                
        logging.debug('[{0}]: bId={1} [{2}], exiting.'.format( datetime.now().strftime('%c') ,bId,behName))



    # --------------------------------------------------------------
    #                  behavior: avoidBySteer()
    # --------------------------------------------------------------
    # queue-driven loop to parse incoming vehicle message, do the math, and turn the other way (mainly for aerial vehicles)
    def avoidBySteer(self,bId,behName,priority,veh,debug):
        e=veh.e
        randFlag=veh.randFlag # (0/1) use random numbers?
        
        logging.debug('\t\t[{0}]: bId={1} [{2}], priority={3}, vid={4}' \
               .format( datetime.now().strftime('%c') , bId, behName, priority, veh.vid))
        dt = 0.5 # (s) periodically loop to check for exit Event, e.is_set()
        #dtAvoid = 5.0 + randFlag*random.uniform(1.0,3.0) # (s) avoid turn duration; smaller is better - if complete and still at-risk it will trigger again
        spd = 2.236 # (m/s) vehicle nominal wander speed (vid=101 should go faster at psi_ic=-0.4636)
        
        while e.is_set() is False:
            
            # clear the que - zoom through all avoidCmd messages that may have piled up
            dtAvoid=dt
            while not veh.qAvoid.empty(): # this empties the queue coming from move core's collision detection (it can send multiple times)
                # payload_i = { 'theOtherOne': vid_j, 'pos': vehData_j['pos'], 'vel': vehData_j['vel'],
                #               'dist_XY': warn_data['dist_XY'], 'distRate': warn_data['distRate'] } # j pos, j vel
                payload = veh.qAvoid.get() # qAvoid message is from veh_udp_io.py;  defaults: Queue.get(block=True, timeout=None)
                
                logging.debug( '\t\tavoid queue size: {0}'.format(veh.qAvoid.qsize()) )
                
                logging.debug('[{0}]: ---------------------------'.format( datetime.now().strftime('%c') ))
                logging.debug('[{0}]: bId={1}, vid={2}, veh pos={3}'.format( datetime.now().strftime('%c') , bId, veh.vid, veh.pos.__dict__))
                logging.debug('[{0}]: bId={1}, received payload={2}'.format( datetime.now().strftime('%c') , bId, payload))
                logging.debug('[{0}]: ---------------------------'.format( datetime.now().strftime('%c') ))
                
                # turn left or right to avoid the other vehicle
                d_y, d_x = self.avoidComputeOtherVehPositionInLocalFrame( veh, payload )
                #dtAvoid = (pi*veh.L_char) / (4*spd*abs(turnCmd)) # hold-time to achieve 45-deg yaw change
                
                evasiveTurnCmd = 0.4 + randFlag*random.uniform(0.0,0.3) # (rad) steer signal to avoid collision
                                     # todo: make this a function of speed, thresholding to below a max lateral acceleration
                
                # if the other vehicle is on my RIGHT, then STEER LEFT to avoid
                if d_y >=0.0:
                    logging.debug('\tother vehicle detected on RIGHT! '.format(payload['theOtherOne']))
                    turnCmd = -(evasiveTurnCmd) # (rad) steer signal turning left (+Z and +z are down, RHR)
                    logging.debug('\t[{0}]: vid={1}, turning left, steer={2}(deg)'.format( datetime.now().strftime('%c') , veh.vid, turnCmd*180/3.14159))
                
                # if the other vehicle is on my LEFT, then STEER RIGHT to avoid
                if d_y < 0.0:
                    logging.debug('\tother vehicle detected on LEFT! '.format(payload['theOtherOne']))
                    turnCmd = +(evasiveTurnCmd) # (rad) steer signal turning right (+Z and +z are down, RHR)
                    logging.debug('\t[{0}]: vid={1}, turning right, steer={2}(deg)'.format( datetime.now().strftime('%c') , veh.vid, turnCmd*180/3.14159))
                
                #pitch = randFlag*random.uniform(-1.0,+1.0) # uniformly distributed random number on [-1 +1]
                if (debug>=1): logging.debug('{0:s}, bId={1:d}, pri={2:d}: turnCmd={3:f} (deg)'.format(behName, bId, priority, turnCmd*180/3.14149))
                
                # enable with these cmds: [ bId , steer , speed, pitch, progress ]
                self.qBehavior.put( [ bId , turnCmd , spd, 0.0, 0.0, 0.0 ] ) # [ bId , steer , speed, pitch, v_z, progress ]
            
            # execute the last turn computed
            e.wait(dtAvoid) # (sec) duration for this maneuver; interruptable sleep()
            
            self.qBehavior.put( [ bId , 0 ] ) # disable with [bId, 0]
        
        logging.debug('[{0}]: bId={1} [{2}], exiting.'.format( datetime.now().strftime('%c') ,bId,behName))



    # --------------------------------------------------------------
    #                  behavior: avoidByBrake()
    # --------------------------------------------------------------
    # queue-driven loop to parse incoming vehicle message, do the math, and slow or stop to avoid hitting another (ground) vehicle on a similar path
    
    # UNFINISHED - UNTESTED - UNFINISHED - UNTESTED
    def avoidByBrake(self,bId,behName,priority,veh,debug):
        e=veh.e
        randFlag=veh.randFlag # (0/1) use random numbers?
        
        logging.debug('\t\t[{0}]: bId={1} [{2}], priority={3}, vid={4}' \
               .format( datetime.now().strftime('%c') , bId, behName, priority, veh.vid))
        dt = 0.5 # (s) periodically loop to check for exit Event, e.is_set()
        #dtAvoid = 5.0 + randFlag*random.uniform(1.0,3.0) # (s) avoid turn duration; smaller is better - if complete and still at-risk it will trigger again
        spd = 2.236 # (m/s) vehicle nominal wander speed (vid=101 should go faster at psi_ic=-0.4636)
        
        while e.is_set() is False:
            
            # clear the que - zoom through all avoidCmd messages that may have piled up
            dtAvoid=dt
            while not veh.qAvoid.empty():
                # payload_i = { 'theOtherOne': vid_j, 'pos': vehData_j['pos'], 'vel': vehData_j['vel'],
                #               'dist_XY': warn_data['dist_XY'], 'distRate': warn_data['distRate'] } # j pos, j vel
                payload = veh.qAvoid.get() # qAvoid message is from veh_udp_io.py;  defaults: Queue.get(block=True, timeout=None)
                
                logging.debug( '\t\tavoid queue size: {0}'.format(veh.qAvoid.qsize()) )
                
                logging.debug('[{0}]: ---------------------------'.format( datetime.now().strftime('%c') ))
                logging.debug('[{0}]: bId={1}, vid={2}, veh pos={3}'.format( datetime.now().strftime('%c') , bId, veh.vid, veh.pos.__dict__))
                logging.debug('[{0}]: bId={1}, received payload={2}'.format( datetime.now().strftime('%c') , bId, payload))
                logging.debug('[{0}]: ---------------------------'.format( datetime.now().strftime('%c') ))
                
                # turn left or right to avoid the other vehicle
                d_y, d_x = self.avoidComputeOtherVehPositionInLocalFrame( veh, payload )
                #dtAvoid = (pi*veh.L_char) / (4*spd*abs(turnCmd)) # hold-time to achieve 45-deg yaw change
                
                # if the other vehicle is in front, slow down
                # example payload={ 'theOtherOne': 100, 'pos': {'X': 30.16, 'Y': 87.31, 'Z': 0.0, 'psi': 0.0,
                #                   'lat': 29.19, 'lon': -81.04}, 'vel': {'Xd': 5.0, 'Yd': 0.0, 'Zd': 0.0,
                #                   'psiDot': 0.0, 'spd_mps': 5.0}, 'dist_XY': 47.48, 'distRate': -13.35}
                vel = payload['vel']
                spd_other = np.sqrt( pow(vel['Xd'],2) + pow(vel['Yd'],2) + pow(vel['Zd'],2) )
                if d_x >=0.0:
                    logging.debug('other vehicle detected IN FRONT. Brake to avoid hitting! '.format(payload['theOtherOne']))
                    spd = 0.8*spd_other
                    logging.debug('[{0}]: vid={1}, turning left, spd={2}(m/s)'.format( datetime.now().strftime('%c') , veh.vid, spd))
                
                if (debug>1): logging.debug('{0:s}, bId={1:d}, pri={2:d}: spd={3:f} (m/s)'.format(behName, bId, priority, spd))
                
                # enable with these cmds: [ bId , steer , speed, pitch, v_z, progress ]
                self.qBehavior.put( [ bId , 0.0 , spd, 0.0, 0.0, 0.0 ] )
            
            # execute the last turn computed
            e.wait(dtAvoid) # (sec) duration to pitch; interruptable sleep()
            
            self.qBehavior.put( [ bId , 0 ] ) # disable with [bId, 0]
        
        logging.debug('[{0}]: bId={1} [{2}], exiting.'.format( datetime.now().strftime('%c') ,bId,behName))



    # -----------------------------------------------------------------
    def avoidComputeOtherVehPositionInLocalFrame( self, veh, payload ):
        # helper function for avoid() behavior
        #
        # this function runs when an avoidance message was received by this
        # vehicle's avoid() behavior
        #   pos is the i'th vehicle's position
        #   payload contains information (from core) about the other incoming vehicle
        randFlag = veh.randFlag
        
        pos_i = veh.pos # (m) structure created within this vehicle model, see myVehicle __init__ constructor near: self.pos = myClass()
        pos_j = payload['pos'] # (m) 'the other guy's position' is a dict in a payload from Move Core, all_vehicles.py, poll_state(), checkDistVel() and 'theOtherOne'
        
        #print('pos_i={0},{1},{2}'.format(pos_i.X,pos_i.Y,pos_i.Z))
        #print('pos_j={0}'.format(pos_j))
        # vector from i'th (me) vehicle to j'th vehicle (the other guy) - recall vectors: "tip minus tail"
        dX = pos_j['X'] - pos_i.X # (m) X_j - X_i   in inertial XYZ frame
        dY = pos_j['Y'] - pos_i.Y # (m) Y_j - Y_i   in inertial XYZ frame
        dZ = pos_j['Z'] - pos_i.Z # (m) Z_j - Z_i   in inertial XYZ frame
        
        psi_i = pos_i.psi # (rad) my heading w.r.t. +X-axis
        
        # is the other guy in front or behind, and on my right or my left?
        #
        # see: Compere_handwritten_notes_Avoidance_maneuver_coord_transformation_Aug_2018.pdf
        # neglecting altitude difference:
        # d_x - location of the other vehicle in my reference frame (fore-to-aft)
        #      if d_x > 0, the other vehicle is in front of me
        #      if d_x < 0, the other vehicle is behind me
        #
        # d_y - location of the other vehicle in my reference frame (left-to-right)
        #      if d_y > 0, the other vehicle is on my right (so turn left to avoid)
        #      if d_y < 0, the other vehicle is on my left (so turn right to avoid)
        d_x = +cos(psi_i)*dX + sin(psi_i)*dY # (m) body-fixed x-axis projection of [dX,dY,dZ] vector
        d_y = -sin(psi_i)*dX + cos(psi_i)*dY # (m) body-fixed y-axis projection of [dX,dY,dZ] vector
        
        logging.debug('[{0}]: vid={1}, d_x={2:0.1f}(m), d_y={3:0.1f}(m), psi_i={4:0.2f}'.format( datetime.now().strftime('%c') , veh.vid, d_x, d_y, psi_i))
        
        return d_y, d_x



    # --------------------------------------------------------------
    #                  behavior: detectAndReport()
    # --------------------------------------------------------------
    # detectAndReport: monitor for priximity to another vehicle and report last-seen time and location
    def detectAndReport(self,bId,behName,priority,veh,debug):
        logging.debug('\t\t[{0}]: bId={1} [{2}], priority={3}'.format( datetime.now().strftime('%c') ,bId,behName,priority))
        e=veh.e
        #geom=veh.geom
        #geom_center = np.array([ geom.cg_X , geom.cg_Y , 0.0 ])
        
        #steer_max = 35*np.pi/180.0 # (rad) set lock-to-lock max steer limit of 35deg, from ME620 Adv. Veh. Dyn. (~0.6rad)
        #k_steer = 1.5 # tuned in Simulink, ME620 Advanced Vehicle Dynamics
        
        use_2d_dist=1 # (0/1) use 2D or 3D distance calculation for detection thresholding?
        dt = 1 # (s) proximity evaluation period
        while e.is_set() is False:
        
            e.wait(dt) # (sec) behavior is dormant for this duration; e.wait() is an interruptable sleep() with independent timers despite using the same event, e
            
            dist_XY = 1e10 # (m) large nunber to hinder detection unless computation indicates to the contrary
            logging.debug('detectAndReport(): qDetect.qsize()={0}'.format(veh.qDetect.qsize()))
            while not veh.qDetect.empty():
                # get latest and greatest position information from Core about object of interest (all_vehicles.py, poll_state() )
                # payload_detect = { 'vid':vid, 'X':pos['X'], 'Y':pos['Y'], 'Z':pos['Z'], 'lat':pos['lat'], 'lon':pos['lon'] }
                payload_detect = veh.qDetect.get()
                dX = veh.pos.X - payload_detect['X']
                dY = veh.pos.Y - payload_detect['Y']
                if use_2d_dist==1:
                    dZ=0.0
                else:
                    dZ = veh.pos.Z - payload_detect['Z']
                
                dist_XY = sqrt( pow(dX,2) + pow(dY,2) + pow(dZ,2) ) # (m) distance from this vehicle to the coordinates of interest
                
                if (debug>0): logging.debug('{0:s}, detectId={1}, qDetect.qsize()={2}, lastSeen={3:0.3f}(s), payload_detect={4}'.\
                                    format(behName, veh.detectMsg.objId, veh.qDetect.qsize(), veh.detectMsg.lastSeen,payload_detect))
            
            # nearby enough to detect?
            if (dist_XY <= self.detectThreshold):
                # yep, we're close enough to say this virtual vehicle could detect the object of interest
                #
                # --> THIS trigger is what a REAL vehicle could REALLY do with a REAL objects in the REAL world
                #
                veh.detectMsg.objId       = payload_detect['vid'] # object id you're looking for (e.g. a specific vid)
                veh.detectMsg.lastSeen    = time.time() # (s) timestamp from last-seen detection
                veh.detectMsg.lastLoc_X   = veh.pos.X # (m) location from last-seem detection
                veh.detectMsg.lastLoc_Y   = veh.pos.Y # (m)
                veh.detectMsg.lastLoc_Z   = veh.pos.Z # (m)
                veh.detectMsg.lastLoc_lat = veh.pos.lat # (decimal degrees)
                veh.detectMsg.lastLoc_lon = veh.pos.lon # (decimal degrees)
                if (debug>0):   logging.debug('{0:s},\t\t detected {1}!!!, lastSeen={2:0.3f}(s)'.\
                                format(behName, veh.detectMsg.objId, veh.detectMsg.lastSeen))
            
            if (debug>0):   logging.debug('{0:s}, detectId={1}, lastSeen={2:0.3f}(s)'.\
                            format(behName, veh.detectMsg.objId, veh.detectMsg.lastSeen))
        
        logging.debug('[{0}]: bId={1} [{2}], exiting.'.format( datetime.now().strftime('%c') ,bId,behName))



    # --------------------------------------------------------------
    #                  behavior: followRoute()
    # --------------------------------------------------------------
    # followRoute process: if enabled, provide steer and speed commands to follow
    # the route specified in the config file in ../scenario and waypoints
    # in the restore_waypoint() function defined in ../routes
    def followRoute(self,bId,behName,priority,veh,debug):
        logging.debug('\t\t[{0}]: bId={1} [{2}], priority={3}'.format( datetime.now().strftime('%c') ,bId,behName,priority))
        e=veh.e
        route=self.route
        routeCfg=self.routeCfg
        
        steer_max = 35*np.pi/180.0 # (rad) set lock-to-lock max steer limit of 35deg, from ME620 Adv. Veh. Dyn. (~0.6rad)
        k_steer = 1.5 # steer gain between 1 and 1.5 is good; tuned in Simulink, ME620 Advanced Vehicle Dynamics
        
        dt = 0.1 # (s) waypoint steering update period
        T_console_update = 1.0 # (s)
        N_console_update = T_console_update/dt # integer number of e.wait(dt)'s to skip before providing a console update
        
        if not hasattr(route,'i'):
            route.i = 1 # if IC has not been set at 1st waypoint, we must be aiming for 1st waypoint; route waypoints are 0-based
            #spd_mps_i=route.spd_mps[ route.i ]
        
        if not hasattr(route,'lap'):
            route.lap=1 # this should be set in route_init() in route_init.py in ./veh_model
        
        if ('waypointDelay' in routeCfg):
            waypointDelay = routeCfg['waypointDelay'] # make a dict of all waypoint delays, like: waypointDelay={3: 5.1, 7: 2.0}
            spd_of_zero = 0.0
            already_paused_at_this_waypoint=False
        
        loopCnt=0
        atEndOfLaps  = False # (T/F) this must be False to start route following and changes to True at the end
        atEndOfRoute = False # (T/F) this (also) must be False to start route following
        
        # compute initial distance to first waypoint, route.i
        dX            = route.X[ route.i ] - veh.pos.X # (m) X-component of vector pointing from veh to next waypoint (tip-tail)
        dY            = route.Y[ route.i ] - veh.pos.Y # (m) Y-component of veh-to-next-waypoint vector (tip - tail)
        dist_XY_start = np.sqrt( pow(dX,2) + pow(dY,2) ) # (m) 2D distance between next waypoint and vehicle
        
        logging.debug('{0}: entering loop starting at waypoint route.i=[{1}], dist_XY_start={2}'.format(behName,route.i,dist_XY_start))
        
        while e.is_set() is False:
            
            e.wait(dt) # (sec) behavior is dormant for this duration; e.wait() is an interruptable sleep() with independent timers despite using the same event, e
            
            loopCnt = loopCnt+1
            
            if (not atEndOfLaps) and (not atEndOfRoute):
                
                if (loopCnt%N_console_update)==0: # modulo test is True every N'th: test = ( (cnt%N)==0 )
                    logging.debug('{0}: route update, current waypoint route.i=[{1}, route.lap=[{2}]'.format(behName,route.i,route.lap))
                
                # --------------------------------------------------------------
                # steer toward the next waypoint - turn which way and how much? (based on 2D distance only)
                dX = route.X[ route.i ] - veh.pos.X # (m) X-component of vector pointing from veh to next waypoint (tip-tail)
                dY = route.Y[ route.i ] - veh.pos.Y # (m) Y-component of veh-to-next-waypoint vector (tip - tail)
                psi_to_waypoint = atan2( dY , dX ) # (rad) 4-quadrant arc-tangent provides orientation from veh to next waypoint
                
                psi_veh = veh.pos.psi         # (rad) current vehicle heading, which could be large from multiple turns (i.e. >> +/- 2pi)
                
                psi_err_raw = psi_to_waypoint - psi_veh # (rad) heading error; this could be a large number, like +/- 100, way beyond +/- pi
                
                # wrap heading error, psi_err_raw, such that psi_err is on [-pi  +pi]
                # credit: Mike Fair, Nov 2004
                spsi = sin(psi_err_raw)
                cpsi = cos(psi_err_raw)
                # psi_err is in body-fixed frame on inteval [-pi +pi] - this essentially says, turn left (-) or turn right (+)
                psi_err = atan2(spsi,cpsi) # (rad) heading error w.r.t. vehicle x-axis, atan2() returns [-pi  +pi]
                
                steer_raw = k_steer*psi_err # (rad) steering gain for path following (simple pursuit control law w/o lateral error term)
                steer = np.clip( steer_raw , -steer_max, +steer_max) # (rad) impose max steer angle, clip is numpy's saturation function
                logging.debug('[{0}]: steer_max={1}, steer_raw={2}, steer={3}'.format( datetime.now().strftime('%c') ,steer_max,steer_raw,steer))
                # --------------------------------------------------------------
                
                # what is velocity command between these 2 waypoints?
                spd_mps_i=route.spd_mps[ route.i ] # (m/s) this speed is held constant for the entire waypoint segment
                
                if ('waypointDelay' in routeCfg) and (route.i in waypointDelay) and already_paused_at_this_waypoint==False:
                    logging.debug('{0}: discovered a waypointDelay at route.i=[{1}], setting speed=0 and waiting {2} seconds...'.format(behName,route.i, waypointDelay[route.i]))
                    self.qBehavior.put( [ bId , steer , spd_of_zero, 0.0, 0.0, 0.0 ] ) # [ bId , steer , speed, pitch, v_z, progress ]
                    time.sleep( waypointDelay[route.i] )
                    already_paused_at_this_waypoint=True # just pause once during this waypoint
                    logging.debug('{0}: done! resuming previous velocity, spd_mps_i={1}, at route.i={2}'.format(behName,spd_mps_i,route.i))
                    self.qBehavior.put( [ bId , steer , spd_mps_i, 0.0, 0.0, 0.0 ] ) # [ bId , steer , speed, pitch, v_z, progress ]
                
                # --------------------------------------------------------------
                # check how close vehicle is to the next waypoint
                dist_XY = np.sqrt( pow(dX,2) + pow(dY,2) ) # (m) 2D distance between next waypoint and vehicle
                # if vehicle is close, trigger the increment to the next waypoint
                if (dist_XY < 2*veh.L_char):
                    route.i = route.i + 1 # increment waypoint index
                    already_paused_at_this_waypoint=False # reset waypointDelay flag for this new waypoint
                    if (debug>0): logging.debug('{0:s}'.format(behName))
                    if (debug>0): logging.debug('{0:s}, distance threshold reached - heading to the next waypoint! route.i={1}, route.lap={2}'.format(behName, route.i, route.lap))
                    if (debug>0): logging.debug('{0:s}'.format(behName))
                    
                    # if you're not doing laps and want to end at endingWaypoint:
                    if ('endingWaypoint' in routeCfg) and (routeCfg['endingWaypoint'] != -1) and (route.i>=routeCfg['endingWaypoint']):
                            atEndOfRoute = True
                            if routeCfg['endOption'] == 'stop':
                                spd_mps_i = 0
                                if (debug>0): logging.debug('{0:s}, reached endingWaypoint - STOPing with v=0!'.format(behName))
                                if (debug>0): logging.debug('{0:s}, final waypoint: {1}; lap num: {2} '.format(behName, route.i, route.lap))
                                veh.qRoute.put( [route.i, route.lap, spd_mps_i] ) # add message for gather_outputs() in myVehicle.py
                    
                    # if there are N waypoints, increment lap counter when route.i>=N
                    # b/c python is 0-based (if route.i=20 and max waypoints is 19,
                    # you're at the last waypoint so increment lap counter at route.i=20)
                    if (route.i>=route.N): # routes and waypoints are 0-based so the i'th waypoint is 1 less in the route definition file
                        # increment lap counter
                        route.lap = route.lap + 1
                        route.i   = routeCfg['lapRestartWaypoint'] # steer toward lapRestartWaypoint
                        if (debug>0): logging.debug('{0:s}, end of waypoints - starting lap [{1}] and heading toward waypoint {2}'.format(behName, route.lap, route.i))
                        veh.qRoute.put( [route.i, route.lap, spd_mps_i] ) # add message for gather_outputs() in myVehicle.py
                        
                        # upon reaching last waypoint, continue at first waypoint or stop?
                        if (route.lap>=route.nLapsMax):
                            atEndOfLaps = True
                            if routeCfg['endOption'] == 'stop':
                                spd_mps_i = 0
                                if (debug>0): logging.debug('{0:s}, end of waypoints and all laps - STOP with v=0!'.format(behName))
                                if (debug>0): logging.debug('{0:s}, final number of laps: '.format(behName, route.lap-1))
                                veh.qRoute.put( [route.i, route.lap, spd_mps_i] ) # add message for gather_outputs() in myVehicle.py
                    veh.qRoute.put( [route.i, route.lap, spd_mps_i] ) # add message for gather_outputs() in myVehicle.py; status update only for monitoring
                    
                    # recompute dist_XY_start at new waypoint once route.i is determined
                    dX            = route.X[ route.i ] - veh.pos.X # (m) X-component of vector pointing from veh to next waypoint (tip-tail)
                    dY            = route.Y[ route.i ] - veh.pos.Y # (m) Y-component of veh-to-next-waypoint vector (tip - tail)
                    dist_XY_start = np.sqrt( pow(dX,2) + pow(dY,2) ) # (m) 2D distance between next waypoint and vehicle
                
                if (debug>1): logging.debug('{0:s}, bId={1:d}, pri={2:d}: steer={3:f}(rad), spd={4:f}(m/s)'.format(behName, bId, priority, steer, spd_mps_i))
                
                # enable and update with these cmds: [ bId , steer , speed, pitch, progress ]
                progressDist = (dist_XY_start-dist_XY) / dist_XY_start # [0 1] progress on distance covered since starting this waypoint
                self.qBehavior.put( [ bId , steer , spd_mps_i, 0.0, 0.0, progressDist ] ) # [ bId , steer , speed, pitch, v_z, progress ]
            
            else: # we're at the end of the route - stop navigating
                self.qBehavior.put( [ bId , 0 ] ) # disable this behavior with [bId, 0]
                dt = 1 # (s) go back to slower polling while no longer computing a dynamic steering input
                if (debug>0): logging.debug('{0:s}, disabling bId={1:d}'.format(behName, bId, priority))
                
        logging.debug('[{0}]: bId={1} [{2}], exiting.'.format( datetime.now().strftime('%c') ,bId,behName))
    
    
    
    
    
    
    
    # --------------------------------------------------------------
    #                  behavior: goToGate()
    # --------------------------------------------------------------
    # periodic turn: steer toward the next gate; if out of perpendicular gate path, steer towards the far gate post
    def goToGate(self,bId,behName,priority,veh,debug):
        logging.debug('\t\t[{0}]: bId={1} [{2}], priority={3}'.format( datetime.now().strftime('%c') ,bId,behName,priority))
        e=veh.e
        gates         = self.gates.gates # class with: gates.gates, gates.firstGate, gates.lap
        lap           = self.gates.lap
        firstGate     = self.gates.firstGate
        randFlag      = veh.randFlag # (0/1) use random numbers?
        
        steer_max = 35*np.pi/180.0 # (rad) set lock-to-lock max steer limit of 35deg, from ME620 Adv. Veh. Dyn. (~0.6rad)
        k_steer = 1.5 # steer gain between 1 and 1.5 is good; tuned in Simulink, ME620 Advanced Vehicle Dynamics
        
        dt = 0.2 # (s) gate steering update period
        T_console_update = 3.0 # (s)
        N_console_update = T_console_update/dt # integer number of e.wait(dt)'s to skip before providing a console update
                
        current_gate = self.gates.current_gate # gate names are keys in the config file; strings like 'gate_1' or whatever is in the .cfg file
        last_gate = current_gate
        #randNum = randFlag*random.uniform(0.0,+1.0)
        
        #logging.debug('gate={0}'.format(gates))
        A = np.array([ gates[ current_gate ]['ptA_X'], gates[ current_gate ]['ptA_Y'] ]) #  (m) 2D gate calculation only; RHR from post A to post B with +Z down defines which side is (+) side of gate
        B = np.array([ gates[ current_gate ]['ptB_X'], gates[ current_gate ]['ptB_Y'] ]) #  (m) post B of current gate
        P = np.array([ veh.pos.X, veh.pos.Y ]) #  (m) 2D gate calculation only
        (s0,L_s0,psi_to_gate,dist_XY,side) = compute_perpendicular_angle_to_line_in_space(A,B,P)
        dist_XY_start = dist_XY # (m) 2D distance between next gate and vehicle
        
        loopCnt=0
        logging.debug('{0}: entering loop starting at gate [{1}]'.format(behName,current_gate))
        while e.is_set() is False:
            
            e.wait(dt) # (sec) behavior is dormant for this duration; e.wait() is an interruptable sleep() with independent timers despite using the same event, e
            
            loopCnt = loopCnt+1
            
            if (loopCnt%N_console_update)==0: # modulo test is True every N'th: test = ( (cnt%N)==0 )
                logging.debug('{0}: time-based update, current gate=[{1}]'.format(behName,current_gate))
            # --------------------------------------------------------------
            # steer toward the gate - turn which way and how much? (based on 2D distance only)
            # see: Compere_handwritten_notes_shortest_perpendicular_distance_from_point_to_line_in_space.2020.05.26.pdf
            
            # compute s0 perpendicular to gate line from A to B; this determines if vehicle
            # is to the left of the gate (pt A), in the gate, or to the right of the gate (pt B)
            P = np.array([ veh.pos.X, veh.pos.Y ]) #  (m) 2D gate calculation only
            
            (s0,L_s0,psi_to_gate,dist_XY,side) = compute_perpendicular_angle_to_line_in_space(A,B,P)
            #logging.debug('[{0}]: s0={1}, L_s0={2}, psi_to_gate={3}, dist_XY={4}, side={5}'.format( datetime.now().strftime('%c') ,s0,L_s0,psi_to_gate,dist_XY,side))
            
            psi_veh = veh.pos.psi         # (rad) current vehicle heading, which could be large from multiple turns (i.e. >> +/- 2pi)
            
            psi_err_raw = psi_to_gate - psi_veh # (rad) heading error; this could be a large number, like +/- 100, way beyond +/- pi
            
            # bound heading error, psi_err_raw, such that psi_err is on [-pi  +pi]
            # credit: Mike Fair, Nov 2004
            spsi = sin(psi_err_raw)
            cpsi = cos(psi_err_raw)
            # psi_err is in body-fixed frame on inteval [-pi +pi] - this essentially says, turn left or turn right
            psi_err = atan2(spsi,cpsi) # (rad) heading error w.r.t. vehicle x-axis, atan2() returns [-pi  +pi]
            
            steer_raw = k_steer*psi_err # (rad) steering gain for path following (simple pursuit control law w/o lateral error term)
            steer = np.clip( steer_raw , -steer_max, +steer_max) # (rad) impose max steer angle, clip is numpy's saturation function
            #logging.debug('[{0}]: steer_max={1}, steer_raw={2}, steer={3}'.format( datetime.now().strftime('%c') ,steer_max,steer_raw,steer))
            
            
            # --------------------------------------------------------------
            # if vehicle has reached current gate, trigger the increment to the next gate
            if (dist_XY <= 1.0*veh.L_char):
                if (debug>0): logging.debug('{0:s}'.format(behName))
                if (debug>0): logging.debug('{0:s}, reached current gate=[{1}]'.format(behName, current_gate))
                if (debug>0): logging.debug('{0:s}'.format(behName))
                
                last_gate    = current_gate # capture current gate num before it's reassigned
                current_gate = gates[ current_gate ]['nextGate'] # figure out where to go next based on what's in the current gate's 'nextGate' dictionary entry (this is assigned in the config file)
                #randNum = randFlag*random.uniform(0.0,+1.0) # update random amount to steer towards the center of the gate to prevent gathering near the closest ends of two gates
                
                if (debug>0): logging.debug('{0:s}, headed to next gate=[{1}]'.format(behName, current_gate))
                A = np.array([ gates[ current_gate ]['ptA_X'], gates[ current_gate ]['ptA_Y'] ]) #  (m) 2D gate calculation only; RHR from post A to post B with +Z down defines which side is (+) side of gate
                B = np.array([ gates[ current_gate ]['ptB_X'], gates[ current_gate ]['ptB_Y'] ]) #  (m) post B of current gate
                dist_XY_start = dist_XY # (m) 2D distance between next gate and vehicle
                
                if (current_gate == firstGate): # increment lap counter; these are both strings
                    lap = lap + 1
                
                veh.qGate.put( [current_gate, lap, veh.vel.spd_mps] ) # add message for gather_outputs() in myVehicle.py; status update only for monitoring
                    
                if (debug>1): logging.debug('{0:s}, bId={1:d}, pri={2:d}: steer={3:f}(rad), spd={4:f}(m/s)'.format(behName, bId, priority, steer, veh.vel.spd_mps))
                
            progressDist = (dist_XY_start-dist_XY) / dist_XY_start # [0 1] progress on distance covered since starting this waypoint
            # enable and update with these cmds: [ bId , steer , speed, pitch, v_z, progress ] # veh.vel.spd_mps
            self.qBehavior.put( [ bId , steer , veh.vel.spd_mps, 0.0, 0.0, progressDist ] ) # assign speed equal to current speed (no change to speed command with gates)
                
        logging.debug('[{0}]: bId={1} [{2}], exiting.'.format( datetime.now().strftime('%c') ,bId,behName))
        
        
        
        
        
        
        
        
        
        
        
    # --------------------------------------------------------------
    #                  behavior: goToPoint()
    # --------------------------------------------------------------
    # go to point : steer toward the next point
    # mission-enabled?: Yes, this is the first mission-enabled behavior
    def goToPoint(self,bId,behName,priority,veh,debug):
        
        logging.debug('\t\t[{0}]: bId={1} [{2}], priority={3}'.format( datetime.now().strftime('%c') ,bId,behName,priority))
        e=veh.e
        points          = self.points.points # class with: points.points, points.IC_pt, points.lap
        lap             = self.points.lap
        IC_pt           = self.points.IC_pt
        randFlag        = veh.randFlag # (0/1) use random numbers?
        runStateLast    = veh.runState[0]
        runStateChanged = False # make local decisions on runState changes
        
        steer_max = 35*np.pi/180.0 # (rad) set lock-to-lock max steer limit of 35deg, from ME620 Adv. Veh. Dyn. (~0.6rad)
        k_steer = 1.5 # steer gain between 1 and 1.5 is good; tuned in Simulink, ME620 Advanced Vehicle Dynamics
        
        dt = 0.2 # (s) steering update period
        T_console_update = 3.0 # (s)
        N_console_update = T_console_update/dt # integer number of e.wait(dt)'s to skip before providing a console update
        
        point_cnt      = 0
        current_point  = self.points.current_point # points are 1-based, by convention only; enforce 1-based points in config file also
        last_point     = current_point
        rThreshold     = 1.0*veh.L_char # (m) radius for triggering point-reached
        Z_BL           = 0.5 # (m) boundary layer in inertial Z direction for tanh() function to achieve commanded vertical setpoint: u_z = zDotMax*tanh( dZ/Z_BL )
        Z_threshold    = 0.01 # (m) elevation threshold for triggering point-reached in Z-direction
        zDotMax        = 1.0 # (m/s) body-fixed max elevation rate for elevation changes (e.g. during take-off and landings)
        #randNum = randFlag*random.uniform(0.0,+1.0)
        
        velCmd_xy      = points[ current_point ]['vel'] # (m/s) horizontal speed command
        dX             = points[ current_point ]['pt_X'] - veh.pos.X  # (m) X-component of vector pointing from veh to next waypoint (tip-tail)
        dY             = points[ current_point ]['pt_Y'] - veh.pos.Y  # (m) Y-component of veh-to-next-waypoint vector (tip - tail)
        dZ             = points[ current_point ]['pt_Z'] - veh.pos.Z  # (m) Z-component of veh-to-next-waypoint vector (tip - tail)
        dist_XYZ_start = np.sqrt( pow(dX,2) + pow(dY,2) + pow(dZ,2) ) # (m) 3D distance between next waypoint location and vehicle's current position
        
        # discriminate between a sequence of points and usingMissionCommands
        goToPointActive=True # prioritize() will always see goToPoint() with hand raised
        if (veh.usingMissionCommands==True):
            goToPointActive=False # only raise hand when missionStateSequencer tells goToPoint() when to activate
        
        loopCnt=0
        logging.debug('{0}: entering loop starting at point [{1}], goToPointActive={2}'.format(behName,current_point,goToPointActive))
        while e.is_set() is False:
            
            e.wait(dt) # (sec) behavior is dormant for this duration; e.wait() is an interruptable sleep() with independent timers despite using the same event, e
            
            loopCnt = loopCnt+1
            
            # use local var to capture veh.runState change that occurred (only) in main_veh_model.py | main()
            if (runStateLast is not veh.runState[0]):
                runStateChanged = True
                runStateLast    = veh.runState[0]
            else:
                runStateChanged = False
            
            if (loopCnt%N_console_update)==0: # modulo test is True every N'th: test = ( (cnt%N)==0 )
                logging.debug('{0}: time-based update, current point=[{1}]'.format(behName,current_point))
            
            
            
            # if there are any missionCommands for this particular vehicle, then listen to missionStateSequencer()
            # otherwise, march through the points
            if (veh.usingMissionCommands==True) and (len(veh.goToPointCmd)>0): # flag for behaviors to activate from missionStateSequencer() or 'nextPoint' or 'nextGate'?
                # check for new commands from missionStateSequencer()
                goToPointActive = True          # (0/1) is goToPoint behavior active for prioritize() to select?
                cmdMsg          = veh.goToPointCmd.pop() # cmdMsg={'pt':pt, 'vel':vel, 'rThresh':rThresh, 'arrivalType':arrivalType}
                current_point   = cmdMsg['pt']  # go to this point now (regardless of approach to previous point)
                velCmd_xy       = cmdMsg['vel'] # (m/s) go this fast
                zDotMax         = cmdMsg['riseRate'] # (m/s) rise rate for vertical maneuvers to hit an elevation setpoint
                dX              = points[ current_point ]['pt_X'] - veh.pos.X  # (m) X-component of vector pointing from veh to next waypoint (tip-tail)
                dY              = points[ current_point ]['pt_Y'] - veh.pos.Y  # (m) Y-component of veh-to-next-waypoint vector (tip - tail)
                dZ              = points[ current_point ]['pt_Z'] - veh.pos.Z  # (m) set IC on Z for this point
                dist_XYZ_start  = np.sqrt( pow(dX,2) + pow(dY,2) + pow(dZ,2) ) # (m) 3D distance between next waypoint location and vehicle's current position
                
                logging.debug('{0}: just received missionStateSequencer command! new current point=[{1}], goToPointActive={2}'.format(behName,current_point,goToPointActive))
                logging.debug('{0}: resetting distance to current_point={1}! dist_XYZ_start=[{2}](m), dZ=[{3}](m)'.format(behName,current_point,dist_XYZ_start,dZ))
            
            #  if runState == 'set', but just once upon change
            if (veh.runState[0]==2) and (runStateChanged==True):
                # this will set the progressDist correctly at first waypoint
                velCmd_xy       = points[ current_point ]['vel'] # (m/s)
                dX              = points[ current_point ]['pt_X'] - veh.pos.X  # (m) X-component of vector pointing from veh to next waypoint (tip-tail)
                dY              = points[ current_point ]['pt_Y'] - veh.pos.Y  # (m) Y-component of veh-to-next-waypoint vector (tip - tail)
                dZ              = points[ current_point ]['pt_Z'] - veh.pos.Z  # (m) Z-component of veh-to-next-waypoint vector (tip - tail)
                dist_XYZ_start  = np.sqrt( pow(dX,2) + pow(dY,2) + pow(dZ,2) ) # (m) 3D distance between next waypoint location and vehicle's current position
                logging.debug('{0}: resetting distance to current_point={1}! dist_XYZ_start=[{2}](m)'.format(behName,current_point,dist_XYZ_start))
                runStateChanged=False
            
            # --------------------------------------------------------------
            
            # steer toward the next waypoint - turn which way and how much? (based on 2D distance only)
            dX              = points[ current_point ]['pt_X'] - veh.pos.X  # (m) X-component of vector pointing from veh to next waypoint (tip-tail)
            dY              = points[ current_point ]['pt_Y'] - veh.pos.Y  # (m) Y-component of veh-to-next-waypoint vector (tip - tail)
            dZ              = points[ current_point ]['pt_Z'] - veh.pos.Z  # (m) Z-component of veh-to-next-waypoint vector (tip - tail)
            dist_XY         = np.sqrt( pow(dX,2) + pow(dY,2) )             # (m) 2D distance between next waypoint and vehicle
            dist_XYZ        = np.sqrt( pow(dX,2) + pow(dY,2) + pow(dZ,2) ) # (m) 3D distance between next waypoint and vehicle
            velCmd_z        = zDotMax*tanh( dZ/Z_BL ) # (m/s) vel command for changing elevations is a saturation function tanh() with a boundary layer
            
            if (dist_XYZ_start>0):
                self.pctCompleteGoToPoint = (dist_XYZ_start-dist_XYZ) / dist_XYZ_start # [0 1] progress on distance covered since starting this waypoint
            else:
                self.pctCompleteGoToPoint = 0.0
            
            
            psi_to_point = atan2( dY , dX ) # (rad) 4-quadrant arc-tangent provides orientation from veh to next waypoint
            psi_veh = veh.pos.psi         # (rad) current vehicle heading, which could be large from multiple turns (i.e. >> +/- 2pi)
            psi_err_raw = psi_to_point - psi_veh # (rad) heading error; this could be a large number, like +/- 100, way beyond +/- pi
            
            # bound heading error, psi_err_raw, such that psi_err is on [-pi  +pi]
            # credit: Mike Fair, Nov 2004
            spsi = sin(psi_err_raw)
            cpsi = cos(psi_err_raw)
            # psi_err is in body-fixed frame on inteval [-pi +pi] - this essentially says, turn left or turn right
            psi_err = atan2(spsi,cpsi) # (rad) heading error w.r.t. vehicle x-axis, atan2() returns [-pi  +pi]
            
            steer_raw = k_steer*psi_err # (rad) steering gain for path following (simple pursuit control law w/o lateral error term)
            steer = np.clip( steer_raw , -steer_max, +steer_max) # (rad) impose max steer angle, clip is numpy's saturation function
            #logging.debug('[{0}]: steer_max={1}, steer_raw={2}, steer={3}'.format( datetime.now().strftime('%c') ,steer_max,steer_raw,steer))
            
            if (dist_XY <= rThreshold):
                logging.debug('{0:s}, reached XY location for points=[{1}]! setting horizontal velCmd_xy=0'.format(behName, current_point))
                velCmd_xy = 0.0 # (m/s) if you're at the (lat,lon) coordinates, then stop (assuming a multi-rotor or VTOL that *can* stop in mid-air)
            
            # --------------------------------------------------------------
            # if vehicle has reached current point in XY and Z directions, trigger the increment to the next point            
            if (dist_XY <= rThreshold) and (abs(dZ) < Z_threshold) and (veh.runState[0]==3) and (goToPointActive==True):
                if (debug>0): logging.debug('{0:s}'.format(behName))
                if (debug>0): logging.debug('{0:s}, reached current point=[{1}]'.format(behName, current_point))
                
                last_point = current_point # capture current point num before it's reassigned
                
                # reached the current_point
                if (veh.usingMissionCommands==True):
                    goToPointActive = False   # (0/1) is goToPoint behavior active for prioritize() to select?
                    veh.goToPointDone.set()   # tell missionStateSequencer() the point was reached
                    
                    # disable this behavior; "put your hand down" so prioritize() no longer selects this behavior; note: make sure there is a lower priority behvaior still enabled and selectable like 'hover' or 'wander'
                    self.qBehavior.put( [ bId , 0 ] ) # disable with [bId, 0]
                    logging.debug('{0:s}, reached point=[{1}]. disabling goToPoint()'.format(behName, current_point))
                else:
                    # proceed to 'nextPoint'
                    current_point = points[ current_point ]['nextPoint'] # figure out where to go next based on what's in the current point's 'nextPoint' dictionary entry (this is assigned in the config file)
                    logging.debug('{0:s}, headed to next point=[{1}]'.format(behName, current_point))
                    velCmd_xy       = points[ current_point ]['vel'] # (m/s) retrieve velocity associated wtih this new waypoint
                    #velCmd_z        = 0.0 # (m/s) elevation rate, positive or negative
                    dX              = points[ current_point ]['pt_X'] - veh.pos.X  # (m) X-component of vector pointing from veh to next waypoint (tip-tail)
                    dY              = points[ current_point ]['pt_Y'] - veh.pos.Y  # (m) Y-component of veh-to-next-waypoint vector (tip - tail)
                    dZ              = points[ current_point ]['pt_Z'] - veh.pos.Z  # (m) Z-component of veh-to-next-waypoint vector (tip - tail)
                    dist_XYZ_start  = np.sqrt( pow(dX,2) + pow(dY,2) + pow(dZ,2) ) # (m) 3D distance between next waypoint location and vehicle's current position
                
                if (current_point==IC_pt): # increment lap counter
                    lap = lap + 1
                
                if (debug>1): logging.debug('{0:s}, bId={1:d}, pri={2:d}: steer={3:f}(rad), spd={4:f}(m/s)'.format(behName, bId, priority, steer, veh.vel.spd_mps))
            
            veh.qPoint.put( [current_point, lap, veh.vel.spd_mps] ) # add message for gather_outputs() in myVehicle.py; status update only for monitoring
            
            # enable and update with these cmds: [ bId , steer , speed, pitch, v_z, progress ] # veh.vel.spd_mps
            if (goToPointActive==True):
                self.qBehavior.put( [ bId , steer , velCmd_xy, 0.0, velCmd_z, self.pctCompleteGoToPoint ] ) # assign speed equal to current speed (no change to speed command with points)
            
            
        logging.debug('[{0}]: bId={1} [{2}], exiting.'.format( datetime.now().strftime('%c') ,bId,behName))
        
        
        
    # --------------------------------------------------------------
    #                  behavior: multiRotorHover()
    # --------------------------------------------------------------
    # behavior to stay still in case goToPoint() and goToGate() are disabled
    # multirotor equivalent of default wander process with lowest priority, but for UAV
    def multiRotorHover(self,bId,behName,priority,veh,debug):
        logging.debug('\t\t[{0}]: bId={1} [{2}], priority={3}'.format( datetime.now().strftime('%c') ,bId,behName,priority))
        
        self.qBehavior.put( [ bId , 0.0 , 0.0, 0.0, 0.0, 0.0 ]) # enable with these cmds: [ bId , steer , speed, pitch, v_z, progress ]
        








if __name__ == "__main__":
    
    from myVehicle import MyVehicle
    from readConfigFile import readConfigFile
    from route_init import route_init
    
    # class MyVehicle:
    #     pass # dummy vehicle class for testing Behaviors class
    
    debug=1 # (0/1/2/3) 0->none, 1->some, 2->more, 3->lots
    vid = 100 # vid == vehicle identifier for this vehicle process, assigned by MoVE core
    
    cfgFile = '../scenario/default.cfg' # python's .ini format config file
    cfgFile = '../scenario/point_figure_8.cfg'
    cfgFile = '../scenario/point_homerun.cfg'
    cfgFile = '../scenario/missionTestWaitTimes.cfg' # config file with easily-test-able time-based delays
    #cfgFile = '../scenario/missionTestWaitTimesAndgoToPoint.cfg' # time delays and goToPoint() to develop missionState behavior enable/disable
    
    cfg, veh_names_builtins, veh_names_live_gps   = readConfigFile( cfgFile, vid ) 
    
    cfg.live_gps_follower = False # (True/False)
    cfg.name = "behaviors testing"
    cfg.runState          = [1]   # initial runstate; valid range is: [1 5], note this is a mutable *list* not an integer so subsequent variables reference the object not the value
    cfg.runStatePrev      =  0    # created in cfg. for behavior accessibility
    
    
    cfg = route_init(cfg) # this creates cfg.routeCfg ; the route_init() function is in routes_functions.py in ./veh_model directory
    #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
    
    # init the vehicle object and launch behavior threads
    veh = MyVehicle(cfg, 0)
    
    cnt=0
    main_thread = threading.main_thread()
    nThreadsAlive = threading.active_count()
    logging.debug('nThreadsAlive='.format(nThreadsAlive))
    
    try:
        while nThreadsAlive>1:
            
            logging.debug('-------------------------------------')
            nThreadsAlive = threading.active_count()
            logging.debug('{0} threads alive, cnt={1}'.format(nThreadsAlive,cnt) )
            #logging.debug('beh.qBehavior.qsize()={0}, beh.qCmdVeh.qsize()={1}, beh.qBehInfo.qsize()={2}'.format( qBehavior.qsize() , beh.qCmdVeh.qsize(), beh.qBehInfo.qsize() ) )
            # note: this qCmdVeh and qBehInfo queues have no consumers unless connected to the vehicle model
            #       which means running this __main__ will have an accumulating qCmdVeh queue size
            
            veh.e.wait(5) # interruptable sleep() wait's unless event flag is set
            
            cnt+=1
            if cnt>5 and veh.e.is_set() is not True:
                print('\n\n\nsending exit event to all threads\n\n\n')
                veh.e.set()
            
        print('nThreadsAlive={}, main_thread exiting.'.format(nThreadsAlive))
        
        
    except KeyboardInterrupt as err:
        print("caught keyboard ctrl-c:".format(err))
        veh.exit()     # exit myVehicle, v2v, behavior, and mState threads
        print("exiting.")
        exit(0)




