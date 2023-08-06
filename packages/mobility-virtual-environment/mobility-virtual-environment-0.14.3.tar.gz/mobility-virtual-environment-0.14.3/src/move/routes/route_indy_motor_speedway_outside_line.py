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
    route.desc = "route on outside line of Indianapolis Motor Speedway"
    
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
39.7931321028286 , -86.2389239976233 , 67
39.7918703806396 , -86.2388975855216 , 67
39.7911702840327 , -86.2388971153642 , 67
39.7906316853537 , -86.2388764220529 , 67
39.7900698044009 , -86.2388298855158 , 67
39.7897216256651 , -86.2387346827464 , 67
39.7894360732326 , -86.2385820987322 , 67
39.7891141305055 , -86.238341649691 , 67
39.788817871658 , -86.238036479615 , 67
39.7885197789772 , -86.2376135617357 , 67
39.7882724051905 , -86.2370571396505 , 67
39.788127802672 , -86.2364993582112 , 67
39.7880834737487 , -86.2359360598508 , 67
39.7880922715731 , -86.2344275742044 , 67
39.7880926866801 , -86.233464322528 , 67
39.7881401186067 , -86.2326843585786 , 67
39.7883822857869 , -86.2318693963812 , 67
39.7886736830572 , -86.2313378611906 , 67
39.7890296867275 , -86.2309058919634 , 67
39.7894879033228 , -86.2305465531209 , 67
39.7899328841997 , -86.2303616187489 , 67
39.7903321631431 , -86.2302977125624 , 67
39.7907639916571 , -86.2302876718721 , 67
39.7912290928981 , -86.2302916783727 , 67
39.7920292549766 , -86.2303023879196 , 67
39.7923608467818 , -86.230320514953 , 67
39.7940128022974 , -86.2303362226614 , 67
39.7958742358825 , -86.2303648739095 , 67
39.7977809503035 , -86.2304016423059 , 67
39.799237981053 , -86.2304251324999 , 67
39.7999437448083 , -86.2304744102016 , 67
39.8004542526737 , -86.2306306510006 , 67
39.8008517878507 , -86.2309056998797 , 67
39.8013070218361 , -86.2313836660375 , 67
39.8015924264253 , -86.2318407531305 , 67
39.801800614242 , -86.2323457408582 , 67
39.8019202906823 , -86.2328474023952 , 67
39.8019563869222 , -86.2333912241079 , 67
39.801958315272 , -86.234252432911 , 67
39.8019507797851 , -86.2352322935232 , 67
39.8019364520013 , -86.2361004994636 , 67
39.8018607665705 , -86.2368076499582 , 67
39.8016658284365 , -86.2373837621828 , 67
39.8014054109008 , -86.2378976149554 , 67
39.8009728498666 , -86.2384239190578 , 67
39.8005945215714 , -86.2387194087994 , 67
39.800297424712 , -86.2388802288009 , 67
39.7998217151239 , -86.239003844329 , 67
39.7994121109276 , -86.2390149769366 , 67
39.7985808625838 , -86.2390192943786 , 67
39.7974431764827 , -86.2389914486958 , 67
39.7968407556343 , -86.2389835219401 , 67
39.7957460733383 , -86.2389647673889 , 67
39.7935563241033 , -86.2389200603867 , 67
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
    route.spd_mps = 0.4*spd_mps # (m/s)
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

    
    



























