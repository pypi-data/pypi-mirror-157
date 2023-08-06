
__module_name__ = "_training_loop.py"
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])


# import packages #
# --------------- #
from tqdm.notebook import tqdm


def _training_loop(
    learner, X_train, X_val, epochs, validation_frequency=50, print_frequency=50
):

    for epoch in tqdm(range(1, epochs + 1)):
        learner.train(X_train)
        if epoch % validation_frequency == 0:
            learner.validate(X_val)
            
        if epoch % print_frequency == 0:
            msg = "Epoch: {:>4} | Training Loss: {:>10.3f} | Validation Loss: {:>10.3f}"
            print(msg.format(epoch, learner._training_loss[-1], learner._validation_loss[-1]))