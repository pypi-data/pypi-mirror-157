#!/usr/bin/env python3
#
# a class for vehicle-to-vehicle communication among simulated vehicle models
#
# there are 2 threads that are not intended as the primary code interface:
# (a) private thread _v2v_udp_sender()   - sends the current vid's information to all others
# (b) private thread _v2v_udp_receiver() - receives messages from all senders and compiles into v2vState, a dictionary of dictionaries
#
# there are 2 methods designed to be the primary interface that loops quickly:
# (c) method v2vUpdateToNetwork() places an outbound message on the queue for v2v_udp_sender()
# (d) method v2vUpdateFromNetwork()  recives snapshots of entire v2vState with all other vehicle's information
#
# the two relevant update rates specified here are:
# (e) v2v_cint_send - vehicle-to-vehicle communication interval
#     for single-vehicle (outbound) updates to all others
# (f) v2v_cint_read - v2vState update from all other vehicles
#     which is a snapshot compiled from all other vehicles received by this vehicle
#
# Marc Compere, comperem@gmail.com
# created : 09 Oct 2021
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
import os
import sys
import socket
import struct
import threading
from collections import deque

import msgpack
import numpy as np
import logging
from pprint import pformat # pretty print v2v structure
sys.path.append(os.path.relpath("../scenario")) # find ../scenario/readConfigFile.py w/o (a) being a package or (b) using linux file system symbolic link
from readConfigFile import readConfigFile

import random
from datetime import datetime # for loop printing in __main__ below; not needed in v2v class

logging.basicConfig( level=logging.DEBUG,format='(%(threadName)-14s %(process)d) %(message)s') # https://docs.python.org/3/library/logging.html#logrecord-objects

