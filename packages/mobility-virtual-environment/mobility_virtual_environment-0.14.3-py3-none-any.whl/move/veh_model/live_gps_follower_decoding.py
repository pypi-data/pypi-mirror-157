#!/usr/bin/python3
#
# live_gps_follower_decoding.py -   define 1 function to decode and return a gps
#                                   message received over udp
#
# this function is called only in recv_gps() thread which resides in veh_udp_io.py
# and is only executed when live_gps_follower==True for the launched vehicle model
#
#
# Marc Compere, comperem@gmail.com
# created : 18 Jul 2018
# modified: 23 Jul 2021
#
# --------------------------------------------------------------
# Copyright 2018 - 2020 Marc Compere
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

import msgpack
import logging
import time

import code # drop into a python interpreter to debug using: code.interact(local=dict(globals(), **locals()))


logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-14s) %(message)s',
)

# see dict_from_list_example.py
def dictionary_from_list(lst):
    res_dct = { 'field'+str(i): lst[i] for i in range(0, len(lst)) }
    return res_dct


def auto_detect_message_type( data ):
    
    gps_data_format_select = -1 # init with non-useful value assuming it gets updated properly below
    #code.interact(local=dict(globals(), **locals()))
    
    # check if this data is all-ASCII. if so, then it's from HyperIMU. If not, then it's from a msgpack udp sender
    if isascii(data.decode('ISO-8859-1'))==True:
        # this is either HyperIMU (Android) or SensorLog (iPhone)
        fields=data.decode().split(",") # decode makes it a string; split provides individual fields as a list
        
        # make a decision on timestamp:
        # HyperIMU provides unixTime*1000 which is 13 digits before the decimal point:      fields[0] = '  1595085157366     '
        # SensorLog provides unixTime   , which is 10 digits before the decimal point:      fields[0] = '1595100684.386936'
        var=round( float(fields[0]) ) # HyperIMU gives: var=1595085157366,   SensorLog gives: var=1595100684
        n=len(str(var))               # HyperIMU gives: n=13,                SensorLog gives: n=10
        
        if (n>0) & (n>11):
            gps_data_format_select = 1 # HyperIMU
            autoDetectMsgType=False
            logging.debug(' ')
            logging.debug("\tauto-detected HyperIMU message! assigning gps_data_format_select={0}".format(gps_data_format_select) )
            logging.debug(' ')
        
        if (n>0) & (n<=11):
            gps_data_format_select = 2 # SensorLog
            autoDetectMsgType=False
            logging.debug(' ')
            logging.debug("\tauto-detected SensorLog message! assigning gps_data_format_select={0}".format(gps_data_format_select) )
            logging.debug(' ')
        
        if n==0:
            logging.debug(' ')
            logging.debug("\n\n\tError - received GPS message with length n=0. unable to auto-detect live GPS sender type".format(gps_data_format_select) )
            logging.debug(' ')
        
    else:
        # this wasn't an ASCII message
        gps_data_format_select=0 # 0->binary GPS message from (a) Xbee or (b) other custom device sending binary data
        logging.debug(' ')
        logging.debug("\n\tauto-detected custom non-ascii message! assigning gps_data_format_select={0}".format(gps_data_format_select) )
        logging.debug(' ')
        autoDetectMsgType=False

    return gps_data_format_select







# gps_data_format_select == 0 -> xbee bridge, serial_GPS_Xbee_receiver_v6.py or similar,
#                                or serial_GPS_to_UDP_with_pynmea_GLONASS.py
#
# gps_data_format_select == 1 -> HyperIMU Android app with these settings:
#   (a) only accel sensor turned on
#   (b) Stream Protocol: udp stream
#   (c) Sampling Rate: 500ms, 100ms, 10ms; whatever you want and the network allows
#   (d) Persistent: checked yes (not sure if this is used or works or not)
#   (e) Header: Timestamp and MAC address both toggled ON (and battery)
#   (f) Trailer: GPS toggled on
#   (g) Trailer: NMEA toggled on
#   (h) Stay Awake: checked yes
#
# gps_data_format_select == 2 -> SensorLog iPhone app with these settings:
# General logging settings:
#   (a) logging rate: 10Hz
#   (b) log format:  ,  csv
#   (c) fill empty data with previous: ON
#   (d) ML friendly datatypes (csv): ON
#   (e) log to file: ON
#   (f) log to stream: ON
# Stream settings: 
#   (g) protocol: udp
#   (h) ip: [insert MoVE ip]
#   (i) port: [insert port], recall GPS port = udp_port_base_gps + vid
# Sensors and data:
#   (j) Core Location: ON
#   (k) Label: ON

