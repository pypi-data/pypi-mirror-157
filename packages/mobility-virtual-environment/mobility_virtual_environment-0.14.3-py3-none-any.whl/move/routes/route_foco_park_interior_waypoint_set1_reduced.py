#!/usr/bin/python3
#
# restore waypoints for COUNTER-CLOCKWISE interior lap 1 in Spring Canyon Park in Fort Collins Colorado
#
# usage:
#    ./route_foco_park_interior_waypoint_set1_reduced.py
#
#
# Marc Compere, comperem@gmail.com
# created : 14 Jul 2019
# modified: 17 Jul 2019
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
    route.desc = "route foco, CCW interior lap 1 in Spring Canyon Park in Ft. Collins Colorado from lat/lon recorded in SensorLog iPhone app"
    
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
40.5436068105,-105.1274429745,0.2025213000
40.5436112479,-105.1274434942,0.1168217000
40.5436118690,-105.1274408554,0.0588861900
40.5436140018,-105.1274365191,0.0791101800
40.5436135439,-105.1274278310,0.0737596500
40.5436139529,-105.1274264527,0.0602379200
40.5436143609,-105.1274268417,0.2847727000
40.5436141729,-105.1274259124,0.2847727000
40.5436067773,-105.1274250461,0.7197464000
40.5435984441,-105.1274140781,1.8218280000
40.5435758714,-105.1273683006,1.6005500000
40.5435651753,-105.1273522227,2.9258080000
40.5435570467,-105.1273108836,3.3348390000
40.5435224256,-105.1272237104,3.6637500000
40.5434851240,-105.1271807920,2.8284220000
40.5434544155,-105.1269959682,2.6662870000
40.5434457612,-105.1269667933,3.1364840000
40.5434249240,-105.1269358013,3.2741060000
40.5433716463,-105.1268993769,3.0809550000
40.5433528640,-105.1268769187,3.0152270000
40.5432668898,-105.1267471687,2.7607920000
40.5432426652,-105.1267291828,2.7607920000
40.5432111085,-105.1267223836,2.8082660000
40.5431627068,-105.1267007502,2.9703990000
40.5430927106,-105.1266357489,3.1967570000
40.5430785306,-105.1266168258,2.7136230000
40.5430798191,-105.1265856157,2.8691730000
40.5431018974,-105.1264569228,2.9595110000
40.5431010581,-105.1264285705,2.8652390000
40.5430937813,-105.1263922702,3.0108100000
40.5430642141,-105.1263476788,3.0108100000
40.5429930766,-105.1262964453,3.1958500000
40.5429642930,-105.1262916565,3.1958500000
40.5429409929,-105.1262807401,2.8519530000
40.5429208121,-105.1262634379,2.8519530000
40.5428952806,-105.1262316865,2.7981440000
40.5428800780,-105.1262000714,3.1106860000
40.5428749403,-105.1261794201,3.1106860000
40.5428764119,-105.1261381607,2.8290050000
40.5428972363,-105.1260778848,2.8893380000
40.5428911000,-105.1259057967,2.8607870000
40.5428642388,-105.1258054062,2.9531290000
40.5427885562,-105.1257230614,2.8208480000
40.5427729377,-105.1256946277,2.8208480000
40.5427516220,-105.1256709754,2.8208480000
40.5427206284,-105.1256189335,1.8874030000
40.5427060109,-105.1256093266,1.8874030000
40.5426958449,-105.1255962358,1.6283160000
40.5426787259,-105.1255548448,1.6645790000
40.5426817796,-105.1255431423,1.7261630000
40.5426757054,-105.1254574825,1.2705830000
40.5426774193,-105.1254397057,1.2348970000
40.5426990870,-105.1253662701,1.4000450000
40.5427141550,-105.1253388602,1.1535820000
40.5427355198,-105.1253136541,1.8552670000
40.5427442628,-105.1252974976,1.8552670000
40.5427903320,-105.1252604333,1.7377250000
40.5428304905,-105.1252392412,1.9016780000
40.5428566011,-105.1252360081,1.8156850000
40.5429051905,-105.1252482045,2.5526210000
40.5429949468,-105.1252797261,2.7620720000
40.5430594309,-105.1252752927,2.7620720000
40.5430867226,-105.1252658992,1.7979700000
40.5431050000,-105.1252689164,1.7979700000
40.5431187414,-105.1252747858,1.6631310000
40.5431875720,-105.1252420212,2.8582520000
40.5432928780,-105.1252287005,2.5631580000
40.5433721133,-105.1252590907,2.9710200000
40.5434046213,-105.1252904733,2.9976940000
40.5434207725,-105.1253260032,2.8939680000
40.5434382054,-105.1253508952,2.8939680000
40.5434583002,-105.1253565594,2.8939680000
40.5434919630,-105.1253574738,3.1404090000
40.5435472985,-105.1253081643,3.0664060000
40.5435714406,-105.1252999110,3.2857750000
40.5436006381,-105.1253192734,3.0664060000
40.5436181462,-105.1253470383,2.8157660000
40.5436380655,-105.1253660786,2.7187210000
40.5437073682,-105.1253826942,2.3642730000
40.5437270678,-105.1253773969,1.8055340000
40.5437456675,-105.1253842489,1.6645620000
40.5437520796,-105.1253981278,1.6947630000
40.5437728307,-105.1254149296,1.8694050000
40.5437879072,-105.1254218951,1.8694050000
40.5437996755,-105.1254307170,1.4536450000
40.5438054150,-105.1254380753,1.4443330000
40.5438173833,-105.1254371800,1.6183210000
40.5438706567,-105.1254104793,1.5599430000
40.5439232685,-105.1253679525,1.5949620000
40.5439389042,-105.1253646980,1.5729560000
40.5439814316,-105.1253796966,1.6349120000
40.5439979374,-105.1253931153,1.6349120000
40.5440135881,-105.1254115726,1.6311860000
40.5440135720,-105.1254346213,1.8576580000
40.5440053256,-105.1255633772,1.9907120000
40.5439987071,-105.1255929771,1.9748230000
40.5439928272,-105.1256361285,1.7624710000
40.5439864934,-105.1256524456,1.4279830000
40.5439906591,-105.1256586576,1.4279830000
40.5439934001,-105.1256848480,1.4067040000
40.5439933454,-105.1256989626,0.9826605000
40.5439865280,-105.1257338594,0.9945713000
40.5439868310,-105.1257470281,0.9945713000
40.5439901258,-105.1257591996,0.9369618000
40.5439895479,-105.1257763355,1.0340510000
40.5439963487,-105.1258422097,1.0788180000
40.5439751349,-105.1258991840,1.6494850000
40.5439720089,-105.1259126465,1.2560320000
40.5439685207,-105.1259600154,1.2756170000
40.5439710843,-105.1259726512,1.3183470000
40.5439742615,-105.1259795671,1.3183470000
40.5439767316,-105.1259960850,1.3183470000
40.5439890659,-105.1260293828,1.3527930000
40.5439891431,-105.1260453948,1.4325080000
40.5439696478,-105.1261005684,1.2615410000
40.5439604029,-105.1261862913,1.0370390000
40.5439697619,-105.1262114333,1.1677580000
40.5439678839,-105.1262242577,1.1677580000
40.5439738221,-105.1262834458,1.3752370000
40.5440003766,-105.1263523879,3.0324450000
40.5440253209,-105.1265370524,2.6447670000
40.5440073746,-105.1266295875,2.5655280000
40.5439954882,-105.1266542353,2.5655280000
40.5439871232,-105.1267130797,2.4422170000
40.5439906032,-105.1267414097,2.4422170000
40.5440332911,-105.1269344816,2.5666330000
40.5440366146,-105.1270076160,2.3512420000
40.5440240496,-105.1270321425,2.3512420000
40.5439954013,-105.1270546310,2.5119210000
40.5439470177,-105.1270792796,2.4893020000
40.5439300783,-105.1271010826,2.4731110000
40.5439005000,-105.1271239462,2.4731110000
40.5438833040,-105.1271525610,2.5733560000
40.5438474525,-105.1272726595,2.4082530000
40.5438359960,-105.1273274733,2.5392720000
40.5438008884,-105.1273564997,2.5218960000
40.5437771046,-105.1273692282,2.5218960000
40.5437575267,-105.1273728861,2.7590870000
40.5437374659,-105.1273874674,2.8313130000
40.5437027606,-105.1274482619,2.4357050000
40.5436833619,-105.1274684606,1.5742580000
        """
    # all math and route following must be done in orthogonal coordinates, so
    # convert these lat/lon pairs to UTM coordinates which assumes a flat Earth
    # within this UTM zone (there are 60 zones around Earth)
    
    list_of_rows = my_multi_line_string_of_lat_lon_points.split('\n')
    
    X=[] # initialize a native python list
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
            
            lat             = float( str[0] )
            lon             = float( str[1] )
            speed_single_pt = float( str[2] )
            
            # utm library converts from lat/lon in decimal degrees to orthogonal
            # XYZ coordinates in meters within a single UTM zone
            (X_single_pt,Y_single_pt,zone,latBand) = utm.from_latlon(lat,lon) # these are typically giant numbers, like (X,Y)=(489174.484, 4488110.896)
            
            # list.append() is super fast for growing native python lists dynamically
            X.append( X_single_pt ) # X_origin and Y_origin are also typically giant numbers, like 
            Y.append( Y_single_pt )
            spd_mps.append( speed_single_pt )
            cnt=cnt+1
    #print('---')
    
    X       = np.array(     X  ) # convert native python lists to numpy array objects
    Y       = np.array(     Y  )
    Z       = np.zeros( len(X) ) # (m) initialize Z with numpy array of all zeros
    spd_mps = np.array( spd_mps  ) # (m/s) commanded speed for all waypoints is from SensorLog's original GPS-based recording
    
    
    # --------------------------------------------------------------------------
    # now stuff these arrays (python lists) into the route object create at the top
    # MoVE will use this function's return 'route' object from here on out
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
    if (makePlots==True):
        multiprocessing.Process(target=plot_graph, args=(route,)).start()
        print("exiting main")
        os._exit(0) # this exits immediately with no cleanup or buffer flushing

    
    



























