import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
params = np.load('4_plane_parameters_0.npy')
params
fig1 = plt.figure()
for i in range(params.shape[0]):
    x, y = np.meshgrid(range(100), range(100))
    z = (1 - params[i][0]*x - params[i][1]*y)/params[i][2]
    plt3d = fig1.gca(projection='3d')
    plt3d.plot_surface(x, y, z, alpha=0.2)

plt.show()