def live_gps_follower_decoding(vid,data,addr,gps,sensorData,unixTime,gps_unixTime,gps_data_format_select,debug):
    #gps_data_format_select = 1
    #logging.debug('live_gps_follower_decoding(): gps_data_format_select={0}'.format(gps_data_format_select))
    #logging.debug('live_gps_follower_decoding(): addr={0}'.format(addr))
    #logging.debug('live_gps_follower_decoding(): data={0}'.format(data))
    
    t_last          = unixTime     # capture unixtime     before updating it
    t_last_remote   = gps_unixTime # capture gps_unixTime before updating it
    unixTime        = time.time()  # time on the machine running this script
    
    
    if gps_data_format_select==0:
        msg    = msgpack.unpackb(data)
        if debug>0: logging.debug('vid={0} received {1} bytes from [{2}:{3}]'.format(vid,len(data),addr[0],addr[1]))
        if debug>0: logging.debug('data={0}'.format(msg))
        #print('msg=',msg)
        #code.interact(local=dict(globals(), **locals()))
        
        # Xbee message?
        if 'xbee_msg_id' in msg:
            xbee_msg_id_str=msg['xbee_msg_id'].decode('utf-8')
            
            if (xbee_msg_id_str=='xb01') or (xbee_msg_id_str=='xb02'):
                gps_unixTime = msg['timestamp'] # (s) unix time from GPS over Xbee network
                
                localtime_remote = time.asctime( time.localtime( gps_unixTime ) ) # human readable time from incoming data
                gps['dt']               = unixTime     - t_last
                gps['dt_remote']        = gps_unixTime - t_last_remote
                #if debug>0: print('t={0}, '.format(unixTime - tStart), end='')
                if debug>0: logging.debug('unixTime={0:0.10f}, gps_unixTime={1:0.10f}, dt={2:0.10f}, dt_remote={3:0.10f}, localtime_remote, {4}, ' \
                                  .format(unixTime, gps_unixTime, gps['dt'], gps['dt_remote'], localtime_remote) )
                
                # gps['unixTime'], gps['lat'], gps['lon'], gps['alt_m'], gps['true_course'], gps['psi'], gps['spd_mps'], gps['validity']
                gps['unixTime']     = gps_unixTime          # unixtime
                gps['lat']          = msg['lat']            # lat
                gps['lon']          = msg['lon']            # lon
                gps['alt_m']        = msg['alt_m']          # alt_m
                                                            # true_course
                gps['yaw_deg']      = msg['yaw_deg']        # psi
                                                            # spd_mps
                gps['validity']     = True # Xbee senders do not send until gps time and lat,lon are !=0.0
                
                # everything else is sensorData
                sensorData['mac']          = msg['xbee_mac']
                sensorData['xbee_time']    = msg['xbee_timestamp']
                sensorData['hostname_str'] = msg['hostname_str']
                sensorData['xbee_msg_id']  = msg['xbee_msg_id']
                sensorData['pressure_Pa']  = msg['pressure_Pa']
                sensorData['Temp_C']       = msg['Temp_C']
                sensorData['Hum_RH']       = msg['Hum_RH']
                sensorData['WSpeed_mps']   = msg['WSpeed_mps']
                sensorData['WDir_deg']     = msg['WDir_deg']
                sensorData['vx_mps']       = msg['vx_mps']
                sensorData['vy_mps']       = msg['vy_mps']
                sensorData['vz_mps']       = msg['vz_mps']
                sensorData['roll_deg']     = msg['roll_deg']
                sensorData['pitch_deg']    = msg['pitch_deg']
                sensorData['P_rps']        = msg['P_rps']        # (rad/s)
                sensorData['Q_rps']        = msg['Q_rps']        # (rad/s)
                sensorData['R_rps']        = msg['R_rps']        # (rad/s)
                sensorData['logfile_size'] = msg['logfile_size']
                sensorData['batt_stat']    = -1                  # batt_stat; unknown from Xbee messages
            
            if xbee_msg_id_str == 'xb03':
                pass
        
        else:
            gps_unixTime = float( gps_msg[0] ) # (s) unix time from incoming gps data
            localtime_remote = time.asctime( time.localtime( gps_unixTime ) ) # human readable time from incoming data
            dt               = unixTime        - t_last
            dt_remote        = gps_unixTime - t_last_remote
            #if debug>0: print('t={0}, '.format(unixTime - tStart), end='')
            if debug>0: print('unixTime={0:0.10f}, gps_unixTime={1:0.10f}, dt={2:0.10f}, dt_remote={3:0.10f}, localtime_remote={4}, ' \
                              .format(unixTime, gps_unixTime, dt, dt_remote, localtime_remote), end='')
            
            lat         = float( gps_msg[1] )
            lon         = float( gps_msg[2] )
            elev        = float( gps_msg[3] )
            SOS         = float( gps_msg[4] )
            batt_stat   = -1
            if debug>0: print('gps_unixTime={0:0.10f}, (lat,lon,elev), {1:<10.8},{2:<10.8},{3:<10.8}, SOS=[{4}]'.format(gps_unixTime,lat,lon,elev,SOS))
        
    elif gps_data_format_select==1: # decode HyperIMU Android app v3.0.4.6 thru 3.1.2.8
        # HyperIMU settings:
        # HyperIMU with Header     : timestamp, mac address, battery info
        # HyperIMU with Sensor List: 1 accelerometer only
        # HyperIMU with Trailer    : GPS and NMEA
        # data='1551283644304,c83870391e80,-0.06578,0.025116,9.767733,29.1886099,-81.0469637,1.8780242415748485,$IMGSA.A.3.............1.6.0.9.1.3*2D,$GPRMC.154236.00.A.2829.343445.N.08122.211526.W.001.2..270219...A*63, \r\n'
        # data='1551283643802,c83870391e80,-0.063388005,0.02392,9.77132,29.1886099,-81.0469637,1.8890983143905267,$GNGSA.A.3.01.03.10.14.16.22.25.26.31.32...1.6.0.9.1.3*21,$GNGSA.A.3.71.72.75..........1.6.0.9.1.3*21,$QZGSA.A.3.............1.6.0.9.1.3*22\r\n'
        # data='1551283643297,c83870391e80,0.0,0.0,0.0,29.1886099,-81.0469637,1.8890983143905267,$GPGSV.3.3.12.16.15.194.25.01.14.277.18.29.04.088..20.02.153.*75,$GLGSV.1.1.03.75.71.257.31.72.69.090.26.71.23.132.27*55,$GPGSA.A.3.01.03.10.14.16.22.25.26.31.32...1.6.0.9.1.3*3F\r\n'
        #
        # Examples with settings above with RMC messages:
        # data='1551284004794,c83870391e80,-0.064584,0.02392,9.782084,29.1886099,-81.0469637,-9.18469754406914,$QZGSA.A.3.............1.9.1.2.1.6*22,$IMGSA.A.3.............1.9.1.2.1.6*2D,$GPRMC.160721.00.A.2829.347472.N.08122.219410.W.000.0.258.4.270219...A*4D\r\n'
        # data='1551284006803,c83870391e80,-0.063388005,0.009568,9.776104,29.1886099,-81.0469637,-9.287555284590116,$IMGSA.A.3.............1.5.1.0.1.2*27,$GPRMC.161321.00.A.2829.347580.N.08122.217595.W.000.4.320.9.270219...A*41, \r\n'
        # data='1551284008805,c83870391e80,-0.066976,0.02392,9.7773,29.1886099,-81.0469637,-9.352595865014328,$IMGSA.A.3.............1.4.0.9.1.1*2D,$GPRMC.161323.00.A.2829.348324.N.08122.217968.W.000.0.320.9.270219...A*4E, \r\n'
        # data='1551284010820,c83870391e80,-0.069368005,0.02392,9.78328,29.1886099,-81.0469637,-9.443007033008303,$IMGSA.A.3.............1.5.1.0.1.2*27,$GPRMC.161325.00.A.2829.348943.N.08122.217971.W.000.4.320.9.270219...A*4F, \r\n'
        #
        # adding battery info:
        # data='1595602001468,c83870391e80,46.0,1.0,1.0,0.441324,0.63388,9.764144,28.489098426392346,-81.3701826451762,14.90819474503712,$GPGSV.3.1.11.28.73.079.23.06.54.230.33.17.54.351.29.19.47.314.27*7F,$GPGSV.3.2.11.03.27.069.23.30.23.186.28.02.17.229.17.22.14.050.28*76,$GPGSV.3.3.11.01.09.040.20.24.10.313..07.00.166.*47\r\n'
        # data='1595602104260,c83870391e80,46.0,1.0,1.0,0.441324,0.638664,9.750988,28.489130753932255,-81.37027355346831,13.861187614926065,$GNGSA.A.3.01.02.03.06.17.19.22.24.28.30...1.3.0.8.1.0*20,$GNGSA.A.3.68.73...........1.3.0.8.1.0*2D,$QZGSA.A.3.............1.3.0.8.1.0*25\r\n'
        #
        fields=data.decode().split(",") # decode makes it a string; split provides individual fields as a list
        msg = dictionary_from_list(fields) # create a dictionary from the 'fields' list for DictWriter in veh_udp_io.py
        #print('\nfields = {0}'.format(fields))
        # fields = ['1551106072416', 'c83870391e80', '-0.052624002', '0.003588', '9.774908', '29.1886099',           '-81.0469637',        '-14.75567060491372\r\n']
        #            unixtime (ms)       mac addr       accel_x       accel_y      accel_z    latitude (dec deg)    longitude (dec deg)      altitude (ft/m ?)
        #                0                  1             2              3            4           5                      6                       7
        #
        # with battery info in header it adds 3 more fields:
        # fields = ['1595602184520', 'c83870391e80', '79.0'   , '0.0'    , '0.0'  , '0.446108', '0.63746804', '9.755773', '28.489092282849466', '-81.37026767543658', '14.183015672434491', '$GNGSA.A.3.01.02.03.06.17.19.22.24.28.30...1.6.1.0.1.2*2E', '$GNGSA.A.3.68.73...........1.6.1.0.1.2*23', '$QZGSA.A.3.............1.6.1.0.1.2*2B\r\n']
        #            unixtime (ms)       mac addr     batt SOC,  charge? , on AC? ,   accel_x ,    accel_y  ,   accel_z ,   latitude (dec deg),  longitude (dec deg),   altitude (ft/m ?) , ...
        #                0                  1             2        3         4          5            6            7                8                      9                    10           ...
        #
        # battery info is 3 numbers, from ianovir: https://ianovir.com/works/mobile/hyperimu/hyperimu-help/
        #   "battery level in percentage (100%:fully charged), the status (1:charging, 0:discharging) and the AC info (1:connected to AC, 0:otherwise)"
        #
        # - almost every message from HyperIMU v.3.0.4.6 on Samsung Galaxy Tab S2 contains GSV or GSA messages.
        # - on the Galaxy Tab S2, HyperIMU delivers 4 messages: GSV, GSA, RMC, LOR  ...with a GSV or GSA is in almost every message
        # - satellite constellations include: GP (USA GPS), GN (Galileo or GLONASS), QZ (Japanese ), PG ($PGLOR is undocumented)
        #
        # $GPRMC - GPS recommended minimum information (lat/lon)
        # $GLGSV, $GPGSV - PS satellites in view (no lat/lon)
        # $GPGSA, $GNGSA, $QZGSA, $IMGSA - GPS DOP and active satellites information (no lat/lon)
        #
        #
        # $GPRMC,225446,A,4916.45,N,12311.12,W,000.5,054.7,191194,020.3,E*68
        #
        # $GPRMC -   http://aprs.gids.nl/nmea/#rmc       or       https://www.gpsinformation.org/dale/nmea.htm#RMC
        #  225446       Time of fix 22:54:46 UTC
        #  A            Navigation receiver warning A = OK, V = warning
        #  4916.45,N    Latitude 49 deg. 16.45 min North
        #  12311.12,W   Longitude 123 deg. 11.12 min West
        #  000.5        Speed over ground, Knots
        #  054.7        Course Made Good, True
        #  191194       Date of fix  19 November 1994
        #  020.3,E      Magnetic variation 20.3 deg East
        #  *68          mandatory checksum
        
        try:
            gps_unixTime = float( fields[0] ) / 1000.0 # (s) unix time from incoming data
            
            localtime_remote = time.asctime( time.localtime( gps_unixTime ) ) # human readable time from incoming data
            gps['dt']               = unixTime     - t_last
            gps['dt_remote']        = gps_unixTime - t_last_remote
            #if debug>0: print('t={0}, '.format(unixTime - tStart), end='')
            if debug>1: logging.debug('unixTime={0:0.10f}, gps_unixTime={1:0.10f}, dt={2:0.10f}, dt_remote={3:0.10f}, localtime_remote, {4}, ' \
                               .format(unixTime, gps_unixTime, gps['dt'], gps['dt_remote'], localtime_remote) )
            
            # gps['unixTime'], gps['lat'], gps['lon'], gps['alt_m'], gps['true_course'], gps['psi'], gps['spd_mps'], gps['validity']
            gps['unixTime']    = gps_unixTime
            gps['lat']         = float( fields[8]  )
            gps['lon']         = float( fields[9]  )
            gps['alt_m']       = float( fields[10] )
            
            sensorData['batt_stat'] = float( fields[2]  ) #  battery status on interval [0  100]            
            sensorData['mac']       =        fields[1]
            sensorData['accel_x']   = float( fields[5] )
            sensorData['accel_y']   = float( fields[6] )
            sensorData['accel_z']   = float( fields[7] )
            
            if debug>1: print('(lat,lon,alt), {0},{1},{2}'.format(gps['lat'],gps['lon'],gps['alt_m']))
        
        except ValueError as err:
            # HyperIMU (sometimes) sends this at startup or re-start: ['Timestamp', 'MAC address', 'K330_Acceleration_Sensor.x', 'K330_Acceleration_Sensor.y', 'K330_Acceleration_Sensor.z', 'GPS.lat', 'GPS.long', 'GPS.alt', 'NMEA.a', 'NMEA.', 'NMEA.c\r\n']
            gps['errorCnt']    += 1
            print('gps[errorCnt]={0}, offending string: [{0}], error: [{1}]'.format(gps['errorCnt'],res,err))
        
        gps['validity'] = True
        # see ./dev/parse_HyperIMU_strings.py for detailed parsing notes
        nmea_msgs = data.decode().split("$")
        for i in range(len(nmea_msgs)):
            #logging.debug("considering this string: {0}".format(nmea_msgs[i]))
            nmea_field = nmea_msgs[i]
            if nmea_field[2:5] == 'RMC':
                logging.debug("found an RMC message: {0}".format(nmea_field))
                rmc_fields = nmea_field.split('.')
                if rmc_fields[3]=='V': # validity - A-ok, V-invalid
                    logging.debug("invalid GPS signal - no data")
                    gps['validity'] = False
                    gps['true_course'] = -1 # no course heading available
                    gps['psi']         = -1 # no IMU yaw orientation available
                    gps['spd_mps']     = -1 # no speed available
                    #for j in range(len(rmc_fields)):
                    #    logging.debug("considering rmc_field[{0}]=[{1}]".format(j,rmc_fields[j]))
                    
                if rmc_fields[3]=='A': # validity - A-ok, V-invalid
                    try:
                        gps['spd_mps']     = float( rmc_fields[10]+'.'+rmc_fields[11] )*0.514445 # (kts)-->(m/s),   1 knot == 0.514445 (m/s)
                        gps['true_course'] = float( rmc_fields[12]+'.'+rmc_fields[13] )*3.14159/180.0 # (deg) --> (rad), course over ground, true (guess: 'true' means w.r.t. true north)
                        gps['psi']         = gps['true_course'] # identical to heading - correct this if IMU yaw angle is avaialble
                        logging.debug("spd_mps={0}, course={1}".format(gps['spd_mps'],gps['true_course']))
                    except ValueError as err:
                        gps['spd_mps']     = -1 # no speed available
                        gps['psi']         = -1 # no IMU yaw orientation available
                        gps['true_course'] = -1 # no course heading available
                        gps['errorCnt']    += 1
                        logging.debug("warning: no speed value provided: err={0}".format(err))
                        logging.debug("gps['errorCnt={0}, nmea_msgs={1}".format(gps['errorCnt'],nmea_msgs[i]))
                        
    elif gps_data_format_select==2: # decode SensorLog iPhone app, v.3.7.1 (b001)
        # SensorLog example:
        # data=['1595071707.024499,      483  , 0  ,  0  ,  1595071706.001017,28.48910972547172,-81.37043923960596,28.01138,    0     ,   -1       ,  3         ,  32.00483309472351,-9999      , ...
        #            logging time  ,  N_sample , ?  ,  ?  ,   locTimestamp    , latitude        ,  longitude       , alt (m), spd (m/s),course (deg), vertAcc (m),     horAcc (m)    , floor(Z)? ,
        #
        #     ... 1595071706.4009,-27.85415649414062,-6.291279315948486,-35.1536865234375,90.81047058105469,97.33438873291016,15.48087978363037  ,      0    \n']
        #        heading time (s),   hdg_x (uTesla) ,   hdg_y (uTesla) ,  hdg_z (uTesla) , true hdg (deg)  ,   mag hdg (deg) , hdg accuracy (deg), data label
        #
        #
        # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # data=['1595072559.36018,       14   , 0  ,  0  ,  1595072557.999896  , 28.48911458815298, -81.37017662530066, 27.04728, 0.1288958  , 154.7445336093 ,     3         ,32.00483309472351,-9999   , ...
        #            logging time  ,  N_sample , ?  ,  ?  ,   locTimestamp      ,  latitude        ,   longitude       ,  alt (m),  spd (m/s) ,  course (deg)  , vertAcc (m)   ,     horAcc (m)  , floor(Z)? ,
        #
        #     ... 1595072558.89111, -10.94240570068359, -29.9536304473877, -22.92153930664062, 143.4702758789062, 149.9942016601562, 17.41634750366211,       0     \n']
        #         heading time (s),    hdg_x (uTesla) ,   hdg_y (uTesla) ,    hdg_z (uTesla) ,  true hdg (deg)  ,    mag hdg (deg) ,  hdg accuracy (deg), data label
        #
        #
        # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # with IP addresses turned on
        # data=['1595073164.99433,       6   , 0  ,  0  ,  1595073162.998489, 28.48910622338724, -81.37016461456788, 26.95977,   0.4033463, 106.9090715307611,        3      , 32.00483309472351, -9999     , ...
        #            logging time ,  N_sample , ?  ,  ?  ,   locTimestamp    ,  latitude        ,   longitude       ,  alt (m),  spd (m/s) ,  course (deg)    , vertAcc (m)   ,      horAcc (m)  , floor(Z)? ,
        #
        #     ... 1595073164.270715,-19.6951904296875  ,-16.32946395874023, -29.29666137695312, 77.74058532714844, 84.26450347900391, 17.40593719482422,      3232235910,      179728669,     0      \n']
        #         heading time (s) ,    hdg_x (uTesla) ,   hdg_y (uTesla) ,    hdg_z (uTesla) ,  true hdg (deg)  ,    mag hdg (deg) ,  hdg accuracy (deg),  WLAN IP addr,   cell IP addr,  data label
        #
        # note: IP addresses are not that useful in SensorLog because the socket reports the inbound ip and port already:
        #       received [266] bytes from [('166.172.186.141', 51086)] with data=['1595076774.968833,4,0,..,0\n']
        #
        # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # deviceID turned OFF, IP addr's turned off
        # data=['1595076774.968833,          4, 0  ,      1595076774.000458,28.48915848932186,-81.37028403400051,27.59947,0.513697,-1,3,8.972258788252345,-9999,1595076774.711246,-12.54215240478516,-29.54190444946289,-24.73403930664062,109.863037109375,116.3871078491211,16.05916023254395,0,179728669,0\n']
        #            logging time  ,  N_sample , ?  ,       locTimestamp    ,  latitude        ,   longitude       ,  alt (m),  spd (m/s) ,  course (deg)    , vertAcc (m)   ,      horAcc (m)  , floor(Z)? ,
        #
        #
        # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # only these two switches turned on: core location and label
        # data=['1595077851.803921,     10    , 0  ,      1595077850.998319, 28.48908614430396, -81.37023515322929, 27.15535,  0.05473348,        -1        ,      3        ,  8.001208273680877, -9999     ,   0       \n']
        #            logging time  ,  N_sample , ?  ,       locTimestamp    ,  latitude        ,   longitude       ,  alt (m),  spd (m/s) ,  course (deg)    , vertAcc (m)   ,      horAcc (m)   , floor(Z)? , data label
        #                  0              1      2                3                4                   5                 6         7              8                9                   10            11          12
        #
        # complete console output:
        #   received [121] bytes from [('166.172.186.141', 59856)] with data=['1595078731.153163,500,0,1595078728.998269,28.48912975062083,-81.37028365519367,27.46736,0,-1,3,17.45553788594633,-9999,0\n']
        #   unixTime=1595078731.2143914700, gps_unixTime=1595078731.1531629562, dt=0.0000107288, dt_remote=1.0070269108, localtime_remote, Sat Jul 18 09:25:31 2020,
        #
        #
        #
        # *final version*: three switches turned on: core location, battery, and label
        # data= '1595545838.956233,      148,     0,        1595545836.9983, 28.48914194304779, -81.37008788249187,  26.8231,           0,        -1        ,      3        , 32.00483309472351 , -9999     ,   1,       0.76     ,       0      \n'
        #            logging time  ,  N_sample , ?  ,       locTimestamp    ,  latitude        ,   longitude       ,  alt (m),  spd (m/s) ,  course (deg)    , vertAcc (m)   ,      horAcc (m)   , floor(Z)? ,   ?,  battery charge,  data label
        #                  0              1      2                3                4                   5                 6         7              8                9                   10            11         12,       13       ,      14
        
        
        
        
        # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # with all switches turned off, there's still an unknown 0 after N_sample:
        # data=['1595077402.559998,240,0\n']
        
        fields=data.decode().split(",") # decode makes it a string; split provides individual fields as a list
        msg = dictionary_from_list(fields) # create a dictionary from the 'fields' list for DictWriter in veh_udp_io.py
        
        try:
            gps_unixTime = float( fields[0] ) # (s) unix time from incoming data
            
            localtime_remote = time.asctime( time.localtime( gps_unixTime ) ) # human readable time from incoming data
            gps['dt']               = unixTime     - t_last
            gps['dt_remote']        = gps_unixTime - t_last_remote
            #if debug>0: print('t={0}, '.format(unixTime - tStart), end='')
            if debug>0: logging.debug('unixTime={0:0.10f}, gps_unixTime={1:0.10f}, dt={2:0.10f}, dt_remote={3:0.10f}, localtime_remote, {4}, ' \
                              .format(unixTime, gps_unixTime, gps['dt'], gps['dt_remote'], localtime_remote) )
            
            gps['unixTime']    = gps_unixTime
            gps['lat']         = float( fields[4] )
            gps['lon']         = float( fields[5] )
            gps['alt_m']       = float( fields[6] )
            gps['true_course'] = float( fields[8] )*3.14159/180.0 # (deg) --> (rad), course over ground, true (guess: 'true' means w.r.t. true north)
            gps['psi']         = gps['true_course'] # identical to heading - correct this if IMU yaw angle is avaialble
            gps['spd_mps']     = float( fields[7] ) # (kts)-->(m/s),   1 knot == 0.514445 (m/s)
            gps['validity']    = True # necessary for function output but unused for SensorLog (used in HyperIMU)
                        
            sensorData['batt_stat'] = 100*float( fields[13] ) #  battery status from SensorLog is on [0.0  1.0], then converted to [0 100]
            sensorData['ip']        =               addr[0]

                
        except ValueError as err:
            # SensorLog sent an unepxected message
            gps['errorCnt']    += 1
            print('gps[errorCnt]={0}, offending string: [{1}], error: [{1}]'.format(gps['errorCnt'],fields,err))
    
    
    
    
    # errbody gotta populate these because they go straight to Core | veh_udp_io.py \ recv_gps
    # gps['unixTime'], gps['lat'], gps['lon'], gps['alt_m'], gps['true_course'], gps['psi'], gps['spd_mps'], gps['validity']
    return gps, sensorData, unixTime, gps_unixTime, msg















