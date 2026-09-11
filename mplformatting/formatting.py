import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator
from contextlib import contextmanager
import matplotlib.ticker as mticker
from matplotlib.ticker import LogFormatterMathtext

# --------------------------
# TICKS BASED ON LIMITS
# --------------------------
import numpy as np
from matplotlib.ticker import FixedLocator

from matplotlib.ticker import FixedLocator, LogLocator
from matplotlib.ticker import LogFormatterMathtext, LogLocator, NullFormatter

from matplotlib.ticker import LogFormatterMathtext, NullFormatter
import os


import numpy as np
import matplotlib.ticker as mticker
# Find the style file relative to this formatting.py file
_style_path = os.path.join(os.path.dirname(__file__), "paper.mpltstyle")

if os.path.exists(_style_path):
    plt.style.use(_style_path)
else:
    raise FileNotFoundError(f"Cannot find paper.mpltstyle at: {_style_path}")


def _set_log_decade_ticks(ax, axis="y", max_ticks=6):
    """
    Set major ticks at (some) integer powers of 10.

    - If the number of visible decades <= max_ticks:
        majors: all integer decades (10^n)
        minors: 2–9 within each decade

    - If the number of visible decades > max_ticks:
        majors: a subset of integer decades (thinned)
        minors: the remaining integer decades (no 2–9 subs)
    """
    if axis == "y":
        vmin, vmax = ax.get_ylim()
        axis_obj = ax.yaxis
    else:
        vmin, vmax = ax.get_xlim()
        axis_obj = ax.xaxis

    # Guard for log scale: vmin, vmax must be > 0
    if vmin <= 0 or vmax <= 0:
        return

    # Exponent range
    emin = int(np.floor(np.log10(vmin)))
    emax = int(np.ceil(np.log10(vmax)))
    exponents = np.arange(emin, emax + 1)

    n_decades = len(exponents)

    if n_decades <= max_ticks:
        # --- Dense case: label every decade, show 2–9 as minor ticks ---
        major_exponents = exponents
        major_locs = 10.0 ** major_exponents

        axis_obj.set_major_locator(FixedLocator(major_locs))

        # Minor ticks: 2..9 within each decade
        minor_locator = LogLocator(base=10.0, subs=range(2, 10))
        axis_obj.set_minor_locator(minor_locator)

    else:
        # --- Sparse case: label only some decades, minor ticks at the rest ---
        step = int(np.ceil(n_decades / max_ticks))
        major_exponents = exponents[::step]
        major_locs = 10.0 ** major_exponents

        # Minor exponents are the "missing" integer powers of 10
        minor_exponents = np.setdiff1d(exponents, major_exponents)
        minor_locs = 10.0 ** minor_exponents if minor_exponents.size else []

        axis_obj.set_major_locator(FixedLocator(major_locs))
        axis_obj.set_minor_locator(FixedLocator(minor_locs))



# --------------------------
# SCIENTIFIC FORMATTER
# --------------------------

_SUPERSCRIPT_MAP = str.maketrans("0123456789-+",
                                 "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺")

def _full_sci_tickformat_plain(x, pos):
    """Format numbers like 1.1×10⁷ without MathText."""
    if x == 0:
        return "0"
    exponent = int(np.floor(np.log10(abs(x))))
    coeff = x / 10**exponent
    exp_str = str(exponent).translate(_SUPERSCRIPT_MAP)
    return f"{coeff:.3g}×10{exp_str}"

def use_full_sci_y(ax):
    """Apply full scientific formatting only to y-axis."""
    formatter = mticker.FuncFormatter(_full_sci_tickformat_plain)
    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.offsetText.set_visible(False)   # just in case


def use_log_format(ax, axis="y", max_ticks=6):
    """Apply 10^n formatting on major ticks and hide minor labels cleanly,
    with major ticks at some integer powers of 10 and minor ticks at
    the remaining integer powers of 10.
    """
    fmt = LogFormatterMathtext()
    minor_fmt = NullFormatter()

    if axis == "y":
        ax.set_yscale("log")
        _set_log_decade_ticks(ax, axis="y", max_ticks=max_ticks)
        ax.yaxis.set_major_formatter(fmt)
        ax.yaxis.set_minor_formatter(minor_fmt)

    elif axis == "x":
        ax.set_xscale("log")
        _set_log_decade_ticks(ax, axis="x", max_ticks=max_ticks)
        ax.xaxis.set_major_formatter(fmt)
        ax.xaxis.set_minor_formatter(minor_fmt)

