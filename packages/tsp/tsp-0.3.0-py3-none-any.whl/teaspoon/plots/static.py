import matplotlib.dates as mdates
import numpy as np
import warnings

from matplotlib import pyplot as plt
from matplotlib.figure import Figure

try:
    from scipy.interpolate import griddata
except ModuleNotFoundError:
    warnings.warn("Missing scipy module. Some functionality will be limited.")

from typing import Union

import teaspoon

def trumpet_curve(depth, t_max, t_min, t_mean, title="", max_depth=None, t_units=u'\N{DEGREE SIGN} C', d_units="m") -> Figure:
    """Plot a trumpet curve

    The function returns a matplotlib Figure object. To show the figure, you must call the `show()` method.

    Parameters
    ----------
    depth : numpy.ndarray
        A d-length array of depths at which temperature values are 
    t_max : numpy.ndarray
        A d-length array of temperature values representing the maximum temperatures over the period at each of the depths.
    t_min : numpy.ndarray
        A d-length array of temperature values representing the minimum temperatures over the period at each of the depths.
    t_mean : str
       A d-length array of temperature values representing the mean temperatures over the period at each of the depths.
    title : str, optional
        A title for the figure, by default ""
    max_depth : float, optional
        If provided, limits the maximum y-axis extent of the plot, by default None
    t_units : unicode, optional
        Units for the x-axis (assumed to be temperature), by default u'\N{DEGREE SIGN} C'
    d_units : str, optional
        Units for the y axis (depth), by default "m"

    Returns
    -------
    Figure
        A matplotlib Figure. Note that to show the figure you must call the `show()` method or `matplotlib.pyplot.show()`.

    Raises
    ------
    ValueError
        _description_
    """
    ## Sanity checks and data 
    if not len(depth) == len(t_max) == len(t_min) == len(t_mean):
        raise ValueError("Length of input arrays must be equal")

    depth = - np.abs(depth)
    
    ## Create figure
    fig, ax1 = plt.subplots()

    ## Create artists
    # TODO:  https://stackoverflow.com/questions/45176584/dotted-lines-instead-of-a-missing-value-in-matplotlib
    line_max = ax1.plot(t_max, depth, marker='.', color='red', gid="max-temperature")
    line_min = ax1.plot(t_min, depth, marker='.', color='blue', gid="min-temperature")
    line_mean = ax1.plot(t_mean, depth, marker='.', color='black', gid="mean-temperature")

    surface = ax1.hlines(y=0.0, xmin=-100, xmax=100, linewidth=0.5, linestyles='dotted', color='grey')
    zero = ax1.vlines(x=0.0, ymin=-100, ymax=100, linewidth=0.5, linestyles='dotted', color='grey')

     ## Set axis properties
    ax1.set_ybound(upper=1, lower=min(depth) - 3)
    
    if max_depth:
        ax1.set_ybound(lower=-abs(max_depth))

    ax1.set_xbound(lower=min(t_min) - 3, upper=max(t_max) + 3)

    ## Set axis labels
    ax1.set_xlabel(f"Temperature [{t_units}]")
    ax1.set_ylabel(f"Depth [{d_units}]")
    ax1.set_title(title)

    return fig


