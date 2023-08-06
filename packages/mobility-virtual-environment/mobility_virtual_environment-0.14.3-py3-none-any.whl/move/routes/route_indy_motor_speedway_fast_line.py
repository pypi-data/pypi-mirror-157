#!/usr/bin/env python3
#
# restore waypoints for an exterior lap around Spring Canyon Park in Fort Collins Colorado
#
# usage:
#    ./route_foco_park_waypoints.py
#
#
# Marc Compere, comperem@gmail.com
# created : 14 Jul 2019
# modified: 29 Jul 2020
#
# --------------------------------------------------------------
# Copyright 2018, 2019 Marc Compere
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

import numpy as np
import logging


# ------------------------------------------------------------------------------
# the restore_waypoint() function gets called from MoVE vehicle model
# or as a stand-alone program with __main__ below
def restore_waypoints( cfg ):
    import numpy as np
    from routes_functions import computeRouteStatistics
    import utm
    
    # create an empty route object 
    class Route:
        pass
    route = Route()
    
    # all waypoints must eventually be in an orthogonal, terrain-fixed XYZ Cartesian coordinate system
    # however, route, or path coordinates may be specified in lat/lon pairs or (X,Y) coordinates directly
    #
    # - if original route coordinates are specified in meters, then use 'meters' for route.originalUnits
    # - if original route coordinates are specified in lat/lon pairs in decimal degrees, use 'decimal_degrees'
    route.originalUnits = 'decimal_degrees' #'meters'
    route.desc = "route on fast line of Indianapolis Motor Speedway"
    
    # -------------------------------
    # specify the route coordinates:
    # -------------------------------
    # the lines below were copy-pasted directly from this .csv: fort_collins_spring_canyon_park_1_lap_13_Jul_2019.csv
    # the .csv file was written by fort_collins_lap_preprocessor.m which works in Matlab or Octave
    #
    # for a series of points without commas, python has something called
    # multi-line strings that are indicates by three quotes in a row (single or double quotes)
    #
    # format: lat,lon,speed (m/s)
    my_multi_line_string_of_lat_lon_points = """
39.7931379552455	,	-86.2388859736218	,	76
39.7917049872514	,	-86.2388597669211	,	76
39.7908262471902	,	-86.2388534351973	,	76
39.7902677086316	,	-86.2387973247797	,	76
39.7898851811244	,	-86.2387118087971	,	76
39.7895236842797	,	-86.2385467541505	,	76
39.7891912272085	,	-86.238311517924	,	76
39.7889136093329	,	-86.2380344757232	,	76
39.7886988493175	,	-86.2377647636745	,	76
39.7884791251762	,	-86.2373785149297	,	76
39.7882679070831	,	-86.2368338511231	,	76
39.7881905502715	,	-86.2364821829912	,	76
39.7881261781947	,	-86.2360832296321	,	76
39.7881003568571	,	-86.2355610091821	,	76
39.7880995664694	,	-86.2348047877598	,	76
39.7881023898898	,	-86.2338480981935	,	76
39.7881411524481	,	-86.2331276502477	,	76
39.7882373929841	,	-86.23252672726	,	76
39.7884495618597	,	-86.231891900514	,	76
39.7887327454437	,	-86.2314058437774	,	76
39.789043585347	,	-86.2310156686257	,	76
39.7894267936558	,	-86.2306842558506	,	76
39.7898584177639	,	-86.2304733432228	,	76
39.7901521260928	,	-86.2303774491441	,	76
39.7906217074152	,	-86.2303096624191	,	76
39.7914874601249	,	-86.2303098818802	,	76
39.7924401739854	,	-86.230319599394	,	76
39.7941946814293	,	-86.2303510129326	,	76
39.7957390357503	,	-86.2303715584169	,	76
39.7983791170419	,	-86.2304262538633	,	76
39.7997253798889	,	-86.2304879398294	,	76
39.8003765274331	,	-86.2306771061792	,	76
39.8007950756279	,	-86.2309572174469	,	76
39.8011757638875	,	-86.2313320976475	,	76
39.8014616001497	,	-86.2318009294117	,	76
39.8016803570202	,	-86.2323043703024	,	76
39.8018266953357	,	-86.2328507234341	,	76
39.8018824566579	,	-86.2333414085897	,	76
39.801909402799	,	-86.2338647134964	,	76
39.8019161384472	,	-86.2349192383296	,	76
39.8018797915155	,	-86.2356608429396	,	76
39.8018454499687	,	-86.2362530471522	,	76
39.801729157075	,	-86.2368658895232	,	76
39.801507822115	,	-86.2374982568143	,	76
39.8011610454603	,	-86.23806032458	,	76
39.8006774733236	,	-86.2385159499869	,	76
39.8002365400123	,	-86.2387871188793	,	76
39.7997631365082	,	-86.2389368818263	,	76
39.7993029614969	,	-86.2389850823471	,	76
39.7987376916414	,	-86.2389957872474	,	76
39.7971886028798	,	-86.2389750494843	,	76
39.7960750891383	,	-86.2389398051099	,	76
39.7935596100777	,	-86.2388822026414	,	76
        """
    # all math and route following must be done in orthogonal coordinates, so
    # convert these lat/lon pairs to UTM coordinates which assumes a flat Earth
    # within this UTM zone (there are 60 zones around Earth)
    
    list_of_rows = my_multi_line_string_of_lat_lon_points.split('\n')
    
    # initialize native python lists
    lat=[]
    lon=[]
    X=[]
    Y=[]
    spd_mps=[]
    cnt=0
    #print('---')
    for row in list_of_rows:
        #print(row)
        if row.strip() != '': # strip() removes leading and trailing whitespace
            #print( repr(row) ) # repr() shows invisible characters to distinguish spaces from tabs and newlines
            #str=row.strip().split("\t")
            str=row.strip().split(",")
            #print('processing row {0}: [{1}]'.format(cnt,str))
            
            lat_single_pt   = float( str[0] )
            lon_single_pt   = float( str[1] )
            speed_single_pt = float( str[2] )
            
            # utm library converts from lat/lon in decimal degrees to orthogonal
            # XYZ coordinates in meters within a single UTM zone
            (X_single_pt,Y_single_pt,zone,latBand) = utm.from_latlon(lat_single_pt,lon_single_pt) # these are typically giant numbers, like (X,Y)=(489174.484, 4488110.896)
            
            # list.append() is super fast for growing native python lists dynamically
            lat.append( lat_single_pt )
            lon.append( lon_single_pt )
            X.append( X_single_pt ) # X_origin and Y_origin are also typically giant numbers, like 
            Y.append( Y_single_pt )
            spd_mps.append( speed_single_pt )
            cnt=cnt+1
    #print('---')
    
    lat     = np.array(   lat  ) # convert native python lists to numpy array objects
    lon     = np.array(   lon  )
    X       = np.array(     X  )
    Y       = np.array(     Y  )
    Z       = np.zeros( len(X) ) # (m) initialize Z with numpy array of all zeros
    spd_mps = np.array( spd_mps  ) # (m/s) commanded speed for all waypoints is from SensorLog's original GPS-based recording
    
    
    # --------------------------------------------------------------------------
    # now stuff these arrays (python lists) into the route object create at the top
    # MoVE will use this function's return 'route' object from here on out
    route.lat = lat
    route.lon = lon
    route.X = X # (m) X array in cartesian XYZ coordinates
    route.Y = Y # (m) Y array in cartesian XYZ coordinates
    route.Z = Z # (m) Z array in cartesian XYZ coordinates
    route.spd_mps = 0.35*spd_mps # (m/s)
    if '__file__' in locals():
        route.source = __file__ # this file's name
    else:
        route.source = __name__ # __main__ when debugging in a terminal console
    
    route = computeRouteStatistics(route)
    
    return(route)
# ------------------------------------------------------------------------------


logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-14s) %(message)s',
)



if __name__ == "__main__":
    
    import matplotlib.pyplot as plt
    import multiprocessing
    import os
    from routes_functions import computeRouteStatistics, plot_graph
    
    print("starting __main__")
    
    class Cfg:
        pass
    
    cfg = Cfg()
    #cfg.vid=101
    #cfg.L_char = 1.0 # (m) example vehicle's characteristic length
    #cfg.v_max = 20.0 # (m/s) example vehicle's maximum speed
    
    # this function is called from the vehicle model, main_veh_model.py
    route = restore_waypoints( cfg )
    
    # print full route data structure
    #for key,val in route.__dict__.items():
    #    print("{0}={1}".format(key,val))
    
    # optionally bring the plot window up in a separate process
    makePlots=True #False
    skipNthLabel=1 #1 % use 10 or 50 if waypoint labels clutter the plot
    if (makePlots==True):
        multiprocessing.Process(target=plot_graph, args=(route,skipNthLabel)).start()
        print("exiting main")
        os._exit(0) # this exits immediately with no cleanup or buffer flushing

    
    



