# --------------------------
# MIXED TICK DIRECTIONS
# --------------------------
def _drop_edges(locs, vmin, vmax):
    lo, hi = min(vmin, vmax), max(vmin, vmax)
    return [v for v in locs
            if lo <= v <= hi
            and not (np.isclose(v, lo) or np.isclose(v, hi))]


def _sync_twins(ax, *_):
    """Mirror the main axes' ticks onto the top/right twins."""
    ax_top = getattr(ax, "_top_ticks_ax", None)
    ax_right = getattr(ax, "_right_ticks_ax", None)
    if ax_top is None or ax_right is None:
        return

    # --- top twin mirrors x ---
    ax_top.set_xscale(ax.get_xscale())
    ax_top.set_xlim(ax.get_xlim())
    x0, x1 = ax.get_xlim()
    # NOTE: ask the MAIN axes for its ticks; never hand its locator object
    # to the twin, that would rebind locator.axis to the twin.
    ax_top.xaxis.set_major_locator(
        FixedLocator(_drop_edges(ax.get_xticks(), x0, x1)))
    ax_top.xaxis.set_minor_locator(
        FixedLocator(_drop_edges(ax.get_xticks(minor=True), x0, x1)))

    # --- right twin mirrors y ---
    ax_right.set_yscale(ax.get_yscale())
    ax_right.set_ylim(ax.get_ylim())
    y0, y1 = ax.get_ylim()
    ax_right.yaxis.set_major_locator(
        FixedLocator(_drop_edges(ax.get_yticks(), y0, y1)))
    ax_right.yaxis.set_minor_locator(
        FixedLocator(_drop_edges(ax.get_yticks(minor=True), y0, y1)))


def setup_mixed_tick_directions(ax):
    # (Re-)assert direction on EVERY call, not just the first one.
    ax.tick_params(axis='x', which='both',
                   bottom=True, top=False, direction='out')
    ax.tick_params(axis='y', which='both',
                   left=True, right=False, direction='out')

    if not getattr(ax, "_mixed_tick_setup_done", False):
        ax_top = ax.twiny()
        ax_right = ax.twinx()
        ax._top_ticks_ax = ax_top
        ax._right_ticks_ax = ax_right
        ax._mixed_tick_setup_done = True

        for a in (ax_top, ax_right):
            a.set_navigate(False)
            a.patch.set_visible(False)

        ax.callbacks.connect('xlim_changed', lambda a: _sync_twins(ax))
        ax.callbacks.connect('ylim_changed', lambda a: _sync_twins(ax))
    else:
        ax_top = ax._top_ticks_ax
        ax_right = ax._right_ticks_ax

    # Top twin: x ticks inward on top only; its y axis must be fully dead.
    ax_top.xaxis.set_major_formatter(NullFormatter())
    ax_top.xaxis.set_minor_formatter(NullFormatter())
    ax_top.tick_params(axis='x', which='both', top=True, bottom=False,
                       direction='in', labeltop=False, labelbottom=False)
    ax_top.tick_params(axis='y', which='both', left=False, right=False,
                       labelleft=False, labelright=False)
    ax_top.yaxis.set_visible(False)
    ax_top.spines['bottom'].set_visible(False)

    # Right twin: y ticks inward on right only; its x axis must be fully dead.
    ax_right.yaxis.set_major_formatter(NullFormatter())
    ax_right.yaxis.set_minor_formatter(NullFormatter())
    ax_right.tick_params(axis='y', which='both', right=True, left=False,
                         direction='in', labelright=False, labelleft=False)
    ax_right.tick_params(axis='x', which='both', bottom=False, top=False,
                         labelbottom=False, labeltop=False)
    ax_right.xaxis.set_visible(False)
    ax_right.spines['left'].set_visible(False)

    _sync_twins(ax)
    return ax

def _is_top_row(ax):
    try:
        ss = ax.get_subplotspec()
        return ss.rowspan.start == 0
    except AttributeError:
        return True

