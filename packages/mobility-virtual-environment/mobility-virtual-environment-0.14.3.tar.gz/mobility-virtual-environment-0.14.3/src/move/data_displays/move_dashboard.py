#!/usr/bin/env python3
#
# move_dashboard.py - dashboard gui to start and monitor MoVE experiments defined by scenario configuration files
#
# based on: radioButtonGroup_example_5.py
#
# the simplest way to run is the bash shell script:  ./run_move_dashboard.sh
#
# or run directly with:     bokeh serve --show move_dashboard.py
#
# Marc Compere, comperem@gmail.com
# created : 01 May 2020
# modified: 02 Jul 2022
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
import subprocess
from queue import Queue
from threading import Thread, Event
from collections import deque
from datetime import date, datetime
import time
from random import randint
import logging
import socket
import msgpack

from bokeh.plotting import figure, show, curdoc
#from bokeh.io import curdoc
from bokeh.models import Paragraph, RadioButtonGroup, Select, ColumnDataSource, Toggle, Button, StringEditor
from bokeh.models import DataTable, TableColumn, DateFormatter, NumberFormatter, Select, HTMLTemplateFormatter
from bokeh.models.widgets import Div, DataTable, TableColumn
from bokeh.models.widgets    import DateFormatter
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.layouts import column, layout, row
from bokeh.models import CustomJS, MultiChoice
sys.path.append(os.path.relpath("../scenario")) # find ../scenario/readConfigFile.py w/o (a) being a package or (b) using linux file system symbolic link
from readConfigFile import readConfigFile # for displaying correct columns
import pprint


logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-14s) %(message)s',)

debug=1 # (0/1/2/3) 0->none, 1->some, 2->more, 3->lots


# ---------------------------------------------------------------------
#screen_width=1200
screen_width=900
description = Div(background='lightgreen', text="""<b><code>move_dashboard.py</code></b> - MoVE GUI dashboard data display with command buttons""", width=screen_width)
uptime_bar = Div(background='lightskyblue' , width=screen_width, text="", render_as_text=True)




# ---------------------------------------------------------------------
#print('\n\n\tcwd={}\n'.format( os.getcwd() ))
MOVE_HOME=os.path.dirname(os.getcwd()) # MOVE_HOME should be base of MoVE; os.path.dirname() gives parent directory
#MOVE_HOME=os.getcwd() # MOVE_HOME is base of MoVE
print('\n\n\tMOVE_HOME=[{}]\n'.format(MOVE_HOME))
CFG_DIR=MOVE_HOME+'/scenario'
CORE_DIR=MOVE_HOME+'/core'
DISPLAY_DIR=MOVE_HOME+'/data_displays'
global cfgFile

def scan_all_cfg_files():
    cfg_list=[] # init empty list
    print('\tscanning config files in [{0}]'.format(CFG_DIR))
    for file in os.listdir( CFG_DIR ):
        if file.endswith(".cfg"): # the .endswith() is a string manipulation built-in
            print('\t {0}'.format(file))
            cfg_list.append(file)
            #print(os.path.join( CFG_DIR , file))
    cfg_list.sort() # make file list display in alphabetical order
    #print('cfg_list={0}'.format(cfg_list))
    return cfg_list

# pull-down for scenario select
def select_handler(attr, old, new):
    print("\tScenario selection: " + new)

cfg_list = scan_all_cfg_files() # make list the first time for Select pull-down
scenario_file_select = Select(title="Scenario selection:", value="default.cfg", options=cfg_list)
scenario_file_select.on_change('value',select_handler)
scenario_file_select.height_policy='fit'
scenario_file_select.height=80



# ---------------------------------------------------------------------
def core_ON_OFF_handler(new):
    print('\tbutton: Radio ON_OFF ' + str(new) + ' selected.')
    #print('RSGPS_buttons={0}'.format(dir(RSGPS_buttons)))
    #RSGPS_buttons.visible = bool(new)
    if new==1: # enable button to ON state
        print('\tbutton: launching main_core.py process')
        qProcButton.put(3) # press the button, launch ./main_core.py
        eRSGPS.clear() # set to False; this causes periodic callback to auto-set Ready-Set-Go-Pause-Stop button from latest udp message
        core_ON_OFF.button_type='success' # options: default (grey), primary (tiel), success (green), warning (orange), danger (red)
    else:
        print('\tbutton: stopping main_core.py process')
        qProcButton.put(4) # press the button, terminate ./main_core.py
        core_ON_OFF.button_type='primary'

core_ON_OFF = RadioButtonGroup(labels=["Core OFF", "Core ON"], active=0)
core_ON_OFF.height_policy='fit'
core_ON_OFF.height=80
core_ON_OFF.button_type='primary' # options: default (grey), primary (tiel), success (green), warning (orange), danger (red)
#core_ON_OFF.margin=(100,100,100,100)
#core_ON_OFF.width_policy='fit'
#core_ON_OFF.width=100
core_ON_OFF.on_click(core_ON_OFF_handler)






# ---------------------------------------------------------------------
# RSGPS --> Ready, Set, Go, Pause, Stop
def RSGPS_radio_handler(new):
    print('\tRadio button option ' + str(new) + ' selected.')
    print('\teRSGPS.is_set()==[{0}]'.format(eRSGPS.is_set()))
    if new==0:
        RSGPS_buttons.button_type='primary' # ready / tiel
        if eRSGPS.is_set()==True:
            qProcButton.put(6) # press the button, issue commands for all vehicles to enter runState 1, or READY
    if new==1:
        RSGPS_buttons.button_type='warning' # set / orange
        if eRSGPS.is_set()==True:
            qProcButton.put(7) # press the button, issue commands for all vehicles to enter runState 1, or SET
    if new==2:
        RSGPS_buttons.button_type='success' # go / green
        if eRSGPS.is_set()==True:
            qProcButton.put(8) # press the button, issue commands for all vehicles to enter runState 1, or GO
    if new==3:
        RSGPS_buttons.button_type='default' # pause / grey
        if eRSGPS.is_set()==True:
            qProcButton.put(9) # press the button, issue commands for all vehicles to enter runState 1, or PAUSE
    if new==4:
        RSGPS_buttons.button_type='danger'  # stop / red
        veh_launch_toggle.disabled=False # re-enable launch button
        veh_launch_toggle.active=False # set to Un-launched state
        scenario_lock_toggle.disabled=False # you could select a different scenario file
        if eRSGPS.is_set()==True:
            print('sending qProcButton.put(10)')
            qProcButton.put(10) # press the button, issue commands for all vehicles to enter runState 1, or STOP
    
        
    
    
