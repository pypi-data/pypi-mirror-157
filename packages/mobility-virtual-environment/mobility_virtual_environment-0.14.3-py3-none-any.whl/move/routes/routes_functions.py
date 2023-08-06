# routes_functions.py - helper functions for plotting and computing route statistics
#
# intended calling functions are main_veh_model.py and each route definition
# file (e.g. route_01_waypoint.py)
#
# Marc Compere, comperem@gmail.com
# created : 13 Jul 2019
# modified: 30 Jul 2019
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

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-14s) %(message)s',
)

# compute some statistics about the route - for interest and also debugging
def computeRouteStatistics(route):
    import sys
    import numpy as np
    
    MAX_FLOAT=sys.float_info.max
    fcn_name = sys._getframe().f_code.co_name # bizarre python from stackoverflow to report currently executing function name
        
    route.N = len(route.X)
    if ( not (route.N==len(route.Y)) and (route.N==len(route.Z)) ):
        logging.debug('\t{0}() error - all lengths must be equal for a valid route! '.format( fcn_name, route.N ))
        logging.debug('\t{0}() error - len(route.X)={1}, len(route.Y)={2}, len(route.Z)={3}'.format( fcn_name, route.N, len(route.Y), len(route.Z) ))
        logging.debug('\t{0}() exiting'.format( fcn_name ))
        exit(-1)
        
    # compute path length
    S = [0]           # (m) path length, initialize a native python list for append speed (native python list.append() is 100x faster than numpy.append())
    lenTot = 0.0      # (m)
    dSmin = MAX_FLOAT # (m) minimum segment length (note: if this becomes small (like 1e-100) the path has repeated waypoints)
    dSmax = 0.0       # (m) max segment length (note: if this becomes large, like 1e6, the path may have errors or may need to be offset by a UTM origin)
    for i in range(1,route.N):
        dX = route.X[i] - route.X[i-1]
        dY = route.Y[i] - route.Y[i-1]
        dZ = route.Z[i] - route.Z[i-1]        
        dS = np.sqrt( pow(dX,2) + pow(dY,2) + pow(dZ,2) ) # (m) segment length from waypoint i to (i+1)
        #logging.debug('i={0}, dS={1}'.format(i,dS))
        if dS<dSmin: dSmin=dS # capture minumum segment length
        if dS>dSmax: dSmax=dS # capture maximum segment length
        lenTot = lenTot + dS # (m) accumulate total path length as a scalar
        S.append(lenTot) # (m) tack on the most recent path length
    S = np.array(S) # convert to numpy array once dynamic sizing is complete
    
    route.S=S
    route.dist=S[-1] # (m) route distance
    route.dSmin = dSmin # (m) smallest of all route segments
    route.dSmax = dSmax # (m) largest of all route segments
    
    # print waypoints as a sequence of [X,Y,Z] points with distance and speed commands
    for i in range(route.N):
        logging.debug('\ti={0:<4}, (X,Y,Z) = ( {1:8.3f}, {2:8.3f}, {3:8.3f} )(m),  dist={4:8.1f}(m),   spd_mps={5:6.1f}(m/s)'.format( i,route.X[i],route.Y[i],route.Z[i],route.S[i],route.spd_mps[i] ))
    
    logging.debug('')
    logging.debug('\t{0}() route.source        : [{1}]'.format( fcn_name, route.source ))
    logging.debug('\t{0}() route.originalUnits : [{1}]'.format( fcn_name, route.originalUnits ))
    logging.debug('\t{0}() route.desc          : [{1}]'.format( fcn_name, route.desc ))
    logging.debug('\t{0}() route.N             : [{1}] (waypoints)'.format( fcn_name, route.N ))
    logging.debug('\t{0}() route.dist          : [{1:0.3f}] (m)'.format( fcn_name, route.dist )) # negative indices count from the end
    logging.debug('\t{0}() segment min         : [{1:0.3f}] (m)'.format( fcn_name, route.dSmin ))
    logging.debug('\t{0}() segment max         : [{1:0.3f}] (m)'.format( fcn_name, route.dSmax ))
    logging.debug('')
    
    return(route)
    




def plot_graph(route,skipNthLabel=1):
    import matplotlib.pyplot as plt
    
    print("entered plot_graph()")
    
    # UTM coordinates converted from lat/lon pairs are frequently large
    # floating point numbers that obscure detail in the smaller decmial places.
    if hasattr(route,'originalUnits') and route.originalUnits == 'decimal_degrees':
        print('\t\tnote: plotting with simple origin defined from first waypoint')
        print('\t\t      this provides perspective on route geometry')
        print('\t\t      but is not the same origin as specified in the scenario config file')
        X_tmp_origin_for_plotting_only=route.X[0] # (m)
        Y_tmp_origin_for_plotting_only=route.Y[0] # (m)
    else:
        X_tmp_origin_for_plotting_only=0.0 # (m)
        Y_tmp_origin_for_plotting_only=0.0 # (m)
    
    fig, ax = plt.subplots()
    ax.plot(route.X-X_tmp_origin_for_plotting_only, route.Y-Y_tmp_origin_for_plotting_only, '.-')
    
    plotWaypointLabels = True #False
    if plotWaypointLabels is True:
        start=0
        stop=route.N
        #skipNthLabel=10 #1 % use 10 or 50 if waypoint labels clutter the plot
        for i in range( start,stop,skipNthLabel ):
            #print('x={0}'.format(x[i]))
            plt.text(route.X[i]-X_tmp_origin_for_plotting_only, route.Y[i]-Y_tmp_origin_for_plotting_only, str(i+1), fontsize=12, horizontalalignment='center', verticalalignment='bottom') # verticalalignment: 'top', 'center', 'bottom' or 'baseline'
    
    ax.set(xlabel='x-axis (m)', ylabel='y-axis (m)', title='{0}'.format(route.desc))
    ax.grid()
    ax.axis('equal')
    
    #fig.savefig("test.png")
    plt.show() # this will block and remain a viable process as long as the figure window is open
    print("exiting plot_graph() process")



