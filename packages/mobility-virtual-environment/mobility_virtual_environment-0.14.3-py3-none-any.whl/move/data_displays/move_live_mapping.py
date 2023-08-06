# The MoVE live mapping data display uses Bokeh visualization library to display
# multiple real or simulated vehicles on a satellite imagery basemap.
# This illustrates motion of all vehicles and pedestrians in the MoVE scenario
# on a 2D, top-down map view with terrain overlays.
#
# This is a 'bokeh serve' script and not intended as a stand-alone python program.
#
#
# The simplest way to run *locally* is the bash shell script in Linux
# with:
#     ./run_move_live_mapping.sh -f ../scenario/default.cfg
#
# or at a command line from ./move/data_displays directory:
#    bokeh serve --show --port=5007 move_live_mapping.py --args -f ../scenario/default.cfg
#
#
# But to serve Bokeh on a machine at 68.204.225.63 over the web, perhaps in a screen session:
#
#    bokeh serve --allow-websocket-origin=68.204.225.63:5007  move_live_mapping.py --args -f ../scenario/default.cfg
#
# then open this link:
#    http://68.204.225.63:5007/move_live_mapping
#
#
# Garrett Holden, gholden3510@gmail.com
# Marc Compere, comperem@gmail.com
# created : 15 Nov 2018
# modified: 04 Jul 2022
#
# ---
# Copyright 2018 - 2022 Marc Compere
#
# This file is part of the Mobility Virtual Environment (MoVE).
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
# ---


import os
import sys
import time
import random
import socket, traceback
import struct
import utm

import imutils # rotate_bound()
import numpy as np
import msgpack
from bokeh.io import output_file, show
from bokeh.models.widgets import Slider, Div
from bokeh.models.ranges import DataRange1d
from bokeh.models import Range1d
from bokeh.layouts import column, layout
from bokeh.models import Button, Title, LabelSet, WheelZoomTool, HoverTool
from bokeh.plotting import ColumnDataSource, figure, curdoc, output_file, show
from bokeh.colors import RGB
from bokeh.tile_providers import get_provider, Vendors
from collections  import deque
import cv2 # imread()
import imutils # rotate_bound()

import logging
from threading import Thread, Event
from queue import Queue
from datetime import datetime
from math import sin,cos,atan2
import numpy as np # for geofence bounding box only
sys.path.append(os.path.relpath("../scenario")) # this provides visibility to ../scenario/readConfigFile.py w/o a linux file system symbolic link
from readConfigFile import readConfigFile

# --- for importing route_init() ---
import os
import sys
#sys.path.append(os.path.relpath("./veh_model")) # this allows my_cool_module.py (in dir1) to be found by an import in dir2
sys.path.append(os.path.relpath("../veh_model")) # this allows my_cool_module.py (in dir1) to be found by an import in dir2
from route_init import route_init
# --- --- --- --- --- --- --- --- ---


import code # drop into a python interpreter to debug using: code.interact(local=locals())

print('--- entering {0} ---'.format(sys.argv[0]))

print("sys.argv=",sys.argv)

n=len(sys.argv)
if n==3 and sys.argv[1]=='-f':
    pwd     = os.getcwd()
    #print('pwd={0}'.format(pwd))
    cfgFile = sys.argv[2] # run_move_live_mapping.sh provides an absolute config file location
    print('reading scenario config file: {}'.format(cfgFile))
    #cfgFile = '../scenario/default.cfg' # python's .ini format config file
    #cfgFile = '../scenario/point_homerun.cfg'
    print('cfgFile={}'.format(cfgFile))
    cfg, veh_names_builtins, veh_names_live_gps = readConfigFile( cfgFile, -1 )
    
else:
    print('\n')
    print('\t usage  :    bokeh serve --show move_live_mapping.py --args -f ../scenario/config.cfg\n')
    print('\t example:    bokeh serve --show move_live_mapping.py --args -f ../scenario/default.cfg\n')
    sys.exit(0)


debug=1 # (0/1/2/3) 0->none, 1->some, 2->more, 3->lots