RSGPS_buttons = RadioButtonGroup(
        labels=["Ready", "Set", "Go", "Pause", "Stop"], active=0)
#RSGPS_buttons.disabled=True
RSGPS_buttons.height_policy='fit'
RSGPS_buttons.height=80
RSGPS_buttons.button_type='primary' # ready / tiel
RSGPS_buttons.on_click(RSGPS_radio_handler)
RSGPS_buttons.disabled=True # start disabled; enable if (a) launch vehicles or (b) udp sees Core with running vehicles in vehicle table



# ---------------------------------------------------------------------
def veh_launch_toggle_handler(new):
    print('\tveh_launch_toggle value: [' + str(new) + ']')
    if new is True:
        scenario_lock_toggle.disabled=True # cannot change scenario while processes are launched
        RSGPS_buttons.active=0
        RSGPS_buttons.disabled=False
        qProcButton.put(5) # press the button, run ./main_launch_veh_process.py
        veh_launch_toggle.label='Vehicle processes: Launched'
        veh_launch_toggle.button_type='success' # options: default (grey), primary (tiel), success (green), warning (orange), danger (red)
        veh_launch_toggle.disabled=True # cannot just 'unlaunch' - must issue Stop message
        eRSGPS.set() # this enables buttons for commanding runState changes with main_changeRunState.py (without Core running)
    else:
        veh_launch_toggle.label='Press to Launch Vehicle Processes'
        veh_launch_toggle.button_type='default'

veh_launch_toggle = Toggle(label="Press to Launch Vehicle Processes", button_type='primary')
veh_launch_toggle.on_click(veh_launch_toggle_handler)
veh_launch_toggle.height_policy='fit'





# ==============================================================================
# =         BEGIN:   web console output and subprocess execution               =
# ==============================================================================
doc=curdoc() # make a copy so bokeh server and thread use same curdoc()

template="""<div style="background:<%= "wheat" %>"> <%= value %> </div>"""
formatter =  HTMLTemplateFormatter(template=template)

web_console_data = dict(index=[], msg_list=[])
web_console_src = ColumnDataSource(data=web_console_data)

web_console = DataTable(source=web_console_src,
              columns=[TableColumn(field="msg_list", title="Debug Console", formatter=formatter, editor=StringEditor())],
              width=1200, height=240, editable=True) #, index_position=None,

ii = 0 # console snap-to index
qProcLine=Queue()


# -----------------------------------------------------------------------------
qProcLine=Queue()
nLines=500 # lines of history output to keep in scrollbar
def print_subproc_output():
    global ii
    data = dict(index=[ii], msg_list=["{0}".format(qProcLine.get())])
    web_console_src.stream(data, nLines) # add just the new info; keep nLines in scrollbar history
    web_console_src.selected.indices = [ii] # snap to bottom DataTable cell
    if ii<(nLines-1):
        ii += 1


