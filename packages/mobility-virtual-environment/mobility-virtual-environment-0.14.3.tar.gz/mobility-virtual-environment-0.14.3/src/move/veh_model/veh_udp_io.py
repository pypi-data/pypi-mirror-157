#!/usr/bin/env python3
#
# veh_udp_io.py - thread definitions for receiving and sending to and from
#                 the vehicle model, main_veh_model.py
#
# this file is intended as a Class definition for main_veh_model.py and is
# not intended for running at the command prompt. Having said that, there is
# a main function below for debugging and testing new methods.
#
# Marc Compere, comperem@gmail.com
# created : 18 Jul 2018
# modified: 04 Jul 2022
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

import os
import sys
import time
from datetime import datetime
import threading
import queue
import logging
import socket
import msgpack # fast serialize/deserialize of complete python data structures, better than struct.pack(): sudo pip3 install msgpack-python
import msgpack_numpy as m # msgpack for numpy objects: sudo pip3 install msgpack-numpy
sys.path.append(os.path.relpath("../scenario")) # find ../scenario/readConfigFile.py w/o (a) being a package or (b) using linux file system symbolic link
from readConfigFile import readConfigFile
from myVehicle import MyVehicle
from live_gps_follower_decoding import live_gps_follower_decoding, auto_detect_message_type
import csv # for DictWriter

import code # drop into a python interpreter to debug using: code.interact(local=dict(globals(), **locals()))