# helper function for coordinate conversion between lat/lon in decimal degrees to Web Mercator for plotting
# modified from lnglat_to_meters() by @jbednar (James A. Bednar)
# https://github.com/bokeh/bokeh/issues/10009#issuecomment-628982394
def LatLon_to_EN(latitude , longitude):
    """
    Projects the given (latitude, longitude) values into Web Mercator
    coordinates (meters East of Greenwich and meters North of the Equator).
    
    Longitude and latitude can be provided as scalars, Pandas columns,
    or Numpy arrays, and will be returned in the same form.  Lists
    or tuples will be converted to Numpy arrays.
    
    Examples:
       easting, northing = lnglat_to_meters(-74,40.71)
       
       easting, northing = lnglat_to_meters(np.array([-74]),np.array([40.71]))
       
       df=pandas.DataFrame(dict(longitude=np.array([-74]),latitude=np.array([40.71])))
       df.loc[:, 'longitude'], df.loc[:, 'latitude'] = lnglat_to_meters(df.longitude,df.latitude)
    """
    if isinstance(longitude, (list, tuple)):
        longitude = np.array(longitude)
    if isinstance(latitude, (list, tuple)):
        latitude = np.array(latitude)
        
    origin_shift = np.pi * 6378137
    easting = longitude * origin_shift / 180.0
    northing = np.log(np.tan((90 + latitude) * np.pi / 360.0)) * origin_shift / np.pi
    return (easting, northing)





# simple item index search in a list
def myFindItem(myList,searchItem):
    try:
        idx=myList.index(searchItem)
    except ValueError:
        idx=None
        #print('{0}(): {1} not found in list'.format( myFindItem.__name__ ,searchItem))
    return(idx)

# return a signed angle bound on the interval [-pi  +pi]
def wrap(a): 
    sa=sin(a)
    ca=cos(a)
    return ( atan2(sa,ca) )



TOOLTIPS_VEH = [
    ("vehicle id"           , "@vid"),
    ("vehicle name"         , "@vehName"),
    ("vehicle type"         , "@vehType"),
    ("veh sub type"         , "@vehSubType"),
    ("behavior name"        , "@bIdName"),
    ("speed (m/s)"          , "@spd_mps"),
    ("heading (deg)"        , "@heading_deg"),
    ("(lat,lon)"            , "(@lat, @lon)"),
    ("(X,Y) (m)"            , "(@posX, @posY)"),
    ("elev (m)"             , "(@posZ)"),
    ("last core update"     , "@updateTime"),
    ("GPS time"             , "@gps_unixTime"),
    ("runState"             , "@runState"),
    ("goto waypt or gate"   , "@waypoint"), # waypoint or gate index
    ("behavior progress"    , "@bIdProgress"),
    ("lap num"              , "@lap")
    #("(Easting,Northing)" , "($x, $y)"),
]


# x_axis_type, y_axis_type may be: "linear", "log", "datetime", "mercator"
#plot = figure(x_range=(SW_corner_EN[0], NE_corner_EN[0]), y_range=(SW_corner_EN[1], NE_corner_EN[1]),
plot = figure(x_axis_type="mercator", y_axis_type="mercator",
              tools="pan,wheel_zoom,save,reset,crosshair",
              sizing_mode='stretch_both',
              x_range=Range1d(0,0),y_range=Range1d(0,0)) # use Range1d()'s to prevent axes auto-scaling
              #tooltips=TOOLTIPS_VEH,


plot.title.text  = "Mobility Virtual Environment Map View"
plot.title.align = "center"
plot.title.text_color = "blue"
plot.title.text_font_size = "25px"
#plot.title.background_fill_color = "lightgray"
plot.toolbar.active_scroll = plot.select_one(WheelZoomTool) # make wheel_zoom tool active by default; from https://discourse.bokeh.org/t/wheelzoom-active-by-default-not-working/2509

# assign axes min and max
range_padding=400 # (m) in web mercator coordinates
print('Assigning map center with (Easting,Northing) extents of +/-{0} meters'.format(range_padding))
(Easting, Northing) = LatLon_to_EN( cfg.lat_origin, cfg.lon_origin )

Xmin=Easting-range_padding  # (m) in web mercator map projection units
Xmax=Easting+range_padding  # (m)
Ymin=Northing-range_padding # (m)
Ymax=Northing+range_padding # (m)
#plot.circle(x='easting', y='northing', size=15, fill_alpha=0.8, source=source)
#plot.image_rgba(image='image', x='easting', y='northing', dw='dw', dh='dh', source=source) #, x_range=[Xmin,Xmax],y_range=[Ymin,Ymax])
plot.x_range.start = Xmin # prevent auto-scaling by assigning a Range1d() at initialization then assign extents (here) when you know them
plot.x_range.end   = Xmax
plot.y_range.start = Ymin
plot.y_range.end   = Ymax
print("----- Xmin,Xmax=({0},{1}) , Ymin,Ymax=({2},{3})".format(Xmin,Xmax,Ymin,Ymax))




