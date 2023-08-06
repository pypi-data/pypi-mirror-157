import liblip as ll
import sys
import math
import random

# test function, here just a product of sin(2x)sin(2y),...
def fun2( dat, dim):
    s = 1.0
    for j in range( dim): s *= math.sin( 2 * dat[j])
    return s


dim = 3
npts = 1500
lip_const = 10.0
K2 = 100
        
print( "-- test object oriented start --");        

    
print( "-- test object oriented end --")