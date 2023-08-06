#!/usr/bin/python3
#
# srt.py - soft real time prints the communication interval and wall-clock elapsed time
#
# the question is: how small can the communication interval
#                  be set while still achieving a reasonable SRT error?
# the answers are OS system dependent.
#
# usage:
#     ./srt.py        (default is 1.0 second communication interval, cInt)
#     ./srt.py 0.1    (set cInt=1/10'th second for 10Hz communication intervals)
#
# Marc Compere, comperem@gmail.com
# created : 16 Apr 2017
# modified: 30 May 2018
#
# --------------------------------------------------------------
# Copyright 2018, 2022 Marc Compere
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

import sys
import time
import subprocess



# BEGIN: srt() ------------------------------------------------------------
# srt() - soft real time code to ensure long duration simulation
#         time proceeds with wall-clock time
def srt( tStart, tNow, cInt, srtCnt, elapsedErrAccum, srtOutput ): # (0/1) print to console or not

    # loopTime: start
    tLast                = tNow        # capture last loop timestamp
    tNow                 = time.time() # what time is it now?    (wall-clock time)
    loopTime             = tNow - tLast # (s) loopTime is used only for monitoring; can be removed
    elapsedTimeSim       = (srtCnt)*cInt # (s) elapsed simulated time is srtCnt*dt, 'cInt' == Communication Interval
    elapsedTimeWallClock = tNow - tStart # (s) total elapsed wall-clock time as measured by system clock
    elapsedErr         = elapsedTimeSim - elapsedTimeWallClock # measured wall-clock time must match N occurrences of cInt, the communication interval
    elapsedErrAccum    = elapsedErrAccum + elapsedErr


    srtSleepLaw=0 # (0/1) select which method for achieving soft-real-time
    if srtSleepLaw==0:
        # the delay law is a PI controller. adjustment is on current time error and accumulated time error
        sleepTime = max(0.0 , cInt + elapsedErr + 0.3*elapsedErrAccum ) # sleep time must always be >= 0.0 seconds
    else:
        sleepTime = max(0.0 , elapsedErr  + 0.3*elapsedErrAccum )

    time.sleep( sleepTime ) # sleep just the right amount to communicate at wall-clock intervals

    srtMargin = 100*sleepTime/cInt
    if (srtOutput>0):
        print("  srt margin [ {0:-6.1f} ] (%),  srt pace err [{1:10.6f}] (s)   ".format( srtMargin, elapsedErr) , end="")  # no EOL, no newline
    elif (srtOutput>2):
        print("  srt margin [ {0:-6.1f} ](%),  elapsedErr [ {1:0.6f} ](s),  elapsedErrAccum [ {2:0.6f} ](s),  loopTime [ {3:0.6f} ],  srtCnt [ {4:i} ]" \
                .format(srtMargin, elapsedErr, elapsedErrAccum, loopTime, srtCnt) , end="") # no EOL, no newline
    srtCnt=srtCnt+1

    return [tNow, srtCnt, srtMargin, elapsedErr, elapsedErrAccum]
# END: srt() ------------------------------------------------------------


if __name__ == "__main__":

    if len(sys.argv)>1:
        cInt = float( sys.argv[1] ) # set communication interval from command line
        continuous=1
        print('running continuously')
    else:
        continuous=0
        cInt = 1.0 # (s) communication interval for console output

    print("communication interval for console output = [ {0:0.6f} ](sec)".format(cInt) )

    clkRes = time.get_clock_info('time').resolution
    print("OS                     [ %s \t]"        % sys.platform )
    print("clock resolution       [ %0.10f \t](s)" % clkRes )
    print("communication interval [ %0.6f \t](s)" % cInt )

    # ---- srt() variables -----
    srtCnt=0
    elapsedErrAccum=0.0
    srtOutput = 1 # (0/1/2)
    tStart=time.time() # seconds since Jan 1, 1970 00:00:00; a massive number, e.g. 1517836676.8555398
    tNow=tStart
    print("soft-real-time output? [ {} \t](s)".format(srtOutput) )
    print("Start: ", time.ctime(), ", tStart: ", tStart, "(s)" )
    # --------------------------



    while ( continuous==1 or srtCnt < 20 ):

        # enforce soft-real-time in the while-loop ticking along at cInt (s), the communication interval
        #[tNow, srtCnt, elapsedErrAccum] = srt( tStart, tNow, cInt, srtCnt, elapsedErrAccum, srtOutput ) # (0/1) console output?
        [tNow, srtCnt, srtMargin, elapsedErr, elapsedErrAccum] = srt( tStart, tNow, cInt, srtCnt, elapsedErrAccum, srtOutput ) # (0/1) console output?

        elapsedTimeSim       = (srtCnt)*cInt # (s) elapsed simulated time is srtCnt*dt, 'cInt' == Communication Interval
        elapsedTimeWallClock = tNow - tStart # (s) total elapsed wall-clock time as measured by system clock

        # execute other code here within the loop being ticked at cInt
        time.sleep(0.3)

        if (srtOutput>0):
            print("  elapsedTimeSim [ %0.6f ](s),  elapsedTimeWallClock [ %0.6f ](s)" \
                    % (elapsedTimeSim, elapsedTimeWallClock))

    print("End  : ", time.ctime(),", srtCnt=", srtCnt )
