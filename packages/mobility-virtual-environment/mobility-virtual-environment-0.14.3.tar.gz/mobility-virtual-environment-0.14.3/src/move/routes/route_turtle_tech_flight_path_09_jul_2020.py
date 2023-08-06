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
    route.desc = "route over ocean for observing turtles during nesting season"
    
    # -------------------------------
    # specify the route coordinates:
    # -------------------------------
    # the lines below were copy-pasted directly from this .csv: fort_collins_spring_canyon_park_1_lap_13_Jul_2019.csv
    # the .csv file was written by fort_collins_lap_preprocessor.m which works in Matlab or Octave
    #
    # for a series of points without commas, python has something called
    # multi-line strings that are indicates by three quotes in a row (single or double quotes)
    #

# simple small route over ocean to test laps
#27.9997722 , -80.5239734 , 18
#27.9999     , -80.5231499 , 18
#27.9995432 , -80.523  , 18
#27.9993682 , -80.5237531 , 18


    # format: lat,lon,speed (m/s)
    my_multi_line_string_of_lat_lon_points = """
27.9997722 , -80.5239734 , 18
28.0043691 , -80.5231499 , 18
28.0046389 , -80.5231499 , 18
28.0071473 , -80.5231499 , 18
28.0074171 , -80.5231499 , 18
28.0076285 , -80.5224688 , 18
28.0073587 , -80.5224688 , 18
28.0033233 , -80.5224689 , 18
28.0030535 , -80.5224689 , 18
28.0017379 , -80.5217878 , 18
28.0020077 , -80.5217878 , 18
28.0075702 , -80.5217877 , 18
28.0078399 , -80.5217877 , 18
28.0080514 , -80.5211065 , 18
28.0077816 , -80.5211066 , 18
28.0006921 , -80.5211068 , 18
28.0004224 , -80.5211068 , 18
27.9991068 , -80.5204257 , 18
27.9993766 , -80.5204257 , 18
28.007993 , -80.5204254 , 18
28.0082628 , -80.5204254 , 18
28.0084742 , -80.5197443 , 18
28.0082044 , -80.5197443 , 18
27.998061 , -80.5197447 , 18
27.9977912 , -80.5197447 , 18
27.9964756 , -80.5190638 , 18
27.9967454 , -80.5190637 , 18
28.0084158 , -80.5190632 , 18
28.0086856 , -80.5190632 , 18
28.008897 , -80.518382 , 18
28.0086272 , -80.5183821 , 18
27.9954298 , -80.5183828 , 18
27.99516 , -80.5183828 , 18
27.9938444 , -80.5177018 , 18
27.9941142 , -80.5177018 , 18
28.0088386 , -80.5177009 , 18
28.0091084 , -80.5177009 , 18
28.0093198 , -80.5170198 , 18
28.00905 , -80.5170198 , 18
27.9927986 , -80.5170209 , 18
27.9925288 , -80.5170209 , 18
27.9912132 , -80.51634 , 18
27.991483 , -80.51634 , 18
28.0092614 , -80.5163387 , 18
28.0095312 , -80.5163386 , 18
28.0097426 , -80.5156575 , 18
28.0094728 , -80.5156575 , 18
27.9901674 , -80.5156591 , 18
27.9898976 , -80.5156591 , 18
27.9890991 , -80.5149781 , 18
27.9893689 , -80.5149781 , 18
28.0096842 , -80.5149764 , 18
28.009954 , -80.5149763 , 18
28.0101653 , -80.5142952 , 18
28.0098955 , -80.5142952 , 18
27.9895838 , -80.5142971 , 18
27.989314 , -80.5142971 , 18
27.989529 , -80.5136161 , 18
27.9897988 , -80.5136161 , 18
28.0101069 , -80.5136141 , 18
28.0103767 , -80.5136141 , 18
28.0105881 , -80.5129329 , 18
28.0103183 , -80.5129329 , 18
27.9900137 , -80.5129351 , 18
27.9897439 , -80.5129351 , 18
27.9899589 , -80.5122541 , 18
27.9902286 , -80.512254 , 18
28.0105297 , -80.5122518 , 18
28.0107995 , -80.5122517 , 18
28.0110108 , -80.5115706 , 18
28.010741 , -80.5115706 , 18
27.9904436 , -80.511573 , 18
27.9901738 , -80.511573 , 18
27.9903887 , -80.510892 , 18
27.9906585 , -80.510892 , 18
28.0109524 , -80.5108895 , 18
28.0112222 , -80.5108894 , 18
28.0109687 , -80.5102083 , 18
28.0106989 , -80.5102084 , 18
27.9908734 , -80.510211 , 18
27.9906036 , -80.510211 , 18
27.9908185 , -80.50953 , 18
27.9910883 , -80.5095299 , 18
28.0095739 , -80.5095274 , 18
28.0098437 , -80.5095274 , 18
28.0087187 , -80.5088464 , 18
28.0084489 , -80.5088464 , 18
27.9913033 , -80.5088489 , 18
27.9910335 , -80.5088489 , 18
27.9912484 , -80.5081679 , 18
27.9915182 , -80.5081678 , 18
28.0073239 , -80.5081655 , 18
28.0075937 , -80.5081654 , 18
28.0064687 , -80.5074845 , 18
28.0061989 , -80.5074845 , 18
27.9917331 , -80.5074868 , 18
27.9914633 , -80.5074868 , 18
27.9916782 , -80.5068058 , 18
27.991948 , -80.5068057 , 18
28.0050738 , -80.5068036 , 18
28.0053436 , -80.5068036 , 18
28.0042186 , -80.5061227 , 18
28.0039488 , -80.5061227 , 18
27.9921629 , -80.5061247 , 18
27.9918931 , -80.5061247 , 18
27.992108 , -80.5054437 , 18
27.9923778 , -80.5054436 , 18
28.0028238 , -80.5054418 , 18
28.0030936 , -80.5054418 , 18
28.0019686 , -80.5047609 , 18
28.0016988 , -80.5047609 , 18
27.9925927 , -80.5047626 , 18
27.9923229 , -80.5047626 , 18
27.9925378 , -80.5040816 , 18
27.9928076 , -80.5040815 , 18
28.0005737 , -80.5040801 , 18
28.0008435 , -80.50408 , 18
27.9997185 , -80.5033992 , 18
27.9994487 , -80.5033992 , 18
27.9930225 , -80.5034005 , 18
27.9927527 , -80.5034005 , 18
27.9929676 , -80.5027195 , 18
27.9932373 , -80.5027194 , 18
27.9983236 , -80.5027184 , 18
27.9985934 , -80.5027183 , 18
27.9974684 , -80.5020375 , 18
27.9971986 , -80.5020376 , 18
27.9934522 , -80.5020383 , 18
27.9931824 , -80.5020384 , 18
27.9933973 , -80.5013573 , 18
27.9936671 , -80.5013573 , 18
27.9960735 , -80.5013568 , 18
27.9963433 , -80.5013567 , 18
27.9952183 , -80.5006759 , 18
27.9949485 , -80.500676 , 18
27.993882 , -80.5006762 , 18
27.9936122 , -80.5006763 , 18
27.9964432 , -80.5211128 , 18
27.9993682 , -80.5237531 , 18
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
    route.spd_mps = spd_mps # (m/s)
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

    
    



