def colour_contour(depths, times, values, title="", colours: "Union[str, list]"='symmetric', contour:list=[], label_contour=False, max_depth=None, gap_fill=False, 
                   d_units="m", **kwargs) -> Figure:
    """Create a colour-contour plot. 

    The x-axis is time and the y-axis is depth. Data values are interpolated and coloured.

    Parameters
    ----------
    depths : numpy.ndarray
        A d-length array of depths at which measurements are collected.
    times : numpy.ndarray
        A t-length array of python datetimes at which measurements are collected
    values : numpy.ndarray
        An array with shape (t,d) of values at each depth-time coordinate
    title : str, optional
        A title for the figure, by default ""
    colours : Union[str, list], optional
        Either a list of colours to be used for the colour bar, or one of:
        * **symmetric**: 
        * **dynamic**: 
        ,by default 'symmetric'
    contour : list, optional
        A list of float values. If provided, draw contours at each of those values, by default []
    label_contour : bool, optional
        Whether or not to label contour lines. Ignored if `contour` is empty, by default False
    max_depth : float, optional
        If provided, limits the maximum y-axis extent of the plot, by default None
    gap_fill : bool, optional
        _description_, by default False
    d_units : str, optional
        Units for the y axis (depth), by default "m"

    Returns
    -------
    Figure
        A matplotlib Figure. Note that to show the figure you must call the `show()` method or `matplotlib.pyplot.show()`.
    """
    tsp = teaspoon.TSP(times, depths, values)

    # Extract x, y and z (array) values
    X = tsp.times
    Y = -abs(tsp.depths)

    if gap_fill:
        try:
            smoothed = griddata(points = np.stack([tsp.long.dropna()['time'].values.astype(float),
                                                tsp.long.dropna()['depth'].values]).transpose(),
                                values = tsp.long.dropna()['temperature_in_ground'].values,  
                                xi = np.stack([tsp.long['time'].values.astype(float),
                                                tsp.long['depth'].values]).transpose(),
                                rescale=True, method='linear')
        except NameError:
            warnings.warn("Missing scipy library. Could not do gap filling.")
            gap_fill = False
            Z = np.array(tsp.wide.drop('time', axis=1)).transpose() 

        Z = smoothed.reshape(len(depths), len(values))
    
    else:
        Z = np.array(tsp.wide.drop('time', axis=1)).transpose()

    # Set up plot
    fig, ax1 = plt.subplots()

    clev = contour_levels(Z, colours, step=1)

    # Add data
    cs = ax1.contourf(X, Y, Z, levels=clev, cmap=plt.cm.coolwarm)
    fig.colorbar(cs, ticks = np.arange(-25,25,5))

    if len(contour) > 0:
        cs2 = ax1.contour(X, Y, Z, levels = contour, colors='k', linewidths = 1)
        if label_contour:
            plt.clabel(cs2, fontsize=8, inline=1, fmt="%1.0f")

    # Set axis properties
    if max_depth:
        ax1.set_ybound(lower=-abs(max_depth))

    ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.AutoDateLocator()))
    fig.autofmt_xdate()
    plt.subplots_adjust(bottom = 0.2, top = 0.95, left = 0.2, right = 0.95)

    # Set axis labels
    ax1.set_xlabel('Time')
    ax1.set_ylabel(f"Depth [{d_units}]")
    ax1.set_title(title)
    

    return fig


def time_series(depths, times, values, title='', d_units='m') -> Figure:
    """Create a time-series plot

    Using time as the X axis and data values as the y axis. Depths are plotted as their own lines.

    Parameters
    ----------
    depths : numpy.ndarray
        1-d list or array of datetimes with length d.
    times : numpy.ndarray
        1-d list or array of datetimes with length t.
    values : array
        An array of data values with shape (t,d). 
    title : str, optional
        A title for the plot, by default ''
    d_units : str, optional
        Units of the depths variable, by default 'm'

    Returns
    -------
    Figure
        A matplotlib Figure. Note that to show the figure you must call the `show()` method or `matplotlib.pyplot.show()`.
    """

    # Set up plot
    fig, ax = plt.subplots()

    # Add data elements
    lines = []
    for i, d in enumerate(depths):
        line_i, = ax.plot(times, values[:,i], lw=1, label=f'{d} {d_units}')
        lines.append(line_i)

    # Add legend
    leg = ax.legend(fancybox=True, shadow=True)

    lined = {}  # Will map legend lines to original lines.
    for legline, origline in zip(leg.get_lines(), lines):
        legline.set_picker(True)  # Enable picking on the legend line.
        lined[legline] = origline
    
    on_pick = create_legend_picker(fig, lined)
    fig.canvas.mpl_connect('pick_event', on_pick)

    # Set axis properties

    # Set axis labels
    ax.set_xlabel('Time')
    ax.set_ylabel(f"Depth [{d_units}]")
    ax.set_title(title)

    return fig


