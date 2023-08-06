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
    route.desc = "route on inside line of Indianapolis Motor Speedway"
    
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
39.7931425418671 , -86.2388233405866 , 58.1
39.7920317297645 , -86.2388011981574 , 58.1
39.7906939854471 , -86.2387868468725 , 58.1
39.7901752265831 , -86.2387488314172 , 58.1
39.789808338871 , -86.2386347992525 , 58.1
39.7894326207965 , -86.2384426575281 , 58.1
39.7890145696252 , -86.2381029447893 , 58.1
39.7886108862293 , -86.237572405947 , 58.1
39.7883901612987 , -86.2370910838366 , 58.1
39.7882511099057 , -86.236638221689 , 58.1
39.7881782906913 , -86.2362604501384 , 58.1
39.7881546420175 , -86.2356897318449 , 58.1
39.7881601398315 , -86.2347992726314 , 58.1
39.788172322431 , -86.2334327590669 , 58.1
39.7882273341278 , -86.2327806244594 , 58.1
39.7883139230498 , -86.2323592551063 , 58.1
39.7885061297627 , -86.2318455095785 , 58.1
39.788774511019 , -86.2313761230146 , 58.1
39.7891116978612 , -86.2309847766533 , 58.1
39.789446493449 , -86.2307028939629 , 58.1
39.7897823429162 , -86.2305315011089 , 58.1
39.7902127939264 , -86.2303986875775 , 58.1
39.7905594571209 , -86.230382214394 , 58.1
39.7912830234859 , -86.2303807923939 , 58.1
39.792275810595 , -86.230404566114 , 58.1
39.7932011392069 , -86.2304241462238 , 58.1
39.794813046967 , -86.23044732925 , 58.1
39.7970704987838 , -86.230487612313 , 58.1
39.7982199317733 , -86.230514510734 , 58.1
39.7992811200643 , -86.2305188288838 , 58.1
39.7997010611832 , -86.2305366800659 , 58.1
39.8001220513603 , -86.2306170508381 , 58.1
39.8005228587149 , -86.2307896255499 , 58.1
39.8008794641508 , -86.2310465315267 , 58.1
39.8012296107331 , -86.2314418668555 , 58.1
39.8014535365143 , -86.2317814144162 , 58.1
39.8016737740862 , -86.2322769228348 , 58.1
39.8018090510535 , -86.2327389480739 , 58.1
39.8018742793216 , -86.233155721752 , 58.1
39.8018918919689 , -86.2334772919496 , 58.1
39.8018830772166 , -86.2339731684695 , 58.1
39.8018841393422 , -86.2345626088156 , 58.1
39.801857411263 , -86.2361062676624 , 58.1
39.801799955945 , -86.2365842278036 , 58.1
39.8016944967607 , -86.2370359710028 , 58.1
39.8014785651879 , -86.2375664600915 , 58.1
39.8012160034181 , -86.2380000516724 , 58.1
39.8009469880084 , -86.2382970519018 , 58.1
39.8006692732545 , -86.2385421857841 , 58.1
39.8003423449032 , -86.2387446795692 , 58.1
39.8000201758715 , -86.2388559831143 , 58.1
39.799725890342 , -86.2389125076693 , 58.1
39.7994133880535 , -86.2389291228612 , 58.1
39.7990414337871 , -86.2389097342921 , 58.1
39.7985729080635 , -86.2389178803594 , 58.1
39.7979888221411 , -86.238926872611 , 58.1
39.7975977400612 , -86.2389006029813 , 58.1
39.7971378121355 , -86.2388863991185 , 58.1
39.7963083977832 , -86.238882705963 , 58.1
39.7949236009397 , -86.2388402144443 , 58.1
39.7941729803632 , -86.238828664168 , 58.1
39.7935592062348 , -86.2388261489038 , 58.1
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
    route.spd_mps = 0.5*spd_mps # (m/s)
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
    
    



























