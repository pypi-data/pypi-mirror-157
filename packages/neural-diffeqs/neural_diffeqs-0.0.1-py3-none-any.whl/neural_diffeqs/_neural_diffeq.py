
__module_name__ = "_neural_diffeq.py"
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])


# import packages #
# --------------- #
import torch


# import local dependencies #
# ------------------------- #
from ._compose_nn_sequential import _compose_nn_sequential


#### -------------------------------------------------------- ####


def _mu(mu, y):
    return mu(y)


def _sigma(sigma, y, brownian_size):
    return sigma(y).view(y.shape[0], y.shape[1], brownian_size)


#### -------------------------------------------------------- ####


class NeuralDiffEq(torch.nn.Module):

    noise_type = "general"
    sde_type = "ito"

    def __init__(self, mu, sigma=False, brownian_size=1):
        super(NeuralDiffEq, self).__init__()

        self.mu = mu
        self.sigma = sigma
        self._brownian_size = brownian_size

    def f(self, t, y0):
        return self.mu(y0)

    def forward(self, t, y0):
        return self.mu(y0)

    def g(self, t, y0):
        return _sigma(self.sigma, y0, self._brownian_size)
    
    
#### -------------------------------------------------------- ####
    
    
def _neural_diffeq(
    mu={1: [125, 125]},
    sigma={1: [125, 125]},
    in_dim=2,
    out_dim=2,
    mu_activation_function=torch.nn.Tanh(),
    sigma_activation_function=torch.nn.Tanh(),
    dropout=True,
    dropout_probability=0.5,
    brownian_size=1,
):
    """
    Instantiate a neural differential equation.

    Parameters:
    -----------
    in_dim
        Dimension size of input state
        type: int
        default: 2

    out_dim
        Dimension size of input state
        type: int
        default: 2

    mu
        dictionary-style composition of hidden architecture of the drift neural network
        type: dict
        default: {1: [125, 125]}

    sigma
        dictionary-style composition of hidden architecture of the diffusion neural network. Also may
        function as a boolean indicator to exclude a stochastic diffusion term. To negate stochastic
        term (thereby composing an ODE instead of an SDE), set `sigma=False`.
        type: dict (or bool)
        default: {1: [125, 125]}
    
    mu_activation_function
        Torch activation function of the mu (drift) neural network
        type: torch.nn.modules.activation
        default: torch.nn.Tanh()

    sigma_activation_function
        Torch activation function of the sigma (diffusion) neural network
        type: torch.nn.modules.activation
        default: torch.nn.Tanh()
    
    dropout
        Boolean indicator to include dropout in network architecture. If sigma is False, this
        argument is automatically adjusted to False.
        type: bool
        default: True

    dropout_probability
        Probability between 0 and 1 of node dropout for a given linear layer. If dropout is False,
        this argument is null.
        type: float
        default: 0.5

    brownian_size
        Dimension-wise complexity of the stochastic brownian noise.
        type: int
        default: 1

    Returns:
    --------
    NeuralDiffEq
    """

    if not sigma:
        dropout = False
        
    else:
        sigma = _compose_nn_sequential(
            in_dim=in_dim,
            out_dim=in_dim,
            hidden_layer_nodes=sigma,
            activation_function=sigma_activation_function,
            dropout=dropout,
            dropout_probability=dropout_probability,
        )

    mu = _compose_nn_sequential(
        in_dim=in_dim,
        out_dim=in_dim,
        hidden_layer_nodes=mu,
        activation_function=mu_activation_function,
        dropout=dropout,
        dropout_probability=dropout_probability,
    )

    return NeuralDiffEq(mu=mu, sigma=sigma, brownian_size=brownian_size)