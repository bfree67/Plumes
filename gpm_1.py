# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 12:01:06 2019
Python 3.5
@author: Brian

Implement a Gaussian plume model using stability class coefficients
Coefficients from G. A. Davidson,1990, A Modified Power Law Representation 
of the Pasquill-Gifford Dispersion Coefficients, J. of the Air & Waste Management Association,Vol 40:8
doi:10.1080/10473289.1990.10466761
"""

import numpy as np
import math

def PQ_sigma_y(A):
    ### stability class coefficients for sigma_y
    if A == 'A':
        PQ_sy_class = np.asarray([209.6, 0.8804, -0.006902])  ## Class A
    if A == 'B':
        PQ_sy_class = np.asarray([154.7, 0.8932, -0.006271])  ## Class B
    if A == 'C':
        PQ_sy_class = np.asarray([103.3, 0.9112, -0.004845])  ## Class C
    if A == 'D':
        PQ_sy_class = np.asarray([68.28, 0.9112, -0.004845]) ## Class D
    if A == 'E':
        PQ_sy_class = np.asarray([51.05, 0.9112, -0.004845]) ## Class E
    if A == 'F':
        PQ_sy_class = np.asarray([33.96, 0.91121, -0.004845]) ## Class E

    ### assign coefficients
    ay = PQ_sy_class[0]
    by = PQ_sy_class[1]
    cy = PQ_sy_class[2]
    
    return ay, by, cy

def PQ_sigma_z(A):
    ### stability class coefficients for sigma_z
    if A == 'A':
        PQ_sz_class = np.asarray([417.9, 2.058, 0.2499])  ## Class A
    if A == 'B':
        PQ_sz_class = np.asarray([109.8, 1.064, 0.01163])  ## Class B
    if A == 'C':
        PQ_sz_class = np.asarray([61.14, 0.9147, 0.])  ## Class C
    if A == 'D':
        PQ_sz_class = np.asarray([30.38, 0.7306, -0.032]) ## Class D
    if A == 'E':
        PQ_sz_class = np.asarray([21.14, 0.6802, -0.04522]) ## Class E
    if A == 'F':
        PQ_sz_class = np.asarray([13.72, 0.6584, -0.05367]) ## Class E

    ### assign coefficients
    az = PQ_sz_class[0]
    bz = PQ_sz_class[1]
    cz = PQ_sz_class[2]
    
    return az, bz, cz

def C(x,y,z):
 ### calculates Gaussian plume concentration at a point in space
 ### Continuous, Steady-state, Source at Ground Level, 
 ### Wind Moving in x Direction at constant velocity U

    MQ = 20 ## emission rate in g/second
    U = 3 ## wind speed in m/s
     
    x_km = x/1000  ### convert input distance to km
    ay,by,cy = PQ_sigma_z('A')
    az, bz, cz = PQ_sigma_y('A')
    
    sig_y = ay*(x_km**(by+cy*math.log(x_km))) ## output in m
    sig_z = az*(x_km**(bz+cz*math.log(x_km)))  ## output in m
    
    #print(sig_y, sig_z)

    exp_term = math.exp(-.5*((y**2)/sig_y**2)+(z**2)/(sig_z**2))

    C = (MQ/(math.pi*U*sig_y*sig_z))*exp_term

    return C        
            
Coord = [(650,40),(500,30),(150,100)]       
coord_n = len(Coord)
for pt in range(coord_n):
    x,y = Coord[pt]
    print(pt,C(x,y,0))