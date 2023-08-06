
__module_name__ = "__init__.py"
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])


from ._LinearVAE import _LinearVAE as LinearVAE

from ._compose_nn_sequential import _NeuralNetwork as NN
from ._compose_nn_sequential import _compose_nn_sequential as compose_nn_sequential
