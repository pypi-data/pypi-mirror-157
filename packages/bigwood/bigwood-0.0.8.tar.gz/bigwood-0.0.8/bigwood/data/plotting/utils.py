"""Utility functions for plotting functions"""
import subprocess
from functools import wraps
from pathlib import Path
from sys import platform

from .conf import PLOT_DIR, TO_CLIPBOARD


def savefig(func):
    """Decorator for saving matplotlib figs"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        fig, ax, fig_labels = func(*args, **kwargs)
        if PLOT_DIR and fig:
            if isinstance(fig_labels, tuple):
                figname = f"{fig_labels[0]} {fig_labels[1]} vs {fig_labels[2]}.png"
            else:
                figname = f"{fig_labels}.png"

            figpath = Path(PLOT_DIR, figname)
            print(f"saving to {figpath}")
            fig.savefig(figpath, dpi=300, bbox_inches="tight", transparent=False)
            if TO_CLIPBOARD:
                copy_to_clipboard(figpath)

    #        return func(*args, **kwargs)
    return wrapper


def copy_to_clipboard(file):
    """Wrapper to copy a image file to the system clipboard on a Mac.

    Args:
        file: filepath to image to copy.
    """

    if platform == "darwin":

        subprocess.run(
            [
                "osascript",
                "-e",
                f'set the clipboard to (read (POSIX file "{file}") as JPEG picture)',
            ],
            check=True,
        )
    elif platform == "linux":

        subprocess.run(
            ["xclip", "-selection", "clipboard", "-t", "image/png", "-i", {file}],
            check=True,
        )
