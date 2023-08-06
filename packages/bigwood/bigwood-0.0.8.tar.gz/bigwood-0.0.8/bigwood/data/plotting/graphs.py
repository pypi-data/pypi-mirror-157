"""Lib for regular graphs"""
from functools import wraps

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd
from matplotlib import axes

from .utils import savefig


class Notations:
    """Wrapper class for useful functions for adding annotations
    to a mpl plot"""

    def __init__(self):
        pass


class Axes:
    """Wrapper class for useful functions for dealing with non-standard
    axes for mpl
    """

    pass


def _apply_text(ax, text: dict):

    if text.get("position"):
        position = text["position"]
    else:
        # use top left
        position = (0.05, 0.95)

    if text.get("size"):
        size = text["size"]
    else:
        size = 10

    ax.text(
        position[0],
        position[1],
        text["text"]["message"],
        transform=ax.transAxes,
        fontsize=size,
        verticalalignment="top",
    )


def _apply_note(ax, note: dict):

    if note.get("colour"):
        colour = note.get("colour")
    else:
        colour = "r"

    if note.get("hline") is not None:
        ax.axhline(y=note["hline"], color=colour, linestyle="--", lw=2, xmax=100)

    if note.get("vline") is not None:
        ax.axvline(x=note["vline"], color=colour, linestyle="--", lw=2, ymax=100)

    if note.get("text") is not None:
        _apply_text(ax, note)


