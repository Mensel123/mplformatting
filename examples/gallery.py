"""Render the canonical hard cases so they can be eyeballed / diffed.

    python examples/gallery.py --out build/gallery          # current checkout
    git stash && python examples/gallery.py --out build/before && git stash pop
    python examples/gallery.py --out build/after

Then compare build/before/*.png with build/after/*.png.
Nothing here asserts anything -- it exists so a human can look.
"""
import argparse
import pathlib

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from mplformatting import apply

CASES = {}


def case(fn):
    CASES[fn.__name__] = fn
    return fn


@case
def linear():
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 200)
    ax.plot(x, np.sin(x))
    apply(ax)
    return fig


@case
def log_y_few_decades():
    """Dense branch: minor ticks at 2-9 inside every decade."""
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 200)
    ax.plot(x, 10 ** (1 + 0.3 * x))
    ax.set_yscale("log")
    apply(ax)
    return fig


@case
def log_y_many_decades():
    """Sparse branch: majors thinned, minors at the remaining decades."""
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 200)
    ax.plot(x, 10 ** (0.02 + 1.5 * x))
    ax.set_yscale("log")
    apply(ax, max_yticks=4)
    return fig


@case
def loglog():
    fig, ax = plt.subplots()
    x = np.logspace(0, 4, 200)
    ax.plot(x, x ** 1.5)
    ax.set_xscale("log")
    ax.set_yscale("log")
    apply(ax)
    return fig


@case
def limits_changed_after_apply():
    """Regression: the twins used to freeze at the old limits."""
    fig, ax = plt.subplots()
    ax.plot(np.linspace(0, 10, 50), np.linspace(0, 10, 50))
    apply(ax)
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 60)
    return fig


@case
def applied_twice():
    fig, ax = plt.subplots()
    ax.plot(np.linspace(0, 10, 50), np.linspace(0, 10, 50))
    apply(ax)
    apply(ax)
    return fig


@case
def shared_grid():
    fig, axes = plt.subplots(2, 2, sharex=True, sharey=True)
    x = np.linspace(0, 10, 200)
    for i, a in enumerate(axes.flat):
        a.plot(x, 10 ** (1 + 0.2 * (i + 1) * x))
        a.set_yscale("log")
        apply(a)
    fig.supxlabel("X")
    fig.supylabel("Y")
    return fig


@case
def with_colorbar():
    fig, ax = plt.subplots()
    im = ax.imshow(np.random.default_rng(0).random((20, 20)),
                   extent=[0, 10, 0, 10], origin="lower", aspect="auto")
    apply(ax)
    fig.colorbar(im, ax=ax)
    return fig


@case
def with_wrapped_legend():
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 200)
    ax.plot(x, np.sin(x), label="a rather long series label")
    ax.plot(x, np.cos(x), label="another long series label")
    ax.legend()
    apply(ax, legend_wrap_chars=14)
    return fig


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="build/gallery")
    p.add_argument("--only", nargs="*", help="subset of case names")
    args = p.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    names = args.only or list(CASES)
    for name in names:
        fig = CASES[name]()
        fig.savefig(out / f"{name}.png", dpi=110)
        plt.close(fig)
        print(f"wrote {out / name}.png")


if __name__ == "__main__":
    main()