# https://docs.bokeh.org/en/latest/docs/reference/models/annotations.html
title2 = Title(text="locations: SIMULATED", text_color="red", align="center")
plot.add_layout(title2, "above")


# -------------------- text box with a LabelSet() object ------------------------
# text box on map graphic shows: [Sun Jul 18 15:35:49 2021] received updates for 5 vids: [100, 101, 102, 103, 104]
# LabelSet() object is an annotation: https://docs.bokeh.org/en/latest/docs/reference/models/annotations.html
# Bokeh's allowable color strings: https://docs.bokeh.org/en/latest/docs/reference/colors.html
nLines=4 # max number of lines
text_str = ['{0}'.format(line) for line in range(nLines)] # init with empty strings
x_scr_lo=20; x_scr_hi=67
label_data = ColumnDataSource(data=dict(x=[x_scr_lo]*nLines, y=np.linspace(x_scr_lo,x_scr_hi,nLines), text=text_str))
plot_label = LabelSet(x='x', y='y', text='text',
              text_font_size='11pt', background_fill_color='lightskyblue',
              x_units='screen', y_units='screen',
              background_fill_alpha=0.2, text_color='blue', source=label_data)
plot.add_layout(plot_label)



#set source dictionary for mapping vehicle objects with the basemap
veh_data = dict(    vid          = [],
                    vehName      = [],
                    vehType      = [],
                    vehSubType   = [],
                    gps_unixTime = [],
                    updateTime   = [],
                    runState     = [],
                    bIdName      = [],
                    bIdProgress  = [],
                    t            = [],
                    posX         = [],
                    posY         = [],
                    posZ         = [],
                    lat          = [],
                    lon          = [],
                    heading_deg  = [],
                    spd_mps      = [],
                    #batt_stat    = [],
                    image_orig   = [],
                    image        = [],
                    dh           = [],
                    dw           = [],
                    easting      = [],
                    northing     = [],
                    waypoint     = [],
                    lap          = [],
                    easting_img  = [],
                    northing_img = [] )

# initialize the source.data dictionary:
source = ColumnDataSource(   data=veh_data   ) # init with two dictionaries with all empty fields
ds_new = dict(source.data) # make shallow copy of current table data

# --------- image icon Zoom scaling ------------------
myXrange_o = plot.x_range.end - plot.x_range.start
# scale icon images when zoom changes
def zoom_callback(attr,new,old):
    global zoom_scale
    global myXrange_o
    myXrange = plot.x_range.end - plot.x_range.start
    #print('myXrange_o={0}. myXrange={1}'.format(myXrange_o,myXrange))
    if myXrange_o==0: myXrange_o=myXrange
    zoom_scale = 1.1*myXrange/myXrange_o
    if zoom_scale<0.1: zoom_scale=0.1
    if zoom_scale>4.0 : zoom_scale=4.0
    print('zoom_scale={0}, myXrange_o={1}, myXrange={2}'.format(zoom_scale,myXrange_o,myXrange))    
plot.x_range.on_change('end', zoom_callback)
zoom_scale=1.0 # initial zoom scaling factor




uptime_bar  = Div(background='lightskyblue' , width=1000, text="", render_as_text=True)
udp_update_str = 'init' # initialize update string so udp_listener_thread() and periodic_callback_update_browser() see it

# -----------------------------------------------------------------
#                          bring in the basemap
# -----------------------------------------------------------------
# open-source map tile providers for a basemap:
# - OSM, or OpenStreetMap, open-source, editable maps database
# - ESRI, or Environmental Systems Research Institute's open-source map data
#tile_provider = get_provider(Vendors.OSM) # a good map with labels, roads, and features
#tile_provider = get_provider(Vendors.WIKIMEDIA) # similar to OSM, slightly different coloring
tile_provider = get_provider(Vendors.ESRI_IMAGERY) # satellite imagery
plot.add_tile(tile_provider)


# add vehicle graphics objects *after* tile provider to keep vehicles visible on top of the map
r_veh=plot.image_rgba(image='image', x='easting_img', y='northing_img', dw='dw', dh='dh',source=source)
h_veh = HoverTool(renderers=[r_veh], tooltips=TOOLTIPS_VEH)
plot.add_tools(h_veh)

# notes:
# - latitude is a North-South coordinate
# - longitude is an East-West coordinate
# - Web Mercator is a global mapping with no useful units (not meters or feet)


# -------------- make bounding box line --------------
EN = LatLon_to_EN(cfg.lat_origin,cfg.lon_origin) # (lat,lon) to web mercator

