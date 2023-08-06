
__module_name__ = "_LinearVAE.py"
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])


# import packages #
# --------------- #
import torch


# import local dependencies #
# ------------------------- #
from ._supporting_functions._Learner import _Learner
from ._supporting_functions._utilities import _no_transform
from ._supporting_functions._training_loop import _training_loop
from ._supporting_functions._KL_Divergence import _KL_Divergence
from ._supporting_functions._build_encoder_decoder import _build_encoder_decoder
from ._supporting_functions._reparameterize import _reparameterize
from ._supporting_functions._OptimalTransportLoss import _OptimalTransportLoss

from .._utilities._get_device import _get_device

from ._supporting_functions._plot_loss import _plot_loss

class _LinearVAE(torch.nn.Module):
    def __init__(
        self,
        X_data,
        latent_dim,
        hidden_layers=1,
        lr=1e-3,
        power=2,
        dropout=0.1,
        activation_function_dict={"LeakyReLU": torch.nn.LeakyReLU()},
        device=0,
        optimizer=torch.optim.Adam,
        reconstruction_loss_function=_OptimalTransportLoss("cuda:0"),
        reparameterization_loss_function=_KL_Divergence,
        silent=False,
    ):
        super(_LinearVAE, self).__init__()

        self._latent_dim = latent_dim
        self._device = _get_device(device)
        self._hidden_layers = hidden_layers
        self._power = power
        self._dropout = dropout
        self._lr = lr
        self._activation_function_dict = activation_function_dict
        self._silent = silent

        self._X_data = X_data
        for key, value in self._X_data.items():
            self._X_data[key] = value.to(self._device)

        self._data_dim = self._X_data["train"].shape[-1]

        self._encoder, self._decoder = _build_encoder_decoder(
            data_dim=self._data_dim,
            latent_dim=self._latent_dim,
            hidden_layers=self._hidden_layers,
            power=self._power,
            dropout=self._dropout,
            activation_function_dict=self._activation_function_dict,
            device=self._device,
            silent=self._silent,
        )
        self._model_params = list(self._encoder.parameters()) + list(
            self._decoder.parameters()
        )
        self._optimizer = optimizer(params=self._model_params, lr=self._lr)
        self._reconstruction_loss_function = reconstruction_loss_function
        self._reparameterization_loss_function = reparameterization_loss_function
        self._learner = _Learner(self)

    def encode(self, X, transform=_no_transform):

        self._X_latent = transform(self._encoder(X))

    def reparameterize(self):

        self._X_latent, self._mu, self._log_var = _reparameterize(self._X_latent)

    def decode(self, transform=_no_transform, return_reconstructed=True):

        self._X_reconstructed = transform(self._decoder(self._X_latent))
        if return_reconstructed:
            return self._X_reconstructed

    def train(self, epochs, validation_frequency=5, lr=1e-3, print_frequency=20):

        self._training_epoch_count = self._learner._training_epoch_count
        self._validation_frequency = validation_frequency

        if lr != self._lr:
            if not self._silent:
                print("Updating learning rate from: {} to: {}".format(self._lr, lr))
            self._optimizer.defaults["lr"] = self._lr = lr

        _training_loop(
            self._learner,
            self._X_data["train"],
            self._X_data["valid"],
            epochs,
            validation_frequency,
            print_frequency,
        )
        
    def plot_loss(self):
        
        _plot_loss(self._learner._training_loss,
                   self._learner._validation_loss,
                   self._validation_frequency,
                  )