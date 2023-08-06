
__module_name__ = "_load_torch.py"
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])


# import packages #
# --------------- #
def _load_torch(path):
    return torch.load(path)