# the next 5 lines convert boundary dimensions from UTM to (lat,lon) to web mercator
(X_origin,Y_origin,zone_num,zone_letter)=utm.from_latlon(cfg.lat_origin,cfg.lon_origin) # (lat,lon) to utm for origin's zone_num and zone_letter
(lat_upper,lon_upper) = utm.to_latlon( (X_origin+cfg.boundary_Xmax) , (Y_origin+cfg.boundary_Ymax) , zone_num, zone_letter)
(lat_lower,lon_lower) = utm.to_latlon( (X_origin+cfg.boundary_Xmin) , (Y_origin+cfg.boundary_Ymin) , zone_num, zone_letter)
EN_upper = LatLon_to_EN(lat_upper,lon_upper) # (lat,lon) to web mercator
EN_lower = LatLon_to_EN(lat_lower,lon_lower) # (lat,lon) to web mercator

X_line1 = np.array([EN_lower[0], EN_lower[0], EN_upper[0], EN_upper[0], EN_lower[0]]) # (m) easting offset
Y_line1 = np.array([EN_lower[1], EN_upper[1], EN_upper[1], EN_lower[1], EN_lower[1]]) # (m) northing offset
#print('(a) X_line1={0}'.format(X_line1))
#print('(a) Y_line1={0}'.format(Y_line1))

plot.line(X_line1, Y_line1, line_width=2, color="yellow")



# -------------- make lines for route waypoints --------------
if hasattr(cfg,'veh_routes') and (len(cfg.veh_routes)>0): # and False:
    #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
    # ----------------------------- route init ---------------------------------
    # plot all waypoints for each vehicle configured to followRoute() on a route
    for k,v in cfg.veh_routes.items():
        cfg.vid=int( k.split('_')[1] ) # convert string 'vid_100' to 100 integer
        cfg, veh_names_builtins, veh_names_live_gps = readConfigFile( cfgFile, cfg.vid ) # run readConfigFile() for individual vehicles; previous readConfigFile() used vid=-1 which is generic for all vehicles; thus does not populate routes for individual vehicles
        print('\tveh_routes: executing route_init() for vid={0}'.format(cfg.vid))
        cfg = route_init( cfg )
        for j in range(cfg.route.N):
            print('\tvid={0}, j={1}, cfg.route.lat={2},cfg.route.lon={3},cfg.route.X={4},cfg.route.Y={5},cfg.route.Z={6}'.format( cfg.vid, j, cfg.route.lat[j], cfg.route.lon[j], cfg.route.X[j], cfg.route.Y[j], cfg.route.Z[j] ))
        print('\tveh_routes: plotting waypoint route line() for vid={0}'.format(cfg.vid))
        Easting_route, Northing_route = LatLon_to_EN(cfg.route.lat, cfg.route.lon)
        #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
        plot.line( Easting_route , Northing_route , line_width=2, color=cfg.route.mapColor )
        print('\tveh_routes: done')

# --------------------------------------------------------------------------





# -------------- make point markers --------------
if hasattr(cfg.points,'points'):
    #set source dictionary for mapping [points] objects to the map with tooltips
    # example: pt_1:  {'lat': 29.189909, 'lon': -81.044963, 'elev': 0.000000, 'nextPoint': 'pt_2', 'vel': 3.0 }
    pt_data = dict( name      = [],
                    lat       = [],
                    lon       = [],
                    elev      = [],
                    nextPoint = [],
                    vel       = [],
                    E         = [],
                    N         = [],
                    posX      = [],
                    posY      = [] )
    # initialize pt_data for sourcePts    
    for point,data in cfg.points.points.items():
        print(point,data)
        pt_data['name'].append(point)
        for k,v in data.items():
            pt_data[k].append(v)
        pt_EN = LatLon_to_EN( data['lat'], data['lon'] )
        pt_data['E'].append(pt_EN[0])
        pt_data['N'].append(pt_EN[1])
        pt_data['posX'].append(pt_EN[0]-X_origin) # (m) dist from origin in East-West or X-direction
        pt_data['posY'].append(pt_EN[1]-Y_origin) # (m) dist from origin in North-South or Y-direction
    sourcePts = ColumnDataSource(data=pt_data)
    
    TOOLTIPS_PT = [
        ("name"     , "@name"),
        ("lat"      , "@lat"),
        ("lon"      , "@lon"),
        ("(X,Y) (m)", "(@posX, @posY)"),
        ("elev (m)" , "@elev"),
        ("nextPoint", "@nextPoint"),
        ("vel (m/s)", "@vel"),
    ]
    # create glyphs wtih tooltips unique to cfg.points.points
    r_pt=plot.plus(x='E', y='N',size=10, color='navy', fill_color='cyan',source=sourcePts) # size=40
    h_pt = HoverTool(renderers=[r_pt], tooltips=TOOLTIPS_PT)
    plot.add_tools(h_pt)





