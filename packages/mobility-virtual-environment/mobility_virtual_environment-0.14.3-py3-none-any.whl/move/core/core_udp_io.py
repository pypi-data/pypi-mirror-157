# Class definition for all udp inputs and outputs to and from MoVE Core,
# which includes:
# - aggregator method for gathering udp messages from all vehicle models
# - updateState method for creating and updating State, which contains all vehicles and states
# - send thread for sending to all vehicles
#
# Marc Compere, comperem@gmail.com
# created : 21 Feb 2017
# modified: 23 Jul 2021
#
# ---
# Copyright 2018 - 2021 Marc Compere
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
import socket
import msgpack # fast serialize/deserialize of complete python data structures: sudo pip3 install msgpack-python
import msgpack_numpy as m # msgpack for numpy objects: sudo pip3 install msgpack-numpy
import select
import queue
import logging
import threading
import pprint

class core_udp_io:
    """A class for aggregating incoming udp vehicle data and returning messages"""

    # =======================================================================================
    #                                      init()
    # =======================================================================================
    def __init__(self, cfg, qVehCmd, debug):

        self.nVehTot         = cfg.nVehTot
        self.vid_base        = cfg.vid_base
        self.udp_port_base   = cfg.udp_port_base
        self.udp_port_offset = cfg.udp_port_offset
        self.udp_ip_in       = cfg.udp_ip_in  # listening for udp from anyone, 0.0.0.0
        self.veh_host_ip = cfg.veh_host_ip # send to this ip; this assumes all vehicles are processes on this ip address (could be localhost or IPv4 address)
        self.tStart     = cfg.tStart
        self.State      = {} # initialize the State dict containing a snapshot of all vehicle's most recently reported states
        self.qVehCmd    = qVehCmd # for send()
        self.errorCnt   = 0 # the udp sendto() has a try-catch exception block
        self.debug      = debug
        self.pp         = pprint.PrettyPrinter(indent=4)

        self.sockets = self.open_and_bind(self.nVehTot, self.vid_base, self.udp_ip_in, self.udp_port_base, debug)

        #logging.debug('total vehicle, behavior, and udp threads: {}'.format( threading.active_count() ))

    # =======================================================================================
    #                                  open_and_bind()
    # =======================================================================================
    # open a udp socket for each vehicle
    def open_and_bind(self, nVehTot, vid_base, udp_ip_in, udp_port_base, debug):
        # open and bind() to listen on N udp sockets
        sockets = {} # dictionary with nVehTot numebr of entries like this: { vid: sockForVid }
        for i in range(nVehTot):
            vid = vid_base + i
            udp_port_in = vid + udp_port_base
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP/IP, create a socket for each vehicle id (vid)
            if debug==1: print("i={0}, sock.bind({1})".format(vid,(udp_ip_in,udp_port_in)))
            sock.bind((udp_ip_in, udp_port_in)) # must bind to listen
            sockets[vid] = sock

        if debug>1: logging.debug('sockets: {0}'.format(sockets))
        return sockets

        # this is an example sockets dict, each of which are bound on the local port for listening:
        #   {100: <socket.socket fd=3, family=AddressFamily.AF_INET, type=SocketKind.SOCK_DGRAM, proto=0, laddr=('0.0.0.0', 5100)>,
        #    101: <socket.socket fd=4, family=AddressFamily.AF_INET, type=SocketKind.SOCK_DGRAM, proto=0, laddr=('0.0.0.0', 5101)>,
        #    102: <socket.socket fd=5, family=AddressFamily.AF_INET, type=SocketKind.SOCK_DGRAM, proto=0, laddr=('0.0.0.0', 5102)> }

    # =======================================================================================
    #                                  aggregator()
    # =======================================================================================
    # aggregator thread gathers udp messages from all vehicles
    #
    # producer!   aggregator() is a data *producer* for the core traffic algorithms
    #             the *consumer* is    All_vehicles::poll_state()   and friends
    def aggregator(self, sockets, cfg, e, eDataPollReq, qState, debug):
        
        cnt=0
        cntSelectTimeout = 0 # determine 'nobody is sending' if this counter exceeds 5
        dt = 0.5 # (s) loop periodically to catch the all-exit signal from main, e.is_set()
        tStart=self.tStart
        
        logging.debug('\nlistening for udp traffic...')
        #logging.debug('\nsockets={}\n'.format(sockets))
        
        while e.is_set() is False:
            if debug==2: logging.debug("{0} listening...   cnt={1}".format(sys.argv[0],cnt))
            
            # select() blocks and controls the loop rate; python select() is an API directly to the OS select() and is fast
            socketsList = list(sockets.values()) # select() takes a list
            inputready,outputready,exceptready = select.select(socketsList,[],[],dt) # 1/2sec timeout to exit gracefully with e.is_set()
            
            if not inputready and not outputready and not exceptready: # planned select() timeout to catch the graceful exit command, e.is_set()
                if debug>1: logging.debug('t={0}: select() timed out. cntSelectTimeout={1}, listening...\n'.format(time.time(),cntSelectTimeout))
                cntSelectTimeout+=1
                if cntSelectTimeout>5:
                    logging.debug('t={0}: select() timed out {1} times - nobody sending!... still listening...\n'.format(time.time(),cntSelectTimeout))
                    self.State = {} # nobody is sending - set State to an empty dictionary
            
            else:
                for s in inputready:
                    
                    # receive all udp packets from vehicles (with vehData) reporting their state information (these are like the FAA's ADS-B out's)
                    msgpackedVehData, addr = s.recvfrom(2048) # buffer size of 2048 bytes
                    if debug>1: logging.debug("recd {0} bytes from [{1}:{2}]".format(len(msgpackedVehData),addr[0],s.getsockname()[1]))
                    
                    # unpack the data into a python dict with vid, time, pos, vel, and other key entries
                    vehData = msgpack.unpackb(msgpackedVehData, object_hook=m.decode)  # fast deserialize of entire python data structure, incl numpy objects
                    #logging.debug('vid={0}, vehData keys: {1}'.format(vehData['vid'],vehData.keys()))
                    
                    # if vehData={'hex': 'ac91d4', 'lat': 28.263794, 'lon': -81.275958, 'nucp': 7, 'seen_pos': 12.9, 'altitude': 33000, 'mlat': [], 'tisb': [], 'messages': 64, 'seen': 3.8, 'rssi': -30.0}
                    if 'hex' in vehData: # this is a real vehicle detected in nearby airspace from ADS-B messages
                        vehData['vehName']=vehData['hex'] # ICAO aircraft number
                        vehData['vehType']='adsb'
                        # populate pos=lat,lon,altitude
                        #          vel
                    
                    
                    if debug>1:
                        #for k,v in vehData.items():
                        #    print('{0}={1}'.format(k,v))
                        
                        vehName = vehData['vehName'].decode("utf-8")
                        vehType = vehData['vehType']
                        rS      = vehData['runState'] # local vars for printing only
                        rsDesc  = cfg.runStateDesc[ rS ] # runState is a list
                        behStr  = vehData['bIdName'].decode("utf-8") # behavior ID name
                        #print(' ')
                        #print( "vehData['pos']={0}".format(vehData['pos']) )
                        #print(' ')
                        # printing notes:
                        #   vehData={}
                        #   vehData['pos']={b'X': -61.91099657735414, b'Y': -7.69870012784862, b'Z': 0.0, b'psi': 2.5090201432794, b'lat': 29.188453294773275, b'lon': -81.04626976449573}
                        #   for item in vehData['pos']:
                        #       print( "{0}={1:-8.4f}".format( item.decode('utf-8') , vehData['pos'][item] ) )
                        posStr    = ''.join(['{0}={1:-10.4f}, '.format(item.decode('utf-8'),vehData['pos'][item]) for item in vehData['pos'].__iter__()]) # pos class was msgunpacked as a dictionary
                        print('posStr={}'.format(posStr))
                        print( 'vehData[srt_err_avg]={0:-8.4f}'.format(vehData['srt_err_avg']) )
                        detectStr = ''.join(['{0}={1:-10.4f}, '.format(item.decode('utf-8'),vehData['detectMsg'][item]) for item in vehData['detectMsg'].__iter__()]) # pos class was msgunpacked as a dictionary
                        logging.debug('vid={0}, vehName={1}, vehType={2}, runState={3}, beh={4}, msg_cnt_in={5}, msg_cnt_out={6}, msg_errorCnt={7}. srt_margin_avg={8}, srt_err_avg={9}, pos={10}'\
                               .format(vehData['vid'], \
                                        vehName,\
                                        vehType, \
                                        rsDesc, \
                                        behStr, \
                                        vehData['msg_cnt_in'],\
                                        vehData['msg_cnt_out'], \
                                        vehData['msg_errorCnt'], \
                                        vehData['srt_margin_avg'], \
                                        vehData['srt_err_avg'],\
                                        posStr ))

                        logging.debug("vid={0}, {1:10s}, {2}, {3}, [{4:<17s}], detect[{5:s}]"\
                               .format(vehData['vid'], vehName, vehType, rsDesc, behStr, detectStr ))
                    if debug>2: logging.debug(" with vehData=[{0}]".format( vehData ))
                    cnt+=1
                    cntSelectTimeout = 0 # reset consecutive timeout counter
                    
                    # update the aggregate state representation, S, with this particular vehicle's new state information
                    self.updateState( vehData ) # update the aggreagte state dict State with the vid'th vehicle data that just came in via udp
            
            
            # data requested? if so, send all veh information for distance and collision processing
            if eDataPollReq.is_set() is True:
                if debug>1: logging.debug('t={0:-6f}: data requested! sending State snapshot of {1} bytes ---'.format(time.time(),sys.getsizeof(self.State)))
                qState.put( self.State ) # queue's are thread-safe and use locks internally
                eDataPollReq.clear()
            
        logging.debug("received exit message! e.is_set()={0}, exiting at: {1}, cnt={2}".format(e.is_set(), time.ctime(), cnt))
        elapsedTime = time.time() - tStart # elapsed wall-clock time in seconds
        logging.debug("\n\nreceived {0} udp packets in {1} seconds, rate={2}(pkts/sec)".format( cnt, elapsedTime, cnt/elapsedTime ))



    # =======================================================================================
    #                                  updateState()
    # =======================================================================================
    # updateState() combines the i'th vehicle's state information into a single large dictionary, State.
    # helper method for aggregator()
    def updateState( self, vehData ):
        
        if self.debug>1: print('vehData: ', end='')
        if self.debug>1: pprint.pprint( vehData )
        # this is what you've got to work with - this object is from udp and *defined* by the vehicle model
        #
        # vehData: {'vid': 104, 'vehName': 'happy', 'vehType': 'aerial', 'vehSubType': 'fixedwing', 'runState': 1,
        #           'msg_cnt_in': 0, 'msg_cnt_out': 5, 'msg_errorCnt': 0, 'srt_margin_avg': 0.0, 'srt_err_avg': 0.0,
        #           't': -1, 'gps_unixTime': 0, 'pos': {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'psi': 0.0, 'hdg': 0.0,
        #           'lat': 29.193110999581492, 'lon': -81.0461709999998}, 'vel': {'Xd': 0.0, 'Yd': 0.0, 'Zd': 0.0,
        #           'psiDot': 0.0, 'spd_mps': 0.0}, 'detectMsg': {'objId': 0, 'lastSeen': 0, 'lastLoc_X': 0,
        #           'lastLoc_Y': 0, 'lastLoc_Z': 0, 'lastLoc_lat': 0, 'lastLoc_lon': 0},
        #           'waypoint_status': {'waypoint': -1, 'lap': -1, 'spd_mps': -1}, 'u': [0.0, 5, 0.0, 0.0],
        #           'bIdCmd': 0, 'bIdName': 'self.wander', 'bIdProgress': 0.0, 'missionAction': 'none',
        #           'missionState': -1, 'missionPctComplete': 0.0, 'missionProgress': -1,
        #           'missionLastCmdTime': 'Thu Apr  7 09:52:26 2022', 'missionStatus': 'readyWait', 'missionCounter': 1,
        #           'L_char': 2.0, 'sensorData': {'mac': 104, 'batt_stat': -1}}
        
        vid = vehData['vid']
        
        # add timestamp and update this vehicle's data in the allVehicle.S state object
        tStamp = time.time()
        tNow = {'tStamp': tStamp }
        self.State[vid] = { **tNow, **vehData } # State is defined as a dictionary of dictionaries; this merge works for Python>=3.5
        
        if self.debug>1: logging.debug('t={0:-0.6f}, sizeof(S)={1}, updating allVeh.S with veh ID: {2}'.format( tStamp, sys.getsizeof(self.State), vid ))
        if self.debug>1:
            print('\nvehData[{0}]:'.format(vid))
            pprint.pprint(vehData)
            print('\n')
            # for example:
            # vehData[100]:
            # {'L_char': 2.0,
            #  'bIdCmd': 100,
            #  'bIdName': 'live_gps_follower',
            #  'batt_stat': -2,
            #  'detectMsg': {'lastLoc_X': 0,
            #                'lastLoc_Y': 0,
            #                'lastLoc_Z': 0,
            #                'lastLoc_lat': 0,
            #                'lastLoc_lon': 0,
            #                'lastSeen': 0,
            #                'objId': 0},
            #  'gps_unixTime': 1627260166.824,
            #  'msg_cnt_in': 2,
            #  'msg_cnt_out': 93,
            #  'msg_errorCnt': 0,
            #  'pos': {'X': -31748.253682491428,
            #          'Y': -77940.73251857888,
            #          'Z': 8.4739990234375,
            #          'hdg': 0.004550436035499999,
            #          'lat': 28.4891077,
            #          'lon': -81.37023534,
            #          'psi': 0.004550436035499999},
            #  'waypoint_status': {'lap': -1, 'spd_mps': -1, 'waypoint': -1},
            #  'runState': 3,
            #  'sensorData': {'accel_x': -1.2568301,
            #                 'accel_y': 0.53389853,
            #                 'accel_z': 9.662517,
            #                 'batt_stat': 81.0,
            #                 'mac': ''},
            #  'srt_err_avg': -6.910800933823066e-05,
            #  'srt_margin_avg': 98.97304725647065,
            #  't': 5.099853277206421,
            #  'u': [0.0, 0.0, 0.0],
            #  'vehName': 'speedracer',
            #  'vehSubType': 'rotorcraft',
            #  'vehType': 'aerial',
            #  'vel': {'Xd': 0.0, 'Yd': 0.0, 'Zd': 0.0, 'psiDot': 0.0, 'spd_mps': 0.0},
            #  'vid': 100}


        if self.debug>=3:
            print('State:') # this contains all timestamped vehData info for all vehicles - tons of debugging output!
            pprint.pprint(self.State)
            print('\n')
            sys.stdout.flush()
            #
            # example output showing two vehicles in State when nVeh==5:
            # ------------------------------------------------------------------
            # State:
            # {100: {'L_char': 2.0,
            #        'bIdCmd': 0,
            #        'bIdName': 'self.wander',
            #        'bIdProgress': 0.0,
            #        'detectMsg': {'lastLoc_X': 0,
            #                      'lastLoc_Y': 0,
            #                      'lastLoc_Z': 0,
            #                      'lastLoc_lat': 0,
            #                      'lastLoc_lon': 0,
            #                      'lastSeen': 0,
            #                      'objId': 0},
            #        'gps_unixTime': 0,
            #        'missionAction': 'none',
            #        'missionCounter': 1,
            #        'missionLastCmdTime': 'Thu Apr  7 09:54:49 2022',
            #        'missionPctComplete': 0.0,
            #        'missionProgress': -1,
            #        'missionState': -1,
            #        'missionStatus': 'readyWait',
            #        'msg_cnt_in': 2,
            #        'msg_cnt_out': 6634,
            #        'msg_errorCnt': 0,
            #        'pos': {'X': -42.25377539184404,
            #                'Y': -22.35524480349018,
            #                'Z': 0.0,
            #                'hdg': 193.42228597926567,
            #                'lat': 29.19290907711141,
            #                'lon': -81.0466055362174,
            #                'psi': 3.37585567948636},
            #        'runState': 3,
            #        'sensorData': {'batt_stat': -1, 'mac': 100},
            #        'srt_err_avg': -4.666328425628314e-05,
            #        'srt_margin_avg': 97.49937585306319,
            #        't': 652.8,
            #        'tStamp': 1649340437.573653,
            #        'u': [0.0, 5, 0.0, 0.0],
            #        'vehName': 'billy',
            #        'vehSubType': 'rotorcraft',
            #        'vehType': 'aerial',
            #        'vel': {'Xd': -4.86342838233175,
            #                'Yd': -1.1606310223020844,
            #                'Zd': 0.0,
            #                'psiDot': 0.0,
            #                'spd_mps': 5.0},
            #        'vid': 100,
            #        'waypoint_status': {'lap': -1, 'spd_mps': -1, 'waypoint': -1}},
            #  101: {'L_char': 2.0,
            #        'bIdCmd': 0,
            #        'bIdName': 'self.wander',
            #        'bIdProgress': 0.0,
            #        'detectMsg': {'lastLoc_X': 0,
            #                      'lastLoc_Y': 0,
            #                      'lastLoc_Z': 0,
            #                      'lastLoc_lat': 0,
            #                      'lastLoc_lon': 0,
            #                      'lastSeen': 0,
            #                      'objId': 0},
            #        'gps_unixTime': 0,
            #        'missionAction': 'none',
            #        'missionCounter': 1,
            #        'missionLastCmdTime': 'Thu Apr  7 09:54:50 2022',
            #        'missionPctComplete': 0.0,
            #        'missionProgress': -1,
            #        'missionState': -1,
            #        'missionStatus': 'readyWait',
            #        'msg_cnt_in': 2,
            #        'msg_cnt_out': 6632,
            #        'msg_errorCnt': 0,
            #        'pos': {'X': 105.52065600744064,
            #                'Y': -140.27093706153428,
            #                'Z': 0.0,
            #                'hdg': 89.31324444975093,
            #                'lat': 29.191845325157892,
            #                'lon': -81.04508504798152,
            #                'psi': 1.55881015469627},
            #        'runState': 3,
            #        'sensorData': {'batt_stat': -1, 'mac': 101},
            #        'srt_err_avg': -0.0001248836516879239,
            #        'srt_margin_avg': 97.29816726157478,
            #        't': 652.6,
            #        'tStamp': 1649340437.5815427,
            #        'u': [0.0, 5, 0.0, 0.0],
            #        'vehName': 'rufus',
            #        'vehSubType': 'rotorcraft',
            #        'vehType': 'aerial',
            #        'vel': {'Xd': 0.059929425475751606,
            #                'Yd': 4.999640833496157,
            #                'Zd': 0.0,
            #                'psiDot': 0.0,
            #                'spd_mps': 5.0},
            #        'vid': 101,
            #        'waypoint_status': {'lap': -1, 'spd_mps': -1, 'waypoint': -1}},
            #  102: {'L_char': 2.0,
            #        'bIdCmd': 0,
            #        'bIdName': 'self.wander',
            #        'bIdProgress': 0.0,
            #        'detectMsg': {'lastLoc_X': 0,
            #                      'lastLoc_Y': 0,
            #                      'lastLoc_Z': 0,
            #                      'lastLoc_lat': 0,
            #                      'lastLoc_lon': 0,
            #                      'lastSeen': 0,
            #                      'objId': 0},
            #        'gps_unixTime': 0,
            #        'missionAction': 'none',
            #        'missionCounter': 1,
            #        'missionLastCmdTime': 'Thu Apr  7 09:54:50 2022',
            #        'missionPctComplete': 0.0,
            #        'missionProgress': -1,
            #        'missionState': -1,
            #        'missionStatus': 'readyWait',
            #        'msg_cnt_in': 2,
            #        'msg_cnt_out': 6630,
            #        'msg_errorCnt': 0,
            #        'pos': {'X': 114.46604127387126,
            #                'Y': 21.66283055863908,
            #                'Z': 0.0,
            #                'hdg': 529.3726608707703,
            #                'lat': 29.1933069228167,
            #                'lon': -81.04499367377333,
            #                'psi': 9.2392957446329},
            #        'runState': 3,
            #        'sensorData': {'batt_stat': -1, 'mac': 102},
            #        'srt_err_avg': -0.0001261043548129242,
            #        'srt_margin_avg': 97.24538520283159,
            #        't': 652.4,
            #        'tStamp': 1649340437.5893018,
            #        'u': [0.0, 5, 0.0, 0.0],
            #        'vehName': 'dopey',
            #        'vehSubType': 'fixedwing',
            #        'vehType': 'aerial',
            #        'vel': {'Xd': -4.914237171823453,
            #                'Yd': 0.9221024992204627,
            #                'Zd': 0.0,
            #                'psiDot': 0.0,
            #                'spd_mps': 5.0},
            #        'vid': 102,
            #        'waypoint_status': {'lap': -1, 'spd_mps': -1, 'waypoint': -1}},
            #  103: {'L_char': 2.0,
            #        'bIdCmd': 0,
            #        'bIdName': 'self.wander',
            #        'bIdProgress': 0.0,
            #        'detectMsg': {'lastLoc_X': 0,
            #                      'lastLoc_Y': 0,
            #                      'lastLoc_Z': 0,
            #                      'lastLoc_lat': 0,
            #                      'lastLoc_lon': 0,
            #                      'lastSeen': 0,
            #                      'objId': 0},
            #        'gps_unixTime': 0,
            #        'missionAction': 'none',
            #        'missionCounter': 1,
            #        'missionLastCmdTime': 'Thu Apr  7 09:54:50 2022',
            #        'missionPctComplete': 0.0,
            #        'missionProgress': -1,
            #        'missionState': -1,
            #        'missionStatus': 'readyWait',
            #        'msg_cnt_in': 2,
            #        'msg_cnt_out': 6628,
            #        'msg_errorCnt': 0,
            #        'pos': {'X': 73.90933295744412,
            #                'Y': 82.8745145074905,
            #                'Z': 0.0,
            #                'hdg': -35.458760722467446,
            #                'lat': 29.193859260581657,
            #                'lon': -81.04541108919274,
            #                'psi': -0.61887211272708},
            #        'runState': 3,
            #        'sensorData': {'batt_stat': -1, 'mac': 103},
            #        'srt_err_avg': -0.00011440753932220074,
            #        'srt_margin_avg': 97.16139081422392,
            #        't': 652.2,
            #        'tStamp': 1649340437.5992248,
            #        'u': [0.0, 5, 0.0, 0.0],
            #        'vehName': 'grumpy',
            #        'vehSubType': 'fixedwing',
            #        'vehType': 'aerial',
            #        'vel': {'Xd': 4.072666405034263,
            #                'Yd': -2.9005841400147823,
            #                'Zd': 0.0,
            #                'psiDot': 0.0,
            #                'spd_mps': 5.0},
            #        'vid': 103,
            #        'waypoint_status': {'lap': -1, 'spd_mps': -1, 'waypoint': -1}},
            #  104: {'L_char': 2.0,
            #        'bIdCmd': 0,
            #        'bIdName': 'self.wander',
            #        'bIdProgress': 0.0,
            #        'detectMsg': {'lastLoc_X': 0,
            #                      'lastLoc_Y': 0,
            #                      'lastLoc_Z': 0,
            #                      'lastLoc_lat': 0,
            #                      'lastLoc_lon': 0,
            #                      'lastSeen': 0,
            #                      'objId': 0},
            #        'gps_unixTime': 0,
            #        'missionAction': 'none',
            #        'missionCounter': 1,
            #        'missionLastCmdTime': 'Thu Apr  7 09:54:50 2022',
            #        'missionPctComplete': 0.0,
            #        'missionProgress': -1,
            #        'missionState': -1,
            #        'missionStatus': 'readyWait',
            #        'msg_cnt_in': 2,
            #        'msg_cnt_out': 6626,
            #        'msg_errorCnt': 0,
            #        'pos': {'X': -79.30802708812878,
            #                'Y': 163.2590862396749,
            #                'Z': 0.0,
            #                'hdg': -424.09039692880225,
            #                'lat': 29.194584244065894,
            #                'lon': -81.04698744370327,
            #                'psi': -7.4017736262366},
            #        'runState': 3,
            #        'sensorData': {'batt_stat': -1, 'mac': 104},
            #        'srt_err_avg': -8.334636683684944e-05,
            #        'srt_margin_avg': 97.44846633375843,
            #        't': 652.0,
            #        'tStamp': 1649340437.6106033,
            #        'u': [0.0, 5, 0.0, 0.0],
            #        'vehName': 'happy',
            #        'vehSubType': 'fixedwing',
            #        'vehType': 'aerial',
            #        'vel': {'Xd': 2.1847633318618387,
            #                'Yd': -4.497422504474308,
            #                'Zd': 0.0,
            #                'psiDot': 0.0,
            #                'spd_mps': 5.0},
            #        'vid': 104,
            #        'waypoint_status': {'lap': -1, 'spd_mps': -1, 'waypoint': -1}}}
            # ------------------------------------------------------------------
            
    # =======================================================================================
    #                                        send()
    # =======================================================================================
    # thread for sending messages from multiple locations in core to 1 or all vehicles
    # message dictionary structure: msg = {'vid':vid, 'type':type, 'payload': data }
    def send(self, e, qVehCmd, debug):
        logging.debug('started udp send() thread')
        #logging.debug('\nsockets={}\n'.format(sockets))
        udpSendCnt=0
        dt=0.5 # (s) loop periodically to catch the all-exit signal from main, e.is_set()

        while e.is_set() is False:
            if debug>1: logging.debug("{0} waiting for a qVehCmd event...   cnt={1}".format(sys.argv[0],udpSendCnt))

            try:
                msg = qVehCmd.get(block=True, timeout=dt) # get the command from whomever put it there: poll_state() for collision avoidance or detectId information
                if debug>1: logging.debug("[{0}]: udpSendCnt={1}, received command: {2}".format( datetime.now().strftime('%c') , udpSendCnt, msg))

                # here's what just came over the qVehCmd from    all_veh::poll_state()   :
                #     msg_i = { 'vid': vid_i, 'type' : 'avoidCmd', 'payload':payload_i }     (send *to* vid)
                #     payload_i = { 'theOtherOne': vid_j, 'pos': vehData_j['pos'], 'vel': vehData_j['vel'], 'dist': warn_data['dist'], 'distRate': warn_data['distRate'] } # j pos, j vel
                #if msg['type'] is 'avoidCmd':

                if debug>1: logging.debug('[{0}]: sending msg type [{1}] to vid [{2}]'.format( datetime.now().strftime('%c') , msg['type'], msg['vid']))
                if debug>1: logging.debug('\n\n\t\tmsg={}'.format(msg))
                # i'th msg, then j'th message; these two messages came from all_veh::poll_state()
                vid = msg['vid'] # send to this vehicle (we assume is running on veh_host_ip)
                udp_port_out = vid + self.udp_port_base + self.udp_port_offset # remote process is listening on this port
                msgPacked = msgpack.packb(msg, default=m.encode) # fast serialize for entire python data structure w/o detailing each field (incl numpy datatypes)
                try:
                    nBytes = self.sockets[vid].sendto(msgPacked,(self.veh_host_ip, udp_port_out)) # for now, we assume all vid's are at the same ip address
                    udpSendCnt+=1
                    if (self.debug>1): logging.debug('nBytes sent: {0} to {1}:{2}, udpSendCnt={3}'.format(nBytes, self.veh_host_ip, udp_port_out, udpSendCnt))
                except OSError as err:
                    self.errorCnt +=1
                    logging.debug('caught OSError number [{0}]!: {1}'.format(self.errorCnt,err))
                    # OSError: [Errno 101] Network is unreachable


                # this is an example sockets dict, each of which are bound on the local port for listening:
                #   {100: <socket.socket fd=3, family=AddressFamily.AF_INET, type=SocketKind.SOCK_DGRAM, proto=0, laddr=('0.0.0.0', 5100)>,
                #    101: <socket.socket fd=4, family=AddressFamily.AF_INET, type=SocketKind.SOCK_DGRAM, proto=0, laddr=('0.0.0.0', 5101)>,
                #    102: <socket.socket fd=5, family=AddressFamily.AF_INET, type=SocketKind.SOCK_DGRAM, proto=0, laddr=('0.0.0.0', 5102)> }



                # if (self.debug>0): logging.debug('t={}: sending msg type [{0}] to vid [{1}]'.format(time.time(), msg['type'], msg['vid']))
                # msgPacked = msgpack.packb(msg, default=m.encode) # fast serialize for entire python data structure w/o detailing each field (incl numpy datatypes)
                # self.sockets
                # nBytes = self.sock_out.sendto(msgPacked,self.veh_host_ip) # assume all vehicles are on the same remote machine -
                # self.sendCnt+=1
                # if (self.debug>0): logging.debug('nBytes sent: {0}, udpSendCnt={1}'.format(nBytes,self.sendCnt))

            except queue.Empty:
                if debug>1: logging.debug("t={0:-0.6f}: looping periodically to catch exit event...   udpSendCnt={1}".format(time.time(),udpSendCnt))



        logging.debug("received exit message! e.is_set()={0}, exiting at: {1}, udpSendCnt={2}".format(e.is_set(), time.ctime(), udpSendCnt))
        elapsedTime = time.time() - self.tStart # elapsed wall-clock time in seconds
        logging.debug("\n\nsent {0} cmds in {1:0.6} seconds, rate={2:0.1f}(cmds/sec)".format( udpSendCnt, elapsedTime, udpSendCnt/elapsedTime ))


    # =======================================================================================
    #                                  close()
    # =======================================================================================
    # close all udp sockets
    #
    # if this is unused, DELETE
    # def close( self ):
    #     # close all ports
    #     for i in range(self.nVehTot):
    #         vid = i + self.vid_base
    #         sock=self.sockets[vid]
    #         if debug==1: print("vid={}, sock.close()".format(vid))
    #         sock.close()