# run a subprocess in the background and stream console output to the web_console text box
def blocking_call_subprocess(eProc,qProcButton):
    global cfg
    lineCnt=0
    while eProc.is_set() is False:
        qmsg = qProcButton.get(block=True) # block here until button press
        print('received qProcButton qmsg=[{0}]'.format(qmsg))
        
        cfg_str = '{0}/{1}'.format(CFG_DIR,scenario_file_select.value)  # CFG_DIR=MOVE_HOME+'/scenario'
        
        if qmsg==0: # launch MoVE mapping process in a new brower window
            #exe_str = '{0}/run_move_live_mapping.sh'.format(DISPLAY_DIR)
            print('move_dashboard.py pwd={0}'.format( os.getcwd() )) # ./MoVE/v1.14_dev/src/move/data_displays
            if os.path.isdir('../bin_src'):
                exe_str = '../bin_src/run_move_live_mapping.sh' # this will only occur during development when run from move source code tree
            else:
                exe_str = 'run_move_live_mapping.sh' # expected result for move as an installed python package
                                                     # this shell script is in the path, in ./bin, wherever python3 installed it
                
            cmd = [exe_str, '-f', cfg_str] # ./run_move_map_client.sh -f ../scenario/default.cfg
            #cmd = ['bokeh', 'serve', '--port=5007', '--show', '--args', '-f', cfg_str] # ./run_move_map_client.sh -f ../scenario/default.cfg
            print('\texe_str={0}'.format(exe_str))
            print('\tcmd={0}'.format(cmd),flush=True)
            map_proc = subprocess.Popen(cmd,stdout=subprocess.DEVNULL)
            
        if qmsg==1: # kill MoVE mapping process
            if 'map_proc' in locals():
                helper_str1 = 'terminating MoVE map display process with: map_proc.kill()'
                qProcLine.put( '{0}'.format(helper_str1) )
                doc.add_next_tick_callback(print_subproc_output) # update web console; technique from: https://stackoverflow.com/a/60745271/7621907
                map_proc.kill() # send SIGKILL signal to shell script that launched the map subprocess (but this doesn't kill bokeh)
                del(map_proc)
                
                kill_str="kill -9 ` ps ax | grep move_live_mapping | grep -v grep | awk '{print $1}' `"
                helper_str1 = 'and with shell process: {0}'.format(kill_str)
                qProcLine.put( '{0}'.format(helper_str1) )
                doc.add_next_tick_callback(print_subproc_output) # update web console; technique from: https://stackoverflow.com/a/60745271/7621907
                adios = subprocess.Popen(kill_str,shell=True) # shell=True required to issue Linux shell command
            else:
                helper_str2 = '{0}: no map_proc variable to terminate. doing nothing.'.format(datetime.now().strftime('%c'))
                qProcLine.put( '{0}'.format(helper_str2) )
                doc.add_next_tick_callback(print_subproc_output) # update web console; technique from: https://stackoverflow.com/a/60745271/7621907
        
        if qmsg==2:
            cmd = ['screen', '-ls']
        
        if qmsg==3: # start ./main_core.py
            exe_str = '{0}/main_core.py'.format(CORE_DIR)
            cmd = ['python3', exe_str, '-f', cfg_str] # ./main_core.py -f ../scenario/default.cfg
            qProcLine.put( 'Launching {0}'.format(cmd) )
            doc.add_next_tick_callback(print_subproc_output) # update web console; technique from: https://stackoverflow.com/a/60745271/7621907
            proc_core = subprocess.Popen(cmd) # launch ./main_core.py as a running background process (do not monitor output in python - it's in the console where bokeh launches this script)
        
        if qmsg==4: # stop ./main_core.py
            if 'proc_core' in locals(): # if proc_core exists, then stop it
                proc_core.terminate() # end this subprocess
        
        
        if qmsg==5: # launch vehicles with output streamed to div textbox
            exe_str = '{0}/main_launch_veh_process.py'.format(CORE_DIR)
            cmd = ['python3', exe_str, '-f', cfg_str] # ./main_launch_veh_process.py -f ../scenario/default.cfg
        
        
        if qmsg==6: # tell all vehicles to enter runState=1 --> READY
            exe_str = '{0}/main_changeRunState.py'.format(CORE_DIR)
            cmd = ['python3', exe_str, '-f', cfg_str, '1'] # ./main_changeRunState.py -f ../scenario/default.cfg 1
        
        if qmsg==7: # tell all vehicles to enter runState=2 --> SET
            exe_str = '{0}/main_changeRunState.py'.format(CORE_DIR)
            cmd = ['python3', exe_str, '-f', cfg_str, '2'] # ./main_changeRunState.py -f ../scenario/default.cfg 2
        
        if qmsg==8: # tell all vehicles to enter runState=3 --> GO
            exe_str = '{0}/main_changeRunState.py'.format(CORE_DIR)
            cmd = ['python3', exe_str, '-f', cfg_str, '3'] # ./main_changeRunState.py -f ../scenario/default.cfg 3
        
        if qmsg==9: # tell all vehicles to enter runState=4 --> PAUSE
            exe_str = '{0}/main_changeRunState.py'.format(CORE_DIR)
            cmd = ['python3', exe_str, '-f', cfg_str, '4'] # ./main_changeRunState.py -f ../scenario/default.cfg 4
        
        if qmsg==10: # tell all vehicles to enter runState=5 --> STOP
            exe_str = '{0}/main_changeRunState.py'.format(CORE_DIR)
            cmd = ['python3', exe_str, '-f', cfg_str, '5'] # ./main_changeRunState.py -f ../scenario/default.cfg 5
        
        if qmsg==11: # find filename and size of most likely Core logfile
            # get the top line from:   ls -lt /tmp/*State.csv
            exe_str=' ls -lt {0}/*State.csv'.format(cfg.logfile_loc_core)
            ps = subprocess.Popen(exe_str, stdout=subprocess.PIPE, shell=True)
            res=ps.communicate()
            top_line = list(res)[0].decode('utf-8').split('\n')[0]
            print('\ttop_line={0}'.format(top_line))
            if top_line is not None:
                qProcLine.put( '{0}'.format(top_line) )
            doc.add_next_tick_callback(print_subproc_output) # update web console; technique from: https://stackoverflow.com/a/60745271/7621907
        
        # make the subprocess.Popen() call with 'cmd' just constructed above (except for certain cases)
        if qmsg in [2, 5, 6, 7, 8, 9, 10]: # launch cmd and redirect stdout and stderr to div textbox
            qProcLine.put( 'Launching: {0}'.format(cmd) ) # send string to web console
            doc.add_next_tick_callback(print_subproc_output) # update web console; technique from: https://stackoverflow.com/a/60745271/7621907
            #print('executing {0}'.format(cmd))
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)   
            for line in iter(process.stdout.readline, b''):
                #print('line={0}'.format(line)) # command output in command line console, line-by-line
                qProcLine.put( '{0}'.format(line.decode('utf-8')) ) # send string to web console
                doc.add_next_tick_callback(print_subproc_output) # technique from: https://stackoverflow.com/a/60745271/7621907


    logging.debug('thread exiting') 


# -----------------------------------------------------------------------------
# add white space in the web_console
def bt_map_launch_callback():
    qProcButton.put(0) # launch map subprocess in a new browser window

bt_width=120
bt_map_launch = Button(label="Start Map process" , button_type="success", width=bt_width)
bt_map_launch.on_click(bt_map_launch_callback)

def bt_map_kill_callback():
    qProcButton.put(1) # kill map subprocess (this will not close the browser)

bt_map_kill = Button(label="Stop Map Process" , button_type="success", width=bt_width)
bt_map_kill.on_click(bt_map_kill_callback)

# -----------------------------------------------------------------------------
def bt_subproc_callback2():
    qProcButton.put(2) # press the button, trigger the blocking subprocess

bt_subproc2 = Button(label="Veh models on?" , button_type="warning", width=bt_width)
bt_subproc2.on_click(bt_subproc_callback2)

# -----------------------------------------------------------------------------
# add white space in the web_console
def add_whitespace():
    qProcLine.put(' ')
    doc.add_next_tick_callback(print_subproc_output) # technique from: https://stackoverflow.com/a/60745271/7621907
    qProcLine.put(' ')
    doc.add_next_tick_callback(print_subproc_output)

bt_space = Button(label="add whitespace" , button_type="success", width=bt_width)
bt_space.on_click(add_whitespace)

# -----------------------------------------------------------------------------
def bt_logfile_size_callback():
    qProcButton.put(11) # check logfile size

bt_logfile_size = Button(label="Core Logfile Status?" , button_type="success", width=bt_width)
bt_logfile_size.on_click(bt_logfile_size_callback)

# ==============================================================================
# =                       END: console output                                  =
# ==============================================================================