class Veh_udp_io:
    """A class for udp messaging between this vehicle and MoVE core"""
    
    def __init__(self, cfg, veh):
        
        self.vid               = cfg.vid
        self.name              = cfg.name
        self.core_host_ip      = cfg.core_host_ip
        self.udp_port_out      = cfg.vid + cfg.udp_port_base  # udp sending (outbound) port for this vid process (vehicle-to-core-aggregator)
        self.udp_port_in       = self.udp_port_out + cfg.udp_port_offset # this veh listens for commands on this port (core-command-and-control-to-veh)
        self.udp_port_gps      = cfg.udp_port_gps
        self.live_gps_follower = cfg.live_gps_follower
        
        # outbound udp is a function call; inbound is a looping thread blocked by recvfrom()
        self.core_addr  = (cfg.core_host_ip, self.udp_port_out)
        self.sock_out   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # udp/ip socket
        self.os_pid     = os.getpid()
        self.errorCnt   = 0 # the udp sendto() has a try-catch exception block
        self.debug      = cfg.debug # (0/1) for verbose network send/recv console output
        self.veh        = veh # the MyVehicle object from main
        
        self.sendCnt    = 0 # udp sent packet count to Core
        self.recvCnt    = 0 # udp received packet count from Core
        self.recvCntGps = 0 # udp received packet count from HyperIMU or other GPS sender
        
        self.gps        = {} # initialize empty dictionaries for incoming udp messages to live-gps-follower vehicle
        self.sensorData = {}
        
        self.e          = threading.Event()
        self.eRunState  = threading.Event() # for signaling a runState change
        self.runState   = cfg.runState  # recall: this is a *mutable* list for class and main visibility
        self.qRunState  = queue.Queue() # for conveying the new runState and optional additional payload (like ICs)
        
        # udp_in / recv is a thread with a blocking socket, udp_out() is a *function* called as necessary
        self.t1         = threading.Thread( name='udp_io.recv_core' , target=self.recv_core , args=(self.e, self.vid )).start()
        t2              = threading.Thread( name='udp_console' , target=self.udp_console_update, args=()).start()
        if cfg.live_gps_follower==True:
            self.t3     = threading.Thread( name='udp_io.recv_gps' , target=self.recv_gps , args=(self.e, self.vid, self.gps, self.sensorData) ).start()
        
        logging.debug('[{0}]: total threads active: {1}'.format(  datetime.now().strftime('%c') , threading.active_count() ))
        
    # -----------------------------------------------------------------------------------
    #                                 send_core()
    # -----------------------------------------------------------------------------------
    # *method* (not a thread) to send udp packets to MoVE core for status updates (timing is controlled by enclosing loop, e.g. srt() in main_veh_model.py)
    def send_core(self, vehData):
        if (self.debug>2): logging.debug('vid={0}: sending to [{1}:{2}]'.format(self.vid, self.core_host_ip, self.udp_port_out))
        msgpackedVehData = msgpack.packb(vehData, default=m.encode) # fast serialize for entire python data structure w/o detailing each field (incl numpy datatypes)
        try:
            nBytes = self.sock_out.sendto(msgpackedVehData,self.core_addr)
            self.sendCnt+=1
            if (self.debug>2): logging.debug('nBytes sent: {0}, udpSentCnt={1}'.format(nBytes,self.sendCnt))
        except OSError as err:
            self.errorCnt +=1
            logging.debug('caught OSError number [{0}]!: {1}'.format(self.errorCnt,err))
            # OSError: [Errno 101] Network is unreachable
        
    # -----------------------------------------------------------------------------------
    #                               udp_console_update()
    # -----------------------------------------------------------------------------------
    # thread for printing udp messages to the console (no network, just text to the console)
    def udp_console_update(self):
        
        dt = 2 # (s) console output period for udp updates (not udp sending - just console output)
        #dt=200 # (s) debugging value to keep threads from flooding the console
        tStart = time.time()
        os_pid = os.getpid()
        
        while self.e.is_set() is False: # when Event e.is_set() is True, main and all threads exit
            self.e.wait(dt)
            elapsedTime = time.time() - tStart
            #while not q_in.empty(): # clear the que; do not block when empty
            #    recvCnt=q_in.get()
            #while not q_out.empty(): # clear the que; do not block when empty
            #    sendCnt=q_out.get()
            str1='eTime: {0:6.2f}(s), vid={1}, name={2}, os_pid={3}, core_ip=[{4}]'.format(elapsedTime, self.vid, self.name, os_pid, self.core_host_ip)
            str2=', port {0} msgs recd {1}'.format(self.udp_port_in , self.recvCnt)
            str3=', port {0} msgs sent {1}'.format(self.udp_port_out, self.sendCnt)
            if self.live_gps_follower==True:
                str4=', GPS port {0} msgs recd {1}'.format(self.udp_port_gps, self.recvCntGps)
            else:
                str4=''
            logging.debug('')
            logging.debug('{0:s} {1:s} {2:s} {3:s}'.format(str1,str2,str3,str4))
            logging.debug('')
        
        logging.debug('[{0}]: udp_console_update(): exiting'.format( datetime.now().strftime('%c') ))
    
    # -----------------------------------------------------------------------------------
    #                                    recv_core()
    # -----------------------------------------------------------------------------------
    # thread to listen for MoVE-core commands via udp ( thread b/c blocking udp recevfrom() )
    #
    # messages currently handled:
    #   - runStateCmd from Core, main_changeRunState.py
    #   - avoidCmd from Core, all_vehicles.py, poll_state() thread
    #   - detectCmd from Core, all_vehicles.py, poll_state() thread
    def recv_core(self, e, vid):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # udp/ip socket
        sock.settimeout(0.5) # timeout ensures graceful exit close to this duration
        # listen to anyone, not just core_host_ip; bind() fails with core_host_ip in core_addr
        core_addr = ('0.0.0.0',self.udp_port_in) # listen for core messages at this ip and port
        try:
            sock.bind(core_addr)
            logging.debug('vid={0}: inbound udp thread for core() messages started in os_pid=[{1}]'.format(vid, os.getpid()))
            logging.debug('vid={0}: listening to [{1}:{2}]'.format(vid, '0.0.0.0', self.udp_port_in))
        except OSError as err:
            logging.debug('\n\n')
            logging.debug( '\t\trecv_core(): OSError: error trying to bind() for core() messages!  {0}'.format(err) )
            logging.debug( '\t\trecv_core(): core_addr={}'.format(core_addr))
            logging.debug( '\t\trecv_core(): [{0}]: exiting\n\n\n\n\n\n'.format( datetime.now().strftime('%c') ) )
            self.e.set()     # exit udp_io threads
            self.veh.e.set() # exit MyVehicle and Behavior threads; note: cannot run veh.exit() b/c that's a method that doesn't exit until all exit - infinite loop - thread cannot exit because it's watching if all have exited
            exit(-1)
        
        
        while e.is_set() is False:
            try:
                data,addr = sock.recvfrom(512) # blocking call timeout = 0.5s
                self.recvCnt+=1
            except socket.timeout:
                #logging.error("sock.recvfrom() timeout")
                continue # "continues with the next cycle of the nearest enclosing loop"  (which is 'while e.is_set() is False')
            
            cmd = msgpack.unpackb(data)
            if self.debug>0: logging.debug('[{0}]: vid={1} received {2} bytes from [{3}:{4}], cmd[vid]={5}, cmd[type]={6}'.format( datetime.now().strftime('%c') , vid,len(data),addr[0],self.udp_port_in, cmd['vid'], cmd['type'] ))
            if self.debug>0: logging.debug('[{0}]: cmd={1}'.format( datetime.now().strftime('%c') ,cmd ))
            #print("\nvid=[",vid,"] received [", len(data), "] bytes from [",addr[0],":",udp_port_in,"]i\n", end='', flush=True)
            #print(" with data=[", data, "]")
            #
            # cmd={'vid': 100, 'type': 'avoidCmd', 'payload': {'theOtherOne': 101, 'pos': {'X': -181.49849813671045, 'Y': -199.9328931130526, 'Z': 30.0, 'psi': 3.09683979181008, 'lat': 29.188999992270787, 'lon': -81.04905391504329}, 'vel': {'Xd': -4.994993789034378, 'Yd': 0.2236896231566818, 'Zd': 0.0, 'psiDot': 0.0, 'spd_mps': 4.999999999999999}, 'dist': 34.57177265042399, 'distRate': -2.960424073393138}}
            
            # message fields defined in MoVE core's udpSender_changeRunState.py:
            #    msg = { 'vid':vid, 'type':type, 'payload': data }
            if cmd['vid'] == vid: # this is a message for this vehicle (vid's match)
            
                # what message type is this?
                msgType    = cmd['type']
                msgPayload = cmd['payload']
                if msgType == 'runStateCmd':
                    if msgPayload['runStateCmd'] == 1: # "ready?"
                        logging.debug('[{0}]: vid={1} got runState READY command! runStateCmd={2}'.format( datetime.now().strftime('%c') ,vid,msgPayload['runStateCmd']))
                    
                    if msgPayload['runStateCmd'] == 2: # "set"
                        logging.debug('[{0}]: vid={1} got runState SET command! runStateCmd={2}'.format( datetime.now().strftime('%c') ,vid,msgPayload['runStateCmd']))
                    
                    if msgPayload['runStateCmd'] == 3: # "go"
                        logging.debug('[{0}]: vid={1} got runState GO command! runStateCmd={2}'.format( datetime.now().strftime('%c') ,vid,msgPayload['runStateCmd']))
                    
                    if msgPayload['runStateCmd'] == 4: # "pause"
                        logging.debug('[{0}]: vid={1} got runState PAUSE command! runStateCmd={2}'.format( datetime.now().strftime('%c') ,vid,msgPayload['runStateCmd']))
                    
                    if msgPayload['runStateCmd'] == 5: # "exit"
                        logging.debug('[{0}]: vid={1} got runState ALL-EXIT command! exiting. runStateCmd={2},  setting threading.Event() e.set()'.format( datetime.now().strftime('%c') ,vid,msgPayload['runStateCmd']))
                    
                    self.eRunState.set() # runState raising it's hand - main_veh_model.py will see this
                    self.qRunState.put(msgPayload) # send a message to vehicle main to assign runState
                
                # these came from core: all_vehicles.py, poll_state(), veh_warnings = self.checkDistVel()
                #print( '\n\nself={0}\n\n'.format(vars(self)) )
                
                logging.debug('[{0}]: vid={1} got avoidCmd message2! msgType={2}, self.runState={3}, payload={4}'.format( datetime.now().strftime('%c') ,vid,msgType,self.runState[0],msgPayload))
                if (msgType == 'avoidCmd') and (self.runState[0]==3):
                    # payload_i = { 'theOtherOne': vid_j, 'pos': vehData_j['pos'], 'vel': vehData_j['vel'],
                    #               'dist': warn_data['dist'], 'distRate': warn_data['distRate'] } # j pos, j vel
                    logging.debug('[{0}]: vid={1} got avoidCmd message! payload={2}'.format( datetime.now().strftime('%c') ,vid,msgPayload))
                    if self.live_gps_follower==False:
                        self.veh.qAvoid.put( msgPayload ) # this queue is a message to avoid() in behaviors.py
                    
                if (msgType == 'detectCmd'):
                    # payload_detect = { 'vid':vid, 'X':pos['X'], 'Y':pos['Y'], 'Z':pos['Z'], 'lat':pos['lat'], 'lon':pos['lon'] }
                    logging.debug('[{0}]: vid={1} got detectCmd message! payload={2}'.format( datetime.now().strftime('%c') ,vid,msgPayload))
                    if self.live_gps_follower==False:
                        self.veh.qDetect.put( msgPayload ) # this queue is a message to avoid() in behaviors.py
                    
        logging.debug('exiting.')
    
    
    
    # -----------------------------------------------------------------------------------
    #                                    recv_gps()
    # -----------------------------------------------------------------------------------
    # thread to listen for live GPS lat/lon positions from another udp sender, like HyperIMU (Android), SensorLog (iPhone), or an Xbee bridge
    # note: this thread only starts if cfg.live_gps_follower==True (in veh_udp_io constructor)
    def recv_gps(self, e, vid, gps, sensorData):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # udp/ip socket
        sock.settimeout(0.5) # timeout ensures graceful exit close to this duration
        # listen to anyone, not just core_host_ip; bind() fails with core_host_ip in gps_addr
        gps_addr = ('0.0.0.0',self.udp_port_gps) # listen for GPS lat/lon messages at this ip and port
        try:
            sock.bind(gps_addr)
            logging.debug('vid={0}: inbound udp thread for GPS messages started in os_pid=[{1}]'.format(vid, os.getpid()))
            logging.debug('vid={0}: listening for live gps updates from [{1}:{2}]'.format(vid, gps_addr[0], gps_addr[1]))
        except OSError as err:
            logging.debug('\n\n')
            logging.debug( '\t\trecv_gps(): OSError: error trying to bind() for GPS messages!  {0}'.format(err) )
            logging.debug( '\t\trecv_gps(): gps_addr={}'.format(gps_addr))
            logging.debug( '\t\trecv_gps(): [{0}]: exiting'.format( datetime.now().strftime('%c') ) )
            logging.debug( '\n\n\n\n\n')
            self.e.set()     # exit udp_io threads
            self.veh.e.set() # exit MyVehicle and Behavior threads; note: cannot run veh.exit() b/c that's a method that doesn't exit until all exit - infinite loop - thread cannot exit because it's watch if all have exited
            exit(-1)
        
        gps['unixTime']         = -1
        gps['lat']              = -1
        gps['lon']              = -1
        gps['alt_m']            = -1
        gps['true_course']      = -1
        gps['psi']              = -1
        gps['spd_mps']          = -1
        gps['errorCnt']         =  0
        sensorData['mac']       = -1 # mac address of remote sender (whether Android or iPhone or Xbee)
        sensorData['batt_stat'] = -1 # battery status (only provided by Android's HyperIMU and iPhone's SensorLog)
        unixTime     = time.time()
        gps_unixTime = time.time() # init is incorrect at first dt_remote calculation
        autoDetectMsgType     = True # this triggers a 1-time incoming udp message classifier: HyperIMU or custom GPS+data sender?
        while e.is_set() is False:
            try:
                data,addr = sock.recvfrom(2048) # blocking call but timeout = 1/2 sec
                self.recvCntGps+=1
                if self.debug>1: logging.debug("received [{0}] bytes from [{1}] with message[{2}]".format(len(data),addr,data) )
            except socket.timeout:
                #logging.error("sock.recvfrom() timeout")
                continue # "continues with the next cycle of the nearest enclosing loop"  (which is 'while e.is_set() is False')
            
            # auto-detect which type of GPS sender is sending ASCII data (only HyperIMU or SensorLog)
            if autoDetectMsgType==True:
               gps_data_format_select = auto_detect_message_type(data)
            
            # decode GPS messages from custom GPS sender, HyperIMU, SensorLog or other
            gps, sensorData, unixTime, gps_unixTime, msg = live_gps_follower_decoding(vid,data,addr,gps,sensorData,unixTime,gps_unixTime,gps_data_format_select,self.debug)
            
            #for k, v in sensorData.items():
            #    logging.debug("\t\tsensorData: {0}={1}".format(k,v))
            
            if (autoDetectMsgType==True) and (gps_data_format_select>=0):
                # this should only occur once in the life of this vehicle model
                autoDetectMsgType=False
                try:
                    self.fname_log_gps='{0}_gps.csv'.format(self.veh.fname_log_veh_prefix) # see myVehicle.py | __init__()
                    logging.debug('opening vehicle gps and sensor data log file: {0}'.format(self.fname_log_gps))
                    self.fd_log_gps=open(self.fname_log_gps,'a') # open for subsequent appending
                    logging.debug('defining field names')
                    fieldnames=sorted(list( gps.keys() )) + sorted(list( sensorData.keys() )) + sorted(list( msg.keys() )) # sort to provide consistent csv writer outputs
                    fieldnames.insert(0,'timestamp')
                    fieldnames.insert(len(fieldnames),'addr0')
                    fieldnames.insert(len(fieldnames),'addr1')
                    logging.debug('fieldnames={0}'.format(fieldnames))
                    self.csv_gps = csv.DictWriter( self.fd_log_gps, fieldnames=fieldnames, quoting=csv.QUOTE_NONE, escapechar=' ' ) # <-- don't leave quotes in the .csv file
                    logging.debug('writing csv header')
                    self.csv_gps.writeheader()
                    #self.fd_log_gps.write( self.gps_and_sensor_data ) # append to the log file
                    #self.fd_log_gps.flush()
                except:
                    logging.debug('recv_gps(): logfile file error for gps and sensor data!  {}'.format( sys.exc_info()[0] ) )
                    logging.debug('[{0}]: exiting.'.format( datetime.now().strftime('%c') ) )
                    self.e.set()     # exit udp_io threads
                    self.veh.e.set() # exit MyVehicle and Behavior threads
                    exit(-1)
            
            # log incoming data to .csv in its arrival thread
            # note: this log will show network message delays and floods better than vehicle log file or Core log file
            # for merge notes see: https://stackoverflow.com/a/26853961/7621907
            #logging.debug('      ------- msg -------- msg={0}'.format(msg))
            logging.debug('\tvid={0}, name={1}, sensorData={2}'.format(self.vid, self.name, sensorData))
            dict_to_csv = { **{'timestamp': time.time()}, **gps , **sensorData, **msg, **{'addr0':addr[0], 'addr1':addr[1]} } # merged_dict = { **x , **y }
            self.csv_gps.writerow( dict_to_csv )
            self.fd_log_gps.flush()
            
            # send gps and sensorData dictionaries over to myVehicle.py | gather_live_gps_inputs() method
            if gps['validity']==True:
                #if self.debug>0: logging.debug('gps data: {}'.format( (lat, lon, alt, true_course, spd_mps) ))
                # send a dictionary composed of 2 dictionaries
                self.veh.qLiveGps.put( {'gps':gps, 'sensorData':sensorData} ) # send this to the gather_live_gps_inputs() method in myVehicle.py
        
        if hasattr(self,'fname_log_gps'):
            logging.debug('closing gps and udp sensor data log file [{}]'.format(self.fname_log_gps))
            self.fd_log_gps.close()
        else:
            logging.debug('self.fname_log_gps never opened; exiting without a logfile to close')
        logging.debug('exiting.')




