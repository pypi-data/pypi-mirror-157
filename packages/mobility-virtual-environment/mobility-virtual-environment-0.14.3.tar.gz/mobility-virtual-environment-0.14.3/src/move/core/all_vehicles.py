# VehStates.py - class definitions for gathering and using all vehicle states
#                in a running main_core.py process
#
# Marc Compere, comperem@gmail.com
# created : 29 Jul 2018
# modified: 26 Jun 2022
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

import sys
import time
from datetime import datetime
import copy # copy.deepcopy()
import threading
import numpy as np
import logging
import pprint
from math import sqrt
import struct # for viz udp output
import socket # for viz udp output
import msgpack
import csv # for DictWriter logging to .csv
import code # drop into a python interpreter to debug using: code.interact(local=dict(globals(), **locals()))

#from numba import jit # for making checkDistVel() faster

logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-14s) %(message)s',
)

# csv DictWriter needs fieldnames
# expand the vehInfo dictionary with all unique fieldnames for use with the .csv file only
def generateFieldnames(vehInfo):
    # create unique fieldnames from a dictionary containing dictionaries
    fieldnames=[] # DictWriter will create a .csv with these header names
    newVehInfo={}
    cnt=1
    
    for k,v in vehInfo.items():
        
        # is a dictionary?
        if (type(v) is dict):
            for kk,vv in v.items():
                #print('cnt={0}, k={1}, kk={2}, vv={3}'.format(cnt,k,kk,vv))
                name='{0}_{1}'.format(k,kk)
                fieldnames.append(name)
                newVehInfo[name]=vv
                cnt+=1
        
        elif (type(v) is list):
            #code.interact(local=dict(globals(), **locals()))
            for num,listItem in enumerate(v):
                if (type(listItem) is dict):  # handle dict within the list (within the dict)
                    for kk,vv in listItem.items():
                        name='{0}_{1}'.format(k,kk)
                        fieldnames.append(name)
                        newVehInfo[name]=vv
                else: # handle lists within the list (within the dict)
                    #print('cnt={0}, name=[{1}] , listItem=[{2}]'.format(cnt,name,listItem))
                    name='{0}_{1}'.format(k,num)
                    fieldnames.append(name)
                    newVehInfo[name]=listItem
                    cnt+=1        
        
        else:
            #print('cnt={0}, k=[{0}] , v=[{1}]'.format(cnt,k,v))
            fieldnames.append(k)
            newVehInfo[k]=v
            cnt+=1
    
    return fieldnames, newVehInfo




