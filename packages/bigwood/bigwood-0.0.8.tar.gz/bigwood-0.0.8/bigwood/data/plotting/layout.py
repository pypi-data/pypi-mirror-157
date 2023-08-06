"""Useful arrangements of Matplotlib plots"""
from numpy import ndarray
from matplotlib import axes
from matplotlib import pyplot as plt
from .utils import savefig
import time


@savefig
def stacked_multiplot(funcs: list, nrows: int, ncols: int, title=""):
    """Stacked plots, double the normal width. Good for comparing timeseries

    Args:
        funcs (list): funcs
            A list of partial functions to be plotted.
        nrows (int): nrows
            Number of stacked plots
        ncols (int): ncols
            Width of the plots
        title: What you want the figure title to be.
    """
    size = [ncols * 6.4 * 2, nrows * 4.8 * 0.75]
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=size, sharex=True)
    if len(funcs) == len(axs):
        for i, func in enumerate(funcs):
            func(ax=axs[i])
    fig.suptitle(title, fontsize=16)
    return fig, axs, title


def _get_next_plot(axes):

    for a in axes:
        if isinstance(a, ndarray):
            for sub_a in a:
                yield sub_a
        else:
            yield a


@savefig
def multiplot(funcs: list, nrows: int, ncols: int, title=""):
    """Create a figure of n by m plots with the functions passed in.

    Args:
        funcs (list): funcs
            List of partial functions to plot
        nrows (int): nrows
            Number of plot rows
        ncols (int): ncols
            Number of plot columns
        title: What you want the title to be.
    """
    size = [ncols * 6.4, nrows * 4.8]

    # lots of different things can come out of here for the axes
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=size)

    # if what comes out is not a list, it is a numpy array.
    # we iterate over it.
    if isinstance(axs, ndarray):
        fig_axes = _get_next_plot(axs)
        for i, func in enumerate(funcs):
            func(ax=next(fig_axes))
    # else just use as is
    elif isinstance(axs, axes.Axes):
        if len(funcs) == 1:
            func = funcs[0]
            func(ax=axs)

    fig.suptitle(title, fontsize=16)
    fig.tight_layout()
    return fig, axs, title


@savefig
def singleplot(funcs, title=""):
    """Create a figure of 1 x 1 plot with the functions passed in.

    What is the point I hear you ask?! Well by using this function you get
    a standardised plot size, the image is saved to either the .plot dir or
    your tmp and the image is copied to your clipboard.

    Args:
        funcs (list): funcs
            List of partial functions to plot
        title: What you want the title to be.
    """
    ncols = nrows = 1
    size = [ncols * 6.4, nrows * 4.8]
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=size)
    fig.set_facecolor("white")

    # This should always be the case
    if isinstance(axs, axes.Axes) and not isinstance(funcs, list):
        funcs(ax=axs)

    # We can plot multiple graphs on the
    # same axis
    if isinstance(funcs, list):
        for f in funcs:
            f(ax=axs)

    fig.suptitle(title, fontsize=16)

    # if we don't give a title then the figure will be saved with a timestamp instead.
    if not title:
        title = str(time.time())
    return fig, axs, title
