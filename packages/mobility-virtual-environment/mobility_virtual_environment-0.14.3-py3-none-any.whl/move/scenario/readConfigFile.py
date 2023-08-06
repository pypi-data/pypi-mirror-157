#!/usr/bin/env python3
#
# readConfigFile.py - read a config file and return a cfg data structure
#
# Marc Compere, comperem@gmail.com
# created : 13 Jan 2019
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

import sys
import configparser
import distutils.core
import logging
import code # drop into a python interpreter to debug using: code.interact(local=dict(globals(), **locals()))
from ast import literal_eval # literal_eval() for converting strings into proper dicts
import utm
import getpass # getpass.getuser()


logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-14s) %(message)s',
)

# if a vid argument is not specified, it's set to veh=-1 (this is for main_core.py and main_launch_veh_process.py)
def readConfigFile( cfgFile, vid=-1 ):
    class Cfg: # define an empty class for cfg variable container
        pass
    cfg=Cfg()
    
    cfg.vid = vid # this is vehicle identity of this particular vehicle (or -1 if called from anywhere except the vehicle model)
    
    # instantiate a ConfigParser object allowing comments on every line
    config = configparser.ConfigParser( inline_comment_prefixes=('#',) )
    config.optionxform = str # ensure keys are case sensitive (ConfigParser default is keys are not case sensitive)
    logging.debug( "reading config file: {0}".format(cfgFile) )
    #config.read('default.cfg')
    retVal=config.read( cfgFile )
    if len(retVal)==0:
        logging.debug( "\n\noops - could not locate and read config file: {0}".format(cfgFile) )
        print('could not read config file: {0}'.format(cfgFile))
        print('exiting.',flush=True)
        sys.stdout.flush()
        sys.stderr.flush()
        sys.exit(-1)
    
    try:
        # config file sections
        common               = config['common']
        scenario             = config['scenario']
        core                 = config['core']
        veh_sim              = config['veh_sim']
        veh_v2v              = config['veh_v2v']
        veh_details          = config['veh_details']
        veh_behaviors_global = config['veh_behaviors_global']
        veh_names_live_gps   = config['veh_names_live_gps'] # these two names sections in config file only need scope
        veh_names_builtins   = config['veh_names_builtins'] # in main_launch_veh_process.py (not vehicles) so they're not in cfg. anywhere
    except KeyError as err:
        logging.debug( "\n\noops - didn't find config file section: {0} in {1}".format(err,cfgFile) )
        logging.debug( "\tmake sure cfgFile contains this section and specifies the file location")
        logging.debug( "\tsuch as: cfgFile=\"../scenario/default.cfg\" \n")
        logging.debug( "exiting.")
        sys.exit(-1)
    
    # assign variables on the fly like a C struct; python calls these Class data attributes
    
    # ------------------   SECTION:  COMMON     --------------------------------
    cfg.nVeh_builtin          = int( common[ 'nVeh_builtin'      ] ) # number of MoVE built-in vehicle models to launch, each with behaviors specified in config file
    cfg.nVeh_live_gps         = int( common[ 'nVeh_live_gps'     ] ) # number of live-GPS-follower processes to launch
    cfg.nVeh_custom           = int( common[ 'nVeh_custom'       ] ) # available but unused
    cfg.nVeh_hosts            = int( common[ 'nVeh_hosts'        ] ) # available but unused; always==1
    cfg.core_host_ip          =      common[ 'core_host_ip'      ]   # ip addr of machine running core process
    cfg.veh_host_ip           =      common[ 'veh_host_ip'       ]   # ip addr of machine running vehicle processes
    cfg.vid_base              = int( common[ 'vid_base'          ] ) # base vehicle ID
    cfg.udp_port_base         = int( common[ 'udp_port_base'     ] ) # base port for core-to-veh messages
    cfg.udp_port_offset       = int( common[ 'udp_port_offset'   ] ) # base port for veh-to-core messages; offset may be (+) or (-) as long as: 1000 < port < 65000
    cfg.udp_port_base_gps     = int( common[ 'udp_port_base_gps' ] ) # (0/non-0) 0->vehicle model, non-zero->udp listener port for receiving live GPS inputs
    cfg.debug                 = int( common[ 'debug'             ] ) # debug (0/1/2) more means more debuggig console output
    cfg.username              =      getpass.getuser()               # username on machine running vehicle processes with ssh keys for passwordless login already setup
    
    # ------------------   SECTION:  SCENARIO     ------------------------------
    cfg.boundary_Xmax         = float( scenario[ 'boundary_Xmax' ] ) # define boundaary for for stayInBounds() behavior (if enabled), in behaviors.py
    cfg.boundary_Xmin         = float( scenario[ 'boundary_Xmin' ] ) # define boundaary for for stayInBounds() behavior (if enabled), in behaviors.py
    cfg.boundary_Ymax         = float( scenario[ 'boundary_Ymax' ] ) # define boundaary for for stayInBounds() behavior (if enabled), in behaviors.py
    cfg.boundary_Ymin         = float( scenario[ 'boundary_Ymin' ] ) # define boundaary for for stayInBounds() behavior (if enabled), in behaviors.py   
    try:
        cfg.detectId          = int  ( scenario[ 'detectId'        ] ) # vid for detectAndReport() behavior in vehicles, behaviors.py
    except KeyError as err:
        cfg.detectId          = 0
    
    try:
        cfg.detectThreshold   = float( scenario[ 'detectThreshold' ] ) # (m) radius threshold to trigger detection
    except KeyError as err:
        cfg.detectThreshold   = 0
    
    
    # ------------------   SECTION:  CORE     ----------------------------------
    cfg.sync_veh_and_cfg      =           core.getboolean( 'sync_veh_and_cfg'   ) # (0/1) run rsync before launching vehicle processes?
    cfg.logfile               =      int( core[            'logfile'          ] ) # (0/1) log all vehicles in State to local .csv file periodically?
    cfg.logfile_loc_core      =           core[            'logfile_loc_core' ]   # (0/1) log all vehicles in State to local .csv file periodically?
    
    cfg.dtOut                 =    float( core[            'dtOut'            ] ) # (s) communication output interval for Core to send to viz, database, and csv logfile
    cfg.vizUdpEnabled         =           core.getboolean( 'vizUdpEnabled'      ) # (true/false) send udp messages from all_vehicles.py to visualization machine with Bokeh?
    cfg.vizIp                 =           core[            'vizIp'            ]   # outbound viz udp ip address from all_vehicles.py to Bokeh viz client
    cfg.vizPort               =      int( core[            'vizPort'          ] ) # outbound viz udp port from all_vehicles.py to Bokeh viz client
    cfg.dashIp                =           core[            'dashIp'           ]   # outbound dashboard udp ip address from all_vehicles.py to Bokeh dashboard
    cfg.dashPort              =      int( core[            'dashPort'         ] ) # outbound dashboard udp port from all_vehicles.py to Bokeh dashboard
    
    cfg.dbUdpEnabled          =           core.getboolean( 'dbUdpEnabled'       ) # (true/false) send udp messages from all_vehicles.py to MongoDB record and playback machine?
    cfg.dbIp                  =           core[            'dbIp'             ]   # outbound MongoDB udp ip address from all_vehicles.py
    cfg.dbPort                =      int( core[            'dbPort'           ] ) # outbound MongoDB udp port from all_vehicles.py
    
    
    # -------   SECTION:  V2V, a simple vehicle-to-vehicle communications model   -------
    # assign simple v2v communications variables using udp/ip multicast to emulate a simple
    # broadcast network from all N vehicles to all other vehicles (for simulated vehicles only)
    # veh_model/v2v.py
    cfg.v2vEnabled            =        veh_v2v.getboolean( 'v2vEnabled'         ) # (true/false) enable v2v threads and multicast communications
    cfg.multicast_group       =        veh_v2v[            'multicast_group'  ]   # udp/ip multicast group for all-to-all process communications
    cfg.multicast_port        =   int( veh_v2v[            'multicast_port'   ] ) # udp multicast port for all v2v senders and listeners
    cfg.v2v_cint_send         = float( veh_v2v[            'v2v_cint_send'    ] ) # (s) outbound v2v communication interval
    cfg.v2v_cint_read         = float( veh_v2v[            'v2v_cint_read'    ] ) # (s) outbound v2v communication interval
    cfg.v2v_dRadio            = float( veh_v2v[            'v2v_dRadio'       ] ) # (m) radio range; any vehicles within this distance are radio active
    cfg.v2v_dNeigh            = float( veh_v2v[            'v2v_dNeigh'       ] ) # (m) neighbor range; any vehicles within this distance are neighbors
    
    
    # ------------------   SECTION:  VEH_SIM     -------------------------------
    cfg.vehRuntimeDir_base    =        veh_sim[ 'vehRuntimeDir_base' ]    # runtime directory on remote machine for rsync to move veh_model and config file to, then parallel-ssh to run the model
    cfg.h                     = float( veh_sim[ 'h'                  ] )  # vehicle model ODE solver stepsize; if h=0.01(s) this means 10ms stepsizes in time for RK4 between cInt outputs
    cfg.cInt                  = float( veh_sim[ 'cInt'               ] )  # vehicle process communication interval back to Core; if cInt=0.1 each veh will report pos/vel/health to core at 10Hz
    cfg.hInt                  = float( veh_sim[ 'hInt'               ] )  # heatbeat to core during runState==1 (READY) to indicate alive vehicle
    cfg.randFlag              =   int( veh_sim[ 'randFlag'           ] )  # (0/1) use random numbers? plumbed in everwhere relevant (ICs and random triggers in behaviors)
    cfg.IC_sel                =   int( veh_sim[ 'IC_sel'             ] )  # (0/1/2) default initial contition selector (overriden by vehicle-specific IC entry in veh_details[] cfg file section
    cfg.L_char                = float( veh_sim[ 'L_char'             ] )  # (m) characteristic vehicle length
    cfg.v_max                 = float( veh_sim[ 'v_max'              ] )  # (m/s) max vehicle speed
    cfg.IC_elev               = float( veh_sim[ 'IC_elev'            ] )  # (m) IC on elevation, or altitude in UTM XYZ frame
    cfg.lat_origin            = float( veh_sim[ 'lat_origin'         ] )  # (decimal deg) latitude origin
    cfg.lon_origin            = float( veh_sim[ 'lon_origin'         ] )  # (decimal deg) longitude origin
    cfg.log_level             =   int( veh_sim[ 'log_level'          ] )  # (0/1/2/3) vehicle log level
    cfg.logfile_loc_veh       =        veh_sim[ 'logfile_loc_veh'    ]    # vehicle model's .csv log file location (independent from core's logfile_loc_core)
    
    cfg.vehRuntimeDir         = cfg.vehRuntimeDir_base + '_' + getpass.getuser() # /tmp/move + myusername --> /tmp/move_myusername for runtimeDir
    
    # convert lat/lon origin to UTM XYZ origin so vehicle and behaviors can know the origin offset
    (cfg.X_origin,cfg.Y_origin,cfg.UTM_zone,cfg.UTM_latBand) = utm.from_latlon(cfg.lat_origin,cfg.lon_origin)
    cfg.Z_origin = 0.0; # (m) assume ATO - above take-off so elevations in config file are elevation changes from launch
    
    
    
    # ------------------   SECTION:  VEH_DETAILS:  optionally assign: vehicle name, vehType, vehSubType, initial conditions     -------------------------------
    veh_type_default_str      =        veh_details[ 'veh_type_default' ] # this needs to be in cfg file:        veh_type_default: { 'vehType': 'aerial',      'vehSubType': 'fixedwing' }
    logging.debug('veh_type_default={0}'.format(veh_type_default_str))
    #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
    try:
        veh_type_default = literal_eval(veh_type_default_str) # a dictionary: {'vehType': 'aerial', 'vehSubType': 'rotorcraft'}
    except:
        logging.debug( "config file: problem converting from string to dictionary in {0} --> fix typo in [veh_details] section of config file".format(cfgFile) )
    
    cfg.vehType               =        veh_type_default['vehType']     # 'pedestrian', 'ground', 'aerial', 'surface', or 'underwater'
    cfg.vehSubType            =        veh_type_default['vehSubType']  # 'fixedwing', 'rotorcraft', 'onroad', 'offroad', 'turtle' (there is no error checking - a flying turtle is possible!)
    logging.debug('asisgning default vehType=[{0}] and vehSubType=[{1}]'.format(cfg.vehType,cfg.vehSubType))
    thisVeh="vid_"+str(vid)
    
    # optional vehcile-specific settings: if this is in the cfg file, then use it:
    # vid_101: {'name':'rufus', 'vehType': 'aerial', 'vehSubType':'rotorcraft', 'IC_latlon':'29.193337, -81.045272', 'IC_elev': 0.0, 'IC_yaw_rad': 2.4, 'IC_pt':3 } # 3*pi/4 = 2.3562
    # [veh_details] keys
    if thisVeh in veh_details.keys():
        try:
            veh_details_for_thisVeh = literal_eval( veh_details[ thisVeh ] ) # a dictionary: {'vehType': 'aerial', 'vehSubType': 'rotorcraft'}
        except:
            logging.debug( "config file: problem converting from string to dictionary in {0} (vid={1}) --> fix typo in [ veh_details[thisVeh] ] section of config file".format(cfgFile,thisVeh) )
        
        if 'vehType' in veh_details_for_thisVeh:
            cfg.vehType           = veh_details_for_thisVeh['vehType']    # overwrite default veh type
        
        if 'vehSubType' in veh_details_for_thisVeh:
            cfg.vehSubType        = veh_details_for_thisVeh['vehSubType'] # overwrite default veh sub-type
        
        #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
        logging.debug('found speific vehicle type designation! assigning {0} with vehType=[{1}] and vehSubType=[{2}]'.format(thisVeh,cfg.vehType,cfg.vehSubType))
        if 'name' in veh_details_for_thisVeh:
            cfg.name            = veh_details_for_thisVeh['name']
            logging.debug('found speific vehicle name! assigning {0} with name=[{1}]'.format(thisVeh,cfg.name))
        if 'IC_latlon' in veh_details_for_thisVeh:
            cfg.IC_latlon       = veh_details_for_thisVeh['IC_latlon']
            cfg.IC_sel          = 5 # make this whatever necessary in vehicle model: ../veh_model/main_veh_model.py
            try:
                myLatLon = literal_eval(cfg.IC_latlon) # 'IC_latlon':'29.193899, -81.046432'
                #logging.debug('myLatLon={0}'.format(myLatLon))
                # convert lat/lon origin to UTM XYZ origin so vehicle and behaviors can know the origin offset
                (Xic_raw,Yic_raw,cfg.UTM_zone,cfg.UTM_latBand) = utm.from_latlon(myLatLon[0],myLatLon[1])
                cfg.Xic = Xic_raw - cfg.X_origin
                cfg.Yic = Yic_raw - cfg.Y_origin
            except:
                logging.debug('error converting cfg.IC_latlon={0} to XYZ UTM coordinates'.format(cfg.IC_latlon))
            logging.debug('found speific vehicle name! assigning {0} with cfg.IC_sel={1}, myLatLon={2} and cfg.Xic={3}, cfg.Yic={4}, cfg.UTM_zone={5}, cfg.UTM_latBand={6}' \
                   .format(thisVeh,cfg.IC_sel,myLatLon,cfg.Xic,cfg.Yic,cfg.UTM_zone,cfg.UTM_latBand))
        if 'IC_elev' in veh_details_for_thisVeh:
            cfg.IC_elev         = veh_details_for_thisVeh['IC_elev']
            logging.debug('found speific vehicle name! assigning {0} with IC_elev=[{1}]'.format(thisVeh,cfg.IC_elev))
        if 'IC_yaw_rad' in veh_details_for_thisVeh:
            cfg.IC_yaw_rad      = veh_details_for_thisVeh['IC_yaw_rad']
            logging.debug('found speific vehicle name! assigning {0} with IC_yaw_rad=[{1}]'.format(thisVeh,cfg.IC_yaw_rad))
        if 'firstGate' in veh_details_for_thisVeh:
            cfg.firstGate = veh_details_for_thisVeh['firstGate']
            logging.debug('found speific vehicle name! assigning {0} with firstGate=[{1}]'.format(thisVeh,cfg.firstGate))
        if 'IC_pt' in veh_details_for_thisVeh:
            cfg.IC_pt = veh_details_for_thisVeh['IC_pt']
            logging.debug('found speific vehicle name! assigning {0} with IC_pt=[{1}]'.format(thisVeh,cfg.IC_pt))
    # expected output: cfg.vehType, cfg.vehSubType; optionally: cfg.name, cfg.IC_latlon, cfg.IC_sel, cfg.Xic, cfg.Yic, cfg.IC_elev, cfg.IC_yaw_rad
    
    
    
    
    
    # -------------   SECTION:  VEH_BEHAVIORS_GLOBAL     -----------------------
    # assign each global behavior to a new cfg.behaviors[] list with default global priority number for all vehicles
    # veh_model/behaviors.py
    cfg.behaviorCfg = {} # initialize empty dictionary
    for key,val in list( veh_behaviors_global.items() ):
        # example: item[0]=beh_id_0, item[1]="{'name': 'self.wander', 'priority': 1}"
        cfg.behaviorCfg.update({ key: int(val) })
        if cfg.debug>1: print("key={0}, val={1}".format( key, val ))
        
    #print( cfg.behaviorCfg )
    # cfg.behaviorCfg={'wander': 0, 'periodicTurn': 0, 'periodicPitch': 0, 'stayInBounds': 0, 'avoid': 0, 'detectAndReport': 0, 'followRoute': 0, 'goToGate': 1}
    if cfg.debug>1:
        logging.debug('global behavior summary:')
        print('cfg.behaviorCfg={0}'.format(cfg.behaviorCfg))
        for behName,priority in cfg.behaviorCfg.items():
            print("\tnominal behaviors and priorities in cfg.behaviorCfg: {0}={1}".format(behName,priority))   
    
    
    
    # -----------   SECTION:  VEH_BEHAVIORS_INDIVIDUAL     ---------------------
    # override global defaults on any optional behavior assignments for this particular vehicle
    # veh_model/behaviors.py
    #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
    if (vid>0):
        try:
            # make vehicle-specific modifications to global behavior settings from: [veh_behaviors_individual]
            veh_behaviors_individual = config['veh_behaviors_individual'] # optional per-vehicle behavior settings
            logging.debug('---found config file section for individual vehicle behavior settings---')
            
            for vidStr,val in veh_behaviors_individual.items():
                # example: key=vid_102, val={'self.wander': 1, 'self.periodicTurn': 2, 'self.stayInBounds': 12, 'self.avoid': 10 }
                #print("key={0}, val={1}".format( key, val )) # e.g. key=vid_101, val={'self.wander': 1, 'self.periodicTurn': 2, 'self.stayInBounds': 12, 'self.avoid': 10 }
                thisVeh="vid_"+str(vid)
                if vidStr==thisVeh: # this sez: if vid_100==vid_100, then update behavior priorities
                    logging.debug('---aha! found entry to modify global behaviors for {0}---'.format(thisVeh))
                    if cfg.debug>1: print("vidStr={0}, val={1}".format(vidStr,val))
                    thisVeh_behDict = eval(val) # eval() turns the cfg file string into a proper dict: "{'self.wander': 1, 'self.periodicTurn': 2, 'self.stayInBounds': 12, 'self.avoid': 10 }"
                    for behName,priority in thisVeh_behDict.items():
                        logging.debug("\tassigning veh={0}, behName={1}, priority={2}".format(vid,behName,priority)) # e.g. k=self.wander, v=1
                        #code.interact(local=dict(globals(), **locals()))
                        if behName in cfg.behaviorCfg:
                            cfg.behaviorCfg[behName] = priority
                            if cfg.debug>1: logging.debug('updating cfg.behaviorCfg: {0}={1}'.format(behName,cfg.behaviorCfg[behName]))
                            
        except KeyError as err:
            logging.debug( "error: config file section not found: {0} in {1} (this means there are no vehicle-specific behavior settings - using VEH_BEHAVIORS_GLOBAL settings for this vehicle)".format(err,cfgFile) )
    
    
    
    
    
    
    # --------   SECTION:  POINTS, points of interest for mission commands     --------
    # - not every cfg file will contain locations
    #code.interact(local=dict(globals(), **locals()))
    class Points: # create empty class to stote all varaibles associated with points
        pass
    
    cfg.points       = Points() # make cfg.points a class so it can store data attributes as members
    try:
        # config file section: [points]
        pointsStr           = config['points'] # this is an unusual string container; convert to standard dict
        logging.debug('---found config file section for defining POINTS---')
        points = dict() # init empty dictionary to translate this string container into a normal dictionary
        if cfg.debug>0:
            logging.debug('---point config step 1 of 2, read in all point definitions---')
        for k,v in pointsStr.items():
            logging.debug('\tpoints.items() = {0}={1}'.format(k,v))
            points[ k ] = literal_eval(v) # literal_eval() converts from string into standard Python objects, like dict or list
        cfg.points.points = points # store the dictionary of points within the cfg.points class (for use in goToPoint() or vehicle model's missionState sequencer)
    except KeyError as err:
        logging.debug( "config file section not found: {0} in {1} (this means there are no points specified for any vehicles)".format(err,cfgFile) )
    # expected output: cfg.points class 
    
    # ------------------   SECTION:  STARTING POINT ASSIGNMENT     ---------------------
    #code.interact(local=dict(globals(), **locals()))
    if (vid>0):
        if hasattr(cfg.points,'points') and (len(cfg.points.points)>0):
            if hasattr(cfg,'IC_pt'):
                logging.debug('---point config step 2 of 2, assign starting point---')
                cfg.points.IC_pt = cfg.IC_pt
                logging.debug('\tassigning {0} starting point of [{1}]'.format(thisVeh,cfg.points.IC_pt))
            else:
                cfg.points.IC_pt = list( cfg.points.points.keys() )[0] # if no starting point specified, start at first dictionary key
                logging.debug('\tassigning {0} to default starting point of [{1}]'.format(thisVeh,cfg.points.IC_pt))
            # expected output: cfg.points.IC_pt
            
            # convert lat/lon for all points into UTM coords in meters
            # points are simpler than routes; there is no points_init() the way there is a route_init()
            logging.debug('converting lat/lon pairs for all points into UTM coordinates in meters')
            for k,v in cfg.points.points.items():
                #print('keys={0}'.format(k))     # keys=point_1
                #print('values()={0}'.format(v)) # values()={'ptA_lat': -81.046308, 'ptA_lon': 29.193577,    'ptB_lat': -81.046126, 'ptB_lon': 29.193865,   'nextGate': 2 }
                pt   = ( v['lat'] , v['lon'] )
                pt_Z =   v['elev'] # (m) ATO - above take-off; specified in config file [points]; 0.0 is fine
                (pt_X,pt_Y,pt_zone,pt_latBand) = utm.from_latlon( pt[0], pt[1] ) # (m) these are typically giant numbers, like (X,Y)=(489174.484, 4488110.896)
                #logging.debug('converted {0} pt (lat,lon)=({1},{2}) to X={3}(m), Y={4}(m), UTM zone={5})'.format(k,pt[0],pt[1],pt_X,pt_Y,pt_zone))
                #code.interact(local=dict(globals(), **locals()))
                # store these UTM point coordinates in the cfg.points object
                cfg.points.points[ k ]['pt_X'] = pt_X - cfg.X_origin
                cfg.points.points[ k ]['pt_Y'] = pt_Y - cfg.Y_origin
                cfg.points.points[ k ]['pt_Z'] = pt_Z - cfg.Z_origin
                logging.debug('\tk={0}, cfg.points.points[{0}]={1}'.format(k,cfg.points.points[k]))
                # cfg.points.points is a dictionary:
                # k=pt_1, cfg.points.points[pt_1]={'lat': 29.189909, 'lon': -81.044963, 'elev': 0.0, 'nextPoint': 'pt_2', 'pt_X': 68.91152402607258, 'pt_Y': -47.44667444098741}
                # and: pointNames=list( cfg.points.points.keys() ) --> ['pt_1', 'pt_2', 'pt_3', 'pt_4', 'pt_5', 'pt_6', 'pt_7', 'pt_8']
            
            cfg.points.lap = 1 # start on lap 1
            cfg.points.current_point = cfg.points.IC_pt
        # expected output: cfg.points.IC_pt, 'pt_X' and 'pt_Y' UTM keys, cfg.points.lap, cfg.points.IC_pt
    
    
    
    
    
    
    
    # ------------------   SECTION:  GATES     ---------------------
    # - not every cfg file will contain gates
    # - if config file has any gates, read and make available to all vehicles (assignment is next; farther below)
    # - if vehicle goToGate() is enabled, it'll go to gate assigned in nect section: GATE ASSIGNMENT
    #code.interact(local=dict(globals(), **locals()))
    class Gates: # create empty class to stote all varaibles associated with gates
        pass
    
    cfg.gates       = Gates() # make cfg.gates a class so it can store data attributes as members
    try:
        # config file section: [gates]
        gatesStr           = config['gates'] # this is an unusual string container; convert to standard dict
        logging.debug('---found config file section for defining GATES---')
        gates = dict() # init empty dictionary to translate this string container into a normal dictionary
        if cfg.debug>0:
            logging.debug('---gate config step 1 of 2, read in all gate definitions---')
        for k,v in gatesStr.items():
            logging.debug('\tgates.items() = {0}={1}'.format(k,v))
            gates[ k ] = literal_eval(v) # literal_eval() converts from string into standard Python objects, like dict or list
        cfg.gates.gates = gates # store the dictionary of gates within the cfg.gates class (for use in goToGate() or vehicle model's behaviors.py)
    except KeyError as err:
        logging.debug( "config file section not found: {0} in {1} (this means there are no gates specified for any vehicles)".format(err,cfgFile) )
    # expected output: cfg.gates class 
    
    # ------------------   SECTION:  STARTING GATE ASSIGNMENT     ---------------------
    #code.interact(local=dict(globals(), **locals()))
    if (vid>0):
        if hasattr(cfg.gates,'gates') and (len(cfg.gates.gates)>0):
            if hasattr(cfg,'firstGate'):
                logging.debug('---gate config step 2 of 2, assign starting gate---')
                cfg.gates.firstGate = cfg.firstGate
                logging.debug('\tassigning {0} starting gate of [{1}]'.format(thisVeh,cfg.gates.firstGate))
            else:
                cfg.gates.firstGate = list( cfg.gates.gates.keys() )[0] # if no starting gate specified, start at first dictionary key
                logging.debug('\tassigning {0} to default starting gate of [{1}]'.format(thisVeh,cfg.gates.firstGate))
            # expected output: cfg.gates.firstGate
            
            logging.debug('converting lat/lon pairs for all gates points A and B into UTM coordinates in meters')
            for k,v in cfg.gates.gates.items():
                #print('keys={0}'.format(k))     # keys=gate_1
                #print('values()={0}'.format(v)) # values()={'ptA_lat': -81.046308, 'ptA_lon': 29.193577,    'ptB_lat': -81.046126, 'ptB_lon': 29.193865,   'nextGate': 2 }
                ptA = ( v['ptA_lat'] , v['ptA_lon'] )
                ptB = ( v['ptB_lat'] , v['ptB_lon'] )
                (ptA_X,ptA_Y,ptA_zone,ptA_latBand) = utm.from_latlon( ptA[0], ptA[1] ) # (m) these are typically giant numbers, like (X,Y)=(489174.484, 4488110.896)
                (ptB_X,ptB_Y,ptB_zone,ptB_latBand) = utm.from_latlon( ptB[0], ptB[1] ) # (m)
                #logging.debug('converted {0} pt A (lat,lon)=({1},{2}) to X={3}(m), Y={4}(m), UTM zone={5})'.format(k,ptA[0],ptA[1],ptA_X,ptA_Y,ptA_zone))
                #logging.debug('converted {0} pt B (lat,lon)=({1},{2}) to X={3}(m), Y={4}(m), UTM zone={5})'.format(k,ptB[0],ptB[1],ptB_X,ptB_Y,ptB_zone))
                #code.interact(local=dict(globals(), **locals()))
                # store these UTM gate post coordinates in the cfg.gates object
                cfg.gates.gates[ k ]['ptA_X'] = ptA_X - cfg.X_origin
                cfg.gates.gates[ k ]['ptA_Y'] = ptA_Y - cfg.Y_origin
                cfg.gates.gates[ k ]['ptB_X'] = ptB_X - cfg.X_origin
                cfg.gates.gates[ k ]['ptB_Y'] = ptB_Y - cfg.Y_origin
                logging.debug('\tk={0}, cfg.gates.gates[{0}]={1}'.format(k,cfg.gates.gates[k]))
            
            cfg.gates.lap = 1 # start on lap 1
            cfg.gates.current_gate = cfg.gates.firstGate
        # expected output: cfg.gates.IC_pt, 'ptA_X', 'ptA_Y', 'ptB_X', 'ptB_Y' UTM keys, cfg.gates.lap, cfg.gates.firstGate
    
    
    
    
    
    
    
    
    
    # ------------------   SECTION:  missionCommands   -------------------------------
    # not every cfg file will contain missionCommands
    if (vid>0):
        cfg.missionCommands = {} # init empty dictionary if there are any commands or not
        try:
            # read config file section: [missionCommands]
            missionCommands = config['missionCommands'] # optional mapping from vehicle ID's (vid's) to route numbers in ../routes
            if cfg.debug>0:
                logging.debug('---parsing missionCommands---')
                logging.debug('')
            
            cfg.misCmdCtrledBeh = set() # init empty set() of missionCommand controlled behaviors
            #code.interact(local=dict(globals(), **locals()))
            for key,val in missionCommands.items():
                #logging.debug('{0} = {1}'.format(key,val))
                # examples of key,val:
                #    missionCmd2 = {'vid':100, 'missionState': 10 , 'action':'waitOnVeh',        'otherVeh'       :  101,     'progThresh': 11.0   }
                #    missionCmd4 = {'vid':100, 'missionState': 30 , 'action':'goToPoint',        'point'          : 'pt_A3' }
                #code.interact(local=dict(globals(), **locals()))
                thisCmd = eval(val) # turn string into a proper dictionary
                if vid==thisCmd['vid']: # is the vehicle calling readConfigFile() the same as the vid in this missionCommand?
                    #logging.debug('---aha! found a missionCommand line for {0}'.format(vid))
                    if cfg.debug>0: logging.debug("aha! found mission command: vid={0}: {1} = {2}".format(vid,key,val))
                    cfg.missionCommands[key]=thisCmd
                    thisAction=thisCmd['action']
                    if (thisAction=='goToPoint') | (thisAction=='goToGate'): # <-- add any other mission-enabled behaviors
                        #code.interact(local=dict(globals(), **locals()))
                        cfg.misCmdCtrledBeh.add( thisAction ) # this is a unique set of all behaviors in this command list controlled by missionCommands
                        test = thisCmd['point'] in list( cfg.points.points.keys() ) # is thisCmd's point in the list of all points?
                        if test == False: # this helps identify typos or missing points before goToPoint() is told to go there
                            logging.debug("mission command action uses a point that is not defined!: vid={0}".format(vid))
                            logging.debug("mission cfg file line: [{0}], point name not found in cfg file [points] section: [{1}]".format(key,thisCmd['point']))
                            logging.debug("all points in [points]=[{0}]".format( list(cfg.points.points.keys()) ))
                            logging.debug('exiting.')
                            exit(-1)
                            
                    # sort by missionState, not by missionCmd key ('missionState' is a key inside the dictionary, see comments just above); for examples, see: dict_sort_examples.py
                    outSortedByValue = {k: v for k, v in sorted(cfg.missionCommands.items(), key=lambda item: item[1]['missionState'])}
                    #for item in outSortedByValue.items():
                    #    print(item)
                    cfg.missionCommands=outSortedByValue # over-write with sorted result
                    
                    logging.debug('missionCommand summary: discovered [{0}] mission commands for vehicle {1}'.format( len(cfg.missionCommands.keys()), vid ) )
                    logging.debug('these are controlled by missionCommand actions: {0}'.format(cfg.misCmdCtrledBeh))
                    
        except KeyError as err:
            logging.debug( "config file section not found: {0} in {1} (this means there are no missionCommands specified for any vehicles)".format(err,cfgFile) )
        
        # create flag for mission-enabled behaviors to determine who controls them - missionStateSequencer() or 'nextPoint' or 'nextGate'?
        cfg.usingMissionCommands=False
        if len(cfg.missionCommands)>0:
            cfg.usingMissionCommands=True
        logging.debug('readConfigFile() assigning cfg.usingMissionCommands={0} for vid={1}'.format(cfg.usingMissionCommands,vid))
        
        # output: cfg.missionCommands dictionary --> *sorted* by missionState
        # example:
        #   missionCmd1 = {'vid': 100, 'missionState': 1, 'action': 'goToPoint', 'point': 'pt_A1'}
        #   missionCmd2 = {'vid': 100, 'missionState': 10, 'action': 'waitOnVeh', 'otherVeh': 101, 'progThresh': 11.0}
        #   missionCmd3 = {'vid': 100, 'missionState': 20, 'action': 'goToPoint', 'point': 'pt_A2'}
        #   missionCmd4 = {'vid': 100, 'missionState': 30, 'action': 'goToPoint', 'point': 'pt_A3'}
        #   missionCmd5 = {'vid': 100, 'missionState': 40, 'action': 'waitOnVeh', 'otherVeh': 101, 'progThresh': 31.0}
        #   missionCmd6 = {'vid': 100, 'missionState': 100, 'action': 'goToMissionState', 'newMissionState': 1}
        #
        #code.interact(local=dict(globals(), **locals()))
        
        
        
        
        
        
        
        
        
        
    # ------------------   SECTION:  VEH_ROUTE_ASSIGNMENTS     -----------------
    # not every cfg file will contain waypoint routes
    try:
        # config file section: [veh_route_assignments]
        veh_routes         = config['veh_route_assignments'] # optional mapping from vehicle ID's (vid's) to route numbers in ../routes
        if cfg.debug>0:
            logging.debug('---route config step 1 of 4---')
            logging.debug('')
            #code.interact(local=dict(globals(), **locals()))
            for veh,routeParam in veh_routes.items():
                logging.debug('\t{0}={1}'.format(veh,routeParam))
        cfg.veh_routes = veh_routes # this class attribute will trigger further route configuration in the vehicle model (route_init.py) but not in core
    except KeyError as err:
        logging.debug( "config file section not found: {0} in {1} (this means there are no waypoint routes specified for any vehicles)".format(err,cfgFile) )
    
    
    
    
    # ------------------   SECTION:  DATATABLE_DISPLAY     ---------------------
    # return a list of all default columns to initialize the DataTable
    cfg.default_display_cols=[] # init empty list
    try:
        # read config file section: [datatable_display]
        datatable_display    = config['datatable_display'] # used in move_dashboard.py
        for k,v in config['datatable_display'].items():
            print('\t display datatable column: {0}, {1}'.format(k, v.strip('\"')))
            cfg.default_display_cols.append(v.strip('\"') ) # want 'Vehicle ID' rather than '"Vehicle ID"'
    except KeyError as err:
        logging.debug( "config file section not found: {0} in {1} (this means the dashboard display will show all columns by default)".format(err,cfgFile) )
    
    
    
    # debugging console output
    if cfg.debug>1:
        # print key-value pairs just assigned from the config file
        for k, v in cfg.__dict__.items():
            logging.debug("cfg: {0} = {1}".format(k, v))
            
        try:
            N_cfg_file_names_builtins = len(veh_names_builtins)
            N_cfg_file_names_live_gps = len(veh_names_live_gps)
            
            print('')
            
            logging.debug('N_cfg_file_names_builtins='.format(N_cfg_file_names_builtins))
            logging.debug('N_cfg_file_names_live_gps='.format(N_cfg_file_names_live_gps))
            
            logging.debug('')
            
            for name,val in veh_names_builtins.items():
                logging.debug('[veh_names_builtins]    {0} = {1}'.format(name,val))
                
            logging.debug('')
            
            for name,val in veh_names_live_gps.items():
                logging.debug('[veh_names_live_gps]    {0} = {1}'.format(name,val))
                
            logging.debug('')
            
        except NameError:
            logging.debug('\n')
            logging.debug('only returned cfg')
            logging.debug('\n')
            
            
    return cfg, veh_names_builtins, veh_names_live_gps




