import logging as logg
import logging as lg
import os
import shutil
import subprocess as sp
import sys
import urllib
from typing import Optional
import torch
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)

matplotlib.use("Agg")


def get_local_or_download(destination: str, source: Optional[str] = None):
    """
    Return file path `destination`, and if it does not exist download from `source`.

    :param destination: Destination path for downloaded file
    :type destination: str
    :param source: URL to download file from
    :type source: str
    :return: Path of local file
    :rtype: str
    """
    destination = os.path.realpath(destination)
    if not os.path.exists(destination):
        if source is not None:
            with urllib.request.urlopen(source) as response, open(
                destination, "wb"
            ) as out_file:
                shutil.copyfileobj(response, out_file)
        else:
            raise ValueError(
                f"{destination} does not exist locally and no download path provided."
            )

    return destination


import gzip as gz
import h5py
import multiprocessing as mp

from tqdm import tqdm
from functools import partial
from datetime import datetime


def plot_eval_predictions(labels, predictions, path="figure"):
    """
    Plot histogram of positive and negative predictions, precision-recall curve, and receiver operating characteristic curve.

    :param y: Labels
    :type y: np.ndarray
    :param phat: Predicted probabilities
    :type phat: np.ndarray
    :param path: File prefix for plots to be saved to [default: figure]
    :type path: str
    """

    pos_phat = predictions[labels == 1]
    neg_phat = predictions[labels == 0]

    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.suptitle("Distribution of Predictions")
    ax1.hist(pos_phat)
    ax1.set_xlim(0, 1)
    ax1.set_title("Positive")
    ax1.set_xlabel("p-hat")
    ax2.hist(neg_phat)
    ax2.set_xlim(0, 1)
    ax2.set_title("Negative")
    ax2.set_xlabel("p-hat")
    plt.savefig(path + ".phat_dist.png")
    plt.close()

    precision, recall, pr_thresh = precision_recall_curve(labels, predictions)
    aupr = average_precision_score(labels, predictions)
    logg.info(f"AUPR: {aupr}")

    plt.step(recall, precision, color="b", alpha=0.2, where="post")
    plt.fill_between(recall, precision, step="post", alpha=0.2, color="b")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.title("Precision-Recall (AUPR: {:.3})".format(aupr))
    plt.savefig(path + ".aupr.png")
    plt.close()

    fpr, tpr, roc_thresh = roc_curve(labels, predictions)
    auroc = roc_auc_score(labels, predictions)
    logg.info(f"AUROC: {auroc}")

    plt.step(fpr, tpr, color="b", alpha=0.2, where="post")
    plt.fill_between(fpr, tpr, step="post", alpha=0.2, color="b")
    plt.xlabel("FPR")
    plt.ylabel("TPR")
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.title("Receiver Operating Characteristic (AUROC: {:.3})".format(auroc))
    plt.savefig(path + ".auroc.png")
    plt.close()


def RBF(D, sigma=None):
    """
    Convert distance matrix into similarity matrix using Radial Basis Function (RBF) Kernel.

    :math:`RBF(x,x') = \\exp{\\frac{-(x - x')^{2}}{2\\sigma^{2}}}`

    :param D: Distance matrix
    :type D: np.ndarray
    :param sigma: Bandwith of RBF Kernel [default: :math:`\\sqrt{\\text{max}(D)}`]
    :type sigma: float
    :return: Similarity matrix
    :rtype: np.ndarray
    """
    sigma = sigma or np.sqrt(np.max(D))
    return np.exp(-1 * (np.square(D) / (2 * sigma ** 2)))


def _hdf5_load_partial_func(k, file_path):
    """
    Helper function for load_hdf5_parallel
    """

    with h5py.File(file_path, "r") as fi:
        emb = torch.from_numpy(fi[k][:])
    return emb


def load_hdf5_parallel(file_path, keys, n_jobs=-1):
    """
    Load keys from hdf5 file into memory

    :param file_path: Path to hdf5 file
    :type file_path: str
    :param keys: List of keys to get
    :type keys: list[str]
    :return: Dictionary with keys and records in memory
    :rtype: dict
    """
    torch.multiprocessing.set_sharing_strategy("file_system")

    if n_jobs == -1:
        n_jobs = mp.cpu_count()

    with mp.Pool(processes=n_jobs) as pool:
        all_embs = list(
            tqdm(
                pool.imap(
                    partial(_hdf5_load_partial_func, file_path=file_path), keys
                ),
                total=len(keys),
            )
        )

    embeddings = {k: v for k, v in zip(keys, all_embs)}
    return embeddings


def augment_data(df):
    """
    For all pairs (A B), also add pairs (B A)
    :param df: Data frame with 3 columns - pair1, pair2, label
    :type df: pd.DataFrame
    :return: Augmented data frame
    :rtype: pd.DataFrame
    """
    x0 = pd.concat((df["X0"], df["X1"]), axis=0)
    x1 = pd.concat((df["X1"], df["X0"]), axis=0)
    y = pd.concat((df["Y"], df["Y"]), axis=0)
    augmented_df = pd.concat([x0, x1, y], axis=1).reset_index(drop=True)
    augmented_df.columns = ["X0", "X1", "Y"]
    return augmented_df


logLevels = {0: lg.ERROR, 1: lg.WARNING, 2: lg.INFO, 3: lg.DEBUG}


def config_logger(file, fmt, level=2, use_stdout=True):
    module_logger = lg.getLogger("D-SCRIPT")
    module_logger.setLevel(logLevels[level])
    formatter = lg.Formatter(fmt)

    fh = lg.FileHandler(file)
    fh.setFormatter(formatter)
    module_logger.addHandler(fh)

    if use_stdout:
        sh = lg.StreamHandler(sys.stdout)
        sh.setFormatter(formatter)
        module_logger.addHandler(sh)

    return module_logger
