#!/usr/bin/python3
#
# restore waypoints for an exterior lap around Spring Canyon Park in Fort Collins Colorado
#
# usage:
#    ./route_foco_park_waypoints_reduced.py
#
#
# Marc Compere, comperem@gmail.com
# created : 14 Jul 2019
# modified: 29 Jul 2020
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
    route.desc = "route foco, an exterior lap around Spring Canyon Park in Ft. Collins Colorado from lat/lon recorded in SensorLog iPhone app"
    
    # -------------------------------
    # specify the route coordinates:
    # -------------------------------
    # the lines below were copy-pasted directly from this .csv: fort_collins_spring_canyon_park_reduced_1_lap_13_Jul_2019.csv
    # the .csv file was written by fort_collins_lap_preprocessor.m which works in Matlab or Octave
    #
    # for a series of points without commas, python has something called
    # multi-line strings that are indicates by three quotes in a row (single or double quotes)
    #
    # format: lat,lon,speed (m/s)
    my_multi_line_string_of_lat_lon_points = """
40.5436783987,-105.1278419687,0.0350459000
40.5436660399,-105.1278686310,1.7443240000
40.5436617903,-105.1279056417,3.3288410000
40.5436395053,-105.1279445296,3.3288410000
40.5435858368,-105.1280095309,3.0670290000
40.5435541516,-105.1280299657,2.8681230000
40.5435326577,-105.1280538892,2.9069180000
40.5434935884,-105.1280756104,2.7256840000
40.5434451257,-105.1280847652,2.4186960000
40.5434294897,-105.1280749925,2.7368760000
40.5434031619,-105.1280737746,2.7322630000
40.5433865279,-105.1280817501,2.7368760000
40.5433592528,-105.1280879513,2.7733500000
40.5433403804,-105.1280839757,3.0075980000
40.5432389382,-105.1281163178,3.2295710000
40.5432069255,-105.1281404857,4.4701480000
40.5431817834,-105.1281901554,4.6740610000
40.5430734243,-105.1283214909,5.0531130000
40.5430451323,-105.1283737726,5.6016570000
40.5430055855,-105.1284234062,5.8110460000
40.5429575856,-105.1284613151,5.8110460000
40.5429095113,-105.1284842406,6.0140960000
40.5427838076,-105.1284657151,6.4721260000
40.5426639714,-105.1284884819,6.3275350000
40.5426124926,-105.1285110487,6.1309270000
40.5425195647,-105.1285896762,5.6701600000
40.5424709237,-105.1287043639,5.5662140000
40.5424473697,-105.1288266319,5.1699800000
40.5423660320,-105.1288785269,5.4365840000
40.5423134648,-105.1288558922,6.3213270000
40.5422144198,-105.1287581129,6.6291090000
40.5421006456,-105.1285492693,7.0073900000
40.5420661917,-105.1284649617,7.6105550000
40.5420461819,-105.1279589590,8.4278840000
40.5420918572,-105.1276513871,8.1973890000
40.5421618067,-105.1273942896,8.2027120000
40.5421746593,-105.1271010349,8.0709830000
40.5421350943,-105.1269087545,8.3154440000
40.5420187312,-105.1266440825,8.5632090000
40.5418574183,-105.1264273867,8.5403050000
40.5414889018,-105.1261097567,7.7276700000
40.5413934546,-105.1259749293,7.7276700000
40.5412883178,-105.1257568311,7.0927470000
40.5412935899,-105.1257292412,4.0691740000
40.5413252470,-105.1256412569,3.8594660000
40.5413671131,-105.1254447666,3.6465520000
40.5413839075,-105.1253969192,2.4840990000
40.5413765098,-105.1253747198,2.4840990000
40.5413761902,-105.1253676525,1.8524470000
40.5413974331,-105.1253570388,0.7851635000
40.5414230317,-105.1253281626,0.7851635000
40.5414765098,-105.1252878523,5.3017140000
40.5415838701,-105.1250899490,5.0029040000
40.5416685817,-105.1250168419,5.0029040000
40.5416824507,-105.1250134117,2.4090570000
40.5416952148,-105.1250025271,3.0925160000
40.5417195968,-105.1249693544,2.6431210000
40.5417374134,-105.1249534791,2.6431210000
40.5417585080,-105.1249561614,2.6187100000
40.5417888966,-105.1249678201,4.0494480000
40.5418206662,-105.1250068042,4.0916300000
40.5420080554,-105.1250997686,4.8181260000
40.5420369584,-105.1251433072,4.8181260000
40.5423122265,-105.1252404337,6.9191070000
40.5426090104,-105.1252758252,8.4465180000
40.5430781964,-105.1251692772,8.7754580000
40.5433865559,-105.1252017929,8.5712870000
40.5439593861,-105.1253308778,7.9657160000
40.5443730014,-105.1253266271,7.8388860000
40.5452150626,-105.1251078853,5.1438090000
40.5452583074,-105.1251115514,5.1288260000
40.5454208886,-105.1252008192,4.7751890000
40.5454783275,-105.1252811344,5.3740900000
40.5455073014,-105.1253329415,5.3740900000
40.5455284706,-105.1254079272,5.4987550000
40.5455532544,-105.1256856310,5.5954200000
40.5455483734,-105.1257506555,5.2005000000
40.5454668078,-105.1260077378,5.6442450000
40.5453047364,-105.1261642018,4.9876400000
40.5452190706,-105.1262366280,5.1976100000
40.5451471843,-105.1263283190,5.3958910000
40.5451150910,-105.1263902228,5.6597900000
40.5450196843,-105.1268182565,5.1247170000
40.5450019760,-105.1270623804,5.1175570000
40.5450064292,-105.1271971252,5.1812950000
40.5449988951,-105.1273274337,5.0350020000
40.5449435400,-105.1274249557,5.0350020000
40.5448607490,-105.1275023910,5.0199860000
40.5447753994,-105.1275429820,5.0574540000
40.5446655997,-105.1275431813,5.3856740000
40.5443099855,-105.1274105941,5.2518480000
40.5442647483,-105.1274102600,4.9694620000
40.5442160726,-105.1274424992,5.0108830000
40.5439579327,-105.1275469911,4.6328280000
40.5437597305,-105.1277295312,3.6063190000
40.5437077598,-105.1277562536,2.9234450000
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
    skipNthLabel=4
    if (makePlots==True):
        multiprocessing.Process(target=plot_graph, args=(route,skipNthLabel)).start()
        print("exiting main")
        os._exit(0) # this exits immediately with no cleanup or buffer flushing




























