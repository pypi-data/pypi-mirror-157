#!/usr/bin/python3
#
# basic circle route for MoVE located in ../routes. 
#
# generates waypoints in a circle starting at (0,0,0) for a right-hand-turn 
#
# usage:
#    ./route_01_waypoints.py
#
#
# debugging from python command prompt
#    from route_01_waypoints import restore_waypoints
#    route=restore_waypoints(1.0,2.0)
#
#
# Marc Compere, comperem@gmail.com
# created : 06 Jul 2019
# modified: 11 Jul 2019
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
import utm
import code # uncommented only during debugging; drops into a python interpreter at code.interact()

# ------------------------------------------------------------------------------
# the restore_waypoint() function gets called from MoVE vehicle model but the
# plotting code below only gets called when this is called as a stand-alone program
def restore_waypoints( cfg ):
    import numpy as np
    from routes_functions import computeRouteStatistics
    
    # make a circle
    dTheta = (2*np.pi)/20
    #theta = np.arange(0.0, 2*np.pi, dTheta) # (rad)
    theta = np.arange(np.pi, -np.pi, -dTheta) # (rad) circle for a right-hand turn
    radius = 20.0 # (m)
    
    xOffset = 0.0*radius # (m)
    yOffset = 0.0 # (m)
    
    # waypoint locations in an orthogonal, terrain-fixed XYZ frame
    X = radius*np.cos(theta) + xOffset # (m)
    Y = radius*np.sin(theta) + yOffset # (m)
    Z = np.zeros(len(X)) # (m) initialize Z with numpy array of all zeros
    spd_mps = cfg.v_max*np.ones(len(X)) # (m/s) commanded speed for all waypoints
    
    # the mathematical waypoint definition still needs to be located with lat/lon coordinates
    #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
    lat=np.zeros(len(X))
    lon=np.zeros(len(X))
    for i in range( len(X) ):
        (lat[i], lon[i]) = utm.to_latlon( X[i] + cfg.X_origin , Y[i] + cfg.Y_origin, cfg.UTM_zone, cfg.UTM_latBand ) # readConfigFile.py has populated these from the origin specified in cfg file
    
    # --------------------------------------------------------------------------
    # now stuff these arrays (python lists) into a route object for use by MoVE
    class Route:
        pass
    
    route = Route() # route is a class with (only) data attributes as members
    
    route.originalUnits = 'meters' # 'decimal_degrees'
    route.desc = "simple example circle route at constant speed"    
    
    route.lat     = lat
    route.lon     = lon
    route.X       = X # (m) X array in cartesian XYZ coordinates
    route.Y       = Y # (m) Y array in cartesian XYZ coordinates
    route.Z       = Z # (m) Z array in cartesian XYZ coordinates
    route.spd_mps = spd_mps # (m/s)
    if '__file__' in locals():
        route.source = __file__ # this file's name
    else:
        route.source = __name__ # __main__ when debugging in a terminal console
    route.desc = "route 01, circle, R={0}(m) in XYZ coords".format(radius)
    
    route = computeRouteStatistics(route)
    
    return(route) # return a Route class with data attributes
# ------------------------------------------------------------------------------





if __name__ == "__main__":
    
    import matplotlib.pyplot as plt
    import multiprocessing
    import os
    import sys
    import utm
    from routes_functions import computeRouteStatistics, plot_graph
    
    print("starting __main__")
    
    class Cfg:
        pass
    
    cfg = Cfg()
    cfg.L_char = 1.0 # (m) example vehicle's characteristic length
    cfg.v_max = 20.0 # (m/s) example vehicle's maximum speed
    
    
    # pick a place to originate these X,Y,Z waypoints (this will be in the config file)
    cfg.lat_origin =  29.190337 # (decimal deg) soccer fields, Embry-Riddle Aeronautical Univ, Daytona Beach, Florida
    cfg.lon_origin = -81.045672 # (decimal deg)
    (cfg.X_origin,cfg.Y_origin,cfg.UTM_zone,cfg.UTM_latBand) = utm.from_latlon(cfg.lat_origin,cfg.lon_origin)
    
    
    # this function is called from the vehicle model, main_veh_model.py
    route = restore_waypoints( cfg )
    
    # print full route data structure
    #for key,val in route.__dict__.items():
    #    print("{0}={1}".format(key,val))
    
    # optionally bring the plot window up in a separate process
    makePlots=True #False
    skipNthLabel=2 #1 % use 10 or 50 if waypoint labels clutter the plot
    if (makePlots==True):
        multiprocessing.Process(target=plot_graph, args=(route,skipNthLabel)).start()
        print("exiting main")
        os._exit(0) # this exits immediately with no cleanup or buffer flushing