# ---------------------------------------------------------------------
def scenario_lock_toggle_handler(new):
    global cfg
    print('\tscenario_lock_toggle value: [' + str(new) + ']')
    if new is True:
        scenario_lock_toggle.label       = 'Scenario: Locked, Press to Unlock'
        scenario_lock_toggle.button_type = 'success' # options: default (grey), primary (tiel), success (green), warning (orange), danger (red)
        scenario_file_select.disabled    = True # drop-down is greyed out 
        core_ON_OFF.disabled             = False # "Core OFF", "Core ON"
        veh_launch_toggle.disabled       = False # "Press to Launch Vehicle Processes"
        bt_map_kill.disabled             = False # "Show Map Launch Commands"
        bt_map_launch.disabled           = False # "Show GPS port assignments"
        bt_logfile_size.disabled         = False # "Logfile Size?"
        cfgFile='{0}/{1}'.format( CFG_DIR , scenario_file_select.value )
        print('\treading config file: [{0}]'.format(cfgFile))
        
        # read config file just locked in
        cfg, veh_names_builtins, veh_names_live_gps = readConfigFile( cfgFile, -1 )
        if len(cfg.default_display_cols)>0:
            #print('cfg.default_display_cols={0}'.format(cfg.default_display_cols))
            multichoice_col_sel.value=cfg.default_display_cols # update MultiChoice button values to what was in config file
            cols_subset = selected_columns( cfg.default_display_cols )
            #print('cols_subset={0}'.format( cols_subset ))
            veh_table.columns=cols_subset # dynamically changing columns to match defaults specified in config file
        else:
            print('error: something went wrong reading initial data table column set from config file: {0}'.format(cfgFile))
        
    else:
        scenario_file_select.options     = scan_all_cfg_files() # udpate scenario file list in Select pull-down
        scenario_lock_toggle.label       ='Press to Lock Scenario File'
        scenario_lock_toggle.button_type ='default'
        scenario_file_select.disabled    = False
        
        print('\tstopping main_core.py process')
        qProcButton.put(4) # press the button, terminate ./main_core.py
        core_ON_OFF.button_type          = 'primary'
        core_ON_OFF.active               = 0     # make the button's active state the first, which is "Core OFF"
        core_ON_OFF.disabled             = True  # disable MovE Core until a scenario is selected
        
        veh_launch_toggle.disabled       = True
        RSGPS_buttons.disabled           = True

scenario_lock_toggle = Toggle(label="Press to Lock Scenario File", button_type="default")
scenario_lock_toggle.on_click(scenario_lock_toggle_handler)
scenario_lock_toggle.height_policy='fit'

# disable Core, veh, RSGPS buttons until scenario selected
core_ON_OFF.disabled        = True # "Core OFF", "Core ON"
veh_launch_toggle.disabled  = True # "Press to Launch Vehicle Processes"
RSGPS_buttons.disabled      = True # "Ready", "Set", "Go", "Pause", "Stop"
bt_map_kill.disabled        = True # "Stop Map Process"
bt_map_launch.disabled      = True # "Start Map process"
bt_logfile_size.disabled    = True # "Logfile Size?"




# -----------------------------------------------------------------------------
# simple item index search in a list
def myFindItem(myList,searchItem):
    try:
        idx=myList.index(searchItem)
    except ValueError:
        idx=None
        #print('warning: {0}(): {1} not found in list'.format(myFindItem.__name__ ,searchItem))
    return(idx)




# ==============================================================================
# =                    BEGIN:   vehicle table                                  =
# ==============================================================================
# bound a (in radians) on the interval [0 2*pi]; from wrap_theta.py
def wrap(a):
    sign = lambda x: x and (1, -1)[x<0] # from: https://stackoverflow.com/a/16726462/7621907
    return ( abs(a) % (2*3.14159265359) )*sign(a)

