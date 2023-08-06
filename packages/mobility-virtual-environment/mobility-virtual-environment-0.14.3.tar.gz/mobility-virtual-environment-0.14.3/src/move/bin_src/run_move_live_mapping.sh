#!/bin/bash
#
# bash shell script to run MoVE mapping client
# built using the Bokeh visualization library (https://bokeh.org/)
#
# this script detects it's location, then loads the scenario config file
# from the ../scenarios folder.
# all leading directories, and the trailing .cfg are eliminated. only the config
# file basename is used to load the config file in $MOVE_BASE/scenario
#
# this script's requirements:
# - must allow execution from anywhere at a bash command prompt
# - must allow execution by subprocess.Popen() within the bokeh dashboard
# - must accept 2 arguments '-f <cfg_filename>' where <cfg_filename> can
#   be:
#       - any typical folder+file name         like /home/user/scenario.cfg
#                                                or ../scenario/live_6_veh.cfg
#       - any config file without directories like: myScenario.cfg
#   everything except the base config filename is eliminated and then searched
#   as $MOVE_BASE/scenario/myScenario.cfg
#
# - motivation to point to a real file like ../scenario/default.cfg is still
#   valid to ensure the filename is correct and is in ./$MOVE_BASE/scenario
#
#
# ------------------------------------------------------------------------------
# if LOCAL:
#       ./run_move_live_mapping.sh -f ../scenario/live_6_veh.cfg
# executes:
#       bokeh serve --port=$PORT --show move_live_mapping.py --args -f $2
#
# ------------------------------------------------------------------------------
# if REMOTE:
#       ./run_move_live_mapping.sh -f ../scenario/live_6_veh.cfg remote
# executes:
#       bokeh serve --allow-websocket-origin=$REMOTE_IP:$PORT  move_live_mapping.py --args -f ../scenario/live_6_veh.cfg
#
#
#
# Marc Compere, comperem@erau.edu
# created : 17 Dec 2019
# modified: 25 Jun 2022




# ------------------------------------------------------------
# Q: where does this script reside in local filesystem?
# two answers: (a) source code ./bin_src, or (b) installed python package ./bin
# from: https://stackoverflow.com/a/246128/7621907
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";
echo "script [$0] resides in [$SCRIPT_DIR]"




# ------------------------------------------------------------
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

echo "changing directories to [$MOVE_BASE]"
cd $MOVE_BASE
cd data_displays # move_live_mapping.py is expecting to run from ./move/data_displays




# ------------------------------------------------------------
# Q: using REMOTE argument?
#REMOTE_IP='72.239.121.233'
REMOTE_IP='localhost'
PORT=5007
#bokeh_script='move_live_mapping.py'
#bokeh_script='../data_displays/move_live_mapping.py'
bokeh_script="$MOVE_BASE/data_displays/move_live_mapping.py"


if [ "$3" == "remote" ];
then
    MY_ARG="--port=$PORT --allow-websocket-origin=$REMOTE_IP:$PORT"
    echo using $MY_ARG
    echo
    echo open: $REMOTE_IP:$PORT
    echo
else
    MY_ARG="--port=$PORT --show"
    echo using $MY_ARG
fi    




# ------------------------------------------------------------
# Q: what config file argument was passed?
# from: https://stackoverflow.com/a/1371283/7621907
CFG_FILE=$2              # to assign to a variable
CFG_FILE=${CFG_FILE##*/} # strip all leading directories
echo "config file provided: $2"
echo "config file used    : $MOVE_BASE/scenario/$CFG_FILE"

#exit 0




# ------------------------------------------------------------
# Ok, ready to run the bokeh command with associated config file argument
if [ "$1" == "-f" -a "$2" != "" ];
then
    echo "running 'bokeh serve --log-level debug $MY_ARG $bokeh_script --args -f $MOVE_BASE/scenario/$CFG_FILE"
    echo
    #bokeh serve --show move_live_mapping.py --args -f ../scenario/default.cfg
    #bokeh serve --port=$PORT --show --log-level debug move_live_mapping.py --args -f $2
    #bokeh serve --port=$PORT --show move_live_mapping.py --args -f $2
    bokeh serve $MY_ARG $bokeh_script --args -f $MOVE_BASE/scenario/$CFG_FILE
    #bokeh serve $MY_ARG $bokeh_script --args -f ./scenario/$2
else
    echo "a command line argument must be provided to designate the config file"
    echo "as relative or absolute path to config file."
    echo
    echo "usage examples:"
    echo "                  $0 -f ../scenario/default.cfg"
    echo "                  $0 -f /home/user/move/scenario/default.cfg"
    echo "                  $0 -f default.cfg"
    echo
    echo "                  all these examples will search for default.cfg"
    echo "                  in $MOVE_BASE/scenario"
    echo
    echo "                  currently MOVE_BASE=$MOVE_BASE"
    echo
    echo "BASH_ARGC=$BASH_ARGC"
    echo "BASH_ARGV[0]=${BASH_ARGV[0]}"
fi






# open http://localhost:5006/move_live_mapping