def _hide_ticks_on_frame(ax):
    """
    Hide tick marks that overlap exactly with the frame on all four sides.
    Works for both linear/log and for twinned axes.
    """

    fig = ax.figure
    # Force creation/positioning of tick artists
    fig.canvas.draw()

    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    # Use a small tolerance for float comparisons
    def _is_edge(v, lo, hi):
        return np.isclose(v, lo) or np.isclose(v, hi)

    # --- Main axes: bottom & top (but top ticks are off on this axes) ---
    for tick in ax.xaxis.get_major_ticks() + ax.xaxis.get_minor_ticks():
        loc = tick.get_loc()
        if _is_edge(loc, xmin, xmax):
            # tick.tick1line.set_visible(False)
            tick.tick2line.set_visible(False)

    # --- Main axes: left & right (but right ticks are off on this axes) ---
    for tick in ax.yaxis.get_major_ticks() + ax.yaxis.get_minor_ticks():
        loc = tick.get_loc()
        if _is_edge(loc, ymin, ymax):
            tick.tick2line.set_visible(False)
            if _is_top_row(ax) and np.isclose(loc, ymax):
                # tick.label1.set_visible(False)
                tick.label2.set_visible(False)
            

    # --- Top twin axis ---
    if hasattr(ax, "_top_ticks_ax"):
        ax_top = ax._top_ticks_ax
        for tick in ax_top.xaxis.get_major_ticks() + ax_top.xaxis.get_minor_ticks():
            loc = tick.get_loc()
            if _is_edge(loc, xmin, xmax):
                tick.tick1line.set_visible(False)
                tick.tick2line.set_visible(False)

    # --- Right twin axis ---
    if hasattr(ax, "_right_ticks_ax"):
        ax_right = ax._right_ticks_ax
        for tick in ax_right.yaxis.get_major_ticks() + ax_right.yaxis.get_minor_ticks():
            loc = tick.get_loc()
            if _is_edge(loc, ymin, ymax):
                tick.tick1line.set_visible(False)
                tick.tick2line.set_visible(False)
                # if _is_top_row(ax):
                tick.label1.set_visible(False)
                tick.label2.set_visible(False)
                    

def use_full_linear_ticks(ax, axis="both", precision=6):
    """
    Force full decimal tick labels (not scientific notation) on linear axes.
    `precision` controls decimal places for small numbers.
    """

    def _fmt(x, pos):
        # Avoid scientific notation completely
        if x == 0:
            return "0"
        # Format small numbers with fixed-point notation
        return f"{x:.{precision}f}".rstrip("0").rstrip(".")

    fmt = mticker.FuncFormatter(_fmt)

    if axis in ("x", "both"):
        ax.xaxis.set_major_formatter(fmt)
        ax.xaxis.offsetText.set_visible(False)

    if axis in ("y", "both"):
        ax.yaxis.set_major_formatter(fmt)
        ax.yaxis.offsetText.set_visible(False)

import textwrap

def wrap_legend_labels(ax, max_chars=18):
    """
    Wrap legend labels so the legend doesn't become too wide.
    `max_chars` is the approximate maximum characters per line.
    """
    legend = ax.get_legend()
    if legend is None:
        return

    handles, labels = legend.legend_handles, [t.get_text() for t in legend.get_texts()]

    # Wrap labels to multiple lines
    wrapped_labels = [textwrap.fill(lbl, max_chars) for lbl in labels]

    # --- Extract legend properties safely ---
    loc = legend._loc
    frame_on = legend.get_frame_on()

    # fontsize (may be None if default)
    fontsize = None
    texts = legend.get_texts()
    if texts:
        fontsize = texts[0].get_fontsize()

    # number of columns (stable across versions)
    try:
        legend_box = legend._legend_box.get_children()[1]  # second child = handle/text list
        ncols = legend_box._ncols
    except Exception:
        ncols = 1

    # Remove old legend
    legend.remove()

    # Rebuild wrapped legend
    new_leg = ax.legend(
        handles,
        wrapped_labels,
        loc=loc,
        frameon=frame_on,
        ncol=ncols,
        fontsize=fontsize,
    )
    return new_leg

