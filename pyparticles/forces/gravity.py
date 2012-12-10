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
import scipy.spatial.distance as dist
import pyparticles.forces.force as fr

import pyparticles.pset.opencl_context as occ 

try:
    import pyopencl as cl
    import pyopencl.array as cla
except:
    ___foo = 0


class Gravity( fr.Force ) :
    r"""
    Compute the gravitational force between the particles

    The gravity between two particles is defined as follow:

    .. math::

        \mathbf{F}_{12}=-G \frac{m_1 m_2 }{r^2}\hat{r}_{12}

    Constructor
    
    :param    size:        the number of particles in the system
    :param    dim:         the dimension of the system
    :param    m:           a vector containig the masses
    :param    Const:       the gravitational constant
    """
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
        """
        Set the masses used for computing the forces.
        """
        self.__M[:,:] = m
        
        
    def update_force( self , p_set ):
        """
        Compute the force of the current status of the system and return the accelerations of every particle in a *size by dim* array
        """
        
        self.__D[:] = dist.squareform( dist.pdist( p_set.X , 'euclidean' ) )
        
        self.__Fm[:] = - self.__G * self.__M[:] / ( ( self.__D[:] ) ** 3.0 )
            
        np.fill_diagonal( self.__Fm , 0.0 )
                
        for i in range( self.__dim ):
            self.__V[:,:] = p_set.X[:,i]
            self.__V[:,:] = ( self.__V[:,:].T - p_set.X[:,i] ).T 
                        
            self.__A[:,i] = np.sum( self.__Fm * self.__V[:,:] , 0 )
                
        return self.__A
    
    
    def getA(self):
        """
        Return the currents accelerations of the particles
        """
        return self.__A
    
    A = property( getA , doc="Return the currents accelerations of the particles (getter only)")


    def getF(self):
        """
        Return the currents forces on the particles
        """
        return self.__A * self.__M[:,0]
    
    F = property( getF , doc="Return the currents forces on the particles (getter only)")




class GravityOCL( fr.Force ) :
    r"""
    Compute the gravitational force between the particles

    The gravity between two particles is defined as follow:

    .. math::

        \mathbf{F}_{12}=-G \frac{m_1 m_2 }{r^2}\hat{r}_{12}

    Constructor
    
    :param    size:        the number of particles in the system
    :param    dim:         the dimension of the system
    :param    m:           a vector containig the masses
    :param    Const:       the gravitational constant
    """
    def __init__(self , size , dim=3 , m=None , Consts=1.0 , ocl_context=None ):
        
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
        
        
    def __init_prog_cl(self):
        self.__gravity_prg = """
        __kernel void drag(__global const float *X , 
                           __global const float *M ,
                                          float  G , 
                           __global       float *A )
        {
            int i  = get_global_id(0) ;
            int sz = get_global_size(0) ;
            int n ;
            float dist , f ;
            
            float4 at , u ;
            
            at.x = 0.0 ;
            at.y = 0.0 ;
            at.z = 0.0 ;
            at.w = 0.0 ;
            
            u.w = 0.0 ;
            
            for ( n = 0 ; n < sz ; n++ ) 
            {
                if ( n == i ) continue ;
                
                u.x = X[3*i] - X[3*n]
                u.y = X[3*i+1] - X[3*n+1]
                u.z = X[3*i+2] - X[3*n+2]
                
                dist = length( u ) ;
                
                f = G * M[n] / pown( dist , 3 )
                
                at.x = at.x + f * u.x
                at.y = at.x + f * u.y
                at.z = at.x + f * u.z
            } 
            
            A[3*i] = at.x
            A[3*i+1] = at.y
            A[3*i+2] = at.w
        }
        """
        
        self.__cl_program = cl.Program( self.__occ.CL_context , self.__gravity_prg ).build()    
    
    
    def set_masses( self , m ):
        """
        Set the masses used for computing the forces.
        """
        pass
        
        
    def update_force( self , p_set ):
        """
        Compute the force of the current status of the system and return the accelerations of every particle in a *size by dim* array
        """
        
        pass
                
        return self.__A
    
    
    def getA(self):
        """
        Return the currents accelerations of the particles
        """
        return self.__A
    
    A = property( getA , doc="Return the currents accelerations of the particles (getter only)")


    def getF(self):
        """
        Return the currents forces on the particles
        """
        return self.__A * self.__M[:,0]
    
    F = property( getF , doc="Return the currents forces on the particles (getter only)")