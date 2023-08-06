#!/usr/bin/env bash
#
# bash shell script to run MoVE's command and display dashboard
# built in the web-enabled Bokeh visualization library (https://bokeh.org/)
#
# this script's requirements:
# - must allow execution from anywhere at a bash command prompt
# - must self-detect if it's being run:
#    - from ./bin_src as source code during development
#      or
#    - from ./bin as an installed python package.
#
#
# ------------------------------------------------------------------------------
# if LOCAL:
#       ./run_move_dashboard.sh
# executes:
#       bokeh serve --show $bokeh_script
#
# ------------------------------------------------------------------------------
# if REMOTE:
#       ./run_move_dashboard.sh remote
# executes:
#       bokeh serve --allow-websocket-origin=$IP:$PORT $bokeh_script
#
#
# Marc Compere, comperem@erau.edu
# created : 17 Dec 2019
# modified: 04 Jul 2022


# -------------------------------------------------
# Q: where does this script reside?
# two answers: (a) source code ./bin_src, or (b) installed python package ./bin
# from: https://stackoverflow.com/a/246128/7621907
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";
echo "script [$0] resides in [$SCRIPT_DIR]"


# -------------------------------------------------
# Q: what is move base dir? If source:          it's $SCRIPT_DIR/..
#                           If package install: it's in python's import dir
SCRIPT_BASENAME=`basename $SCRIPT_DIR`
if [[ $SCRIPT_BASENAME == "bin_src" ]];
then # move development source tree
    echo "  SCRIPT_BASENAME=[$SCRIPT_BASENAME] --> assume execution from move source"
    MOVE_BASE=$SCRIPT_DIR/..
else
    echo "  SCRIPT_BASENAME=[$SCRIPT_BASENAME] --> assume execution from installed python package"
    MOVE_BASE=` python3 -c "import move as _; print( _.__path__[0] )" `
fi
echo "using MOVE_BASE=[$MOVE_BASE]"
# ./v1.14_dev/src/move/bin_src/..

#exit 0


echo "changing directories to [$MOVE_BASE]/data_displays"
cd $MOVE_BASE/data_displays # run bokeh from $MOVE_BASE


REMOTE_IP='72.239.121.233'
PORT=5006
#bokeh_script='move_dashboard.py'
bokeh_script="$MOVE_BASE/data_displays/move_dashboard.py"
#bokeh_script='move_dashboard_dev.py'

if [ "$1" == "remote" ];
then
    MY_ARG="--port=$PORT --allow-websocket-origin=$REMOTE_IP:$PORT --show"
    echo using $MY_ARG
    echo
    echo open: $REMOTE_IP:$PORT
    echo
else
    MY_ARG="--port=$PORT --show"
    echo using $MY_ARG
fi    


#PORT=5007
#bokeh serve --port=$PORT --show gps_move_live_mapping.py

echo "running 'bokeh serve $MY_ARG $bokeh_script"
bokeh serve $MY_ARG $bokeh_script



# LOCAL:
# open http://localhost:5006/move_dashboard
#
# REMOTE:
# open http://72.239.121.233:5006/move_dashboard


