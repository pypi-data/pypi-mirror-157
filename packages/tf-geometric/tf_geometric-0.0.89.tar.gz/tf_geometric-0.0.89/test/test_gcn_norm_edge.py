# coding=utf-8
import os

# Enable GPU 0
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

import tf_geometric as tfg
import tensorflow as tf
import numpy as np
from tf_geometric.utils.graph_utils import convert_edge_to_directed

# ==================================== Graph Data Structure ====================================
# In tf_geometric, the data of a graph can be represented by either a collections of
# tensors (numpy.ndarray or tf.Tensor) or a tfg.Graph object.
# A graph usually consists of x(node features), edge_index and edge_weight(optional)

# Node Features => (num_nodes, num_features)
x = np.random.randn(5, 20).astype(np.float32)  # 5 nodes, 20 features

# Edge Index => (2, num_edges)
# Each column of edge_index (u, v) represents an directed edge from u to v.
# Note that it does not cover the edge from v to u. You should provide (v, u) to cover it.
# This is not convenient for users.
# Thus, we allow users to provide edge_index in undirected form and convert it later.
# That is, we can only provide (u, v) and convert it to (u, v) and (v, u) with `convert_edge_to_directed` method.
edge_index = np.array([
    [0, 0, 1, 3],
    [1, 2, 2, 1]
])

# Edge Weight => (num_edges)
edge_weight = np.array([0.9, 0.8, 0.1, 0.2]).astype(np.float32)

# Make the edge_index directed such that we can use it as the input of GCN
edge_index, [edge_weight] = convert_edge_to_directed(edge_index, [edge_weight])

print(tfg.nn.gcn_norm_edge(edge_index, 10))