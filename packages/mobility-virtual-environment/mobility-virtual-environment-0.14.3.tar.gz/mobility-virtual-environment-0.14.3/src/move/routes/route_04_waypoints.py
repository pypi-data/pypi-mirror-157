#!/usr/bin/python3
#
# restore waypoints for an ugly figure 8. 
#
# usage:
#    ./route_04_waypoints.py
#
#
# debugging from python command prompt
#    from route_04_waypoints import restore_waypoints
#    route=restore_waypoints(1.0,2.0)
#
# Marc Compere, comperem@gmail.com
# created : 06 Jul 2019
# modified: 13 Jul 2019
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
def restore_waypoints( L_char, v_max ):
    import numpy as np
    from routes_functions import computeRouteStatistics
    
    # an ugly figure 8
    
    # waypoints are in an orthogonal, terrain-fixed XYZ frame
    
    # for a series of points without commas, python has something called
    # multi-line strings that are indicates by three quotes in a row (single or double quotes)
    my_multi_line_string_of_XY_points = """
     -2.4122217e+000	  3.5527137e-015	
      2.4986147e+000	 -1.0448588e-001	
      7.7229088e+000	  7.3140118e-001	
      1.1275429e+001	 -1.5672882e+000	
      1.3469632e+001	 -3.8659776e+000	
      1.5141406e+001	 -5.4332659e+000	
      1.8380469e+001	 -7.4184976e+000	
      2.1306074e+001	 -8.5678423e+000	
      2.6321396e+001	 -8.9857859e+000	
      2.8097656e+001	 -8.1498988e+000	
      2.9769430e+001	 -6.4781247e+000	
      3.2068119e+001	 -3.5525200e+000	
      3.2590549e+001	 -1.0448588e+000	
      3.4157837e+001	  1.6717741e+000	
      3.5725125e+001	  4.3884071e+000	
      3.9068674e+001	  6.8960682e+000	
      4.3248109e+001	  6.8960682e+000	
      4.4606425e+001	  5.2242941e+000	
      4.5651284e+001	  1.8807459e+000	
      4.6173713e+001	 -2.2986894e+000	
      4.5337826e+001	 -6.3736388e+000	
      4.3770538e+001	 -8.4633565e+000	
      4.0426990e+001	 -8.6723282e+000	
      3.8023815e+001	 -6.2691529e+000	
      3.6769984e+001	 -4.2839212e+000	
      3.5934097e+001	 -2.2986894e+000	
      3.5307182e+001	 -4.1794353e-001	
      3.4575781e+001	  1.2538306e+000	
      3.2904006e+001	  4.4928929e+000	
      3.0396345e+001	  6.1646671e+000	
      2.6948311e+001	  7.0005541e+000	
      2.4231678e+001	  6.5826106e+000	
      2.2350932e+001	  4.4928929e+000	
      2.0470186e+001	  2.6121471e+000	
      1.8693926e+001	  1.1493447e+000	
      1.6499723e+001	 -6.2691529e-001	
      1.3992062e+001	 -2.0897176e+000	
      1.1693372e+001	 -3.4480341e+000	
      9.3946830e+000	 -4.9108365e+000	
      7.0959935e+000	 -7	
      -1            	 -16.5	
      -5.1          	 -16	
      -6.2          	 -14
        """
    
    list_of_rows = my_multi_line_string_of_XY_points.split('\n')
    
    X=[] # initialize a native python list
    Y=[]
    #print('---')
    for row in list_of_rows:
        #print(row)
        if row.strip() != '': # strip() removes leading and trailing whitespace
            #print( repr(row) ) # repr() shows invisible characters to distinguish spaces from tabs and newlines
            str=row.strip().split("\t")
            print(str)
            X.append( float( str[0] ) ) # list.append() is super fast for growing native python lists dynamically
            Y.append( float( str[1] ) )
    #print('---')
    
    X = np.array( X ) # convert native python lists to numpy array objects
    Y = np.array( Y )
    Z = np.zeros(len(X)) # (m) initialize Z with numpy array of all zeros
    speed = 0.2*v_max*np.ones(len(X)) # (m/s) commanded speed for all waypoints
    
    
    # --------------------------------------------------------------------------
    # now stuff these arrays (python lists) into a route object for use by MoVE
    class Route:
        pass
    
    route = Route()
    
    route.X = X # (m) X array in cartesian XYZ coordinates
    route.Y = Y # (m) Y array in cartesian XYZ coordinates
    route.Z = Z # (m) Z array in cartesian XYZ coordinates
    route.speed = speed # (m/s)
    if '__file__' in locals():
        route.source = __file__ # this file's name
    else:
        route.source = __name__ # __main__ when debugging in a terminal console
    route.desc = "route 04, an ugly figure 8 in XYZ coords"
    
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
    
    L_char = 1.0 # (m) example vehicle's characteristic length
    v_max = 20.0 # (m/s) example vehicle's maximum speed    
    
    # this function is called from the vehicle model, main_veh_model.py
    route = restore_waypoints( L_char, v_max )
    
    # print full route data structure
    #for key,val in route.__dict__.items():
    #    print("{0}={1}".format(key,val))
    
    # optionally bring the plot window up in a separate process
    makePlots=True #False
    if (makePlots==True):
        multiprocessing.Process(target=plot_graph, args=(route,)).start()
        print("exiting main")
        os._exit(0) # this exits immediately with no cleanup or buffer flushing

    
    



























