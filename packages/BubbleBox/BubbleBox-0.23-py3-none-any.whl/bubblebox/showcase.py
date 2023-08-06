# Bubblebox Showcases
# Author: Audun Skau Hansen 2022

import bubblebox.mdbox
import bubblebox.binding_models
import bubblebox.ising
import bubblebox.lattice_models

from bubblebox.mdbox import mdbox, box
from bubblebox.binding_models import bindingbox
from bubblebox.ising import isingbox
from bubblebox.lattice_models import latticebox

import numpy as np


from bubblebox.mdbox import no_forces, hook_force, coulomb_force

def ideal_gas(vel = 1, n_bubbles = 216, size = (5,5,5), n_species = 3):
    """
    Set up an ideal gas

    Arguments
    ---
    vel -- standard deviation in velocities
    n_bubbles -- number of bubbles
    size -- size of box
    n_species -- number of different bubbles
    """
    b = mdbox(n_bubbles=n_bubbles, size = size , vel = vel)
    b.forces = no_forces
    b.masses = np.random.randint(1,n_species+1, n_bubbles)
    return b


def fcc_system(size=3, lattice_parameter = 2.0):
    """
    Set up a face-centered cubic system
    ( see https://en.wikipedia.org/wiki/Close-packing_of_equal_spheres )
    for relaxed geometry at the onset of the simulation
    
    Arguments
    ---
    lattice_parameter -- the length of each cell
    size -- number of cells (total number of bubbles is 4*size**3)
    """

    def fcc(Nc = 3):
        """
        Generate a FCC setup

        Returns an fcc simulation box containing 4*Nc**3 particles, 
        with a total volume of (L*Nc)**3.

        (keeping this function limited in scope to keep students unconfused)
        """
        #Lc = L*Nc
        
        coords = []
        for i in range(-Nc, Nc):
            for j in range(-Nc, Nc):
                for k in range(-Nc, Nc):
                    coords.append([i,j,k])

                    coords.append([i+.5,j+.5,k])
                    coords.append([i+.5,j,k+.5])
                    coords.append([i,j+.5,k+.5])

        coords = np.array(coords)

        coords = (coords+.5)/Nc
        coords -= np.mean(coords, axis = 0)[None,:]

        return coords

    pos = fcc(np.abs(size)).T

    b = mdbox(n_bubbles = pos.shape[1], size = (size*lattice_parameter, size*lattice_parameter, size*lattice_parameter), vel = 0)
    b.pos = pos*size*lattice_parameter
    
    return b


def repulsive_gas(n_bubbles = 125, n_species = 5, size = (-6,-6,-6), vel = 1.0, charge = 1.0):
    """
    Generate a gas of repulsive bubbles
    
    Arguments
    ---
    - n_bubbles -- number of bubbles in box
    - n_species -- number of different bubbles
    - size -- size of box (default (-6,-6,-6) )
    - vel -- standard deviation in velocity
    - charge -- scaling of attraction
    """

    b = mdbox(n_bubbles = n_bubbles, size = size, vel = vel)
    b.masses = np.random.randint(1,n_species+1, n_bubbles)
    b.force = coulomb_force
    b.interactions[:,:,0]*=charge
    return b

def attractive_gas(n_bubbles = 125, n_species = 5, size = (-6,-6,-6), vel = 1.0, charge = 1.0):
    """
    Generate a gas of repulsive bubbles
    
    Arguments
    ---
    - n_bubbles -- number of bubbles in box
    - n_species -- number of different bubbles
    - size -- size of box (default (-6,-6,-6) )
    - vel -- standard deviation in velocity
    - charge -- scaling of attraction
    """

    b = mdbox(n_bubbles = n_bubbles, size = size, vel = vel)
    b.masses = np.random.randint(1,n_species+1, n_bubbles)
    b.force = coulomb_force
    b.interactions[:,:,0]*=-charge
    return b

def spring_system(n_bubbles, n_species = 1):
    """
    A system of particles interacting with spring interactions
    """
    b = mdbox(n_bubbles = n_bubbles, size = (5,5,5), vel = 1)
    b.masses = np.random.randint(1,n_species, n_bubbles)
    b.force = hook_force
    b.r2_cut = 25
    return b
    
def flow_system():
    """
    A pipe with bubbles flowing through
    """
    
    
    b = mdbox(125, size = (2,2,-10))
    
    b.masses = 1 + np.exp(-np.sqrt(np.sum(b.pos[:2]**2, axis = 0)))
    b.pos[2] += np.random.uniform(-1,1, 125)
    b.vel[2] = np.random.normal(10,.4,b.n_bubbles)
    return b