def _notations(func):
    """Addition lines / objects for a plot

    Requires a notation dictionary or notation object.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        ax = kwargs["ax"]
        if kwargs.get("notation"):
            notes = kwargs.get("notation")
            if isinstance(notes, list):
                for note in notes:
                    _apply_note(ax, note)
            else:
                _apply_note(ax, notes)
        return func(*args, **kwargs)

    return wrapper


def _axes(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ax = kwargs["ax"]
        if kwargs.get("axes_meta"):
            meta = kwargs.get("axes_meta")

            locator = meta.get("locator")
            ticks = meta.get("ticks")
            length = meta.get("length")
        else:
            locator = ticks = length = dict()

        if not ticks:
            rot = 45
            fontsize = 8

        for tick in ax.get_xticklabels():
            tick.set_rotation(rot)
            tick.set_fontsize(fontsize)

        # axes sizes:
        if length:
            if length.get("x"):
                min_x, max_x = length.get("x")
                ax.set_xlim([min_x, max_x])
            if length.get("y"):
                mi_y, max_y = length.get("y")
                ax.set_ylim([min_y, max_y])

        if locator:
            _locators(ax, locator)

        return func(*args, **kwargs)

    return wrapper


def _locators(ax, locator_config):
    """Deal with number of ticks and appearance etc for ticks on a plot"""

    x_config = locator_config.get("x")
    if x_config:
        if x_config == "hide_labels":
            ax.xaxis.set_major_formatter(plt.NullFormatter())
        elif x_config == "hide_labels_and_ticks":
            ax.xaxis.set_major_locator(plt.NullLocator())
        else:
            ax.xaxis.set_major_locator(plt.MaxNLocator(x_config))

    y_config = locator_config.get("y")
    if y_config:
        if y_config == "hide_labels":
            ax.yaxis.set_major_formatter(plt.NullFormatter())
        elif y_config == "hide_labels_and_ticks":
            ax.yaxis.set_major_locator(plt.NullLocator())
        else:
            ax.yaxis.set_major_locator(plt.MaxNLocator(y_config))


def _labels(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if not kwargs.get("ax") and not kwargs.get("fig"):
            fig, ax = plt.subplots()
            kwargs["ax"] = ax
            kwargs["fig"] = fig
        elif not kwargs.get("ax"):
            _, ax = plt.subplots()
            kwargs["ax"] = ax
        else:
            fig = None
            ax = kwargs["ax"]

        if kwargs.get("labels"):
            labels = kwargs["labels"]
            data = args[0]

            if isinstance(labels, str):
                if labels == "test":
                    x_label = "x"
                    y_label = "y"
                    title = "test"
                else:
                    raise ValueError("Invalid value for labels")

            if isinstance(data, pd.DataFrame) and not labels.get("x"):
                x_label = data.index.name
            else:
                x_label = labels["x"]

            y_label = labels["y"]
            title = labels.get("title") or labels.get("t")

            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(title)
            fig_labels = (title, x_label, y_label)
            kwargs["fig_labels"] = fig_labels
        else:
            raise Exception("No labels!")

        return func(*args, **kwargs)

    return wrapper


@_labels
@_axes
@_notations
@savefig
def basic_line(
    data,
    ax=None,
    labels=None,
    legend=None,
    axes_meta=None,
    fig_labels=None,
    fig=None,
    notation=None,
):
    """Basic line plot.

    Args:
        data: A dataframe. Index becomes x. Columns plotted on x.
        ax: A set of axes to use for a larger figure
        labels: Labels for the axes. Requires a title.
        legend: Turn legend on / off
        axes_meta:
            Dict of axes metadata. Used to tune axes.
                locator:
                length:
                ticks:
        fig_labels:
            Name of the whole figure
        fig:
            Can also pass a fig in here. I did this so we can autosave.
    """

    for i, c in enumerate(data.columns):
        ax.plot(data[data.columns[i]], label=data.columns[i])

    if legend:
        ax.legend(frameon=False)

    return fig, ax, fig_labels


@_labels
@_axes
@_notations
@savefig
def basic_hist(
    data,
    bins=None,
    cumhist=False,
    ax=None,
    axes_meta=None,
    labels=None,
    fig=None,
    notation=None,
    fig_labels=None,
    **kwargs,
):

    if not bins:
        bins = range(min(data), max(data) + 2)

    if cumhist:
        ax.hist(
            data,
            bins,
            cumulative=True,
            histtype="step",
            **kwargs,
        )
    else:
        ax.hist(data, bins, **kwargs)

    return fig, ax, fig_labels


@_labels
@_axes
@_notations
@savefig
def prop_hist(
    data,
    align=None,
    bins=None,
    cumhist=False,
    ax=None,
    axes_meta=None,
    labels=None,
    fig=None,
    notation=None,
    fig_labels=None,
    **kwargs,
):

    if not bins:
        bins = range(min(data), max(data) + 2)

    if not align:
        align = "left"

    weights = np.ones(len(data)) / len(data)

    if cumhist:
        ax.hist(
            data,
            bins,
            cumulative=True,
            histtype="step",
            weights=weights,
            **kwargs,
        )
    else:
        ax.hist(data, bins, weights=weights, **kwargs)

    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_ylabel("Proportion")

    return fig, ax, fig_labels


@_labels
@_axes
@_notations
@savefig
def basic_scatter(
    data,
    ax=None,
    labels=None,
    axes_meta=None,
    legend=None,
    notation=None,
    fig=None,
    fig_labels=None,
):

    # plot
    for i, c in enumerate(data.columns):
        ax.scatter(data.index, data[c], label=data.columns[i])

    # legend
    if legend and isinstance(legend, str):
        ax.legend([f"{legend}"], frameon=False)
    elif legend:
        ax.legend(frameon=False)

    return fig, ax, fig_labels


@_labels
@_axes
@_notations
@savefig
def basic_bar(
    data,
    ax=None,
    labels=None,
    axes_meta=None,
    sizes=None,
    fig=None,
    fig_labels=None,
    plot_meta=None,
):

    if plot_meta:
        ax.bar(data.index, data[data.columns[0]], **plot_meta)
    else:
        ax.bar(data.index, data[data.columns[0]])

    return fig, ax, fig_labels


@savefig
def basic_table(data, title="", ax=None, row_names=None, column_names=None, fig=None):

    if not ax:
        fig, ax = plt.subplots()
    else:
        fig = None

    ax.set_axis_off()
    if not row_names:
        row_names = data.index

    if not column_names:
        column_names = data.columns

    cell_text = data.values

    print(row_names, column_names)
    rcolors = plt.cm.BuPu(np.full(len(row_names), 0.1))
    ccolors = plt.cm.BuPu(np.full(len(column_names), 0.1))

    ax.table(
        cellText=cell_text,
        rowLabels=row_names,
        rowColours=rcolors,
        rowLoc="right",
        colColours=ccolors,
        colLabels=column_names,
        loc="center",
    )

    ax.set_title(title, fontweight="bold")
    return fig, ax, title


def plot_function(*f):
    """Plot whatever functions you pass in."""

    fig, ax = plt.subplots()
    x_data = np.linspace(-5, 5, 100)
    for function in f:
        y = [function(x) for x in x_data]
        ax.plot(x_data, y)
    plt.show()
