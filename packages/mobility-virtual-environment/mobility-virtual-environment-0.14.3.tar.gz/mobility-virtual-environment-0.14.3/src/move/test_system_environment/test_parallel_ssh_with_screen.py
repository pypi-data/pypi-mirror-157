#!/usr/bin/env python3
#
# Marc Compere, comperem@gmail.com
# created : 18 Aug 2019
# modified: 23 Jun 2022
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


# ------------------------------------------------------------------------------
# python which() function from: https://stackoverflow.com/a/34177358/7621907
def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    
    # from whichcraft import which
    from shutil import which
    
    return which(name) is not None
# ------------------------------------------------------------------------------




try:
    from pssh.clients import ParallelSSHClient
    print('import ParallelSSHClient:                      [success]')
except ImportError:
    print('error! parallelssh cannot be imported. fix before proceeding')
    exit(-1)




#print('\nscreen is used to launch multiple vehicle models')
screen_installed = is_tool('screen')
#print('pip3_installed={0}'.format(pip3_installed))
if screen_installed==True:
    print('screen installed?                              [ {0}  ]'.format(screen_installed) )
else:
    print('\nscreen installed?                              [ {0} ] - screen not installed'.format(screen_installed) )
    print('                                                           try:   sudo apt-get install screen\n')







# ----------------------------------------------------------------------
# -------  can parallel-ssh be used to launch a simple command?  -------
# ----------------------------------------------------------------------
output = {} # init empty dictionary
hostList = ['localhost', 'localhost']
nHosts = len(hostList)

if screen_installed == True:
    print('test 1 of 2: testing parallel-ssh', end='')
    try:
        client = ParallelSSHClient( hostList )
        output = client.run_command('which screen',return_list=True)
        print('              [success]')
    except:
        output=[] # empty list
        print('\n    error! test 1 of 2: could not execute simple parallelssh command. fix before proceeding')
        print(' ')
        print('The Python parallelssh package was imported correctly so')
        print('this is likely a password-less ssh login issue.')
        print(' ')
        print('You should be able to log in to the local machine (i.e. localhost)')
        print('securely but without a password.')
        print(' ')
        print('Does this command work at a terminal command prompt?')
        print(' ')
        print('    ssh localhost')
        print(' ')
        print('if not, setup password-less ssh login at the link below and retry this test script')
        print('    https://askubuntu.com/a/46935/652884')
        print(' ')
        





# if parallel-ssh worked immediately above, then try again with 'screen'
if output.__len__() > 0:
    # ----------------------------------------------------------------------
    # -------      can parallel-ssh be used to launch screens?       -------
    # ----------------------------------------------------------------------
    output = {} # init empty dictionary
    cmd=[] # init empty list
    
    print('test 2 of 2: testing parallel-ssh with screen', end='')
    try:
        # construct per-host commands
        for i in range(len(hostList)):
            cmd.append( 'screen -dm -S vid{0} sleep 10'.format(i+1) ) # assuming sleep command is available
            #print('\n{}'.format(cmd))
        output = client.run_command( '%s', host_args=tuple(cmd) ,return_list=True)
        print('  [success]')
    except:
        output=[] # empty list
        print('\nerror! test 2 of 2: could not execute parallelssh command with screen. fix before proceeding')




print('done.', flush=True)
