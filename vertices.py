import itertools

# Define the boundaries
bounds = [0.2, 0.8]

num_vars = 2

# Generate all combinations of (x1, x2, x3, x4)
vertices = list(itertools.product(bounds, repeat=num_vars))

# Function to compute p values
def compute_p_values(vertex):
    point = [0] * (num_vars + 1)
    point[0] = vertex[0]
    for i in range(1, num_vars + 1):
        point[i] = 1
        for j in range(0, i):
            point[i] *= (1 - vertex[j])
        if i < num_vars:
            point[i] *= vertex[i]

    return point

# Compute and print the p values for each vertex
for vertex in vertices:
    p_values = compute_p_values(vertex)
    print(f"Vertex: {vertex}, p-values: {p_values}")

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

x_coords = [compute_p_values(vertex)[0] for vertex in vertices]
y_coords = [compute_p_values(vertex)[1] for vertex in vertices]
z_coords = [compute_p_values(vertex)[2] for vertex in vertices]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(x_coords, y_coords, z_coords, c='r', marker='o')

ax.set_xlabel('p1')
ax.set_ylabel('p2')
ax.set_zlabel('p3')

plt.savefig('vertices.png')

