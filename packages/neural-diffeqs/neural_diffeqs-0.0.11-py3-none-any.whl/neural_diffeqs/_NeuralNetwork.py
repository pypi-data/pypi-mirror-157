
__module_name__ = "_NeuralNetwork.py"
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])


# import packages #
# --------------- #
import torch
from collections import OrderedDict


class _NeuralNetwork:
    def __init__(self):

        self._nn_dict = OrderedDict()
        self._activation_count = 0
        self._hidden_layer_count = 0
        self._dropout_count = 0

    def input_layer(self, in_dim, nodes):

        self._nn_dict["input_layer"] = torch.nn.Linear(in_dim, nodes)

    def activation_function(self, activation_function=torch.nn.LeakyReLU()):

        self._activation_count += 1
        self._nn_dict[
            "activation_{}".format(self._activation_count)
        ] = activation_function

    def dropout(self, probability=0.1):

        self._dropout_count += 1
        self._nn_dict["dropout_{}".format(self._dropout_count)] = torch.nn.Dropout(
            probability
        )

    def hidden_layer(self, nodes_m, nodes_n):

        self._hidden_layer_count += 1
        self._nn_dict["hidden_{}".format(self._hidden_layer_count)] = torch.nn.Linear(
            nodes_m, nodes_n
        )

    def output_layer(self, nodes, out_dim):

        self._nn_dict["output_layer"] = torch.nn.Linear(nodes, out_dim)

    def compose(self):

        return torch.nn.Sequential(self._nn_dict)