# -----------------------------------------------------------------------------
# thread to update datasource with as many udp updates arrive before next periodic_callback_update_browser()
def udp_listener_thread(eNewUdp,e,debug):
    global sen_new
    udp_ip = '0.0.0.0' # listen from anyone
    udp_port = 5556 # listen on port from sender: move_core | all_vehicles.py | dashSock.sendto(), specified in config file
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # udp/ip
    try:
        sock.bind((udp_ip, udp_port)) # must bind() to listen
    except OSError as err:
        logging.debug('OSError: {0}'.format(err) )
        raise
        logging.debug('exiting!')
        exit(-1)
    except:
        logging.debug("Unexpected error:", sys.exc_info()[0])
        raise # raise the error and stop execution
        exit(-1)
    
    cnt=0
    tNow = datetime.now()
    firstVehMsgEverSeen=True # trigger for creating sensor_table columns, sensor_cols; trigger for first loop only
    while e.is_set() is False:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        cnt += 1
        msg = msgpack.unpackb(data) # receive vehInfo for a single vid (from core | all_vehicles.py | poll_state() )
        if debug>1: print("\n move_dashboard.py received [", len(data), "] bytes with msg=",msg)
        if debug>1: print("from [", addr , "], receive cnt=", cnt)
        if debug>1:
            print('\nmsg:')
            pprint.pprint(msg)
            print('\n')        
        # received [ 593 ] bytes with msg= {'vid': 100, 'vehName': 'thor', 'vehType': 'aerial', 'vehSubType': 'fixedwing', 'runState': 3, 'srt_err_avg': 0.0,
        #       't': 121.60004711151123, 'tStamp': 1627317441.9414291, 'gps_unixTime': 1627317443.21, 'batt_stat': -2,
        #       'pos': {'X': -31749.11066457769, 'Y': -77939.00827236427, 'Z': 18.47576904296875, 'psi': 0.004550436035499999, 'hdg': 0.004550436035499999,
        #       'lat': 28.48912324, 'lon': -81.37024415}, 'vel': {'Xd': 0.0, 'Yd': 0.0, 'Zd': 0.0, 'psiDot': 0.0, 'spd_mps': 0.0},
        #       'detectMsg': {'objId': 0, 'lastSeen': 0, 'lastLoc_X': 0, 'lastLoc_Y': 0, 'lastLoc_Z': 0, 'lastLoc_lat': 0, 'lastLoc_lon': 0},
        #       'waypoint_status': {'waypoint': 'gate_1', 'lap': -1, 'spd_mps': -1}, 'u': [0.0, 0.0, 0.0], 'bIdCmd': 100, 'bIdName': 'live_gps_follower',
        #       'sensorData': {'mac': '', 'batt_stat': 67.0, 'accel_x': -1.0606186, 'accel_y': 0.68225354, 'accel_z': 9.698409}}
        
        vid               = msg['vid']
        pos               = msg['pos']
        vel               = msg['vel']
        waypoint_status   = msg['waypoint_status']
        tStamp            = msg['tStamp'] # timestamp when core received this vid's update into State['vid']
        gps_unixTime      = msg['gps_unixTime'] # from the vehicle model's incoming GPS data stream
        #print('vid={0}'.format(vid))
        # retrieve the i'th vehicle's data to edit
        myList = ds_new['vid']
        veh_idx = myFindItem( myList, vid )
        #print('myList={0}'.format(myList))
        #print('vid={0}, veh_idx={1}'.format(vid,veh_idx))
        
        tNow = datetime.now()
        yaw_deg = wrap(pos['psi'])*180.0/3.1415926 # (deg) vehicle yaw orientation
        heading_deg = yaw_deg # (deg) heading, course-over-ground
        uptime_str = '{0}'.format( str(tNow-t0).split('.')[0] ) # truncate microseconds on uptime
        
        if debug>1: print("\t{0}: received {1} bytes updating vid={2}, t_veh={3:10.2f}, X={4:10.2f}(m), Y={5:10.2f}(m), Z={6:10.2f}(m), spd={7:10.2f}(m/s), beh={8}, behProgress={9}"
                        .format( uptime_str, len(data), vid, msg['t'],pos['X'],pos['Y'],pos['Z'],vel['spd_mps'],msg['bIdName'],msg['bIdProgress'] ))
        
        # update lists of vehicle information; ds_new is a dict with each entry is a list, one for each vehicle
        # ds_new:
        #   {'bIdName': [  'no behavior',
        #                  'no behavior',
        #                  'no behavior',
        #                  'no behavior',
        #                  'no behavior'],
        #       'gps_unixTime': ['1969-12-31 19:00:00',
        #                        '1969-12-31 19:00:00',
        #                        '1969-12-31 19:00:00',
        #                        '1969-12-31 19:00:00',
        #                        '1969-12-31 19:00:00'],
        #       'heading_deg': [0.0, 0.0, 0.0, 0.0, 0.0],
        #       'lap': [-1, -1, -1, -1, -1],
        #       'lat': [ 29.193110999581492,
        #                29.193110999581492,
        #                29.193110999581492,
        #                29.193110999581492,
        #                29.193110999581492],
        #       'lon': [-81.0461709999998,
        #               -81.0461709999998,
        #               -81.0461709999998,
        #               -81.0461709999998,
        #               -81.0461709999998],
        #       ... <and so on>
        #
        if veh_idx is None: # oops, vid not found; add new vehicle's row
            print('\tadding vid={0} to list'.format(vid))
            ds_new['vid'                ].append( vid )
            ds_new['vehName'            ].append( msg['vehName'] )
            ds_new['vehType'            ].append( msg['vehType'] )
            ds_new['vehSubType'         ].append( msg['vehSubType'] )
            ds_new['updateTime'         ].append( str(datetime.fromtimestamp(tStamp)).split('.')[0] )
            ds_new['runState'           ].append( msg['runState'] ) # current runState: 1=Ready, 2=Set, 3=GO, 4=Pause, 5=Stop
            ds_new['bIdName'            ].append( msg['bIdName'] ) # current vehicle behavior name
            ds_new['bIdProgress'        ].append( msg['bIdProgress'] ) # current vehicle behavior progress, [0 1]
            ds_new['gps_unixTime'       ].append( str(datetime.fromtimestamp(gps_unixTime)).split('.')[0] )
            ds_new['t'                  ].append( msg['t'] ) # (s) from the vehicle (model or real device)
            ds_new['posX'               ].append( pos['X'] ) # (m)
            ds_new['posY'               ].append( pos['Y'] ) # (m)
            ds_new['posZ'               ].append( pos['Z'] ) # (m)
            ds_new['lat'                ].append( pos['lat'] ) # (dec deg)
            ds_new['lon'                ].append( pos['lon'] ) # (dec deg)
            ds_new['heading_deg'        ].append( heading_deg ) # (deg)
            ds_new['yaw_deg'            ].append( yaw_deg ) # (deg)
            ds_new['spd_mps'            ].append( vel['spd_mps'] ) # (m)
            ds_new['waypoint'           ].append( waypoint_status['waypoint'] ) # current waypoint string or gate name from cfg file
            ds_new['lap'                ].append( waypoint_status['lap'] )      # current lap number
            ds_new['missionAction'      ].append( msg['missionAction'] )        # missionAction like 'waitElapsed', 'goToPoint', or 
            ds_new['missionState'       ].append( msg['missionState'] )         # missionState is an integer like 1, 10 or 100 from the config file's [missionCommands]
            ds_new['missionPctComplete' ].append( msg['missionPctComplete'])    # mission command percent complete, on [0 1]
            ds_new['missionProgress'    ].append( msg['missionProgress'] )      # progress indicator = missionState + pctComplete
            ds_new['missionLastCmdTime' ].append( msg['missionLastCmdTime'] )   # last wall clock time the mission commander issued a command
            ds_new['missionStatus'      ].append( msg['missionStatus'] )        # mission commander's status: 'readyWait', 'active', or 'complete'
            ds_new['missionCounter'     ].append( msg['missionCounter'] )       # counter for all separate mission commands ('goToMissionState' can cause lops which means counter can be higher than all [missionCommands] rows)
            
            #print('---------------')
            #if ('sensorData' in msg) and ('batt_stat' in msg['sensorData']):
            #    ds_new['batt_stat'].append( msg['sensorData']['batt_stat'] ) # GPS sender's battery remaining on [0  100]
            if 'sensorData' in msg:
                sen_new['vid'    ].append(vid)            # vid and vehName are the only two that need assignment
                sen_new['vehName'].append(msg['vehName']) # all others have names and values auto-populated from sensorData dict contents just received
                
                # expand this vehicle's dictionary to include 'vid' and 'vehName' and msg['sensorData']
                #print('1:start---------------')
                #print('sen_new={0}'.format(sen_new)) # sen_new={'vid': [], 'vehName': [], 'mac': 100, 'batt_stat': -1}
                #print('1:end---------------')
                for key,val in msg['sensorData'].items():
                    print(key,val)
                    if key in sen_new: # make sure these {key,value} pairs are in the sen_new dictionary
                        print('\tsen_new[key]={0}'.format(sen_new[key]))
                        sen_new[key].append(val)
                    else:
                        sen_new[key]=[val] # make sure to create a list for future .append'ing
                #print('2:start---------------')
                #print('sen_new={0}'.format(sen_new)) # sen_new={'vid': [], 'vehName': [], 'mac': 100, 'batt_stat': -1}
                #print('2:end---------------')
                
                # add the new TableColumn entries to vid and vehName already in sensor_cols (from it's creation)
                if firstVehMsgEverSeen==True:
                    firstVehMsgEverSeen=False
                    # make sensor_table columns from this message, once because all subsequent messages will have identical data
                    for k in sen_new.keys():
                        sensor_cols.append( TableColumn(field=k,title=k) )
            #print('---------------')
        
        else:
            # change this vid's data
            ds_new['vehName'][veh_idx]            = msg['vehName']
            ds_new['vehType'][veh_idx]            = msg['vehType']
            ds_new['vehSubType'][veh_idx]         = msg['vehSubType']
            ds_new['updateTime'][veh_idx]         = str(datetime.fromtimestamp(tStamp)).split('.')[0]
            ds_new['runState'][veh_idx]           = msg['runState']
            ds_new['bIdName'][veh_idx]            = msg['bIdName'] # current vehicle behavior name
            ds_new['bIdProgress'][veh_idx]        = msg['bIdProgress'] # current vehicle behavior progress, [0 1]
            ds_new['gps_unixTime'][veh_idx]       = str(datetime.fromtimestamp(gps_unixTime)).split('.')[0]
            ds_new['t'][veh_idx]                  = msg['t'] # (s) from the vehicle (model or real device)
            ds_new['posX'][veh_idx]               = pos['X'] # (m)
            ds_new['posY'][veh_idx]               = pos['Y'] # (m)
            ds_new['posZ'][veh_idx]               = pos['Z'] # (m)
            ds_new['lat'][veh_idx]                = pos['lat'] # (dec deg)
            ds_new['lon'][veh_idx]                = pos['lon'] # (dec deg)
            ds_new['heading_deg'][veh_idx]        = heading_deg # (deg)
            ds_new['yaw_deg'][veh_idx]            = yaw_deg # (deg)
            ds_new['spd_mps'][veh_idx]            = vel['spd_mps'] # (m/s)
            ds_new['waypoint'][veh_idx]           = waypoint_status['waypoint'] # current waypoint string or gate name from cfg file
            ds_new['lap'][veh_idx]                = waypoint_status['lap']      # current lap number
            ds_new['missionAction'     ][veh_idx] = msg['missionAction']        # missionAction like 'waitElapsed', 'goToPoint', or 
            ds_new['missionState'      ][veh_idx] = msg['missionState']         # missionState is an integer like 1, 10 or 100 from the config file's [missionCommands]
            ds_new['missionPctComplete'][veh_idx] = msg['missionPctComplete']   # mission command percent complete, on [0 1]
            ds_new['missionProgress'   ][veh_idx] = msg['missionProgress']      # progress indicator = missionState + pctComplete
            ds_new['missionLastCmdTime'][veh_idx] = msg['missionLastCmdTime']   # last wall clock time the mission commander issued a command
            ds_new['missionStatus'     ][veh_idx] = msg['missionStatus']        # mission commander's status: 'readyWait', 'active', or 'complete'
            ds_new['missionCounter'    ][veh_idx] = msg['missionCounter']       # counter for all separate mission commands ('goToMissionState' can cause lops which means counter can be higher than all [missionCommands] rows)
            
            if 'sensorData' in msg:
                #print('3:start---------------')
                #print('sen_new={0}'.format(sen_new)) # sen_new={'vid': [], 'vehName': [], 'mac': 100, 'batt_stat': -1}
                #print('3:end---------------')
                for key,val in msg['sensorData'].items():
                    #print(key,val)
                    if key not in sen_new: # create list of all zeros large enough to contain all possible vehicles reporting their updates to move dashboard
                        sen_new[key]=[0]*(cfg.nVeh_builtin+cfg.nVeh_live_gps)
                    sen_new[key][veh_idx]=val # make sure these {key,value} pairs are in the sen_new dictionary
        
        # if execution gets  here, it means:
        #     (a) move_core.py is running, (because this only listens to main_core.py)
        #     (b) a vehicle model is running and reporting to main_core.py
        # let periodic_callback_update_browser() know at least 1 new udp message arrived since it's last evaluation
        eNewUdp.set() # notify periodic callback that new udp message(s) have arrived since last periodic callback update



