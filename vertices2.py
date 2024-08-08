import itertools
from scipy.spatial import ConvexHull

# Define the boundaries for original pmc
bounds = [0.1, 0.9]

num_vars = 3

vertices = []
for permutation in itertools.permutations(list(range(num_vars)), num_vars):
    vertex = [bounds[0]] * num_vars
    prob_remaining = 1 - num_vars * bounds[0]
    for i in permutation:
        add_this = min(prob_remaining, bounds[1] - vertex[i])
        vertex[i] += add_this
        prob_remaining -= add_this
        if prob_remaining == 0:
            break
    vertices.append(vertex)

print(vertices)

# Function to compute pdash values
def compute_pdash_values(vertex):
    n = len(vertex) - 1
    x = [0] * n
    sum_p = 0

    for i in range(n):
        x[i] = vertex[i] / (1 - sum_p)
        sum_p += vertex[i]
    return x

pdash_values = list(map(compute_pdash_values, vertices))

# Compute and print the p values for each vertex
for vertex in vertices:
    p_values = compute_pdash_values(vertex)
    print(f"Vertex: {vertex}, p-values: {p_values}")

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_subplot(111)

points = ConvexHull(pdash_values).vertices
pdash_values_ordered = [pdash_values[i] for i in points]
ax.fill([x[0] for x in pdash_values_ordered], [x[1] for x in pdash_values_ordered])
ax.scatter([x[0] for x in pdash_values], [x[1] for x in pdash_values], c='b', marker='o')

ax.set_xlabel('p1')
ax.set_ylabel('p2')

plt.savefig('vertices.png')

