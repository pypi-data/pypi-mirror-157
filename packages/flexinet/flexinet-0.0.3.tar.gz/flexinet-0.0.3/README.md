# ![flexinet-logo](/docs/img/flexinet.logo.v3.svg)

A flexible API for instantiating pytorch neural networks composed of sequential linear layers ([`torch.nn.Linear`](https://pytorch.org/docs/stable/generated/torch.nn.Linear.html#torch.nn.Linear)). Additionally, makes use of other elements within the [`torch.nn`](https://pytorch.org/docs/stable/nn.html) module.

## Test implementation 1: Sequential linear neural network

```python
import flexinet

nn = flexinet.models.NN()
```

```python
# example
nn = flexinet.models.compose_nn_sequential(in_dim=50,
                                           out_dim=50,
                                           activation_function=Tanh(),
                                           hidden_layer_nodes={1: [500, 500], 2: [500, 500]},
                                           dropout=True,
                                           dropout_probability=0.1,
                                           )
```

## Test implementation 2: vanilla linear VAE

<img width="400" alt="FlexiLinearAVE" src="/docs/img/flexinet.LinearVAE.svg">

## Installation

To install the latest distribution from [PYPI](https://pypi.org/project/flexinet/):

```BASH
pip install flexinet
```

Alternatively, one can install the development version:

```BASH
git clone https://github.com/mvinyard/flexinet.git; cd flexinet;

pip install -e .
```

### Example

```python
import flexinet as fn
import torch

X = torch.load("X_data.pt")
X_data = fn.pp.random_split(X)
X_data.keys()
```
>`dict_keys(['test', 'valid', 'train'])`

```python
model = fn.models.LinearVAE(X_data,
                            latent_dim=20, 
                            hidden_layers=5, 
                            power=2,
                            dropout=0.1,
                            activation_function_dict={'LeakyReLU': LeakyReLU(negative_slope=0.01)},
                            optimizer=torch.optim.Adam
                            reconstruction_loss_function=torch.nn.BCELoss(),
                            reparameterization_loss_function=torch.nn.KLDivLoss(),
                            device="cuda:0",
                           )
```
<img width="541" alt="from_nb.linear_VAE" src="https://user-images.githubusercontent.com/47393421/168488664-e7918416-8ae8-4369-a6ef-b73449c42b5f.png">

```python
model.train(epochs=10_000, print_frequency=50, lr=1e-4)
```

<img width="541" alt="from_nb.train_in_progress" src="https://user-images.githubusercontent.com/47393421/168489358-620815b0-b129-43af-8eb4-0009c46d3295.png">

```python
model.plot_loss()
```
![loss-plot](https://user-images.githubusercontent.com/47393421/168498723-4b183481-b651-45ba-abf9-72df57a7ee97.png)

## Contact

If you have suggestions, questions, or comments, please reach out to Michael Vinyard via [email](mailto:mvinyard@broadinstitute.org)