# -----------------------------------------------------------------------------
# create a dict with all fields empty for .append() to grow all lists dynamically; one list entry per vehicle
veh_data = dict(
        vid                = [], # 0
        vehName            = [], # 1
        vehType            = [], # 2
        vehSubType         = [], # 3
        updateTime         = [], # 4
        runState           = [], # 5
        bIdName            = [], # 6
        bIdProgress        = [], # 7
        gps_unixTime       = [], # 8  time from GPS unit when live_gps_follower==True
        t                  = [], # 9  (s) from the vehicle (simulated or real device)
        posX               = [], # 10  (m)
        posY               = [], # 11 (m)
        posZ               = [], # 12 (m)
        lat                = [], # 13 (dec deg)
        lon                = [], # 14 (dec deg)
        heading_deg        = [], # 15 (deg) GPS heading, course over ground
        yaw_deg            = [], # 16 (deg) IMU yaw angle
        spd_mps            = [], # 17 (m/s)
        waypoint           = [], # 18 current waypoint or gate number
        lap                = [], # 19 current lap number
        missionAction      = [], # 20 missionAction like 'waitElapsed', 'goToPoint', or 'goToMissionState'
        missionState       = [], # 21 missionState is an integer like 1, 10 or 100
        missionPctComplete = [], # 22 mission command percent complete, on [0 1]
        missionProgress    = [], # 23 progress indicator = missionState + pctComplete
        missionLastCmdTime = [], # 24 last wall clock time the mission commander issued a command
        missionStatus      = [], # 25 mission commander's status: 'readyWait', 'active', or 'complete'
        missionCounter     = [], # 26 counter for all separate mission commands
        #batt_stat    = []  # 27 pct battery remaining on GPS sender device (for live_gps_follower==True)
        )