def ensemble_series(times, values, groups, title="", mode='spaghetti', percentiles=[0,90], show_mean=True, t_units=u'\N{DEGREE SIGN} C') -> Figure:
    """_summary_

    Parameters
    ----------
    times : numpy.ndarray
        A t-length array of python datetimes
    values : numpy.ndarray
        An array of data values with shape (t, n)
    groups : numpy.ndarray
        An n-length array
    title : str, optional
        _description_, by default ""
    mode : str, optional
        _description_, by default 'spaghetti'
    percentiles : list, optional
        _description_, by default [0,90]
    show_mean : bool, optional
        _description_, by default True
    t_units : unicode, optional
        _description_, by default u'\N{DEGREE SIGN} C'

    Returns
    -------
    Figure
        _description_
    """
     # set up plot
    fig, ax = plt.subplots()

    colors = plt.get_cmap("Paired")

    ## Add data
    for i, group in enumerate(np.unique(groups)):
        # Variability
        col2 = colors(2*i)
        col1 = colors(2*i + 1)

        mask = (groups == group)
        subset = values[:,mask]
        
        if mode == 'spaghetti':
            lines = add_spaghetti(ax, times, subset, color=col2)
        
        elif mode=='percentiles':
            lines = add_percentiles(ax, times, subset, percentiles=percentiles, color=col2)
    
        elif mode=='fill':
            lines = add_fill(ax, times, subset, percentiles=percentiles, color=col2)
        
        # Add data for mean
        if show_mean:
            avg = subset.mean(axis=1)
            ax.plot(times, avg, color=col1)

        
    ## Set axis labels
    ax.set_ylabel(f"Temperature [{t_units}]")
    ax.set_xlabel(f"Time")
    ax.set_title(title)

    return fig


def add_spaghetti(axes, xs, ys, color='black',lw=0.5):
    lines = axes.plot(xs, ys, color=color, lw=lw)
    return lines 


def add_percentiles(axes, xs, ys, percentiles=[10,90], color='black', lw=0.5):
    percs = np.percentile(ys, percentiles, axis=1).transpose()
    lines = axes.plot(xs, percs, color=color, lw=lw)
    return lines


def add_fill(axes, xs, ys, percentiles=[10,90], color='black'):
    percs = np.percentile(ys, percentiles, axis=1).transpose()
    lines = axes.fill_between(xs, percs.min(axis=1), percs.max(axis=1), color=color)
    return lines


def alpha(rgba: "tuple[float]", alpha: float) -> tuple:
    alpha = max(0., min(alpha, 1.))
    return rgba * np.array([1., 1., 1., alpha])
    

def contour_levels(data, levels: "Union[str,list]", step=1) -> "np.ndarray":
    if levels == "dynamic":
        return np.arange(np.nanmin(data), np.nanmax(data), step)
    
    elif levels == "symmetric":
        return np.arange(min(np.nanmin(data), -np.nanmax(data) + 1),
                         max(-np.nanmin(data) - 1, np.nanmax(data)), step)
    else:
        try:
            lev = np.array(levels, dtype='float')
            return lev
        except Exception:
            raise TypeError("Contour levels not properly specified")


def create_legend_picker(fig, lined) -> object:
    
    def on_pick(event):
        # On the pick event, find the original line corresponding to the legend
        # proxy line, and toggle its visibility.
        legline = event.artist
        origline = lined[legline]
        visible = not origline.get_visible()
        origline.set_visible(visible)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled.
        legline.set_alpha(1.0 if visible else 0.2)
        fig.canvas.draw()
    
    return on_pick




