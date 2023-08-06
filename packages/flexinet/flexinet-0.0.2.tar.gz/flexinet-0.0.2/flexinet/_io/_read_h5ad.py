

__module_name__ = "_read_h5ad.py"
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])


# import packages #
# --------------- #
from anndata import read_h5ad


def _read_h5ad(path, silent=False):
    
    """
    Parameters:
    -----------
    path
        type: strs
    
    silent
        default: True
        type: bool
    
    Returns:
    --------
    adata
        type: anndata._core.anndata.AnnData
    """

    adata = read_h5ad(path)

    if not silent:
        print(adata)

    return adata