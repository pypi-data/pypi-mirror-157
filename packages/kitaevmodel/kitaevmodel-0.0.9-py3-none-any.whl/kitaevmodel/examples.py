import os
os.add_dll_directory("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.2/bin")
import tensorflow as tf
import numpy as np

from hamiltonian_creator import hexagon_lattice_zigzag
from eigenstates import eigenstates
from image_generator import state_on_the_lattice_uniform
from time_evolution import animated_repr

from hamiltonian_creator import (rectangular_lattice,
                                 hexagon_lattice_zigzag,
                                 stripe_lattice_zigzag, 
                                 hexagon_lattice_armchair, 
                                 stripe_lattice_armchair)

from image_generator import (lattice_with_arrows, 
                             state_on_the_lattice_nodes,
                             state_on_the_lattice_uniform,
                             spectrum_and_density)

graph, pos, max_x, max_y = hexagon_lattice_zigzag(2, 0.1, 0.4, 0)
print(pos)

graph, pos, max_x, max_y = rectangular_lattice(3, 5, 0.1, 0.4, 0)
lattice_with_arrows(graph, pos, max_x, max_y, 
                    file_name='images/lattice_with_interaction.pdf', 
                    save=False, 
                    size=1)

graph, pos, max_x, max_y = hexagon_lattice_zigzag(2, 0.1, 0.4, 0)
lattice_with_arrows(graph, pos, max_x, max_y, 
                    file_name='images/lattice_with_interaction.pdf', 
                    save=False, 
                    size=10)

graph, pos, max_x, max_y = stripe_lattice_zigzag(3, 2, 0.1, 0.4, 0)
lattice_with_arrows(graph, pos, max_x, max_y, 
                    file_name='images/lattice_with_interaction.pdf', 
                    save=False, 
                    size=1)
                     
graph, pos, max_x, max_y = hexagon_lattice_armchair(2, 0.1, 0.4, 0)
lattice_with_arrows(graph, pos, max_x, max_y, 
                    file_name='images/lattice_with_interaction.pdf', 
                    save=False, 
                    size=1)

graph, pos, max_x, max_y = stripe_lattice_armchair(3, 2, 0.1, 0.4, 0)
lattice_with_arrows(graph, pos, max_x, max_y, 
                    file_name='images/lattice_with_interaction.pdf', 
                    save=False, 
                    size=1)

graph, pos, max_x, max_y = hexagon_lattice_zigzag(40, 0.1, 0.4, 0)
    
e, v = eigenstates(graph)
state = tf.make_ndarray(tf.make_tensor_proto(v[:, 3]))
state_on_the_lattice_nodes(graph, pos, state, max_x, max_y, 
                               file_name='images/state_on_nodes.png')
state_on_the_lattice_uniform(graph, pos, state, max_x, max_y, 
                                 file_name='images/state_uniform.pdf')
spectrum_and_density(e)

graph, pos, max_x, max_y = hexagon_lattice_zigzag(40, 0.027, 0.3, 0)
e, v = eigenstates(graph)
v_inv = tf.linalg.inv(v)

initial_state = np.zeros_like(v[:, 0])
initial_state[27] = 1

time = 5
initial_state = tf.constant(initial_state)
animated_repr(initial_state, time, graph, pos, max_x, max_y, e, v, v_inv,
              frames=200 * 2, interval=100, repeat=False, size=10)