def set_linear_tick_intervals(
    ax,
    major_interval_x=None,
    minor_interval_x=None,
    major_interval_y=None,
    minor_interval_y=None,
):
    """
    Apply user-defined tick intervals on linear axes.
    If interval is None → do nothing (fallback logic applies).
    """

    # ----- X-axis -----
    if ax.get_xscale() == "linear":
        xmin, xmax = ax.get_xlim()

        # Major ticks (if requested)
        if major_interval_x is not None:
            major_ticks = np.arange(
                np.floor(xmin / major_interval_x) * major_interval_x,
                np.ceil(xmax / major_interval_x) * major_interval_x + major_interval_x,
                major_interval_x,
            )
            ax.xaxis.set_major_locator(FixedLocator(major_ticks))

        # Minor ticks (if requested)
        if minor_interval_x is not None:
            minor_ticks = np.arange(
                np.floor(xmin / minor_interval_x) * minor_interval_x,
                np.ceil(xmax / minor_interval_x) * minor_interval_x + minor_interval_x,
                minor_interval_x,
            )
            ax.xaxis.set_minor_locator(FixedLocator(minor_ticks))

    # ----- Y-axis -----
    if ax.get_yscale() == "linear":
        ymin, ymax = ax.get_ylim()

        if major_interval_y is not None:
            major_ticks = np.arange(
                np.floor(ymin / major_interval_y) * major_interval_y,
                np.ceil(ymax / major_interval_y) * major_interval_y + major_interval_y,
                major_interval_y,
            )
            ax.yaxis.set_major_locator(FixedLocator(major_ticks))

        if minor_interval_y is not None:
            minor_ticks = np.arange(
                np.floor(ymin / minor_interval_y) * minor_interval_y,
                np.ceil(ymax / minor_interval_y) * minor_interval_y + minor_interval_y,
                minor_interval_y,
            )
            ax.yaxis.set_minor_locator(FixedLocator(minor_ticks))


# --------------------------
# APPLY EVERYTHING
# --------------------------
def apply(
    ax,
    max_xticks=6,
    max_yticks=6,
    sci=True,
    legend_wrap_chars=None,
    major_interval_x=None,
    minor_interval_x=None,
    major_interval_y=None,
    minor_interval_y=None,
):    # linear x-axis
    # ---------------------- Linear Axes ----------------------
    if ax.get_xscale() == "linear" or ax.get_yscale() == "linear":

        # 1) Use interval ticks if provided
        set_linear_tick_intervals(
            ax,
            major_interval_x=major_interval_x,
            minor_interval_x=minor_interval_x,
            major_interval_y=major_interval_y,
            minor_interval_y=minor_interval_y,
        )

        # 2) If no interval was given → fallback to "nice" ticks (≤6)
        if major_interval_x is None and ax.get_xscale() == "linear":
            ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=max_xticks))

        if major_interval_y is None and ax.get_yscale() == "linear":
            if sci:
                use_full_sci_y(ax)
            else:
                use_full_linear_ticks(ax, axis="y")
            ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=max_yticks))


    # linear y-axis: choose between scientific and full decimal
    if ax.get_yscale() == "linear":
        if sci:
            # old behavior: 1.2×10⁻³ style
            use_full_sci_y(ax)
        else:
            # new option: plain decimals, e.g. 0.0012
            use_full_linear_ticks(ax, axis="y")

    # log x-axis
    if ax.get_xscale() == "log":
        use_log_format(ax, axis="x", max_ticks=max_xticks)

    # log y-axis
    if ax.get_yscale() == "log":
        use_log_format(ax, axis="y", max_ticks=max_yticks)

    # Mixed tick directions: left/bottom OUT, top/right IN (no labels)
    setup_mixed_tick_directions(ax)

    if legend_wrap_chars is not None:
        wrap_legend_labels(ax, max_chars=legend_wrap_chars)


    return ax





# --------------------------
# DECORATOR
# --------------------------

def autoformat(func=None, *, max_xticks=6, max_yticks=6, sci=True, powerlimits=(-3,3)):
    """
    Decorator for plotting functions:
    
    @autoformat
    def make_plot():
        fig, ax = plt.subplots()
        ...
        return fig, ax
    """
    def decorator(fn):
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            # Accept (fig, ax) or just ax
            if isinstance(result, tuple):
                fig, ax = result
            else:
                ax = result
                fig = ax.figure

            apply(ax, max_xticks=max_xticks, max_yticks=max_yticks, 
                  sci=sci, powerlimits=powerlimits)
            return fig, ax
        return wrapper

    if func:
        return decorator(func)
    return decorator


# --------------------------
# CONTEXT MANAGER
# --------------------------

@contextmanager
def autoformatting(max_xticks=6, max_yticks=6, sci=True, powerlimits=(-3,3)):
    """
    Usage:
    with autoformatting():
        fig, ax = plt.subplots()
        ax.plot(...)
    """
    yield
    # Apply to all axes created within with-block
    figs = list(map(plt.figure, plt.get_fignums()))
    for fig in figs:
        for ax in fig.get_axes():
            apply(ax, max_xticks=max_xticks, max_yticks=max_yticks,
                  sci=sci, powerlimits=powerlimits)
