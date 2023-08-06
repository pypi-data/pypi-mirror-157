# coding=utf-8
import os

# Enable GPU 0
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import tensorflow as tf
import tf_geometric as tfg
import numpy as np

# Node Features => (num_nodes, num_features)
x = np.random.randn(5, 2).astype(np.float32)  # 5 nodes, 20 features

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

graph = tfg.Graph(x=x, edge_index=edge_index, edge_weight=edge_weight)
batch_graph = tfg.BatchGraph.from_graphs([graph, graph])
print(batch_graph.edge_index)
print(batch_graph.edge_weight)

directed_batch_graph = batch_graph.to_directed()

print("=========")

print(directed_batch_graph.x)
print(directed_batch_graph.edge_index)
print(directed_batch_graph.edge_weight)
print(directed_batch_graph.node_graph_index)
print(directed_batch_graph.edge_graph_index)

directed_batch_graph = batch_graph.to_directed().reorder()

print("=========")

print(directed_batch_graph.x)
print(directed_batch_graph.edge_index)
print(directed_batch_graph.edge_weight)
print(directed_batch_graph.node_graph_index)
print(directed_batch_graph.edge_graph_index)

print("==========")
for graph in directed_batch_graph.to_graphs():
    print("----")
    print(graph)
    print(graph.x)
    print(graph.edge_index)
    print(graph.edge_weight)
