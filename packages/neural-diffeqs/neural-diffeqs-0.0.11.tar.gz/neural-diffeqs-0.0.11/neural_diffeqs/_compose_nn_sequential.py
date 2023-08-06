
__module_name__ = "_compose_nn_sequential.py"
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])


# import packages #
# --------------- #
import torch


# import local dependencies #
# ------------------------- #
from ._NeuralNetwork import _NeuralNetwork


def _compose_nn_sequential(
    in_dim=2,
    out_dim=2,
    activation_function=torch.nn.Tanh(),
    hidden_layer_nodes={1: [75, 75], 2: [75, 75]},
    dropout=True,
    dropout_probability=0.1,
):

    """Compose a sequential linear torch neural network"""

    nn = _NeuralNetwork()

    hidden_layer_keys = list(hidden_layer_nodes.keys())

    nn.input_layer(in_dim=in_dim, nodes=hidden_layer_nodes[hidden_layer_keys[0]][0])
    nn.activation_function(activation_function)

    for layer in hidden_layer_keys:
        layer_nodes = hidden_layer_nodes[layer]
        if dropout:
            nn.dropout(probability=dropout_probability)
        nn.hidden_layer(layer_nodes[0], layer_nodes[1])
        nn.activation_function(activation_function)

    if dropout:
        nn.dropout(probability=dropout_probability)
    nn.output_layer(out_dim=out_dim, nodes=hidden_layer_nodes[hidden_layer_keys[-1]][1])

    return nn.compose()