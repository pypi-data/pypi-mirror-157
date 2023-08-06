
__module_name__ = "_plot_loss.py"
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])


# import packages #
# --------------- #
import matplotlib.pyplot as plt
import numpy as np
import vinplots


def _build_plot():

    fig = vinplots.Plot()
    fig.construct(nplots=1, ncols=1, figsize=1.2)
    fig.modify_spines(ax="all", spines_to_delete=["top", "right"])
    ax = fig.AxesDict[0][0]

    return fig, ax


def _get_loss_plot_coordinates(training_loss, validation_loss, validation_frequency):

    train_x = range(len(training_loss))
    valid_x = np.arange(validation_frequency, int(len(training_loss)+1), validation_frequency)
    
    return train_x, valid_x


def _plot_loss(training_loss, validation_loss, validation_frequency):

    train_x, valid_x = _get_loss_plot_coordinates(
        training_loss, validation_loss, validation_frequency
    )

    fig, ax = _build_plot()

    ax.scatter(train_x, training_loss, c="navy", alpha=0.8, label="Training")
    ax.scatter(valid_x, validation_loss, c="darkorange", alpha=0.8, label="Validation")
    ax.set_xlabel("Epochs", fontsize=12)
    ax.set_ylabel("Total Loss", fontsize=12)
    ax.set_title("VAE Optimization", fontsize=16)
    plt.legend(edgecolor="white", fontsize=14, markerscale=1.2)