# -------------- make gate lines --------------
if hasattr(cfg.gates,'gates'):
    for gate,data in cfg.gates.gates.items():
        print('gate={0}, data={1}'.format(gate,data))
        # gate=gate_1, data={'ptA_lon': -81.046308, 'ptA_lat': 29.193577, 'ptB_lon': -81.046126, 'ptB_lat': 29.193865, 'nextGate': 2}
        # gate=gate_2, data={'ptA_lon': -81.04565, 'ptA_lat': 29.193255, 'ptB_lon': -81.045468, 'ptB_lat': 29.193541, 'nextGate': 1}
        # add lines from A to B (triangle to circle)
        ptA_EN = LatLon_to_EN( data['ptA_lat'], data['ptA_lon'] )
        ptB_EN = LatLon_to_EN( data['ptB_lat'], data['ptB_lon'] )
        plot.line([ptA_EN[0], ptB_EN[0]], [ptA_EN[1], ptB_EN[1]], color='springgreen', line_width=2)
        plot.triangle(x=ptA_EN[0], y=ptA_EN[1],size=10, color='lime', fill_color=None) # size=40
        plot.circle  (x=ptB_EN[0], y=ptB_EN[1],size=10, color='lime', fill_color=None) # size=40




loopCnt = 0 # init global loop counter, this loop is in the browser window


