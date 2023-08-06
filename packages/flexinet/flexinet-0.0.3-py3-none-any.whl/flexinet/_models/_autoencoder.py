
import torch
import numpy as np
from collections import OrderedDict

def _power_space(start, stop, n, power):

    start = np.power(start, 1 / float(power))
    stop = np.power(stop, 1 / float(power))

    return np.power(np.linspace(start, stop, num=n), power)

def _flip(arr):
    return arr.astype(int)[::-1]

def _structure(data_dim, latent_dim, n_hidden_layers, power, encoder=True):
    
    n_hidden_layers += 3
    
    node_array = _power_space(
        start=latent_dim, stop=data_dim, n=n_hidden_layers, power=power
    ).astype(int)
    
    if encoder:
        return _flip(node_array)
    else:
        return node_array
    
def _build_network(
    nodes_by_layer, activation_func, dropout
):

    neural_net = OrderedDict()
    
    for i in range(len(nodes_by_layer) - 1):
        neural_net["layer_{}".format(i)] = torch.nn.Linear(
            nodes_by_layer[i], nodes_by_layer[i + 1]
        )
        if i != len(nodes_by_layer) - 2:
            if dropout:
                neural_net["dropout_{}".format(i)] = torch.nn.Dropout(dropout)
            neural_net["activation_{}".format(i)] = activation_func

    return torch.nn.Sequential(neural_net)

def _decoder(X_dim, latent_dim=10, n_hidden_layers=3, activation_func=torch.nn.LeakyReLU(), power=2, dropout=0.5):
    nodes = _structure(X_dim, latent_dim, n_hidden_layers, power, encoder=False)
    return _build_network(nodes, activation_func, dropout)

def _encoder(X_dim, latent_dim=10, n_hidden_layers=3, activation_func=torch.nn.LeakyReLU(), power=2, dropout=0.5):
    nodes = _structure(X_dim, latent_dim, n_hidden_layers, power, encoder=True)
    return _build_network(nodes, activation_func, dropout)