# ------------------------------------------------------------------------------
# reference: https://learning-python.com/strings30.html
# - ASCII defines character representation only using integers on 0..127
# - UTF-8 encoding represents charachters using a variable-number-of-bytes scheme
# - Latin-1 encoding uses a single-byte on integer range 0..255 (1 8-bit value)
# - Struct and struct.pack() encodes into binary format stored in a bytes object
# - "A bytes object really is a sequence of small integers, each of which is in the range 0..255"
# ------------------------------------------------------------------------------
#
# ascii encoding check from: https://stackoverflow.com/questions/196345/how-to-check-if-a-string-in-python-is-in-ascii
isascii = lambda s: len(s) == len(s.encode()) # this requires 'utf-8' enoding to perform the isascii check properly b/c utf-8 is a multi-byte encoder for characters above 127
# ------------------------------------------------------------------------------




logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-14s) %(message)s',
)





if __name__ == "__main__":
    n=len(sys.argv)
    if n==5 and sys.argv[1]=='-f':
        print('reading scenario config file: {}'.format(sys.argv[2]))
        cfgFile =      sys.argv[2]
        vid     = int( sys.argv[3] )
        #cfgFile = '../scenario/default.cfg' # python's .ini format config file
        #cfgFile='../scenario/live_5_veh_uas_xbee.cfg'
        cfg, veh_names_builtins, veh_names_live_gps   = readConfigFile( cfgFile, vid )
    else:
        print('\n------- {0} is not the primary runtime script --------'.format(sys.argv[0]))
        print('\n-------     ---> for development and debugging only     --------\n')
        print('\t usage  :    {0} -f myScenario.cfg vid udp_port_gps\n'.format(sys.argv[0]))
        print('\t example:    {0} -f ../scenario/default.cfg 100 9000\n'.format(sys.argv[0]))
        sys.exit(0)
    print(sys.argv)
    #code.interact(local=dict(globals(), **locals()))
    # parallel-ssh launcher provides 4 command line arguments:
    cfg.vid         = int( sys.argv[3] ) # vid == vehicle identifier in MoVE core
    core_host_ip    = cfg.core_host_ip   # ip address for inbound and outbound udp messages for this vid
    udp_port_base   = cfg.udp_port_base  # udp port base
    udp_port_offset = cfg.udp_port_offset # udp port offset
    cInt            = cfg.cInt # 0.1 # (s) communication interval
    cfg.runState    = [1] # define as mutable list for class and main visibility
    
    # dummy objects for testing as a stand-alone
    tStart=time.time()
    t = 0.0
    tf= float('inf') # (s) final time of 'inf' means simulate indefinitely
    #tf=8.0 # (s)
    continuous=1
    eVeh = threading.Event()
    
    
    
    localLogFlag=0
    if cfg.log_level>=1:
        localLogFlag=1 # (0/1) write and append a .csv file every cInt?
    
    # this veh instance can be a dynamic model with behaviors, or a simpler live-GPS-follower - both interact with Core
    cfg.live_gps_follower = False
    if cfg.udp_port_base_gps>0:
        cfg.live_gps_follower=True
        cfg.udp_port_gps = cfg.udp_port_base_gps + cfg.vid # if live-GPS-follower, send incoming GPS lat/lon to port: (udp_port_base_gps+vid)
    
    # init the vehicle; no need to launch behavior threads when live_gps_follower==True
    veh = MyVehicle(cfg, localLogFlag)
    
    # this launches 3 processes: recv_core, recv_gps, udp_console_update
    udp_io = Veh_udp_io(cfg, veh) # udp_io has visibility to all veh and behaviors
    udp_io.debug=0 # (0/1) for verbose network send/recv console output
    
    try:
        while ( continuous==1 or t<tf ):

            srt_margin = 50.0
            srt_err = -0.01
            t = time.time() - tStart
            x = { 'X':0.1*t, 'Y':0.2*t, 'Z':0.3*t, 'psi':0.4*t }
            u = { 'steer':0.5*t, 'speed':0.6*t, 'pitch':0.7*t }
            vehData = { 'vid': cfg.vid, 'os_pid': udp_io.os_pid, 'msg_cnt': udp_io.sendCnt,
                        'srt_margin': srt_margin, 'srt_err': srt_err, 't': t, 'x': x, 'u':u }
            
            udp_io.send_core(vehData) # send udp updates at the loop timing, cInt
            
            if udp_io.e.is_set() is True: break # if threading.Event is set, break and exit main()
            udp_io.e.wait(cInt)
    
    except KeyboardInterrupt:
        logging.debug('caught KeyboardInterrupt, exiting.')
        udp_io.e.set() # exit udp_io threads
        veh.e.set()
    
    
    logging.debug('exiting.')
    udp_io.e.set()    # this sends exit command to: recv, udp_console_update
