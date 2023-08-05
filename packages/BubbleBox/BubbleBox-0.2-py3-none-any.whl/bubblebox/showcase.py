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


from bubblebox.mdbox import no_forces

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