def merge_dictionaries(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

class V2V:
    """A class for simulated vehicle-to-vehicle messaging.
       This is a (very) simple model of a broadcast network between vehicles
       implemented, for simulated vehicles only, with udp/ip multicasting"""
    
    def __init__(self,vid,cfg,e):
        
        self.debug=cfg.debug #1 # (0/1)
        self.vid=vid # vehicle ID of this instantiation; self's vid
        self.cntStale=0
        self.v2vPrtFlag=True # (True/False) print v2v console output?
        
        multicast_group = cfg.multicast_group # ipv4 addresses 224.0.0.0 through 230.255.255.255 are reserved for multicast traffic
        multicast_port  = cfg.multicast_port
        
        self.v2v_cint_send = cfg.v2v_cint_send # (s) outbound v2v communication interval for broadcasting a single vehicle's update to all other vehicles
        self.v2v_cint_read = cfg.v2v_cint_read # (s) update v2vState snapshot of all vehicles for use by mission scheduler

        self.v2v_dRadio = cfg.v2v_dRadio # (m) radio range; any vehicles within this distance are radio active
        self.v2v_dNeigh = cfg.v2v_dNeigh  # (m) neighbor range; any vehicles within this distance are neighbors
        
        logging.debug('--- starting v2v subsystem with ---')
        logging.debug('vid={0}, multicast_group={1}, multicast_port={2}'.format(vid,multicast_group,multicast_port))
        logging.debug('send interval={0}, v2vState snapshot interval={1}'.format(self.v2v_cint_send,self.v2v_cint_read))
        logging.debug('v2v_dRadio={0}(m), v2v_dNeigh={1}(m)'.format(self.v2v_dRadio,self.v2v_dNeigh))
        
        self.v2vOutboundDeque = deque(maxlen=1) # single vehicle broadcast;                 deque with maxlen option will not throw an exception when full; deque's are FIFO and just pop the oldest off the end
        self.v2vInboundDeque  = deque(maxlen=1) # full dictionary for transfer to parent thread; deque with maxlen option will not throw an exception when full; deque's are FIFO and just pop the oldest off the end
        self._v2vUdpSendDeq   = deque(maxlen=1) # deque for reporting broadcast network send counter from the _v2v_udp_sender thread
        self._v2vUdpRecvDeq   = deque(maxlen=1) # deque for reporting v2v received-message counter from _v2v_udp_receiver thread
        
        self.v2vMcastCntSent=0 # initial v2v multicast send counter
        self.v2vMcastCntRecd=0 # initial v2v multicast recv counter
        
        self.v2vState={} # init empty v2vState
        
        #self.e = threading.Event()
        self.e = e
        self.tLast=time.time()
        
        if cfg.v2vEnabled==True:
            # start receive thread first to bind() successfully
            t1 = threading.Thread(name='v2v_recv', target=self._v2v_udp_receiver,
                                  args=(multicast_group,multicast_port,self.e))
            t1.start()
            
            t2 = threading.Thread(name='v2v_send', target=self._v2v_udp_sender,
                                  args=(multicast_group,multicast_port,self.e))
            t2.start()
            
    
    # ==============================================================================
    # private _v2v_udp_sender() *thread* is a while loop for sending periodic v2v updates indefinitely
    # input: myUpdate containing this vehicle's state updates to all other vehicles
    # =======================================================================================
    def _v2v_udp_sender(self,multicast_group,multicast_port,e):
        logging.debug('Starting v2v_udp_sender thread')
            
        # Create the datagram socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
        # Set the time-to-live for messages to 1 so they do not go past the local network segment.
        #ttl = struct.pack('b', 1) # ttl==1 means "do not forward packets beyond router"
        ttl = struct.pack('b', 2) # ttl==2 means "send to 1 beyond the router"
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        
        # option for sender only
        #[no workee] sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(multicast_group[0])) # https://stackoverflow.com/a/50604764/7621907
        
        data={} # empty dictionary
        cntSend=0
        tStart = time.time()
        try:
            while e.is_set() is False:
                if len(self.v2vOutboundDeque)>0:
                    data = self.v2vOutboundDeque.pop() # deque() with maxlen=1; no accumulation is possible; it's always length=1 with the latest information
                
                if len(data)>0:
                    msg = msgpack.packb(data)
                    nBytesSent = sock.sendto(msg, (multicast_group,multicast_port))
                    cntSend+=1
                    self._v2vUdpSendDeq.append(cntSend) # route udp multicast send counter back to v2v class
                    if self.debug>1: logging.debug('------------------------------------------------------------------------------------')
                    if self.debug>1: logging.debug("sendto() just sent {0} bytes from vid={1} to multicast group {2}:{3}, cntSend={4}".format(nBytesSent,self.vid,multicast_group,multicast_port,cntSend) )
                
                time.sleep( self.v2v_cint_send ) # sleep in seconds, resolution in 10's of ms
        except:
            print("Unexpected error:", sys.exc_info()[0])
        
        logging.debug('thread exiting')
    
    
    # ==============================================================================
    # the primary *method* interface for sending v2v updates to all other vehicle models
    # this is a simple interface to the outbound message queue; this interval timer method avoids writing deque data at high frequency
    # primary output: nothing, other than number of bytes sent via multicast
    # note: ensure this is non-blocking for use in a fast loop
    # =======================================================================================
    def v2vUpdateToNetwork(self,tNow,data):
        if (tNow-self.tLast)>=self.v2v_cint_send:
            self.v2vOutboundDeque.append(data) # if enough time has elapsed, put data in the deque
            #logging.debug('sent v2v data update at [{0}]'.format(time.strftime('%c',time.localtime(tNow))))
            self.tLast=tNow
    
    
    # ==============================================================================
    # private _v2v_udp_receiver() *thread* enters a while loop to stay alive and block until it receives udp data
    # primary output: raw v2vState from the network containing the entire group of vehicle states as an updating snapshot
    # =======================================================================================
    def _v2v_udp_receiver(self,multicast_group,multicast_port,e):
        logging.debug('Starting v2v_udp_receiver thread listening on multicast_group={0}'.format(multicast_group))
            
        # Create the datagram socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #sock.settimeout(0.2)
        sock.settimeout( self.v2v_cint_read ) # exit gracefully with event e.is_set()
        logging.debug('socket timeout is: {0}'.format( sock.gettimeout() ) )
        
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # required for multiple instances to bind on localhost
        
        try:
            sock.bind((multicast_group,multicast_port)) # must bind to receive
        except:
            logging.debug('error, could not bind() exiting')
            e.set()
        
        # Tell the operating system to add the socket to multicast group on all interfaces.
        group = socket.inet_aton(multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        #mreq = struct.pack('4s4s', group, socket.inet_aton(multicast_group[0])) # https://stackoverflow.com/a/50604764/7621907
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        v2vState = {} # initialize the v2vState dict containing a snapshot of all vehicle's most recently reported states
        cntRecv=0
        tStart = time.time()
        tLast  = tStart # for v2v full table update snapshots
        while e.is_set() is False:
            if self.debug>1: logging.debug('waiting to receive message from: {0}'.format(multicast_group))
            
            try:
                # pickup v2v update from anyone (including self) and update local copy of v2vState{}
                data, addr = sock.recvfrom(1024) # blocking udp receive from *anyone* in the multicast group; buffer size is 1024 bytes
                if len(data)>0:
                    cntRecv += 1
                    self._v2vUdpRecvDeq.append(cntRecv) # route udp multicast send counter back to v2v class
                    msg = msgpack.unpackb(data)
                    if self.debug>1: logging.debug("msg=[{0}]".format(msg) )
                    this_vid     = msg['vid']
                    this_tNowVeh = msg['tNowVeh'] # tNowVeh in the msg is from the originating vehicle
                    if self.debug>1: logging.debug("received [{0}] bytes from {1},vid={2}, cntRecv={3}".format(len(data), addr,this_vid,cntRecv) )
                    
                    # construct a local dictionary of times
                    tNow = time.time() # tLocal_*'s are from the local receiving vehicle
                    tLocal_formatted  = time.strftime("%Y_%m_%d__%H_%M_%S", time.localtime(tNow) )
                    tNowVeh_formatted = time.strftime("%Y_%m_%d__%H_%M_%S", time.localtime(this_tNowVeh) )
                    tLocal = {'tLocal_recd': tNow,             'tLocal_elap': tNow-tStart,
                              'tLocal_fmtd': tLocal_formatted, 'tNowVeh_fmtd':tNowVeh_formatted }
                    
                    # create default v2v fields in another dictionary, assuming the message is from someone else
                    localSelf = {'self': False, 'inRangeRadio':set(), 'inRangeNeigh':set() } # set() adds only unique entries; lists can grow with repeated entries
                    
                    if this_vid==self.vid:
                        # set flag in this v2vState to indicate this is the self's v2vState (not another vid's v2vState)
                        localSelf['self']=True # simplest way to discriminate a neighbor's update from self w/o computing distance
                                               # note: if distance is nonzero and vid's are the same, then there are 2 senders with
                                               #       identical vid's (which could be a problem). This case is not currently detected.
                    
                    # update multicast receive counter that just came in over the network (but only for self's v2vState!)
                    if ('v2vMcastCntRecd' in msg):
                        if (this_vid==self.vid):
                            msg['v2vMcastCntRecd']=cntRecv
                    
                    # mush these dictionaries together and update v2vState{}; note: ensure all merged keys are *new* and not in msg (existing keys may override; merge order dependent)
                    local = merge_dictionaries(tLocal, localSelf)
                    v2vState[this_vid] = merge_dictionaries(local, msg) # v2vState is a dictionary of dictionaries
                    
                    if self.debug>2:
                        logging.debug('v2vState=[')
                        pprint.pprint( v2vState[this_vid] )
                        logging.debug(']')
                    
            except socket.timeout:
                pass
            
            # periodically send out a snapshot of current v2v table to parent thread
            tNow=time.time()
            if ( (tNow-tLast) > self.v2v_cint_read):
                self.v2vInboundDeque.append(v2vState) # this is all vehicle's v2v states ever seen during this simulation
                tLast=tNow
            
            if self.debug>2: logging.debug( "{0}: len(v2vInboundDeque)={1}".format(time.time()-tStart, self.v2vInboundDeque.qsize()) )
        logging.debug('thread exiting')
    
    
    
    
    # function to compute distance from the self's location to another vid within the v2vState
    def _compute_v2v_distance(self,vid,this_vid,v2vState):
        dX = v2vState[vid]['posX'] - v2vState[this_vid]['posX']
        dY = v2vState[vid]['posY'] - v2vState[this_vid]['posY']
        dZ = v2vState[vid]['posZ'] - v2vState[this_vid]['posZ']
        return np.sqrt( pow(dX,2) + pow(dY,2) + pow(dZ,2) ) # (m) distance
    
    
    
    
    # ==============================================================================
    # the primary *method* interface for v2v communications to deliver v2vState updates to the vehicle model
    # primary output: latest and greatest v2vState updated and ready for vehicle model to use
    # note: ensure this is non-blocking for use in a fast loop
    # =======================================================================================
    def v2vUpdateFromNetwork(self,v2vState):
        # v2vInboundDeque is a deque appended every 2 seconds in v2v_udp_receiver()
        if len(self.v2vInboundDeque)>0:
            v2vState = self.v2vInboundDeque.pop() # get current v2vState; deque() with maxlen=1; no accumulation is possible; it's always length=1 with the latest information
            N = len( v2vState.keys() ) # total number of keys in v2vState
            #logging.debug('received v2vState update with {0} entries and {1} bytes:'.format(N,sys.getsizeof(v2vState)))
            staleList=[]
            
            # scan entrire v2vState to:
            # (a) identify processes that aren't updating and mark them stale
            # (b) update radio and neighbor range sets with current v2vState
            for ith_vid in v2vState.copy(): # .copy() forces iterator to use a copy to avoid runtime error from changing dict size; https://stackoverflow.com/a/36330953/7621907
                #logging.debug('vid={0}, evaluating ith_vid={1}'.format(vid,ith_vid))
                if (ith_vid in v2vState) and (v2vState[ith_vid]['stale']==True):
                    if self.debug>1: logging.debug("discovered stale state!, vid={0}".format(ith_vid))
                    staleList.append(ith_vid) # append to stale list
                
                this_tNowveh    = v2vState[ith_vid]['tNowVeh'] # this time is from the other vehicle's computer
                this_stale_flag = v2vState[ith_vid]['stale']
                # old data? vehicle must not be sending anymore
                if (this_stale_flag==False) and (time.time() - this_tNowveh)>(3*self.v2v_cint_read):
                    v2vState[ith_vid]['stale']=True # leave entry there, but flag as stale
                    staleList.append(ith_vid) # append to stale list
                    #v2vState.pop(ith_vid, None) # delete this ith_vid's information from v2vState
                    logging.debug('assigning stale data for ith_vid={0}, leaving in v2vState, cntStale={1}'.format(ith_vid,len(staleList)))
                
                self.cntStale=len(staleList)
                # compute distance from ith_vid to all others so all-to-all range lists are populated correctly (not just self-to-all)
                # result: everyone discerns everyone else's neighbor list
                # note: times and inRange sets are computed fresh each update
                for jth_vid in v2vState.keys():
                    if (jth_vid is not ith_vid): # don't put self in radio or neighbors list; only allow others
                        if (v2vState[ith_vid]['stale'] is False) and (v2vState[jth_vid]['stale'] is False):
                            dist = self._compute_v2v_distance(ith_vid,jth_vid,v2vState) # (m) distance from self's vid to ith_vid which is another vid in v2vstate
                            if (dist<=self.v2v_dRadio):
                                v2vState[ith_vid]['inRangeRadio'].add(jth_vid)  # assign ith_vid's result
                            if (dist<=self.v2v_dNeigh):
                                v2vState[ith_vid]['inRangeNeigh'].add(jth_vid)  # assign ith_vid's result
            
            # update current v2vState metrics
            if self.v2vPrtFlag==True:
                logging.debug('current v2vState size: {0}'.format(N))
                logging.debug('          active size: {0}'.format(N-self.cntStale))
                logging.debug('    stale v2v entries: {0}, {1}'.format( self.cntStale, sorted(staleList) ))
            
            
            if (self.debug>0) and (self.v2vPrtFlag==True):
                logging.debug('v2vUpdateFromNetwork(): ' + pformat(v2vState))
                #pprint.pprint(v2vState) # print all vid's in v2vState
            #if self.debug>0: pprint.pprint( v2vState[vid] ) # print just this vid's state
        
        return v2vState








# local main for stand-alone testing
if __name__ == "__main__":
    n=len(sys.argv)
    print('n={0}, sys.argv={1}'.format(n,sys.argv))
    
    if n==4 and sys.argv[1]=='-f':
        print('reading scenario config file: {}'.format(sys.argv[2]))
        cfgFile =      sys.argv[2]
        vid     = int( sys.argv[3] )
        #cfgFile = '../scenario/default.cfg' # python's .ini format config file
        #cfgFile='../scenario/live_5_veh_uas_xbee.cfg'
        cfg, veh_names_builtins, veh_names_live_gps   = readConfigFile( cfgFile, vid )
        
    elif n==3 and sys.argv[1]=='defaults':
        vid     = int( sys.argv[2] )
        class Cfg():
            pass
            
        cfg=Cfg()
        cfg.debug=1 # (0/1/2)
        cfg.v2vEnabled = True #False #True # (True/False) enable or disable v2v threads
        cfg.multicast_group = '224.3.29.71' # ipv4 addresses 224.0.0.0 through 230.255.255.255 are reserved for multicast traffic
        cfg.multicast_port  = 10000 # udp multicast port for all senders and listeners
        
        cfg.v2v_cint_send = 1.0 # (s) outbound v2v communication interval for broadcasting a single vehicle's update to all other vehicles
        cfg.v2v_cint_read = 2.0 # (s) receiver's observation interval of complete v2vState snapshot; complete v2v netowrk view used by mission scheduler
        
        cfg.v2v_dRadio = 500 # (m) radio range; any vehicles within this distance are radio active
        cfg.v2v_dNeigh = 10  # (m) neighbor range; any vehicles within this distance are neighbors
        
    else:
        print('\n------- {0} is not the primary runtime script --------'.format(sys.argv[0]))
        print('\n-------     ---> for development and debugging only     --------\n')
        print('\t usage   *with* config file :    {0} -f myScenario.cfg vid'.format(sys.argv[0]))
        print('\t example *with* config file :    {0} -f ../scenario/default.cfg 100\n'.format(sys.argv[0]))
        print('\t usage   without config file:    {0} defaults vid'.format(sys.argv[0]))
        print('\t example without config file:    {0} defaults 100\n'.format(sys.argv[0]))
        sys.exit(0)
    #code.interact(local=dict(globals(), **locals())) 
    
    
    # ------------------------------------------------------------------------------
    # BEGIN:               setup specific vehicle positions
    # ------------------------------------------------------------------------------
    class Veh:
        pass
    
    veh = Veh()
    veh.posX=random.uniform(-10.0,+10.0) # (m)
    veh.posY=random.uniform(-10.0,+10.0) # (m)
    veh.posZ=random.uniform(-10.0,+10.0) # (m)
    
    if vid==100:
        veh.posX=0 # (m)
        veh.posY=0 # (m)
        veh.posZ=0 # (m)
        
    if vid==101:
        veh.posX=5 # (m)
        veh.posY=0 # (m)
        veh.posZ=0 # (m)
        
    if vid==102:
        veh.posX=12 # (m)
        veh.posY=0 # (m)
        veh.posZ=0 # (m)
    
    # default mission command metrics all vehicles send to all others in v2v messaging; these are sent with or without any config file [missionCommands]
    missionState       = -1      # missionState is defined in the config file and is an integer
    missionAction      = 'none'  # missionAction is the missionCommand action associated with this missionState
    missionProgress    = -1      # missionProgress is a floating point number equal to: missionState + pctComplete. each action is completed when missionProgress=missionState+1 (or when pctComplete=1.0)
    missionLastCmdTime = datetime.now().strftime('%c')
    missionStatus      = 'readyWait'
    missionCounter     = 0
    
    
    # ------------------------------------------------------------------------------
    #  END :                     setup specific vehicle positions
    # ------------------------------------------------------------------------------
    e = threading.Event()
    
    v2v = V2V(vid,cfg,e) # start vehicle-to-vehicle communications threads
    
    
    cntMain=0
    skipNth=20 # skip this many main loop iterations between logging output
    v2v.v2vPrtFlag=True #False #True # (True/False) print v2v console updates?
    while v2v.e.is_set() is False:
        try:
            
            while True:
                # fast executing loop; nothing can block
                time.sleep(0.1) # if Core cint=0.1, that means vehicle's outputs are updated at 10Hz (in veh.gather_outputs() for runState=={2,3,4})
                
                v2v.v2vState = v2v.v2vUpdateFromNetwork(v2v.v2vState) # check for new inbound v2vState dictionary from multicast receiver
                
                
                
                if (cntMain % skipNth)==0 and (cfg.debug>1):
                    logging.debug('{0}: cntMain={1}, v2vMcastCntRecd={2}, v2vMcastCntSent={3}, len(v2vState)={4}'.format(datetime.now().strftime('%c'),cntMain,v2vMcastCntRecd,v2vMcastCntSent,len(v2vState)))
                
                # -->this works but pulls the v2v multicast receive counter from the network, whereas the method used below pulls from a deque sent by the thread
                # extract v2v multicast received message count (for self's vid only) to send to errbody on next v2vUpdateToNetwork()
                #if vid in v2vState:
                #    v2vMcastCntRecd=v2vState[vid]['v2vMcastCntRecd'] # this vehicle's multicast receiver got this vehicle's multicast sender's message
                
                # update self's v2v multicast recv counter for next v2v send
                if len(v2v._v2vUdpRecvDeq)>0:
                    v2v.v2vMcastCntRecd = v2v._v2vUdpRecvDeq.pop() # get the only item on the deque from v2v multicast receiver thread: multicast recv counter
                
                # update self's v2v multicast send counter for next v2v send
                if len(v2v._v2vUdpSendDeq)>0:
                    v2v.v2vMcastCntSent = v2v._v2vUdpSendDeq.pop() # get the only item on the deque from v2v multicast sender thread: multicast send counter
                
                # create the data dictionary for outbound v2v messages
                v2vData = { 'vid':vid, 'v2vMcastCntSent':v2v.v2vMcastCntSent, 'v2vMcastCntRecd':v2v.v2vMcastCntRecd,
                            'posX':veh.posX, 'posY':veh.posY, 'posZ':veh.posZ, 'tNowVeh':time.time(), 'stale':False,
                            'missionAction':missionAction, 'missionState':missionState, 'missionProgress':missionProgress,
                            'missionLastCmdTime':missionLastCmdTime, 'missionStatus':missionStatus, 'missionCounter':missionCounter }
                v2v.v2vUpdateToNetwork( time.time(), v2vData ) # broadcast this vehicle's data to everyone listening
                cntMain+=1
                
                
        except KeyboardInterrupt as err:
            print("caught keyboard ctrl-c:".format(err))
            v2v.e.set() # tell v2v threads to exit
            print("exiting.")
            exit(0)















