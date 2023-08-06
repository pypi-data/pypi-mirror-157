#!/usr/bin/python3
#
# this MoVE core vehicle model and config file synchronization function uses
# the underlying operating system's rsync() command to replicate the local
# directories ../veh_model and ../scenario to the remote machine's runtime
# directory to ensure the parallel-ssh commands that launch vehicle processes
# use the latest and greatest vehicle model code and config file options
# specified in the MoVE source code on the machine from which MoVE core is executed.
#
# this function gets run each time MoVE's built-in vehicle models get launched
# when this is run: ./MoVE/vX.YY/core/main_veh_proc_launcher.py
#
# Marc Compere, comperem@erau.edu
# created : 12 Jan 2019
# modified: 14 Oct 2020
#
# ---
# Copyright 2018, 2019 Marc Compere
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
import socket # for socket.gethostname()
import subprocess

def sync_vehicle_and_config(srcBase,veh_host_ip,username,runtimeDir):
    
    srcRel  = ['../scenario', '../veh_model', '../routes'] # list of sub-dirs to copy into runtime dest directory
    #dest = 'comperem@matrix:/tmp/MoVE' # runtime directory for built-in vehicle models and live-GPS-followers;
                                       # ssh keys must already be setup for password-less ssh login
    
    dest = '{0}@{1}:{2}'.format(username,veh_host_ip,runtimeDir) # user@host:/runtimeDir on remote host according to rsync and scp format
    print('preparing to rsync a runtime copy of MoVE using ssh login with username={0} to:  {1}'.format(username,dest))

    # copy python source files in core machine's source ../veh_model and ../scenario
    # to the remote machine's runtime direcotry (even if remote machine is localhost)
    #
    # - rsync is a unix/linux command line utility that uses ssh to securely make diff-based copies
    #   synchronizing files from source to dest across the network
    # - note the --exclude's to avoid copying unnecessary folders in source veh_model folder
    #  - rsync will create any new directories to complete the sync command
    #
    # note: the -L means turn sym links in source to file in target in /tmp
    try:
        for item in srcRel:
            src = srcBase + '/' + item
            print( '- - - - - -\nrsync()-ing [{0}] from [{1}] to [{2}]..'.format(src,socket.gethostname(),dest) )
            p = subprocess.run(["rsync", "-aLvh", "--exclude=dev", "--exclude=postProc", "--exclude=__pycache__", src, dest], stdout=subprocess.PIPE, check=True)
            print(p.stdout.decode('utf-8'))
        print('..done.\n- - - - - -')

    except subprocess.CalledProcessError as err:
        print( "\n\noops - caught an rsync() subprocess error: {0}".format(err) )
        print( "exiting.")
        sys.exit(-1)
    
    
    # make sure all relevant files are executable for runtime
    # /tmp/MoVE/scenario/readConfigFile.py
    # /tmp/MoVE/veh_model/main_veh_model.py
    # from config file, it is likely that: runtimeDir='/tmp/MoVE'
    executableFiles = ['/scenario/readConfigFile.py', '/veh_model/main_veh_model.py' ]
    try:
        #print(runtimeDir)
        for name in executableFiles:
            print( 'changing permissions to execute, +x, for [{0}]...'.format( runtimeDir + name ) , end='')
            os.chmod( runtimeDir + name , 0o755) # bizarre octal format
            print('done.')

    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise # raise the error and stop execution
        print( "exiting.")
        sys.exit(-1)
        




# this function is executable at the command line from ./core folder to
# test sync functionality:
#
#   ./sync_function.py
#
if __name__ == "__main__":
    #veh_host_ip = 'matrix'
    #veh_host_ip = 'tensor'
    veh_host_ip = 'localhost'
    username='comperem'
    runtimeDir='/tmp/MoVE_comperem'
    sync_vehicle_and_config(veh_host_ip,username,runtimeDir)