class All_vehicles:
    """ a class for aggregating and processing information from all vehicles """
    
    def __init__( self, cfg, debug ):
        
        self.nVehTot     = cfg.nVehTot
        #self.e          = e # event for stopping threads from main
        self.vid_base    = cfg.vid_base
        self.tStart      = cfg.tStart
        self.tNow        = time.time()
        self.tLast       = 0       # tLast will be updated before use
        self.detectThreshold = cfg.detectThreshold
        print('\n\n\nself.detectThreshold = {0}'.format(self.detectThreshold))
        self.dist        = np.zeros((self.nVehTot, self.nVehTot))  # (row,col), zero-based indices
        self.distLast    = np.zeros((self.nVehTot, self.nVehTot))  # (row,col), zero-based indices
        self.distTable   = np.zeros(( int(((self.nVehTot*self.nVehTot)-self.nVehTot)/2) , 4 )) # ( (n^2-n)/2 ,4) provides 1 row for each possible distance: [ dist, distRate, ith_veh, jth_veh ]
        self.debug       = debug
        self.logfile     = cfg.logfile # (0/1)
        self.fname       = cfg.fname   # 2022_01_26__13_34_46_core_State.csv
        self.fd          = cfg.fd
        self.pp          = pprint.PrettyPrinter(indent=4)
        self.firstVehMsg = True # trigger for creating csv DictWriter and fieldnames; trigger for first loop to received a message from a vehicle model
        
        # udp messages out for Bokeh visualizaton client, 1 vehicle at a time
        self.vizSock       = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) # udp/ip
        self.vizUdpEnabled = cfg.vizUdpEnabled
        self.vizIp         = cfg.vizIp
        self.vizPort       = cfg.vizPort
        
        # udp messages out for Bokeh dashboard status updates, 1 vehicle at a time
        self.dashSock       = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) # udp/ip
        self.dashIp         = cfg.dashIp
        self.dashPort       = cfg.dashPort
        
        # udp messages out for time series database logging of State
        self.dbUdpEnabled  = cfg.dbUdpEnabled
        self.dbSock        = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) # udp/ip
        self.dbIp          = cfg.dbIp
        self.dbPort        = cfg.dbPort
    
    # =======================================================================================
    #                                  poll_state()
    # =======================================================================================
    # consumer! - periodic request to producer (aggregator) for updated State snapshot
    # see: Compere_handwritten_notes_All_to_All_distance_calculation_order_Jul_2018.pdf
    def poll_state(self,e,eDataPollReq,qState,qVehCmd,cfg):
        logging.debug('Starting poll_state() thread')
        pollCnt=0
        
        #dt=0.1 # (s) debugging
        debug = self.debug
        pp    = self.pp
        tStart = self.tStart
        payload_detect = { 'vid':-1, 'X':-1, 'Y':-1, 'Z':-1, 'lat':-1, 'lon':-1 } # initial payload_detect dict for detectAndReport() behavior
        
        while e.is_set() is False:
            
            # cfg.dtOut sets loop rate interval for viz, db, and csv logging output; dt is delay for State update requests to aggregator()
            
            e.wait(cfg.dtOut) # e.wait() is an interruptable sleep() for graceful thread exit
            
            #logging.debug('')
            if debug>1: logging.debug('[{0}] requesting new State snapshot from aggregator()'.format( datetime.now().strftime('%c') ))  # this tells producer to prepare and send data over
            
            eDataPollReq.set() # signal to producer (aggregator) requesting new State snapshot
            
            # if-else statement is needed for graceful exit to avoid waiting on a blocking queue.get
            if e.is_set() is False:
            
                # the entire State struct gets sent here from aggregator() in core_udp_io.py
                State = qState.get(block=True) # get shared data, block until producer (aggregator) puts State there
                nVehInState = len(State)
                if debug>1: logging.debug("[{0}]: pollCnt={1}, received State with {2} vehicles, sizeof(State)={3}".format( datetime.now().strftime('%c') , pollCnt, nVehInState, sys.getsizeof(State)))
                if nVehInState < self.nVehTot:
                    logging.debug('')
                    logging.debug('[{0}]: ---> warning - {1} vehicles out of {2} reporting properly!'.format( datetime.now().strftime('%c') ,nVehInState,self.nVehTot))
                    logging.debug('')
                    #continue # "continues with the next cycle of the nearest enclosing loop"  (which is 'while self.e.is_set() is False')
                
                if debug>1:
                    print('\nState:')
                    pprint.pprint(State)
                    print('\n')
                
                if nVehInState>0:
                    #logging.debug("State object is {0} bytes with State.keys()={1}".format( State.__sizeof__(), State.keys() ))
                    for vid in list(State): # list(State) avoids 'RuntimeError: dictionary changed size during iteration'
                        #logging.debug('vid={0}'.format(vid))
                        #logging.debug('\nState[{0}]={1}'.format(vid,State[vid]))
                        vehName           = State[vid]['vehName']
                        srtStr            = round( State[vid]['srt_err_avg'] ,4)
                        pos               = State[vid]['pos']                # pos is [X,Y,Z, lat,lon, psi], psi is heading in radians
                        #logging.debug('--> pos={}'.format(pos))                # b'pos': {b'X': -179.98957857616685, b'Y': 121.98252730265973, b'Z': 0.0, b'psi': -5.01169680274724, b'lat': 29.18962333484992, b'lon': -81.04748481932248}
                        vel               = State[vid]['vel']                # b'vel': {b'Xd': 1.474294366834035, b'Yd': 4.777704063660853, b'Zd': 0.0, b'psiDot': 0.0, b'spd_mps': 5.0}
                        detectMsg         = State[vid]['detectMsg']          # b'detectMsg': {b'objId': 0, b'lastSeen': 0, b'lastLoc_X': 0, b'lastLoc_Y': 0, b'lastLoc_Z': 0, b'lastLoc_lat': 0, b'lastLoc_lon': 0}
                        waypoint_status   = State[vid]['waypoint_status']  # b'waypoint_status': {b'waypoint': 0, b'lap': 0, b'spd_mps': 0}, from followRoute() behavior
                        u                 = State[vid]['u']                  # b'u': [0.0, 5, 0.0], vehicle inputs
                        #bId               = State[vid]['bIdCmd']
                        bIdName           = State[vid]['bIdName']
                        bIdProgress       = State[vid]['bIdProgress']
                        
                        # detectAndReport() watches for nearby vehicles and messages the other vehicle if it's nearby
                        if (cfg.behaviorCfg['detectAndReport'] > 0):
                            if vid == cfg.detectId:
                                # update all detectCmd fields
                                payload_detect = { 'vid':vid, 'X':pos['X'], 'Y':pos['Y'], 'Z':pos['Z'], 'lat':pos['lat'], 'lon':pos['lon'] }
                                if (debug>0): logging.debug('vid={0}, payload_detect={1}'.format(vid, payload_detect))
                            
                            if ((vid != cfg.detectId) & (cfg.detectId>0)):
                                # send a detectCmd to all other vehicles so they can detect the object (vehicle) of interest
                                msg_detect = { 'vid': vid, 'type' : 'detectCmd', 'payload':payload_detect } # msg to i'th veh; payload_i has j data
                                qVehCmd.put(msg_detect) # these go to core_udp_io.send()
                                if debug>0: logging.debug('vid={0},\t\t msg_detect: {1}'.format(vid,msg_detect))
                                
                        # ------------------------------------------------------------------
                        # for csv file logging, these must be in csv fieldnames in main_core.py:   fieldnames = ['vid', b't', b'pos', b'vel'], and so on
                        # note:
                        # - tStamp is common time for all vehicles and created here in core, not encoded and decoded with msgpack()
                        # - t is simulation time from each vehicle model's process
                        vehInfo = { 'vid'                : State[vid]['vid'],
                                    'vehName'            : vehName,
                                    'vehType'            : State[vid]['vehType'],
                                    'vehSubType'         : State[vid]['vehSubType'],
                                    'runState'           : State[vid]['runState'],
                                    'srt_err_avg'        : srtStr,
                                    't'                  : State[vid]['t'],            # t is the vehicle's sim time, or elapsed time, which can stop if paused (in core_udp_io.py | aggregator() )
                                    'tStamp'             : State[vid]['tStamp'],       # tStamp is the unixtime core received this vid's update to State['vid'] (in core_udp_io.py | updateState() )
                                    'gps_unixTime'       : State[vid]['gps_unixTime'], # (s) unixtime from incoming gps messages (only updates when live_gps_follower==True)
                                    'pos'                : pos,
                                    'vel'                : vel,
                                    'detectMsg'          : detectMsg,
                                    'waypoint_status'    : waypoint_status,
                                    'u'                  : u,
                                    'bIdCmd'             : State[vid]['bIdCmd'],
                                    'bIdName'            : bIdName,
                                    'bIdProgress'        : bIdProgress,
                                    'missionAction'      : State[vid]['missionAction'],      # missionAction like 'waitElapsed' or 'goToPoint'
                                    'missionState'       : State[vid]['missionState'],       # missionState is an integer like 1, 10 or 100 from the config file's [missionCommands]
                                    'missionPctComplete' : State[vid]['missionPctComplete'], # mission command percentage complete on [0 1]
                                    'missionProgress'    : State[vid]['missionProgress'],    # progress indicator = missionState + pctComplete
                                    'missionLastCmdTime' : State[vid]['missionLastCmdTime'], # last wall clock time the mission commander issued a command
                                    'missionStatus'      : State[vid]['missionStatus'],      # mission commander's status: 'readyWait', 'active', or 'complete'
                                    'missionCounter'     : State[vid]['missionCounter'],     # counter for all separate mission commands ('goToMissionState' can cause lops which means counter can be higher than all [missionCommands] rows)
                                    'sensorData'         : State[vid]['sensorData']         # all vehicles have sensorData with at least 'batt_stat' and 'mac' fields
                                  }
                        # vehInfo={'vid': 100, 'vehName': 'myModel', 'vehType': 'aerial', 'vehSubType': 'rotorcraft', 'runState': 1, 'srt_err_avg': 0, 't': -1, 'tStamp': 1643813966.3323777, 'gps_unixTime': 0, 'pos': {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'psi': 0.0, 'hdg': 0.0, 'lat': 29.193110999581492, 'lon': -81.0461709999998}, 'vel': {'Xd': 0.0, 'Yd': 0.0, 'Zd': 0.0, 'psiDot': 0.0, 'spd_mps': 0.0}, 'detectMsg': {'objId': 0, 'lastSeen': 0, 'lastLoc_X': 0, 'lastLoc_Y': 0, 'lastLoc_Z': 0, 'lastLoc_lat': 0, 'lastLoc_lon': 0}, 'waypoint_status': {'waypoint': -1, 'lap': -1, 'spd_mps': -1}, 'u': [0.0, 5, 0.0, 0.0], 'bIdCmd': 0, 'bIdName': 'self.wander', 'bIdProgress': 0.0, 'missionAction': 'none', 'missionState': -1, 'missionPctComplete': 0.0, 'missionProgress': -1, 'missionLastCmdTime': 'Wed Feb  2 09:59:25 2022', 'missionStatus': 'readyWait', 'missionCounter': 1, 'sensorData': {'mac': 100, 'batt_stat': -1}}
                        
                        #code.interact(local=dict(globals(), **locals()))
                        # log State dictionary to local .csv file
                        if (self.logfile==1):
                            
                            # this runs once only if logging
                            if (self.firstVehMsg==True):
                                #fieldnames = [ 'vid', 'vehName', 'vehType', 'runState', 'bIdCmd', 'bIdName', 'srt_err_avg', 'tStamp', 'gps_unixTime', 'pos', 'vel', 'u', 't', 'detectMsg', 'routeStr' ] # specify dictionary field order; veh time unimportant; tStamp is core's common recording time for all vehicles
                                # create fieldnames from the dictionary with lists and dictionaries
                                fieldnames, newVehInfo=generateFieldnames(vehInfo)
                                pp.pprint(fieldnames)
                                self.dw    = csv.DictWriter( cfg.fd, fieldnames=fieldnames, quoting=csv.QUOTE_NONE, escapechar=' ', extrasaction='ignore' ) # inhibits quotes in .csv; ignores fields not in fieldnames
                                logging.debug('logging to: {0}'.format(self.fname))
                                self.dw.writeheader()
                                logging.debug('logging fieldnames: {0}'.format(fieldnames))
                                self.firstVehMsg=False
                            
                            # example fieldnames expanded from the vehInfo dictionary that contains dictionaries:
                            #   vid,vehName,vehType,vehSubType,runState,srt_err_avg,t,tStamp,gps_unixTime,
                            #   pos_X,pos_Y,pos_Z,pos_psi,pos_hdg,pos_lat,pos_lon,vel_Xd,vel_Yd,vel_Zd,vel_psiDot,vel_spd_mps,
                            #   detectMsg_objId,detectMsg_lastSeen,detectMsg_lastLoc_X,detectMsg_lastLoc_Y,
                            #   detectMsg_lastLoc_Z,detectMsg_lastLoc_lat,detectMsg_lastLoc_lon,
                            #   waypoint_status_waypoint,waypoint_status_lap,waypoint_status_spd_mps,
                            #   u,bIdCmd,bIdName,bIdProgress,
                            #   missionAction,missionState,missionPctComplete,missionProgress,
                            #   missionLastCmdTime,missionStatus,missionCounter,sensorData_mac,sensorData_batt_stat
                            fieldnames, newVehInfo=generateFieldnames(vehInfo) # test with: fieldnames_for_dictwriter_header.py
                            self.dw.writerow( newVehInfo )
                            self.fd.flush() # # flush() forces the write at each line - without flush the OS buffers and writes occasionally
                        
                        
                        # core's runtime console output:
                        vid = vehInfo['vid']
                        #vehName = vehInfo['vehName']
                        vehType   = vehInfo['vehType']
                        rS        = vehInfo['runState'] # local vars for printing only
                        rsDesc    = cfg.runStateDesc[ rS ] # runStateDesc is a list; in main_core.py
                        posStr    = ''.join(['{0}={1:-10.4f}, '.format( item, pos[item] ) for item in pos.__iter__()] ) # pos class was msgunpacked as a dictionary
                        velStr    = '{0:6.2f}(m/s)'.format( vel['spd_mps'] )
                        #detectStr = ''.join(['{0}={1:-10.4f}, '.format( item('utf-8'),vehInfo['detectMsg'][item]) for item in vehInfo['detectMsg'].__iter__()] ) # pos class was msgunpacked as a dictionary
                        detectStr = ' lastSeen: {0:.2f}'.format( detectMsg['lastSeen'] )
                        #logging.debug('\n\n\twaypoint_status={0}\n'.format(waypoint_status))
                        routeStr  = 'i={0:5}, lap={1:5d}'.format( waypoint_status['waypoint'],waypoint_status['lap'] )
                        tRecd     = time.strftime("%H:%M.%S", time.localtime( vehInfo['tStamp'] )  ) # vehInfo['tStamp'] is unixtime 1625241792.6287534
                        
                        #print('vehType={0}'.format(vehType))
                        if debug>0: logging.debug('t={0}, vid={1}, name:{2:10}, vehType:{3:3}, runState:{4}, beh:[{5:<17s}], pos:[{6}], vel:[{7}], detect:{8}, route:{9}' \
                                    .format(tRecd,vid,vehName,vehType,rsDesc,bIdName,posStr,velStr, detectStr, routeStr))
                        
                        # ------------------------------------------------------------------
                        # -----     send udp to Bokeh dash and viz applications        -----
                        # ------------------------------------------------------------------
                        # output to Bokeh mapping client and Bokeh dashboard
                        # send i'th vehicle pos and heading to visualization client
                        #logging.debug('for Bokeh dashboard, msg={0}'.format(vehInfo))
                        msg = msgpack.packb(vehInfo)
                        nBytesSentDash = self.dashSock.sendto(msg,(self.dashIp, self.dashPort))
                        #nBytesSentDash=0
                        #logging.debug('dashSock.sendto() just sent: {0} (bytes) to {1}:{2}'.format(nBytesSentDash,self.dashIp, self.dashPort))
                        if self.vizUdpEnabled == True:
                            #logging.debug('sending viz: {0}'.format(vehInfo))
                            nBytesSentViz = self.vizSock.sendto(msg,(self.vizIp, self.vizPort))
                            #nBytesSentViz=0
                            #logging.debug('vizSock.sendto() just sent: {0} (bytes) to {1}:{2}'.format(nBytesSentViz,self.vizIp, self.vizPort))
                        
                        # ------------------------------------------------------------------
                        # -----       send udp message to database logging listener
                        # ------------------------------------------------------------------
                        if self.dbUdpEnabled==True:
                            #msg = msgpack.packb(vehInfo)
                            #logging.debug(  'sending db msg: [{0}], vid={1}, vehInfo sizeof={2}(bytes)'.format( datetime.now().strftime('%c') , vid, vehInfo.__sizeof__() )  )
                            nBytesSentDb    = self.dbSock.sendto(msg,(self.dbIp, self.dbPort))
                            #nBytesSentDebug = self.dbSock.sendto(msg,('127.0.0.1', self.dbPort)) # send to localhost for debugging
                            #logging.debug('dbSock.sendto() just sent: {0} (bytes)'.format(nBytesSentDb))
                
                
                
                
                
                #print("avoidBySteer behavior on? {0}".format(cfg.behaviorCfg['avoidBySteer'] > 0))
                #print("avoidBySteer behavior     {0}".format(cfg.behaviorCfg['avoidBySteer']))
                if (nVehInState>1): # collision checking is only necessary if 2 or more vehicles
                    # number of unique distance calculations from all-to-all vehicles: nCals = (nVehTot^2 - nVehTot)/2
                    # example veh_warning entry: {'dist': 171.27764988647223, 'distRate': -0.12045177410591708, 'vid_i': 100, 'vid_j': 101}
                    veh_warnings = self.checkDistVel( State, pollCnt )
                    if debug>1: logging.debug('dist=\n{0}'.format(self.dist))
                    #         (poll_state    ) dist=
                    #                               [[  0.          -1.          -1.          -1.          -1.        ]     <-- vehicle 101 was missing
                    #                               [  0.           0.         122.12522926 210.31251667 120.97636945]
                    #                               [  0.           0.           0.          88.18728741   1.14885981]
                    #                               [  0.           0.           0.           0.          89.33614722]
                    #                               [  0.           0.           0.           0.           0.        ]]
                    nWarnings = len(veh_warnings)
                    if nWarnings>0: logging.debug('[{0}]: detected {1} impending close-proximity events: veh_warnings={2}'.format( datetime.now().strftime('%c') ,nWarnings,veh_warnings))
                else:
                    nWarnings=0
                
                #nWarnings=0 # core-based collision detection disabled to make core console output cleaner; mdc, 09 Jan 2022
                
                # process collision warnings; send messages to both involved for all detected collisions
                if nWarnings>0:
                    if debug>0: logging.debug('[{0}]:     {1}'.format( datetime.now().strftime('%c') ,veh_warnings))
                    for k,warn_data in veh_warnings.items():
                        if debug>0: logging.debug('[{0}]: placing warning msg {1} of {2} on the veh cmd send queue.'.format( datetime.now().strftime('%c') ,k,nWarnings))
                        
                        # msg = { 'vid':vid, 'type':type, 'payload': data }
                        # send distance, distRate, pos, and vel of 'the other' vehicle
                        vid_i     = warn_data['vid_i'] # which is i'th vehicle in this impending collision?
                        vid_j     = warn_data['vid_j'] # which is j'th vehicle in this impending collision?
                        #print('\t\tvid_i={0}, vid_j={1}'.format(vid_i,vid_j))
                        vehData_i = State[vid_i] # pull State info for i'th and j'th veh
                        vehData_j = State[vid_j]
                        #print('\t\tvehData_i={0},\n\t\tvehData_j={1}'.format(vehData_i,vehData_j))
                        payload_i = { 'theOtherOne': vid_j, 'pos': vehData_j['pos'], 'vel': vehData_j['vel'], 'dist': warn_data['dist'], 'distRate': warn_data['distRate'] } # j pos, j vel
                        payload_j = { 'theOtherOne': vid_i, 'pos': vehData_i['pos'], 'vel': vehData_i['vel'], 'dist': warn_data['dist'], 'distRate': warn_data['distRate']} # i pos, i vel
                        msg_i = { 'vid': vid_i, 'type' : 'avoidCmd', 'payload':payload_i } # msg to i'th veh; payload_i has j data
                        msg_j = { 'vid': vid_j, 'type' : 'avoidCmd', 'payload':payload_j } # msg to j'th veh; payload_j has i data
                        if debug>1: logging.debug('[{0}]: k={1}, msg_i: {2}'.format( datetime.now().strftime('%c') ,k,msg_i) )
                        if debug>1: logging.debug('[{0}]: k={1}, msg_j: {2}'.format( datetime.now().strftime('%c') ,k,msg_j) )
                        
                        # now decide if we should tell the i'th and j'th vehicles (tell 'em once, then give time for them to do something)
                        bIdName_i=vehData_i['bIdName'] # current behavior of the i'th vehicle in this collision warning
                        bIdName_j=vehData_j['bIdName'] # current behavior of the j'th vehicle in this collision warning
                        if debug>1: logging.debug('[{0}]: bIdName_i={1}'.format( datetime.now().strftime('%c') ,bIdName_i) )
                        if debug>1: logging.debug('[{0}]: bIdName_j={1}'.format( datetime.now().strftime('%c') ,bIdName_j) )
                        
                        # - only send a message to the i'th and j'th vehicles if:
                        #   (a) they are in GO runState==3 and
                        #   (b) if they are not already reporting current behavior of avoid()  (bIdCmd==4)
                        # - over-notifying either vehicle will over-fill that vehicle's qAvoid queue
                        # - behavior names are defined in each vehicle's config file and used in behaviors.py
                        if (vehData_i['runState']==3) and (bIdName_i != b'avoidBySteer'):
                            qVehCmd.put(msg_i) # these go to core_udp_io.send()
                            if debug>0: logging.debug('[{0}]:     sent qVehCmd msg_i: {1}'.format( datetime.now().strftime('%c') ,msg_i))
                        if (vehData_j['runState']==3) and (bIdName_j != b'avoidBySteer'):
                            qVehCmd.put(msg_j) # standard queue's are FIFO: "the first tasks added are the first retrieved"
                            if debug>0: logging.debug('[{0}]:     sent qVehCmd msg_j: {1}'.format( datetime.now().strftime('%c') ,msg_j))
                    
                    if debug>1:
                        pp.pprint(veh_warnings)
            
            else:
                logging.debug('[{0}]: e.is_set() is True.. we must be exiting.'.format( datetime.now().strftime('%c') ))
            
            pollCnt+=1
        
        logging.debug('Exiting')


    # =======================================================================================
    #                                  checkDistVels()
    # =======================================================================================
    # compute distances and velocities from all-to-all vehicles and flag problem
    # combinations: dist < distThreshold AND distRate < velThreshold
    # note: nDistCalcs = (N^2 - N) / 2
    # see: Compere_handwritten_notes_All_to_All_distance_calculation_order_Jul_2018,b,corrected.pdf
    # see: test_state.py for an example State object pprinted out
    # this is the vehData object you're working with:
    #
    # vehData for a live-GPS-follower:
    #     vehData[100]:
    #     {b'L_char': 2.0,
    #      b'bIdCmd': 100,
    #      b'bIdName': b'live_gps_follower',
    #      b'msg_cnt_in': 2,
    #      b'msg_cnt_out': 7780,
    #      b'msg_errorCnt': 0,
    #      b'pos': {b'X': -24.395241372170858,
    #               b'Y': 1.7437916691415012,
    #               b'Z': -7.642481848962428,
    #               b'lat': 28.48913525108339,
    #               b'lon': -81.37028220827057,
    #               b'psi': 0.0007036987067222222},
    #      b'runState': 3,
    #      b'srt_err_avg': 1.0509490978165446e-05,
    #      b'srt_margin_avg': 99.21716356956115,
    #      b't': 1551724310.8288968,
    #      b'u': [0.0, 0.0, 0.0],
    #      b'vel': {b'Xd': 0.0,
    #               b'Yd': 0.0,
    #               b'Zd': 0.0,
    #               b'psiDot': 0.0,
    #               b'spd_mps': 0.051444500000000004},
    #      b'vid': 100}
    #
    # vehData for a builtin simulated vehicle:
    #     vehData[102]:
    #     {b'L_char': 2.0,
    #      b'bIdCmd': 0,
    #      b'bIdName': b'wander',
    #      b'msg_cnt_in': 2,
    #      b'msg_cnt_out': 7780,
    #      b'msg_errorCnt': 0,
    #      b'pos': {b'X': -19.5776316052822,
    #               b'Y': 11.42763997314918,
    #               b'Z': 0.0,
    #               b'lat': 28.489222795533035,
    #               b'lon': -81.37023329995787,
    #               b'psi': -9.1086756784772},
    #      b'runState': 3,
    #      b'srt_err_avg': 3.329277039711076e-05,
    #      b'srt_margin_avg': 97.81467819892526,
    #      b't': 303.5,
    #      b'u': [0.0, 2.0, 0.0],
    #      b'vel': {b'Xd': -1.9009085923038558,
    #               b'Yd': -0.6217286576195221,
    #               b'Zd': 0.0,
    #               b'psiDot': 0.0,
    #               b'spd_mps': 0.0},
    #      b'vid': 102}

    #@jit # numba compiles just in time and executes this function faster than native python
    def checkDistVel( self, State, pollCnt ):
        #logging.debug('[{0}]: checkDistVel()'.format( datetime.now().strftime('%c') ))
        nVehTot = self.nVehTot
        tStart = self.tStart
        vid_base = self.vid_base
        debug = self.debug
        pp = self.pp # pretty-print object for debugging output
        veh_warnings = {} # init empty dict for default return value
        
        # first make sure State contains nVehTot number of entries
        nVehInState = len( list(State) ) # len of a list:   list(State) = [100, 101, 102]
        if debug>1: logging.debug('[{0}]: nVehTot={1}, unique entries in State: {2}'.format( datetime.now().strftime('%c') ,nVehTot,nVehInState))
        
        # increment dist and time for distRate estimate
        self.distLast = np.copy(self.dist) # numpy provides deep copy
        self.tLast    = copy.deepcopy(self.tNow) # capture last time this function was called (wall-clock time)
        self.tNow     = time.time()
        
        # proceed to address all nVehTot entries in State()
        # see: Compere_handwritten_notes_All_to_All_distance_calculation_order_Jul_2018,b,corrected.pdf
        if nVehTot >= 2:
            cnt     = 0  # total loop counter
            warnCnt = 0  # warnCnt is <= cnt; only those that are a problem increment warnCnt
            for i in range(0,nVehTot): # i indexes State rows; this achieves i=0:(N-1) b/c range stops 1 short
                for j in range(i+1,nVehTot): # j indexes State columns; this achieves j=(i+1):(N-1) b/c range() stops 1 short
                    
                    # ---------------------------------------------------------------
                    # try to get both the i'th and j'th vehicle's State information
                    # if either fails, skip the distance test and assign dist[i][j]=-1
                    try:
                        vehData_i = State[i+vid_base]
                        both_vehicles_available=True # so far, so good ( i'th vehicle was retrieved from State )
                    except:
                        both_vehicles_available=False
                    
                    if both_vehicles_available==True:
                        try:
                            vehData_j = State[j+vid_base] # ok, both the i'th and j'th vehicles are retrieved from State
                        except:
                            both_vehicles_available=False
                    
                    # ---------------------------------------------------------------
                    if both_vehicles_available:
                        pos_i = vehData_i['pos']
                        pos_j = vehData_j['pos']
                        #print('pos_i({0}) = {1},{2},{3}'.format(i+vid_base,pos_i[0],pos_i[1],pos_i[2]))
                        #print('pos_j({0}) = {1},{2},{3}'.format(j+vid_base,pos_j[0],pos_j[1],pos_j[2]))
                        #pp.pprint(vehData_j)
                        v_i = vehData_i['vel']
                        v_j = vehData_j['vel']
                        
                        # vector from i'th vehicle to j'th vehicle - recall vectors: "tip minus tail"
                        #logging.debug('pos_j={0}'.format(pos_j)):
                        #    pos_j={b'X': 0.0, b'Y': 0.0, b'Z': 0.0, b'psi': 0.0, b'lat': 28.489120188913493, b'lon': -81.37003291735377}
                        dX = pos_j['X'] - pos_i['X'] # (m) X_j - X_i   in inertial XYZ frame
                        dY = pos_j['Y'] - pos_i['Y'] # (m) Y_j - Y_i   in inertial XYZ frame
                        dZ = pos_j['Z'] - pos_i['Z'] # (m) Z_j - Z_i   in inertial XYZ frame
                        
                        self.dist[i][j] = sqrt( pow(dX,2) + pow(dY,2) + pow(dZ,2) ) # (m) 2-norm, Euclidian norm
                        
                        # numerical derivative to estimate distance-rate between the i'th and j'th vehicles (negative means they're getting closer)
                        dt = self.tNow - self.tLast # elapsed time since last State update
                        if abs(dt) < 1e-6: dt=1e-6 # avoid divide-by-zero
                        if pollCnt==0: self.distLast[i][j] = np.copy(self.dist[i][j]) # first time only - avoids massive rates b/c 'set' may have caused large position change
                        distRate = (self.dist[i][j] - self.distLast[i][j]) / dt # estimated distance rate between i'th and j'th vehicles
                        if debug>1: logging.debug('\t\t\t\tdt={0:0.3f}, dist={1:0.3f}, distRate = {2:0.3f}'.format(dt,self.dist[i][j],distRate))
                        
                        # check is there's an impending collision between the i'th and j'th vehicles
                        # todo 1: modifiy vehData to: (1) vehData_out and (2) add vehicle type and characteristic length
                        # todo 2: make distRate threshold = minus 1% of smaller velocity between the i-j'th pair (consider: F22 and Cessna; want trigger on smaller vel)
                        L_char_i = vehData_i['L_char'] # (m) characteristic length for the i'th vehicle
                        L_char_j = vehData_j['L_char'] # (m) characteristic length for the j'th vehicle
                        L_char = L_char_i + L_char_j
                        if debug>1: logging.debug('\t\t\t\t[{0}]: dist[{1}][{2}]={3:0.2f},  distRate = {4:0.2f}' \
                                           .format( datetime.now().strftime('%c') ,i+vid_base,j+vid_base,self.dist[i][j],distRate))
                        
                        if 1:
                            distThreshold = self.detectThreshold # from config file
                        else:
                            dt_warn = 2 # (s) lead time before possible collision to deliver a warning
                            distThreshold = 2*max( v_i['spd_mps'],v_j['spd_mps'] )*dt_warn
                            #distThreshold = 10*L_char # v=dx/dt, so: dx=v*dt and dt=dx/v
                        #print('distThreshold={0},v_i_X={1}'.format(distThreshold,v_i['Xd']))
                        distRateThresh = 0.0 # (m/s)
                        #if (distMetric <= self.distThreshold):
                        if (self.dist[i][j] <= distThreshold) and (distRate < distRateThresh):
                            logging.debug('[{0}]: possible collision! notifiy veh[{1}] and veh[{2}]!  dist={3:0.3f}(m), d_thresh={4:0.3f}(m), distRate={5:0.3f}(m/s), dRate_thresh={6}(m/s)' \
                                   .format( datetime.now().strftime('%c') ,i+vid_base,j+vid_base,   self.dist[i][j],distThreshold,   distRate,distRateThresh)) # , distMetric={5}  ,distMetric
                            warnCnt += 1
                            # both vehicles need to know the other is there, the dist, and the distRate
                            veh_warnings[warnCnt] = { 'vid_i':(i+vid_base), 'vid_j':(j+vid_base), 'dist':self.dist[i][j], 'distRate':distRate }
                    else:
                        # one or both of these vehicles are not available in the current State
                        distRate=0.0 # (m/s) dummy during startup or for missing vehicle in State
                        self.dist[i][j] = -1.0 # (m) nonsensical distance is a flag to indicate either the i'th or j'th vehicle was not present, so no distance can be computed
                    
                    self.distTable[cnt]= [ self.dist[i][j] , distRate , i+vid_base , j+vid_base ] # [(m),(m/s),-,-] update the (i,j)'th row with [ dist, distRate, ith_veh, jth_veh ]
                    cnt += 1 # distance counter will count up to (n^2-n)/2
        else:
            logging.debug('[{0}]: skipping checkDistVels(), State not large enough yet'.format( datetime.now().strftime('%c') ))
        
        return veh_warnings