def throttle_2d():
    """
    Bubbles moving through a throttle, prototype
    """
    nx = 50
    ny = 10

    sx = 70
    sy = 20
    b =mdbox(n_bubbles = nx*ny, size = (-sx,sy))
    b.pos = np.array(np.meshgrid(np.linspace(-sx,sx, nx+1)[:-1], np.linspace(-sy,sy, ny+1)[:-1])).reshape(2,-1)
    b.pos = b.pos - np.mean(b.pos, axis = 1)[:, None]

    s,dr = 1.6, 1030


    alpha = .001
    opening = 0.8
    lower_edge = b.pos[1] <  sy*(-1 + opening*np.exp(-alpha*b.pos[0]**2))
    upper_edge = b.pos[1] >  sy*( 1 - opening*np.exp(-alpha*b.pos[0]**2))

    t = np.linspace(-1,1,np.sum(lower_edge))*50
    b.pos[:,lower_edge] = np.array([t, -1 + sy*(-1 + opening*np.exp(-alpha*t**2))])
    b.pos[:,upper_edge] = np.array([t, 1 + sy*( 1 - opening*np.exp(-alpha*t**2))])

    b.interactions[:,:,0] = 10

    b.interactions[lower_edge, :, 0] = .1
    b.interactions[lower_edge, :, 1] = np.sqrt(2)
    b.interactions[:, upper_edge, 0] = .1
    b.interactions[:, lower_edge, 1] = np.sqrt(2)


    #upper_edge = np.sum((b.pos-np.array([0,s*sy]).reshape(2,-1))**2, axis = 0)<dr
    #lower_edge = np.sum((b.pos+np.array([0,s*sy]).reshape(2,-1))**2, axis = 0)<dr
    #
    b.masses[upper_edge] = 3
    b.masses[lower_edge] = 3
    #theta = np.linspace(-1,1,np.sum(upper_edge))*1.4
    #b.pos[:,upper_edge] = np.array([.8*dr**.5*np.sin(theta), -.8*dr**.5*np.cos(theta)+s*sy])

    #theta = np.linspace(-1,1,np.sum(lower_edge))*1.4
    #b.pos[:,lower_edge] = np.array([.8*dr**.5*np.sin(theta), .8*dr**.5*np.cos(theta)-s*sy])

    b.active[upper_edge] = False
    b.active[lower_edge] = False



    b.vel[0] = np.random.normal(6,.5,b.n_bubbles)
    
    return b


def fcc_custom(size=(3,3,3), lattice_parameter = 2.0):
    """
    Set up a face-centered cubic system
    ( see https://en.wikipedia.org/wiki/Close-packing_of_equal_spheres )
    for relaxed geometry at the onset of the simulation
    
    Arguments
    ---
    lattice_parameter -- the length of each cell
    size -- number of cells (total number of bubbles is 4*size**3)
    """

    def fcc(Nx, Ny, Nz):
        """
        Generate a FCC setup

        Returns an fcc simulation box containing 4*Nc**3 particles, 
        with a total volume of (L*Nc)**3.

        (keeping this function limited in scope to keep students unconfused)
        """
        #Lc = L*Nc
        
        coords = []
        for i in range(-Nx, Nx):
            for j in range(-Ny, Ny):
                for k in range(-Nz, Nz):
                    coords.append([i,j,k])

                    coords.append([i+.5,j+.5,k])
                    coords.append([i+.5,j,k+.5])
                    coords.append([i,j+.5,k+.5])

        coords = np.array(coords)

        coords = (coords+.5)
        coords = coords*(np.array(size, dtype = float)**-1)[None,:]
        coords -= np.mean(coords, axis = 0)[None,:]

        return coords

    pos = fcc(*np.abs(np.array(size))).T

    b = mdbox(n_bubbles = pos.shape[1], size = np.array(size)*lattice_parameter, vel = 0)
    b.pos = lattice_parameter*pos*np.array(size, dtype = float)[:, None]
    
    return b

def throttle_3d_membrane(membrane_width = 0.5, lattice_parameter = 3.0):
    b = fcc_custom(size = (-5,1,1), lattice_parameter = lattice_parameter)
    membrane_index = np.abs(b.pos[0])<membrane_width
    b.active[membrane_index] = False
    b.masses[membrane_index] = 3
    
    b.vel[0] = np.random.normal(6,.5,b.n_bubbles)
    return b