# PyParticles : Particles simulation in python
# Copyright (C) 2012  Simone Riva
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import sys
import scipy.spatial.distance as dist

import pyparticles.forces.force as fr

class Gravity( fr.Force ) :
    def __init__(self , size , dim=3 , m=None , Consts=1.0 ):
        
        self.__dim = dim
        self.__size = size
        self.__G = Consts
        self.__A = np.zeros( ( size , dim ) )
        self.__Fm = np.zeros( ( size , size ) )
        self.__V = np.zeros( ( size , size ) )
        self.__D = np.zeros( ( size , size ) )
        self.__M = np.zeros( ( size , size ) )
        if m != None :
            self.set_masses( m )
        
        
    
    def set_masses( self , m ):
        self.__M[:,:] = m
        
        #print(" --- M ----")
        #print( self.__M[:,:] )
        #print()
    
    def update_force( self , p_set ):
        
        self.__D[:] = dist.squareform( dist.pdist( p_set.X , 'euclidean' ) )
        
        #print(" --- D ----")
        #print( self.__D[:,:] )
        #print()
        
        self.__Fm[:] = - self.__G * self.__M[:] / ( ( self.__D[:] ) ** 3.0 )

        for j in range( self.__size ) :
            self.__Fm[j,j] = 0.0
        
        #print(" --- Fm ----")
        #print( self.__Fm[:,:] )
        #print()        
        
        for i in range( self.__dim ):
            self.__V[:,:] = p_set.X[:,i]
            self.__V[:,:] = ( self.__V[:,:].T - p_set.X[:,i] ).T 
                        
            self.__A[:,i] = np.sum( self.__Fm * self.__V[:,:] , 0 )
        
        #print(" --- F ----")
        #print( self.__F )
        #print()
        
        return self.__A
    
    def getA(self):
        return self.__A
    
    A = property( getA )


    def getF(self):
        return self.__A * self.__M[:,0]
    
    F = property( getF )