table_source = ColumnDataSource(veh_data)

keyList = list( veh_data.keys() )
col_titles=[] # maintain the source list of data column titles here (and nowhere else)
col_titles.append("Veh ID")             # 0
col_titles.append("Veh Name")           # 1
col_titles.append("Veh Type")           # 2
col_titles.append("Veh Sub Type")       # 3
col_titles.append("Last Core Update")   # 4
col_titles.append("Run State")          # 5
col_titles.append("Behvaior")           # 6
col_titles.append("Beh Progress")       # 7
col_titles.append("GPS time")           # 8
col_titles.append("Veh time (s)")       # 9
col_titles.append("X Loc (m)")          # 10
col_titles.append("Y Loc (m)")          # 11
col_titles.append("Z Loc (m)")          # 12
col_titles.append("Lat")                # 13
col_titles.append("Lon")                # 14
col_titles.append("Heading (deg)")      # 15
col_titles.append("Yaw (deg)")          # 16
col_titles.append("Veh Spd (m/s)")      # 17
col_titles.append("Waypoint")           # 18
col_titles.append("Lapnum")             # 19
col_titles.append("misAction")          # 20 missionAction like 'waitElapsed', 'goToPoint', or 'goToMissionState'
col_titles.append("misState")           # 21 missionState is an integer like 1, 10 or 100
col_titles.append("misPctComplete")     # 22 mis command percent complete, on [0 1]
col_titles.append("misProgress")        # 23 progress indicator = missionState + pctComplete
col_titles.append("misLastCmdTime")     # 24 last wall clock time the mission commander issued a command
col_titles.append("misStatus")          # 25 mission commander's status: 'readyWait', 'active', or 'complete'
col_titles.append("misCounter")         # 26 counter for all separate mission commands
#col_titles.append("Battery")           # 27

# superset of all possible columns to display; only some are typically selected by the MultiChoice button
table_columns = [
            TableColumn(field=keyList[0],  title=col_titles[0],width=100),                                                  # 0
            TableColumn(field=keyList[1],  title=col_titles[1],width=100),                                                  # 1
            TableColumn(field=keyList[2],  title=col_titles[2],width=100),                                                  # 2
            TableColumn(field=keyList[3],  title=col_titles[3],width=100),                                                  # 3
            TableColumn(field=keyList[4],  title=col_titles[4],width=200), #,formatter=DateFormatter()),                    # 4
            TableColumn(field=keyList[5],  title=col_titles[5],width=50),                                                   # 5
            TableColumn(field=keyList[6],  title=col_titles[6],width=150),                                                  # 6
            TableColumn(field=keyList[7],  title=col_titles[7],width=150,formatter=NumberFormatter(format="0,0.00")),       # 7
            TableColumn(field=keyList[8],  title=col_titles[8],width=250),                                                  # 8
            TableColumn(field=keyList[9],  title=col_titles[9],width=100,formatter=NumberFormatter(format="0,0.00")),       # 9
            TableColumn(field=keyList[10], title=col_titles[10],width=80,formatter=NumberFormatter(format="0,0.000")),       # 10
            TableColumn(field=keyList[11], title=col_titles[11],width=80,formatter=NumberFormatter(format="0,0.000")),      # 11
            TableColumn(field=keyList[12], title=col_titles[12],width=80,formatter=NumberFormatter(format="0,0.000")),      # 12
            TableColumn(field=keyList[13], title=col_titles[13],width=100,formatter=NumberFormatter(format="0.000000")),    # 13
            TableColumn(field=keyList[14], title=col_titles[14],width=100,formatter=NumberFormatter(format="0.000000")),    # 14
            TableColumn(field=keyList[15], title=col_titles[15],width=100,formatter=NumberFormatter(format="0,0.0")),       # 15
            TableColumn(field=keyList[16], title=col_titles[16],width=100,formatter=NumberFormatter(format="0,0.0")),       # 16
            TableColumn(field=keyList[17], title=col_titles[17],width=100,formatter=NumberFormatter(format="0,0.000")),     # 17
            TableColumn(field=keyList[18], title=col_titles[18],width=100),                                                 # 18, waypoint is a string like 'gate_1' or 'point_1'
            TableColumn(field=keyList[19], title=col_titles[19],width=100,formatter=NumberFormatter(format="0,0")),         # 19
            TableColumn(field=keyList[20], title=col_titles[20],width=100),                                                 # 20
            TableColumn(field=keyList[21], title=col_titles[21],width=100),                                                 # 21
            TableColumn(field=keyList[22], title=col_titles[22],width=100,formatter=NumberFormatter(format="0,0.00")),      # 22
            TableColumn(field=keyList[23], title=col_titles[23],width=100,formatter=NumberFormatter(format="0,0.00")),      # 23
            TableColumn(field=keyList[24], title=col_titles[24],width=100),                                                 # 24
            TableColumn(field=keyList[25], title=col_titles[25],width=100),                                                 # 25
            TableColumn(field=keyList[26], title=col_titles[26],width=100),                                                 # 25
            #TableColumn(field=keyList[20], title=col_titles[27],width=100,formatter=NumberFormatter(format="0,0")),        # 26
]
# DateFormatter   doc: https://docs.bokeh.org/en/latest/docs/reference/models/widgets.tables.html#bokeh.models.widgets.tables.CellFormatter
# NumberFormatter doc: https://docs.bokeh.org/en/latest/docs/reference/models/widgets.tables.html#bokeh.models.widgets.tables.CellFormatter



