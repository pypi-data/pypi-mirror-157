# routes.py - waypoint following route function definitions for
#             main_veh_model.py and behaviors.py
#
# Marc Compere, comperem@gmail.com
# created : 11 Jul 2019
# modified: 30 Jul 2020
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

import logging

# route_init.py gets called from 'bokeh serve' which doesn't work with logging.debug --> use all prints here

# inialize routes in vehicle model, main_veh_model.py
#
# if the vehicle model configuration file specifies a route, this function
# looks in ../routes for the waypoint definition file and
# (a) imports restore_waypoints() as a python function
# (b) executes the restore_waypoint() function which resides in ../routes
# (c) performs some basic statistics from within restore_waypoint() such as
#     estimate path length and number of waypoints in computeRouteStatistics()
#
# when creating new route definition files (in ../routes) change the routeFileName.py
# but keep the same function name: restore_waypoints()
#
def route_init( cfg ):
    
    import sys
    import os
    import code # uncommented only during debugging; drops into a python interpreter at code.interact()
    
    # recall from behaviors.py:     self.behaviorCfg = {'wander': 1, 'periodicTurn': 2, 'periodicPitch': '0', 'stayInBounds': 12, 'avoid': 10, 'detectAndReport': '0', 'followRoute': '0'}
    print('route_init(): ----------- ')
    print(cfg.behaviorCfg)
    print('route_init(): ----------- ')
    if hasattr(cfg,'veh_routes') and (cfg.behaviorCfg['followRoute']>0): # if veh_routes exists, the 'veh_route_assignments' section must have been in the config file, see readConfigFile()
        class RouteCfg: # define an empty class for a routeCfg variable container
            pass        
        cfg.routeCfg=RouteCfg() # every vehicle needs a routeCfg object if it's configured for waypoint following or not
        
        # all vehicles wake up and look for a route assignment - some will; some won't
        for veh,routeParam in cfg.veh_routes.items():
            # veh = 'vid_100'
            # routeParam = "{'route_script':'route_01_waypoints.py', 'nLapsMax':19999, 'startOption':'startAt', 'startingWaypoint':1, 'lapRestartWaypoint':1, 'endOption':'stop', 'color':'magenta' }"
            #print('veh from config file: {0}'.format(veh))
            thisVeh='vid_'+str(cfg.vid) # this is the currently executing vehicle process vid for comparison with the config file routes list
            
            # were any routes speified for this particular vehicle?
            #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
            if veh == thisVeh:
                print('\t---route config step 2 of 4---')
                print('\t\taha! a route assignment is specified in the config file for {0}'.format(veh))
                print('\t\tvid={0}, routeParam=[{0}]'.format(veh,routeParam)) # routeParam = vid_100 {'route_script':'route_01_waypoints.py', 'nLapsMax':19999, 'startOption':'startAt', 'startingWaypoint':1, 'lapRestartWaypoint':1, 'endOption':'stop', 'color':'magenta' }
                try:
                    routeCfg        = eval(routeParam) # convert "string" to dict object: {'route_script':'route_01_waypoints.py', 'nLapsMax':19999, 'startOption':'startAt', 'startingWaypoint':1, 'lapRestartWaypoint':1, 'endOption':'stop', 'mapColor':'magenta' }
                    routeCfg['vid'] = veh
                except KeyError as err:
                    logging.debug( "config file error in assigning routeCfg for vehicle: [{0}] in {1}, err={2}".format(veh,cfgFile,err) )
                cfg.routeCfg=routeCfg
                # expected output: cfg.routeCfg with dict keys: route_script, nLapsMax, startOption, startingWaypoint, lapRestartWaypoint, endOption, mapColor
                                
                if (cfg.routeCfg['startingWaypoint']<1): # routes and waypoints are 0-based 
                    cfg.routeCfg['startingWaypoint']=1 # IC starts at startingWaypoint (which is likely 0) and heads towards 1st waypoint
                    print('\t\tvid={0} warning - updating routeCfg[''startingWaypoint'']=1: {1}'.format(cfg.vid, cfg.routeCfg))
                
                print('\t\tvid={0} using routeCfg:')
                for k,v in cfg.routeCfg.items():
                    print('\t\t\t{0}={1}'.format(k,v))
                
                # import the restore_waypoints() function defined in the route file, routeScript (this is a python file like route_01_waypoints.py in ../routes)
                print('\t---route config step 3 of 4---')
                vehModelFullName = os.path.join( os.getcwd() , sys.argv[0] ) # filename and full directory of executing vehicle model python file
                baseDir,fName = os.path.split( vehModelFullName ) # basedir will change, but fName will always be fName=main_veh_model.py
                #print('vehModelFullName={0}'.format(vehModelFullName))
                #print('baseDir={0}, fName={1}'.format( baseDir,fName) )
                routesLocation="/../routes"
                print('\tos.path.join( baseDir, routesLocation ): [{0}]'.format( os.path.join(baseDir+routesLocation) ))
                sys.path.append( os.path.join(baseDir+routesLocation) )
                
                exec_str = 'from {} import restore_waypoints'.format( os.path.splitext(cfg.routeCfg['routeScript'])[0] ) # from route_01_waypoints import restore_waypoints
                print('\t\tattempting to import route waypoints function from [{0}] with: [{1}]'.format(routesLocation,exec_str))
                try:
                    # import the route_01_waypoint.py file with the restore_waypoint() function with route waypoints we're trying to access
                    # we want this: from route_01_waypoints import restore_waypoints
                    exec( exec_str, globals() ) # eval() is for expressions; import is a statement ; use exec for statements; globals() makes this function available after the exec() command (it fails without globals() argument)
                    print('\t\trestore_waypoints() function successfully imported')
                except ImportError as err:
                    print('\tfailed on importing restore_waypoints() function, err=[{0}]'.format(err))
                    print('\terror: exiting because route waypoints unable to be loaded')
                    exit(-1)
                
                # now call the function that was successfully imported from ../routes
                print('\t---route config step 4 of 4---')
                print('\t\tattempting to call restore_waypoints() function from {0}/{1}'.format(routesLocation,cfg.routeCfg['routeScript']))
                #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
                #
                # notes:
                #   cfg.routeCfg is from MoVE config file reader in ../scenarios and contains options and the filename from which to load waypoints
                #   cfg.route is from ../routes and contains the restore_waypoints() function with waypoints in XYZ space in meters, plus speeds in m/s
                try:
                    
                    cfg.route = restore_waypoints( cfg ) # this function must reside in ../routes and be a file named the same as in the MoVE config file [veh_route_assignments] (e.g. route_01_waypoints.py)
                    
                    cfg.route.mapColor = cfg.routeCfg['mapColor'] # cfg.route gets sent to move_live_mapping_v3.py (not routeCfg)
                    cfg.route.nLapsMax = cfg.routeCfg['nLapsMax']
                    cfg.route.lap      = 1 # start on lap 1, even if it's a 1-way route or nLapsMax is 1
                    
                    print('\t\trestore_waypoints() function successfully executed from [{0}/{1}]'.format(routesLocation,cfg.routeCfg['routeScript']))
                    
                    print('\t\tcurrent route lap is {0} of {1}'.format(cfg.route.lap,cfg.route.nLapsMax))
                    print('\t---route configuration complete---')
                    
                except Exception as err:
                    print('\n\n\tfailed on restore_waypoints() function call in [{0}/{1}], err=[ {2} ]'\
                                .format(routesLocation,cfg.routeCfg['routeScript'],err))
                    print('\n\n\t-->get this running without error, then retry with vehicle model" [{0}/{1}]\n\n'\
                                .format(routesLocation,cfg.routeCfg['routeScript']))
                    print('\terror: exiting because route waypoints unable to be loaded')
                    exit(-1)
    
    return( cfg ) # send back cfg.routeCfg