################# Get location data from UDP, make it readable, and error check it #####################
def udp_listener_thread(eNewUdp,e,debug):
    global udp_update_str
    udp_ip = '0.0.0.0' # listen from anyone
    udp_port = 5555 # listen on port from move_core.py | all_vehicles.py | specified in config file
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # udp/ip
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(1) # this non-busy wait allows browser to update while core (and vehicles) are not sending
    #sock.settimeout( 1.5 ) # block for inbound udp from MoVE core for 1.5 seconds 
    
    try:
        sock.bind((udp_ip, udp_port)) # must bind() to listen
        print("\nbokeh process listening for MoVE Core data on [{0}:{1}]\n".format(udp_ip,udp_port))
    except OSError as err:
        print('OSError: {0}'.format(err) )
        raise
        print('exiting!')
        exit(-1)
    except socket.error as err:
        print("problem binding on [{0}:{1}] with: {2}".format(udp_ip,udp_port,err))
        if err.errno == errno.EADDRINUSE:
            print("port is already in use")
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise # raise the error and stop execution
        exit(-1)
    
    print('listening for core; socket timeout is: {0}'.format( sock.gettimeout() ) )
    
    cnt=0
    t0 = datetime.now() # t0 = datetime.datetime(2020, 7, 11, 15, 32, 6, 951469)
    tLast = t0
    console_out_interval = 1 # (s) console output interval
    vid_update = [] # list of vid's update during the last console output interval; this gets cleared each console_out_interval
    while e.is_set() is False:
        #check if udp packet is available from MoVE Core ( move_core.py | all_vehicles.py | poll_state() | dashSock )
        #print(sys.argv[0]," listneing for vizData messages from MoVE Core on udp port [", port, "]")
        try:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            #print('received {0} bytes from {1}'.format(len(data),addr))
            #print('data={0}'.format(data))
        except socket.timeout:
            data=[]
            tNow = datetime.now()
            print('[{0}] waiting for updates from move core...'.format( tNow.strftime("%c") ))
        except:
            data=[]
            print("Unexpected error:", sys.exc_info()[0])
        
        # send periodic status update to console of all vid's recently updated
        tNow = datetime.now()        
        if (tNow.timestamp() - tLast.timestamp()) > console_out_interval:
            unique_vids = list(set(vid_update)) # set() creates only unique entries
            udp_update_str='[{0}] received updates for {1} vid''s: {2}'.format(tNow.strftime("%c"),len(unique_vids),unique_vids)
            #print(udp_update_str) # the only console output (duplicated in plot_label LabelSet() object)
            tLast = tNow
            vid_update = [] # reset most-recently-updated vid list
        
        #if there is a packet, decode info for a single vehicle
        if len(data)!= 0:
            cnt += 1
            msg = msgpack.unpackb(data) # update for a single vehicle
            if debug>1: print("\nreceived [", len(data), "] bytes with msg=",msg)
            if debug>1: print("from [", addr , "], receive cnt=", cnt)
            
            # received [ 447 ] bytes with msg= {'vid': 101, 'vehName': 'Phone', 'vehType': 'aerial', 'vehSubType': 'fixedwing', 'runState': 1,
            #                                   'srt_err_avg': 0.0, 't': -1, 'tStamp': 1603321037.602022, 'gps_unixTime': 0, 'batt_stat': -1,
            #                                   'pos': {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'psi': 0.0, 'lat': 0.0, 'lon': 0.0},
            #                                   'vel': {'Xd': 0.0, 'Yd': 0.0, 'Zd': 0.0, 'psiDot': 0.0, 'spd_mps': 0.0},
            #                                   'detectMsg': {'objId': 0, 'lastSeen': 0, 'lastLoc_X': 0, 'lastLoc_Y': 0, 'lastLoc_Z': 0,
            #                                   'lastLoc_lat': 0, 'lastLoc_lon': 0}, 'waypoint_status': {'waypoint': -1, 'lap': -1, 'spd_mps': -1},
            #                                   'u': [0.0, 0.0, 0.0], 'bIdCmd': 101, 'bIdName': 'live_gps_follower'}
            vid               = msg['vid']
            pos               = msg['pos']
            vel               = msg['vel']
            waypoint_status   = msg['waypoint_status']
            
            heading_deg = wrap(pos['psi'])*(180.0/3.1415926) # (deg) heading
            uptime_str = '{0}'.format( str(tNow-t0).split('.')[0] ) # truncate microseconds on uptime
            
            if debug>1: print("{0}: received {1} bytes updating vid={2}, t_veh={3:10.2f}, X={4:10.2f}(m), Y={5:10.2f}(m), Z={6:10.2f}(m), spd={7:10.2f}(m/s), beh={8}"
                            .format( uptime_str, len(data), vid, msg['t'],pos['X'],pos['Y'],pos['Z'],vel['spd_mps'],msg['bIdName'] ))
            
            veh_idx = myFindItem( ds_new['vid'] , vid )
            vid_update.append(vid) # for console update likely has repeated entries for each
            
            if veh_idx is None: # hm, vid not found; must be first time we've seen this one; append new vehicle's data to each list
                
                vehType    = msg['vehType']
                vehSubType = msg['vehSubType']
                
                (Easting, Northing) = LatLon_to_EN(pos['lat'], pos['lon'])
                ds_new['vid'].append(          vid                )
                ds_new['vehName'].append(      msg['vehName']     )
                ds_new['vehType'].append(      vehType            )
                ds_new['vehSubType'].append(   vehSubType         )
                ds_new['gps_unixTime'].append( str(datetime.fromtimestamp( msg['gps_unixTime'] )).split('.')[0] )
                ds_new['updateTime'].append(   str(datetime.now()).split('.')[0] )
                ds_new['runState'].append(     msg['runState']    ) # current runState: 1=Ready, 2=Set, 3=GO, 4=Pause, 5=Stop
                ds_new['bIdName'].append(      msg['bIdName']     ) # current vehicle behavior name
                ds_new['bIdProgress'].append(  msg['bIdProgress'] ) # current behavior progress, on [0 1]
                ds_new['t'].append(            msg['t']           ) # (s) from the vehicle (model or real device)
                ds_new['posX'].append(         pos['X']           ) # (m)
                ds_new['posY'].append(         pos['Y']           ) # (m)
                ds_new['posZ'].append(         pos['Z']           ) # (m)
                ds_new['lat'].append(          pos['lat']         ) # (dec deg)
                ds_new['lon'].append(          pos['lon']         ) # (dec deg)
                ds_new['heading_deg'].append(  heading_deg        ) # (deg)
                ds_new['spd_mps'].append(      vel['spd_mps']     ) # (m)
                #ds_new['batt_stat'].append( msg['batt_stat'] )    # (%) SOC, battery remaining
                ds_new['northing'].append( Northing               ) # tack on the un-rotated image - it will rotate on next periodic_callback update
                ds_new['easting'].append( Easting                 ) # tack on the un-rotated image - it will rotate on next periodic_callback update
                ds_new['waypoint'].append( waypoint_status['waypoint'] ) # current waypoint or gate number
                ds_new['lap'].append( waypoint_status['lap']      )           # current lap around the waypoint set or gate sequence
                
                icon_fname='none'
                if (vehType == 'aerial'):
                    icon_fname='icons/aerial_fixedwing_grn_32x32.png' # default fixed-wing icon
                    if (vehSubType == 'rotorcraft'):
                        icon_fname='icons/aerial_quad_32x32_arrow.png'
                if (vehType == 'ground'):
                    icon_fname='icons/ground_passenger_car_black_32x32.png' # default generic ground vehicle
                    icon_fname='icons/{0}_32x32.png'.format(vehSubType) # if vehSubType='ground_truck_blue', then select ./icons/ground_truck_blue_32x32.png
                if (vehType == 'pedestrian'):
                    icon_fname='icons/ped_female1_32x32.png' # default female
                    if (vehSubType == 'male'):
                        icon_fname='icons/ped_male1_32x32.png'
                if (vehType == 'surface'):
                    icon_fname='icons/surface_boat_a_32x32.png' # default generic surface vehicle, boat
                    if (vehSubType == 'surface_turtle_a'):
                        icon_fname='icons/{0}_32x32.png'.format(vehSubType) # assign icon as "<vehSubType>_32x32.png" where vehSubType is assigned in config file
                print('\tnew vid detected, adding vid={0}, vehType={1}, vehSubType={2}, loading icon: {3}'.format(vid,vehType,vehSubType,icon_fname))
                frame = cv2.imread(icon_fname,-1)
                image_orig = frame[::-1].copy().view(dtype=np.uint32)
                
                #img_orig = cv2.imread('myQuad_32x32.png',-1)
                #img_orig = cv2.imread('myQuad_256x256.png',-1)
                #img_orig = cv2.imread('myQuad_32x32_xy_coords.png',-1)
                
                image_rot = imutils.rotate_bound(image_orig.view(dtype=np.uint8), heading_deg) # use imutils with cv2 formated (.view'ed) image
                dh, dw, _ = image_rot.shape # note: *not* updating dh & dw here makes image change in size during rotation
                dh_zoomed = int(zoom_scale*dh)
                dw_zoomed = int(zoom_scale*dw)
                #print('image zoom_scale={0}, dh={1}, dw={2}, dh_zoomed={3}, dw_zoomed={4}'.format(zoom_scale,dh,dw,dh_zoomed,dw_zoomed))
                
                ds_new['image_orig'].append( image_orig ) # tack on the un-rotated image - it will rotate on next periodic_callback update
                ds_new['image'].append( image_rot.view(dtype=np.uint32).squeeze() ) # rotated image gets displayed at startup, with first udp message
                ds_new['dh'].append( dh_zoomed ) # tack on the un-rotated image - it will rotate on next periodic_callback update
                ds_new['dw'].append( dw_zoomed ) # tack on the un-rotated image - it will rotate on next periodic_callback update
                ds_new['northing_img'].append( Northing - (dh_zoomed/2) )
                ds_new['easting_img'].append(  Easting  - (dw_zoomed/2) ) # image is offset a bit b/c corner is img reference
                #print('------')
                #print(ds_new)
                
            else: # change this vid's data
            
                (Easting, Northing) = LatLon_to_EN(pos['lat'], pos['lon'])
                ds_new['vid'][veh_idx]          = msg['vid']
                ds_new['vehName'][veh_idx]      = msg['vehName']
                ds_new['vehType'][veh_idx]      = msg['vehType']
                ds_new['vehSubType'][veh_idx]   = msg['vehSubType']
                ds_new['gps_unixTime'][veh_idx] = str(datetime.fromtimestamp( msg['gps_unixTime'] )).split('.')[0]
                ds_new['updateTime'][veh_idx]   = str(datetime.now()).split('.')[0]
                ds_new['runState'][veh_idx]     = msg['runState']
                ds_new['bIdName'][veh_idx]      = msg['bIdName'] # current vehicle behavior name
                ds_new['bIdProgress'][veh_idx]  = msg['bIdProgress'] # current behavior progress on [0 1]
                ds_new['t'][veh_idx]            = msg['t'] # (s) from the vehicle (model or real device)
                ds_new['posX'][veh_idx]         = pos['X'] # (m)
                ds_new['posY'][veh_idx]         = pos['Y'] # (m)
                ds_new['posZ'][veh_idx]         = pos['Z'] # (m)
                ds_new['lat'][veh_idx]          = pos['lat'] # (dec deg)
                ds_new['lon'][veh_idx]          = pos['lon'] # (dec deg)
                ds_new['heading_deg'][veh_idx]  = heading_deg # (deg)
                ds_new['spd_mps'][veh_idx]      = vel['spd_mps'] # (m/s)
                #ds_new['batt_stat'][veh_idx]    = msg['batt_stat'] # (%) SOC, percent remaining battery
                ds_new['northing'][veh_idx]     = Northing
                ds_new['easting'][veh_idx]      = Easting
                ds_new['waypoint'][veh_idx]     = waypoint_status['waypoint'] # current waypoint or gate number
                ds_new['lap'][veh_idx]          = waypoint_status['lap']      # current lap around the waypoint set or gate sequence
                #print('posX[{0}]={1}'.format(veh_idx,source.data['posX'][veh_idx]))
            
                image_orig = ds_new['image_orig'][veh_idx] # retrieve this vehicle's original, or un-rotated icon
                image_rot = imutils.rotate_bound(image_orig.view(dtype=np.uint8), heading_deg) # use imutils with cv2 formated (.view'ed) image
                dh, dw, _ = image_rot.shape # note: *not* updating dh & dw here makes image change in size during rotation
                dh_zoomed = int(zoom_scale*dh)
                dw_zoomed = int(zoom_scale*dw)
                #print('image zoom_scale={0}, dh={1}, dw={2}, dh_zoomed={3}, dw_zoomed={4}'.format(zoom_scale,dh,dw,dh_zoomed,dw_zoomed))
                #print('(Easting,Northing)=({0},{1})'.format(Easting,Northing))
            
                ds_new['image'][veh_idx]        = image_rot.view(dtype=np.uint32).squeeze()
                ds_new['dh'][veh_idx]           = dh_zoomed
                ds_new['dw'][veh_idx]           = dw_zoomed
                ds_new['northing_img'][veh_idx] = Northing - (dh_zoomed/2)
                ds_new['easting_img'][veh_idx]  = Easting  - (dw_zoomed/2) # image is offset a bit b/c corner is img reference
            
            # notify periodic_callback that new udp message(s) have arrived
            eNewUdp.set() # notify periodic callback that new udp message(s) have arrived since last periodic callback update