# populate initial list of [col_titles] with all column titles (cfg. class is not available until lock button pressed)
multichoice_col_sel = MultiChoice(value=col_titles, options=col_titles, height=100, sizing_mode='stretch_width')
multichoice_col_sel.js_on_change("value", CustomJS(code="console.log('multi_choice: value=' + this.value, this.toString())"))

# choose the subset of all possible columns for display
def selected_columns(title_sel_list):
    # take in a list of titles and return a list of TableColumn()'s in the
    # same order as [titles] (for a common, predictable user experience)
    cols_subset=[]
    for i,item in enumerate(col_titles):
        if item in title_sel_list:
            print('\ti={0}, item={1}'.format(i,item))
            cols_subset.append(table_columns[i])
    return cols_subset


# initialize the DataTable with all columns ( this is before config file is chosen in scenario_lock_toggle_handler )
cols_subset = selected_columns( multichoice_col_sel.value )
veh_table = DataTable(source=table_source, columns=cols_subset, width=screen_width, height=220, header_row=True, editable=True) # height=200 will fit 7 vehicles, but not 8

ds_new = dict(veh_table.source.data) # make shallow copy of current table data



# sensor data table
sensor_data = dict(
        vid          = [], # 0
        vehName      = [], # 1
        )
sensor_source = ColumnDataSource(sensor_data)
sensor_cols = []
#for k in sensor_data.keys():
#    sensor_cols.append( TableColumn(field=k,title=k) )

sensor_table = DataTable(source=sensor_source, columns=[], width=screen_width, header_row=True) # editable=True, height=2000
sen_new = dict(sensor_table.source.data) # make shallow copy of current table data






# -----------------------------------------------------------------------------
def update_table():
    #ds_new = dict( veh_table.source.data ) # get snapshot of current table data
    
    print('\tmultichoice_col_sel={0}'.format(multichoice_col_sel.value))
    print('-------------------')
    cols_subset = selected_columns( multichoice_col_sel.value )
    print('\tcols_subset={0}'.format( cols_subset ))
    print('\t-------------------')
    veh_table.columns=cols_subset # dynamically changing columns!
    


# -----------------------------------------------------------------------------
bt_disp_cols = Button(label="Update Columns" , button_type="warning", width=bt_width)
bt_disp_cols.on_click(update_table)



# ==============================================================================
# =                     END:   vehicle table                                   =
# ==============================================================================





# ------------------------------------------------------------------------------
# create a callback to update the browser's uptime counter and vehicle table
dt = 1000 # (ms) browser update rate specified in add_periodic_callback()
t0=datetime.now()
def periodic_callback_update_browser():
    tNow = datetime.now()
    uptime_str = 'dashboard uptime [{0}]'.format( str(tNow-t0).split('.')[0] ) # truncate microseconds on uptime
    tNow_str   = 'Currently: [{0}]'.format( tNow.strftime("%c") )
    uptime_bar.text = tNow_str + ", " + uptime_str
    
    if eNewUdp.is_set()==True: # new udp message(s) just came in since last periodic callback evaluation
        #print('\nds_new:'), pprint.pprint(ds_new),         print('\n')        
        veh_table.source.data = ds_new # update table with all updates since last periodic_callback_update_browser()
        
        # first time through, sensor_table columns is empty, so populate with sensor_cols just created from incoming msg['sensorData']
        if len(sensor_table.columns)==0:
            sensor_table.columns=sensor_cols
        
        # update sensor_table with most recent values compiled from udp_listener_thread()
        sensor_table.source.data = sen_new # update table with all updates since last periodic_callback_update_browser()
        
        if eRSGPS.is_set()==False: # flag for auto-setting Ready-Set-Go-Pause-Stop button
            RSGPS_buttons.disabled = False # enable the Ready-Set-Go-Pause-Stop button
            RSGPS_buttons.active = ds_new['runState'][0]-1 # assign this runState, which assumes all vehicles are in this runState (element [0] is one vehicle's runState)
            eRSGPS.set() # set to True to prevent subsequent assignments




# arrange all map views in a grid layout then add to the document
layout = layout([
    [description],
    [uptime_bar],
    [scenario_file_select,scenario_lock_toggle],
    [core_ON_OFF],
    [veh_launch_toggle],
    [RSGPS_buttons],
    [bt_map_launch,bt_map_kill,bt_subproc2,bt_space,bt_disp_cols,bt_logfile_size],
    [web_console],
    [multichoice_col_sel],
    [veh_table],
    [sensor_table] ]) #, sizing_mode='scale_width') # "fixed", "stretch_both", "scale_width", "scale_height", "scale_both"

curdoc().add_root(layout)
curdoc().add_periodic_callback(periodic_callback_update_browser, dt) # <-- this controls browser update frequency
curdoc().title = "MoVE Experiment Control and Live Data Display"


# start blocking thread for launching background processes with a button
eProc = Event()
qProcButton = Queue() # queue for sending commands to launch in the host operating system
tProc = Thread(target=blocking_call_subprocess, args=(eProc,qProcButton),daemon=True) # daemon==True allows thread to exit when Bokeh captures ctrl+c
tProc.start() # press button, start thread




# start udp listener thread
#qUdp    = Queue() # queue to get udp data out of the udp_listener() thread and into Bokeh's main thread
#qRSGPS  = Queue() # so udp thread can turn on Ready-Set-Go-Pause-Stop button
eRSGPS  = Event() # initially False; this toggle re-evaluates Ready-Set-Go-Pause-Stop button from incoming udp data (at startup and every time Core is turned on)
e       = Event() # for signaling exit to *all* threads simultaneously (except main() )
eNewUdp = Event() # for notifying periodic callback that new udp data arrived; Event default is_set()==False




# start prioritize() process
pUdp = Thread(name='udp_listener', target=udp_listener_thread,args=(eNewUdp,e,debug),daemon=True) # daemon==True allows thread to exit when Bokeh captures ctrl+c)
#time.sleep(5)
pUdp.start()