# this is what the route portion should look like from a successful
# vehicle model process launch: ./main_veh_model.py -f ../scenario/default.cfg 100   0  myModel
# ------------------------------------------------------------------------------
#    (MainThread    ) 
#    (MainThread    ) ---route config step 2 of 4---
#    (MainThread    ) 	aha! a route assignment is specified in the config file for vid_100
#    (MainThread    ) 	routeParam=['route_01_waypoints.py',2,'startAt',1,'stop']
#    (MainThread    ) 	vid=100 using routeCfg: {'routeScript': 'route_01_waypoints.py', 'nLapsMx': 2, 'startOption': 'startAt', 'startingWaypoint': 1, 'endOption': 'stop'}
#    (MainThread    ) ---route config step 3 of 4---
#    (MainThread    ) 	attempting to import route waypoints function from /../routes: [from route_01_waypoints import restore_waypoints]
#    (MainThread    ) 	restore_waypoints() function successfully imported
#    (MainThread    ) ---route config step 4 of 4---
#    (MainThread    ) 	attempting to call restore_waypoints() function from /../routes/route_01_waypoints.py
#    (MainThread    ) 	i=0   , (X,Y,Z) = (    0.000,    0.000,    0.000 )(m),  dist=     0.0(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=1   , (X,Y,Z) = (    2.447,   15.451,    0.000 )(m),  dist=    15.6(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=2   , (X,Y,Z) = (    9.549,   29.389,    0.000 )(m),  dist=    31.3(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=3   , (X,Y,Z) = (   20.611,   40.451,    0.000 )(m),  dist=    46.9(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=4   , (X,Y,Z) = (   34.549,   47.553,    0.000 )(m),  dist=    62.6(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=5   , (X,Y,Z) = (   50.000,   50.000,    0.000 )(m),  dist=    78.2(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=6   , (X,Y,Z) = (   65.451,   47.553,    0.000 )(m),  dist=    93.9(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=7   , (X,Y,Z) = (   79.389,   40.451,    0.000 )(m),  dist=   109.5(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=8   , (X,Y,Z) = (   90.451,   29.389,    0.000 )(m),  dist=   125.1(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=9   , (X,Y,Z) = (   97.553,   15.451,    0.000 )(m),  dist=   140.8(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=10  , (X,Y,Z) = (  100.000,    0.000,    0.000 )(m),  dist=   156.4(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=11  , (X,Y,Z) = (   97.553,  -15.451,    0.000 )(m),  dist=   172.1(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=12  , (X,Y,Z) = (   90.451,  -29.389,    0.000 )(m),  dist=   187.7(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=13  , (X,Y,Z) = (   79.389,  -40.451,    0.000 )(m),  dist=   203.4(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=14  , (X,Y,Z) = (   65.451,  -47.553,    0.000 )(m),  dist=   219.0(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=15  , (X,Y,Z) = (   50.000,  -50.000,    0.000 )(m),  dist=   234.7(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=16  , (X,Y,Z) = (   34.549,  -47.553,    0.000 )(m),  dist=   250.3(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=17  , (X,Y,Z) = (   20.611,  -40.451,    0.000 )(m),  dist=   265.9(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=18  , (X,Y,Z) = (    9.549,  -29.389,    0.000 )(m),  dist=   281.6(m),   speed=   5.4(m/s)
#    (MainThread    ) 	i=19  , (X,Y,Z) = (    2.447,  -15.451,    0.000 )(m),  dist=   297.2(m),   speed=   5.4(m/s)
#    (MainThread    ) 
#    (MainThread    ) 	computeRouteStatistics() route.source: [route_01_waypoints]
#    (MainThread    ) 	computeRouteStatistics() route.desc  : [route 01, circle, R=50.0(m) in XYZ coords]
#    (MainThread    ) 	computeRouteStatistics() route.N     : [20] (waypoints)
#    (MainThread    ) 	computeRouteStatistics() route.dist  : [297.225] (m)
#    (MainThread    ) 	computeRouteStatistics() segment min : [15.643] (m)
#    (MainThread    ) 	computeRouteStatistics() segment max : [15.643] (m)
#    (MainThread    ) 
#    (MainThread    ) 	restore_waypoints() function successfully executed from [/../routes/route_01_waypoints.py]
#    (MainThread    ) ---route configuration complete---
#
#