# ascii encoding check from: https://stackoverflow.com/questions/196345/how-to-check-if-a-string-in-python-is-in-ascii
isascii = lambda s: len(s) == len(s.encode()) # this requires 'utf-8' enoding to perform the isascii check properly b/c utf-8 is a multi-byte encoder for characters above 127

# runtime test tool for verifying network data is coming in and being received properly
if __name__ == "__main__":
    import socket
    import sys
    
    vid=100
    UDP_IP = "0.0.0.0" # listen to everyone
    UDP_PORT = 9000+int(vid)
    
    n=len(sys.argv)
    if n>=2:
        UDP_PORT = int(sys.argv[1])
    else:
        print('\n\t usage  :    python3 {0} PORTNUM\n'.format(sys.argv[0]))
        print('\t example:    python3 {0} 9103\n'.format(sys.argv[0]))
        sys.exit(0)
        
    print('listening on port: {}'.format(UDP_PORT))    
    #print('__name__={0}'.format(__name__))
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # udp/ip socket
    sock.bind((UDP_IP, UDP_PORT))
    
    # define simple GPS class for use as a struct
    gps={}
    sensorData={} # this ensures every live-gps-follower has at least an empty sensorData dictionary
    
    gps['unixTime']=[]
    gps['lat']=[]
    gps['lon']=[]
    gps['alt_m']=[]
    gps['yaw']=[] # vehicle orientation, yaw, or psi from an IMU
    gps['true_course']=[] # hdg from a gps (deg)
    gps['spd_mps']=[]
    gps['batt_stat']=[]
    gps['errorCnt']=0
    unixTime     = time.time()
    gps_unixTime = time.time() # init is incorrect at first dt_remote calculation
    autoDetectMsgType = True # this triggers a 1-time incoming udp message classifier: HyperIMU, SensorLog or custom GPS sender?
    
    #gps_data_format_select=2 # 0->GPS+LoRa custom, 1->HyperIMU (Android), 2-->SensorLog (iPhone)
    
    byteMin=1e10 # minimum bytes received per udp packet
    byteMax=0    # maximum bytes received per udp packet
    debug=1 # (0/1/2)
    cnt=0
    
    while True:
        logging.debug('-------------------------------------------------')
        try:
            data,addr = sock.recvfrom(2048) # blocking call but timeout = 1s
            cnt+=1
            #print("received [{0}] bytes from [{1}], cnt={2}".format(len(data),addr,cnt))
            print("data={0}".format(data))
        except socket.timeout:
            logging.error("sock.recvfrom() timeout")
        
        # auto-detect which type of GPS sender is sending data
        if autoDetectMsgType==True:
            autoDetectMsgType, gps_data_format_select = auto_detect_message_type(autoDetectMsgType, data)
        
        # decode GPS messages from custom GPS sender, HyperIMU, SensorLog or other
        gps, sensorData, unixTime, gps_unixTime = live_gps_follower_decoding(vid,data,addr,gps,sensorData,unixTime,gps_unixTime,gps_data_format_select,debug)
        
        logging.debug(' ')
        for k,v in gps.items():
            print('gps[{0}] = {1}'.format(k,v))
        
        if len(data)<byteMin: byteMin=len(data)
        if len(data)>byteMax: byteMax=len(data)
        print('min and max bytes received: [{0}  {1}] (bytes), gps[errorCnt]={2}'.format(byteMin,byteMax,gps['errorCnt']))
        logging.debug(' ')