# ---------------------------------------------------------------------
# create a callback that will add a number in a random location
dt = 100 # (ms) browser update rate specified in add_periodic_callback()
t0=datetime.now()
def periodic_callback_update_browser():
    global loopCnt, udp_update_str
    loopCnt+=1
    
    # dynamically update label text to know if it's running
    tNow = datetime.now()
    uptime_str = 'map uptime [{0}]'.format( str(tNow-t0).split('.')[0] ) # truncate microseconds on uptime
    tNow_str   = 'Currently: [{0}]'.format( tNow.strftime("%c") )
    title2.text = tNow_str + ", " + uptime_str
    
    #tNow_str   = 'Currently: [{0}]'.format( tNow.strftime("%c") )
    #uptime_str = 'map uptime [{0}]'.format( str(tNow-t0).split('.')[0] ) # truncate microseconds on uptime
    #uptime_bar.text = tNow_str + ", " + uptime_str
    
    #if ds_new['posX']: # only print if key exists
    #    veh_idx=0
    #    print('posX={0:0.3f}, posY={1:0.3f}, E={2}, N={3}'.format(ds_new['posX'][veh_idx],ds_new['posY'][veh_idx],ds_new['northing'][veh_idx],ds_new['easting'][veh_idx]))
    #print('plot.x_range.start={0}, plot.x_range.end={1}, plot.y_range.start={2}, plot.y_range.end={3}'.format(plot.x_range.start,plot.x_range.end,plot.y_range.start,plot.y_range.end))
    
    if eNewUdp.is_set()==True: # new udp message(s) just came in since last periodic callback evaluation
        source.data = ds_new # update map data with most recent vehicle udp message (from udp_listener_thread() )
        
        # update text box in lower left with latest udp and vid message summary
        new_text=label_data.data['text'] # grab current string list
        new_text.pop() # drop the oldest (last)
        new_text.insert(0, udp_update_str )
        label_data.data=dict(x=[20]*nLines, y=np.linspace(x_scr_lo,x_scr_hi,nLines), text=new_text)


# put the map in a layout and add to the document. Callback every 10ms
# plot in a layout and add to the document
#layout = column(uptime_bar,plot)
layout = column(plot)
layout.sizing_mode='stretch_both' # set separately to avoid also setting children
                                  # "fixed", "stretch_height", "stretch_width", "stretch_both", "scale_width", "scale_height", "scale_both"



curdoc().add_root(layout)
curdoc().add_periodic_callback(periodic_callback_update_browser, dt)
curdoc().title = "MoVE live map view"



# start udp listener thread
e       = Event() # for signaling exit to *all* threads simultaneously (except main() )
eNewUdp = Event() # for notifying periodic callback that new udp data arrived; Event default is_set()==False


# start prioritize() process
p = Thread(name='udp_listener', target=udp_listener_thread,args=(eNewUdp,e,debug),daemon=True) # daemon==True allows thread to exit when Bokeh captures ctrl+c)
p.start()