# this function is executable at the command line from ./core folder to
# test config file functionality:
#
#   python3 readConfigFile.py
#
if __name__ == "__main__":
    
    
    import os
    import sys
    sys.path.append(os.path.relpath("../veh_model")) # this allows my_cool_module.py (in dir1) to be found by an import in dir2
    from route_init import route_init
    
    
    
    #cfgFile = 'default.cfg' # test a failed file location
    #cfgFile = '../scenario/default.cfg' # config .cfg files use python's .ini format
    #cfgFile = '../scenario/gate_figure_8.cfg'
    #cfgFile = '../scenario/route_foco_park.cfg'
    #cfgFile = '../scenario/route_indy_inside_outside_and_fast_line_traffic.cfg'
    #cfgFile = '../scenario/route_simple_circle.cfg'
    #cfgFile = '../scenario/turtle_tech_basic.cfg'
    #cfgFile = '../scenario/route_NATO_departure.cfg'
    #cfgFile = '../scenario/missionDefault.cfg' # Dec 2021/Jan 2022
    cfgFile = '../scenario/point_figure_8.cfg'
    
    
    #cfg = readConfigFile( cfgFile )
    vid=100 # vid is typically assigned in main_launch_veh_process.py
    #vid=101
    #vid=-1
    cfg, veh_names_builtins, veh_names_live_gps = readConfigFile( cfgFile, vid )
    
    print('--------------- done with readConfigFile() ---------------')
    print('\n\n\n\n')
    print('nVeh_builtin={0}'.format(cfg.nVeh_builtin))
    print('nVeh_live_gps={0}'.format(cfg.nVeh_live_gps))
    print('nVeh_custom={0}'.format(cfg.nVeh_custom))
    names_gps=list( veh_names_live_gps.keys() )
    print(names_gps)
    print( 'length of names_gps list: ',len(names_gps) )
    
    # this clip goes into move_live_mapping_v3.py to plot all waypoint routes in bokeh
    # ----------------------------- route init ---------------------------------
    # plot all waypoints for each vehicle configured to followRoute() on a route
    #code.interact(local=dict(globals(), **locals()))
    print('--------------- begin routes -------------------------')
    if hasattr(cfg,'veh_routes') and (len(cfg.veh_routes)>0): # (cfg.behaviorCfg['followRoute']>0)
        for k,v in cfg.veh_routes.items():
            cfg.vid=int( k.split('_')[1] ) # convert string 'vid_100' to 100 integer
            cfg, veh_names_builtins, veh_names_live_gps = readConfigFile( cfgFile, cfg.vid ) # previous readConfigFile() was with vid=-1 and does not populate routes for generic vid=-1
            cfg = route_init( cfg )
            for j in range(cfg.route.N):
                print('\tvid={0}, j={1}, cfg.route.lat={2},cfg.route.lon={3},cfg.route.X={4},cfg.route.Y={5},cfg.route.Z={6}'
                    .format( cfg.vid, j, cfg.route.lat[j], cfg.route.lon[j], cfg.route.X[j], cfg.route.Y[j], cfg.route.Z[j] ))
    else:
        print('\t[ no routes specified in config file ]')   
    print('---------------  end routes  -------------------------')
    
    
    print('\n\n\n')
    print('--------------- begin points -------------------------')
    #code.interact(local=dict(globals(), **locals()))
    if hasattr(cfg,'points') and hasattr(cfg.points,'points'):
        if len(cfg.points.points)>0: # if not empty...
            for pt,data in cfg.points.points.items():
                print('pt={0}, data={1}'.format(pt,data))
        else:
            print('\t[ no points specified in config file ]')   
    else:
        print('\t[ no points attribute in cfg class ]')   
    print('---------------  end points  -------------------------')
    
    
    
    
    print('\n\n\n')
    print('---------- begin mission commands (for vid={0}) --------------------'.format(vid))
    #code.interact(local=dict(globals(), **locals()))
    if hasattr(cfg,'missionCommands'):
        if len(cfg.missionCommands)>0: # if not empty...
            for cmd,data in cfg.missionCommands.items():
                print('cmd={0}, data={1}'.format(cmd,data))
        else:
            print('\t[ no missionCommands specified in config file ]')   
    else:
        print('\t[ no missionCommands attribute in cfg class ]')   
    print('---------------  end mission commands (for vid={0})  -------------------------'.format(vid))
    
    
    
    
    
    
    print('\n\n\n')
    print('--------------- begin gates -------------------------')
    #code.interact(local=dict(globals(), **locals()))
    if hasattr(cfg,'gates') and hasattr(cfg.gates,'gates'):
        if len(cfg.gates.gates)>0: # if not empty...
            for gate,data in cfg.gates.gates.items():
                print('gate={0}, data={1}'.format(gate,data))
        else:
            print('\t[ no gates specified in config file ]')   
    else:
        print('\t[ no gates attribute in cfg class ]')   
    print('---------------  end gates  -------------------------')

