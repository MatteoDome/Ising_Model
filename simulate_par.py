import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
from scipy.ndimage import convolve
import math
import itertools
from numba import jit

#   Simulation parameters
N = 10
T = 1
n_iter = 10000
n_iter_init = 1000
betaJ = 0.01
E= np.zeros([n_iter - n_iter_init])

##Hoshen Kopelman

lattice_hk = np.random.choice([1, -1], size = [N, N])
largest_label = 0
label_hk = np.zeros([N, N])
links_hk= np.zeros([N, N, 2])

@jit
def link(N, lattice_hk, links_hk, betaJ):
    prob = np.exp(-2*betaJ)
    for i, j in itertools.product(range(N), range(N)):
        if lattice_hk[i,j] == lattice_hk[(i-1)%N, j]:
            if np.random.uniform(0,1) < prob:
                links_hk[i,j,0] = 0
            else:
                links_hk[i,j,0] = 1

        if lattice_hk[i,j] == lattice_hk[i, (j-1)%N]:
            if np.random.uniform(0,1) < prob:
                links_hk[i,j,1] = 0
            else:
                links_hk[i,j,1] = 1
    return links_hk

@jit
def latti_upd(N, lattice_hk, links_hk, betaJ):
    largest_label = 0 
    label_hk = np.zeros([N, N])
    for i, j in itertools.product(range(N), range(N)):
        if links_hk[i,j,0] == 1 and links_hk[i,j,1] != 1:                        #can be done in one if
            label_hk[i,j] = label_hk[(i-1)%N, j]
        if links_hk[i,j,1] == 1 and links_hk[i,j,0] != 1:
            label_hk[i,j] = label_hk[i, (j-1)%N]
        elif links_hk[i,j,1] == 1 and links_hk[i,j,0] == 1:
            label_hk[i,j] = label_hk[(i-1)%N, j]
        elif all(links_hk[i,j,:]) != 1:
            largest_label += 1
            label_hk[i,j] = largest_label
    print("----")
    print(largest_label)
    for i, j in itertools.product(range(N), range(N)):
        if links_hk[i,j,0] ==1 and label_hk[i,j] != label_hk[(i-1)%N, j]:
            label_hk[i, j] = min(label_hk[i,j], label_hk[(i-1)%N, j])
            label_hk[(i-1)%N, j] = min(label_hk[i,j], label_hk[(i-1)%N, j])
        if links_hk[i,j,1] ==1 and label_hk[i,j] != label_hk[i, (j-1)%N]:
            label_hk[i, j] = min(label_hk[i,j], label_hk[i, (j-1)%N])
            label_hk[i, (j-1)%N] = min(label_hk[i,j], label_hk[i, (j-1)%N])
        if links_hk[(i+1)%N,j,0] ==1 and label_hk[i,j] != label_hk[(i+1)%N, j]:
            label_hk[i, j] = min(label_hk[i,j], label_hk[(i+1)%N, j])
            label_hk[(i+1)%N, j] = min(label_hk[i,j], label_hk[(i+1)%N, j])
        if links_hk[i,(j+1)%N,1] ==1 and label_hk[i,j] != label_hk[i, (j+1)%N]:
            label_hk[i, j] = min(label_hk[i,j], label_hk[i, (j+1)%N])
            label_hk[i, (j+1)%N] = min(label_hk[i,j], label_hk[i, (j+1)%N])

    largest_label = largest_label +1
    up_lattice = np.zeros([N, N])
    new_spin = np.random.choice([1, -1], size = largest_label)

    for i, j in itertools.product(range(N), range(N)):
        up_lattice[i, j] = new_spin[(label_hk[i,j])]
    
    return up_lattice

def compute_energy(lattice):
    k = np.array([[0,1,0],[1,0,1],[0,1,0]])
    neighbour_sum = convolve(lattice, k, mode='wrap')
    energy = -0.5*(np.sum(neighbour_sum*lattice))

    return energy

lattice_sum = np.zeros(100)
x = np.zeros(100)
chi = np.zeros(100)
magnetization = np.zeros(100)
for i in range (0, n_iter):
    link(N, lattice_hk, links_hk, betaJ)
    lattice_hk = latti_upd(N, lattice_hk, links_hk, betaJ)
    lattice_sum[i%100] = abs(lattice_hk.sum())
    if i%100==0:
        x[int(i/100)] = betaJ
        chi[int(i/100)] = np.mean(lattice_sum*lattice_sum)/(N*N*N*N)
        magnetization[int(i/100)] = np.mean(lattice_sum)/(N)
        betaJ+=0.01
        lattice_sum = np.zeros(100)


    # print(i)

plt.plot(x,magnetization)
plt.show()
    # # if i > n_iter_init:
    # #     E[i-n_iter_init] = compute_energy(lattice_hk)
    # # print("-------")
    # print(i)

# Cv = np.var(E)*betaJ/(N*N)
# print(Cv)