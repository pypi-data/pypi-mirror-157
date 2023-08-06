# utility functions supporting the vehicle model, main_veh_model.py
#
# Marc Compere, comperem@gmail.com
# created : 14 Jul 2018
# modified: 05 Aug 2020
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

from math import floor,sin,cos
import numpy as np
#from scipy import io
from collections import deque # moving average window


# simple moving average is a subset of all FIR filters - this slows down the
# soft-real-time margin and overrun numbers as they stream by
#
# grow a double-ended que until it is the window length, then slide the window, FIFO
def update_window(y,u,n):
    if len(y)<n:
        y.append(u) # append to the right side of the deque list (this is the newest, or entering data)
    else:
        y.append(u) # append 1 number to the right side (this is the newest, or entering data)
        y.popleft() # remove 1 number from the left side (this is the oldest, or exiting data)
    return y

# simple moving average - call this function repeatedly with new single-point updates
#    sma   - simple moving average, scalar
#    y     - deque containing window of last N samples
#    u_new - new data point, new sample
#    n     - window size
def simple_moving_average(sma,y,u_new,n):
    if len(y) < n:
        u_oldest = 0.0
    else:
        u_oldest = y[0]
    delta = (u_new - u_oldest)/n
    smaNew = sma + delta
    y = update_window(y,u_new,n)
    return [smaNew , y]






# BEGIN: rk4() ------------------------------------------------------------
# take a single step of stepsize, h
def rk4_single_step(f, t, x, u, h):
    k1 = h * f(t, x, u)
    k2 = h * f(t + 0.5 * h, x + 0.5 * k1, u)
    k3 = h * f(t + 0.5 * h, x + 0.5 * k2, u)
    k4 = h * f(t + h, x + k3, u)
    tNew = t + h
    xNew = x + (k1 + k2 + k2 + k3 + k3 + k4) / 6
    return tNew, xNew
# END: rk4() --------------------------------------------------------------




# BEGIN: xdot=f(t,x,u) ----------------------------------------------------
# f() defines the vehicle as a dynamic system with state-rates: xdot=f(t,x,u)
def f( t, x, u ):
    # this function returns the state-rates, xDot[] = f(t,x,u)
    #
    # this vehicle can represent as simple car (for pitch==0)
    # or a fixed-wing aircraft
    #
    # vehicle body-fixed frame is not SAE; recall SAE is: +x forward, +y out passenger side window, +z down
    #
    # here,
    # vehicle body-fixed frame is ENU counterpart: +x forward, +y out driver side window, +z up
    # this is done this way because the Web Mercator projection is ENU (East-North-Up)
    # references:
    # (a) https://en.wikipedia.org/wiki/Local_tangent_plane_coordinates
    # (b) http://www.dirsig.org/docs/new/coordinates.html
    # (c) ./Documentation/Compere_handwritten_notes_SAE_ENU_NED_and_all_that.pdf
    #
    # for detailed derivation see: 01b_A Simple 2D Kinematic Steering Model.pdf
    #                              from Compere's ME620 Adv. Veh. Dyn. course
    #                              the derivation is in SAE coords but the map
    #                              coords are ENU (East-North-Up) so these are
    #                              just as easily ENU coords.
    # ENU: X->East, Y->North, Z->Up  , psidot->CCW (rhr)
    # SAE: X->East, Y->South, Z->Down, psidot->CW  (rhr)
    # to convert between ENU and SAE, either direction:
    # (a) multiply Y-axis by -1, (b) multiply Z-axis by -1, multiply psidot by -1
    #
    # extract simple vehicle input commands
    delta=u[0] # (rad) steer cmd (+) is left turn, (normally + is right turn in SAE coords, but this is ENU, not SAE)
    speed=u[1] # (m/s) speed cmd
    pitch=u[2] # (rad) pitch cmd (+->nose up)
    v_z  =u[3] # (m/s) body-fixed z-axis velocity command for multi-rotors or VTOL fixed-wing aircraft
    #
    v_x = speed # (m/s) body-fixed x-vel
    b = 1.7   # (m) dist from cg to rear axle
    L = 2.74  # (m) wheelbase length
    psi = x[3] # (rad) psi, heading angle w.r.t. true North
    psiDot = delta*v_x/L # (rad/s) yaw rate
    T_transpose = np.array( [[cos(psi) ,-sin(psi)],
                             [sin(psi) , cos(psi)]] )
    v_xy=np.array( [v_x,b*psiDot] ) # (m/s) body-fixed vel
    v_XY = T_transpose @ v_xy   # inertial XY velocity
    v_Z  = v_x*sin(pitch) + v_z # inertial Z-dir rate in climb or descent, plus body-fixed z-velocity for multi-rotors or VTOL

    # x[0] = X   (m) inertial frame X-position
    # x[1] = Y   (m) inertial frame Y-position
    # x[2] = Z   (m) inertial frame Y-position
    # x[3] = psi (rad) vehicle yaw angle, or heading
    # return numpy array xdot = f(t,x,u)
    return np.array([
        v_XY[0], # (m/s) X-vel in inertial ENU XYZ frame
        v_XY[1], # (m/s) Y-vel in inertial ENU XYZ frame
        v_Z    , # (m/s) Z-vel in inertial ENU XYZ frame
        psiDot      ]   # (rad/s) yaw rate w.r.t. inertial ENU XYZ frame
    )
