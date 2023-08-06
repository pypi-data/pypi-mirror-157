#!/usr/bin/env python3
#
# script test for required Python modules
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

anyFailed=False




#print('\npip3 is used to install python3 packages')
#pip3_installed = is_tool('pip3')
#if pip3_installed==True:
#    print('pip3 installed?              [ {0}  ]'.format(pip3_installed) )
#else:
#    print('\npip3 installed?              [ {0} ] - pip3 not installed'.format(pip3_installed) )
#    print('                               try:   sudo apt install python3-pip\n')




try:
    import os
    import sys
    import csv
    import time
    import code
    import copy
    import queue
    import pprint
    import random
    import select
    import socket
    import struct
    import string
    import logging
    import threading
    import traceback
    import subprocess
    import configparser
    import distutils
    import multiprocessing
    from math import sin,cos,atan2,pi,copysign,sqrt,floor,isinf
    from datetime import datetime
    from collections import deque
    from shutil import which # only for test_screen_bash_parallel_ssh.py
    print('import base python packages: [success]')
except ImportError:
    print('\nimport base python packages:   error! a standard python 3 package was unable to be imported. fix before proceeding\n')
    anyFailed=True




try:
    import numpy as np
    print('import numpy:                [success]')
except ImportError:
    print('\nimport numpy:                  error! numpy import failed. fix before proceeding')
    #print('                               try:   sudo apt-get install python3-numpy\n')
    print('                               try:   pip3 install numpy\n')
    anyFailed=True




try:
    import msgpack
    print('import msgpack:              [success]')
except ImportError:
    print('\nimport msgpack:                error! msgpack import failed. fix before proceeding')
    print('                               try:   pip3 install msgpack\n')
    anyFailed=True




try:
    import msgpack_numpy as m
    print('import msgpack_numpy:        [success]')
except ImportError:
    print('\nimport msgpack_numpy:          error! msgpack_numpy import failed. fix before proceeding')
    print('                               try:   pip3 install msgpack-numpy\n')
    anyFailed=True




try:
    import utm
    print('import utm:                  [success]')
except ImportError:
    print('\nimport utm:                    error! utm import failed. fix before proceeding')
    print('                               try:   pip3 install utm\n')
    anyFailed=True




try:
    from pssh.clients import ParallelSSHClient
    print('import ParallelSSHClient:    [success]')
except ImportError:
    print('\nimport ParallelSSHClient:      error! ParallelSSHClient import failed. fix before proceeding')
    print('                               try:   pip3 install parallel-ssh\n')
    anyFailed=True




try:
    import bokeh
    print('import bokeh:                [success]')
except ImportError:
    print('\nimport bokeh:                  error! bokeh import failed. fix before proceeding')
    print('                               try:   pip3 install bokeh\n')
    anyFailed=True




try:
    import matplotlib.pyplot as plt
    print('import matplotlib.pyplot:    [success]')
except ImportError:
    print('\nimport matplotlib.pyplot:      error! matplotlib.pyplot import failed. fix before proceeding')
    print('                               try:   pip3 install matplotlib\n')
    anyFailed=True




print('done.')
if anyFailed==True:
    print('\n\n\tsome tests failed!')
    print('\n\treview and fix.\n')
else:
    print('\n\n\tall tests passed which means all python libraries are installed for MoVE to work.')
    print('\n\tnext: make sure openssh is installed and password-less login works')
    print('\t      with:\n')
    print('\t           python3 test_parallel_ssh_with_screen.py\n')