# iPhone SensorLog messages vary between 117bytes and 160 bytes:
# a 119 byte message:
#       ------------------------------------------------------------------
#       received [119] bytes from [('166.172.186.141', 37737)], cnt=276
#       data='1595100684.386936,39 ,0, 1595100684.00088,28.48916740056183,-81.37026280680185,26.92925,   0      ,    -1    ,      3         ,     16.00241654736175,    -9999,      0      \n'
#                   gps_unixTime   , N ,?,   gps_unixTime  ,     lat         ,       lon        ,  elev  , spd (m/s), hdg (deg),  vertAcc (m)   ,      horAcc (m)      , floor Z ,   data label
#
#       ------------------------------------------------------------------
# a 146 byte message:
#       received [146] bytes from [('166.172.186.141', 37737)], cnt=54
#       data='1595101596.004547,948,0,1595101594.999183,28.48918283120133,-81.37018655203003,27.27028,0.001056639,277.6014001728228,        3       ,   32.00483309472351  ,   -9999 ,   2   \n'
#                   gps_unixTime   , N ,?,   gps_unixTime  ,     lat         ,       lon        ,  elev  ,  spd (m/s),        hdg (deg),  vertAcc (m)   ,      horAcc (m)      , floor Z ,   data label



# Android HyperIMU messages vary in size from 178 bytes to 354 bytes:
# a 178 byte message:
#       ------------------------------------------------------------------
#       received [178] bytes from [('166.172.187.14', 59242)]                                [  notice - lost GPS signal!  ]
#       data='1595101955082     ,c83870391e80  ,    0.0    ,    0.0    ,    0.0    ,         0.0         ,         0.0            ,         0.0        ,$GNGSA.A.1.............140.0.99.0.99.0*2B,$GNGSA.A.1.............140.0.99.0.99.0*2B,$QZGSA.A.1.............140.0.99.0.99.0*29\r\n'
#              gps_unixTime*1000  ,    device MAC,  accel_x     accel_y      accel_z    latitude (dec deg)    longitude (dec deg)      altitude (ft/m ?)
#
# a 237 byte message:
#       ------------------------------------------------------------------
#       received [237] bytes from [('192.168.1.1', 42389)], cnt=5
#       data='  1595085157366     ,  c83870391e80,   -0.13754  ,  1.21394  ,  9.712716  ,  28.488984634226806  ,  -81.37018144435015   ,  -6.667265845435829,$GNGSA.A.1.............140.0.99.0.99.0*2B,$QZGSA.A.1.............140.0.99.0.99.0*29,$IMGSA.A.1.............140.0.99.0.99.0*26\r\n'
#                  gps_unixTime*1000  ,    device MAC,    accel_x       accel_y      accel_z    latitude (dec deg)    longitude (dec deg)      altitude (ft/m ?)
#
# a 354 byte message:
#       ------------------------------------------------------------------
#       received [354] bytes from [('192.168.1.1', 42389)], cnt=13
#       data='1595085165397,c83870391e80,-0.105248004,1.206764,9.710324,28.48896781261742,-81.37017124360123,-6.666474443108373,$PGLOR.9.STA.145037.27.0.000.0.000.689.137.9999.0.P.D.L.1.C.0.S.00000000.0.2.R.00000000.TPEF.12.67014.LC...*02,$GPGSV.3.1.12.28.73.047.19.19.44.302.23.22.17.057.21.17.54.337.*72,$GPGSV.3.2.12.06.46.221..30.31.189..03.27.078..01.16.039.*7A\r\n'