# END: xdot=f(t,x,u) ----------------------------------------------------







# ---------------------------
def myRem(x):
    return ( x-floor(x) )
# print(        myRem(3.14)     )    yields:   0.14000000000000012
# print( round( myRem(3.14),14) )    yields:   0.14
# ---------------------------



# find angle for vehicle to aim towards the gate
# from: point_to_perpendicular_line_in_space.py
# and : Compere_handwritten_notes_shortest_perpendicular_distance_from_point_to_line_in_space.2020.05.26.pdf
# compute angle from vehicle at point P to the next gate with end points at points A and B
def compute_perpendicular_angle_to_line_in_space(A,B,P,randNum=0.0):
    
    r_PA = A - P # (m) vector from P to A
    r_AB = B - A # (m) vector from A to B
    
    #print('r_PA={0}'.format(r_PA))
    #print('r_AB={0}'.format(r_AB))
    
    # s0 is unitless and indicates percentage proximity to pt_B (if s0=0.7, perpendicular point is 70% along the line from pt_A to pt_B) 
    s0 = -np.dot(r_PA,r_AB) / np.inner(r_AB,r_AB) # inner product is magnitude^2; same as:   np.linalg.norm(r_AB) * np.linalg.norm(r_AB)
    
    
    # -----------------------------
    # modification on 05 Aug 2020, to avoid ping-pong collection at one side of non-parallel gates;
    # randomize trajectory to 'other side' of gate; randNum must be on (0.0 1.0)
    randMag=0.2
    #if s0>0.5:
    if s0>randNum:
        s0=s0-randMag*randNum; # if perpendicular point is closer to pt_B, steer a bit to the center or towards pt_A
    
    #if s0<0.5:
    if s0<randNum:
        s0=s0+randMag*randNum; # if perpendicular point is closer to pt_A, steer a bit to the center or towards pt_B
    # -----------------------------
    
    
    # generate angle from point P to perpenducular intersection point
    # along line L at point L(s0) somewhere between points A and B
    L_s0  = A + s0*(B-A) # (m) point along line AB that is perpendicular to point P
    theta = np.arctan2( L_s0[1]-P[1] , L_s0[0]-P[0] ) # (rad) direction from point P to somewhere in the gate
    dist  = np.linalg.norm( L_s0-P ) # (m) dist from P to perpendicular intersection point, L(s0) 
    
    if s0<0:
        # output angle to point B b/c perpendicular intersection is behind A (this will steer vehicle to opposite post and change when veh is inside channel perpendicular to gate posts A-to-B
        theta = np.arctan2( B[1]-P[1] , B[0]-P[0] ) # (rad) aim for point A because P is left of gate (past A)
        dist  = np.linalg.norm( B-P ) # (m) dist from P to gate post B because s0<0
    
    if s0>1:
        # output angle to point A b/c perpendicular intersection is beyond B (this will steer vehicle to opposite post and change when veh is inside channel perpendicular to gate posts A-to-B
        theta = np.arctan2( A[1]-P[1] , A[0]-P[0] ) # (rad) aim for point B because P is to right of gate (past B)
        dist  = np.linalg.norm( A-P ) # (m) dist from P to gate post A because s0>1
    
    # which side is P on?
    r_AB_cross_AP = np.cross( np.append(r_AB,0) , np.append(-r_PA,0) )
    side = np.sign( r_AB_cross_AP[2] ) # (+) when point P is on the (+) side using RHR and +Z down; (-) when P on negative side
    
    return(s0,L_s0,theta,dist,side)


