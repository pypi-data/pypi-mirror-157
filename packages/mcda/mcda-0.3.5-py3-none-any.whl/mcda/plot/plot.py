"""This module gathers all plotting functions.

All those functions use `matplotlib <https://matplotlib.org/>`
and `graphviz <https://graphviz.org/>`.
"""
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union, cast

import graphviz
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from graphviz import Digraph
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path as MPath
from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes
from matplotlib.spines import Spine
from matplotlib.ticker import FixedLocator
from matplotlib.transforms import Affine2D
from pandas import Index, Series

from ..core.aliases import NumericValue, PerformanceTable
from ..core.relations import (
    Relation,
    RelationType,
    transitive_reduction_matrix,
)


def piecewise_linear_colormap(
    colors: Any, name: str = "cmap"
) -> mcolors.LinearSegmentedColormap:
    """Create piecewise linear colormap.

    :param colors: list of any type of color accepted by :mod:`matplotlib`
    :param name: name of the created colormap
    :return: piecewise linear colormap
    """
    return mcolors.LinearSegmentedColormap.from_list(name, colors)


def radar_projection_name(num_vars: int) -> str:
    """Give projection corresponding to radar with `num_vars` axes.

    :param num_vars: number of axes of the radar plot
    :return:
    """
    return f"radar{num_vars}"


def create_radar_projection(num_vars: int, frame: str = "circle"):
    """Create a radar projection with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    :param num_vars: number of variables for radar chart
    :param frame: shape of frame surrounding axes ('circle' or 'polygon')

    Example:
        If you want to create radar projections up to a reasonable amount of
        variables. You can use the code below:

        .. code:: python

            from mcda.plot.new_plot import create_radar_projection

            for i in range(1, 12):
                create_radar_projection(i, frame="polygon")
    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarTransform(PolarAxes.PolarTransform):
        def transform_path_non_affine(self, path):
            # Paths with non-unit interpolation steps correspond to gridlines,
            # in which case we force interpolation (to defeat PolarTransform's
            # autoconversion to circular arcs).
            if path._interpolation_steps > 1:
                path = path.interpolated(num_vars)
            return MPath(self.transform(path.vertices), path.codes)

    class RadarAxes(PolarAxes):

        name = radar_projection_name(num_vars)
        # use 1 line segment to connect specified points
        RESOLUTION = 1
        PolarTransform = RadarTransform

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location("N")

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == "circle":
                return Circle((0.5, 0.5), 0.5)
            elif frame == "polygon":
                return RegularPolygon(
                    (0.5, 0.5), num_vars, radius=0.5, edgecolor="k"
                )
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == "circle":
                return super()._gen_axes_spines()
            elif frame == "polygon":
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(
                    axes=self,
                    spine_type="circle",
                    path=MPath.unit_regular_polygon(num_vars),
                )
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(
                    Affine2D().scale(0.5).translate(0.5, 0.5) + self.transAxes
                )
                return {"polar": spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)


class Figure:
    """This class is a wrapper around :class:`matplotlib.figure.Figure`

    It plots and organizes any number of :class:`mcda.plot.new_plot.Axis`.

    If `ncols` (resp. `nrows`) is ``0``, then columns will be added (resp.
    rows) when a row is full (resp. column). If both are ``0``, the grid layout
    will be as balanced as possible.

    :param fig: matplotlib figure to use (if not provided, one will be created)
    :param figsize: figure size in inches as a tuple (`width`, `height`)
    :param ncols: number of columns for the subplot layout
    :param nrows: number of rows for the subplot layout
    :param tight_layout:
        if ``True``, matplotlib `tight_layout` function is used to organize
        axes

    .. note::
        if `ncols` or `nrows` is ``0``, an unlimited number of axes can be
        added to the figure

    .. seealso::
        `Matplotlib tight layout guide <https://matplotlib.org/stable/tutorials/intermediate/tight_layout_guide.html>`_
            Guide on tight-layout usage to fit plots within figures more cleanly
    """  # noqa E501

    def __init__(
        self,
        fig: Any = None,
        figsize: Tuple[float, float] = None,
        ncols: int = 0,
        nrows: int = 0,
        tight_layout: bool = True,
    ):
        self.fig = fig
        self.axes: List[Axis] = []
        self.figsize = figsize
        self.layout = (nrows, ncols)
        self.tight_layout = tight_layout

    def reset(self):
        """Reset `fig` attribute"""
        self.fig = (
            plt.figure()
            if self.figsize is None
            else plt.figure(figsize=self.figsize)
        )

    @property
    def max_axes(self) -> NumericValue:
        """Return maximum number of axes the figure can handle.

        :return:
        """
        if self.layout[0] == 0 or self.layout[1] == 0:
            return float("inf")
        return self.layout[0] * self.layout[1]

    def create_add_axis(self, projection: str = None) -> "Axis":
        """Create an axis and add it to figure.

        :param projection: projection to use in created axis
        :return: created axis
        """
        axis = Axis(projection=projection)
        self.add_axis(axis)
        return axis

    def add_axis(self, axis: "Axis"):
        """Add axis to the figure.

        :param axis:
        """
        if len(self.axes) > self.max_axes:
            raise IndexError("already max number of axes")
        self.axes.append(axis)
        axis.figure = self

    def _pre_draw(self):
        """Prepare figure before drawing."""
        self.fig.clear()
        nb = len(self.axes)
        nrows, ncols = self.layout
        if self.layout[0] == 0 and self.layout[1] == 0:
            nrows = int(np.ceil(np.sqrt(nb)))
            ncols = int(np.ceil(nb / nrows))
        elif self.layout[0] == 0:
            nrows = int(np.ceil(nb / ncols))
        elif self.layout[1] == 0:
            ncols = int(np.ceil(nb / nrows))
        for i, axis in enumerate(self.axes):
            if axis.projection is None:
                ax = self.fig.add_subplot(nrows, ncols, i + 1)
            else:
                ax = self.fig.add_subplot(
                    nrows,
                    ncols,
                    i + 1,
                    projection=axis.projection,
                )
            axis.ax = ax

    def _draw(self):
        """Draw all axes."""
        for axis in self.axes:
            axis.draw()

    def _post_draw(self):
        """Apply operations after axes drawings complete."""
        if self.tight_layout:
            self.fig.tight_layout()
        self.fig.show()

    def draw(self):
        """Draw figure and all its axes content."""
        if self.fig is None:
            self.fig = (
                plt.figure()
                if self.figsize is None
                else plt.figure(figsize=self.figsize)
            )
        self._pre_draw()
        self._draw()
        self._post_draw()


class Axis:
    """This class is a wrapper around :class:`matplotlib.axes.Axes`

    It draws any number of :class:`mcda.plot.new_plot.Plot` on a same subplot.

    :param figure: figure holding the object
    :param plots: list of plots to draw
    :param ax: matplotlib axes
    :param title: title of the object
    :param xlabel: label to use for `x` axis
    :param ylabel: label to use for `y` axis
    :param xlabel_tilted:
        if ``True`` `xlabel` is tilted to better fit
    :param projection:
        projection to use when creating `ax` attribute from scratch
    """

    def __init__(
        self,
        figure: Figure = None,
        plots: "List[Plot]" = None,
        ax: Any = None,
        title: str = None,
        xlabel: str = None,
        ylabel: str = None,
        xlabel_tilted: bool = False,
        projection: str = None,
    ):
        self.figure = figure
        self.plots = [] if plots is None else plots
        self.ax = ax
        self.title = title
        self.projection = projection
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xlabel_tilted = xlabel_tilted
        self.plots = []
        self.legend = False
        self.legend_title: Optional[str] = None
        self.legend_location: Optional[str] = None

    def draw(self):
        """Draw the subplot and all its plots."""
        if self.ax is None:
            fig = Figure()
            fig.add_axis(self)
            fig.draw()
            return

        for p in self.plots:
            p.draw()
        if self.legend is not None:
            if np.any([plot.label is not None for plot in self.plots]):
                if self.legend_location == "left":
                    self.ax.legend(
                        loc="center right",
                        bbox_to_anchor=(0, 0.5),
                        title=self.legend_title,
                    )
                if self.legend_location == "right":
                    self.ax.legend(
                        loc="center left",
                        bbox_to_anchor=(1, 0.5),
                        title=self.legend_title,
                    )
                if self.legend_location == "top":
                    self.ax.legend(
                        loc="lower center",
                        bbox_to_anchor=(0.5, 1),
                        title=self.legend_title,
                    )
                if self.legend_location == "bottom":
                    self.ax.legend(
                        loc="upper center",
                        bbox_to_anchor=(0.5, 0),
                        title=self.legend_title,
                    )
        if self.title is not None:
            self.ax.set_title(self.title)
        if self.xlabel is not None:
            options = (
                {"rotation": -45, "ha": "left", "rotation_mode": "anchor"}
                if self.xlabel_tilted
                else {}
            )
            self.ax.set_xlabel(self.xlabel, **options)
        if self.ylabel is not None:
            self.ax.set_ylabel(self.ylabel)

    def add_plot(self, plot: "Plot"):
        """Add a plot to the subplot.

        :param plot:
        """
        self.plots.append(plot)
        plot.axis = self

    def add_legend(self, title: str = "", location: str = "right"):
        """Add a legend to the subplot

        :param title: title of the legend
        :param location: location of the legend
            Supported values: ``'left'``, ```'right'``, `'top'``, ``'bottom'``

        ..note::
            only labeled plot are drawn in the legend
        """
        self.legend = True
        self.legend_title = title
        self.legend_location = location


class Plot:
    """This class is the base of all plot objects of this package.

    :param axis: subplot on which to be plotted
    :param label: label that will be displayed in the legend
    """

    def __init__(self, axis: Axis = None, label: str = None):
        self.axis = axis
        self.label = label

    @property
    def default_axis(self) -> Axis:
        """Default subplot object on which to plot itself."""
        return Axis()

    @property
    def ax(self):
        """Matplotlib axes direct access"""
        return self.axis.ax

    def draw(self):
        """Draw this plot."""
        if self.axis is None:
            ax = self.default_axis
            ax.add_plot(self)
            ax.draw()
            return
        self._pre_draw()
        self._draw()
        self._post_draw()

    def _pre_draw(self):
        """Prepare this plot."""
        pass

    def _draw(self):
        """Do the actual drawing of this plot."""
        pass

    def _post_draw(self):
        """Apply necessary operations after plot is drawn."""
        pass


class CartesianPlot(Plot):
    """This class represents 2D cartesian plots.

    :param x: data abscissa to plot
    :param y: data ordinates to plot
    :param xlim: limits used for `x` axis
    :param ylim: limits used for `y` axis
    :param xticks: ticks used for `x` axis
    :param yticks: ticks used for `y` axis
    :param xticklabels: labels used to replace numeric ticks for `x` axis
    :param yticklabels: labels used to replace numeric ticks for `y` axis
    :param xticklabels_tilted:
        if ``True`` `xticklabels` are tilted to better fit
    :param axis: subplot on which to be plotted
    :param label: label that will be displayed in the legend
    """

    def __init__(
        self,
        x: List[NumericValue],
        y: List[NumericValue],
        xlim: Tuple[NumericValue, NumericValue] = None,
        ylim: Tuple[NumericValue, NumericValue] = None,
        xticks: List[NumericValue] = None,
        yticks: List[NumericValue] = None,
        xticklabels: List[str] = None,
        yticklabels: List[str] = None,
        xticklabels_tilted: bool = False,
        axis: Axis = None,
        label: str = None,
    ):
        Plot.__init__(self, axis, label)
        self.x = x
        self.y = y
        self.xlim = xlim
        self.ylim = ylim
        self.xticks = xticks
        self.yticks = yticks
        self.xticklabels = xticklabels
        self.yticklabels = yticklabels
        self.xticklabels_tilted = xticklabels_tilted

    def _post_draw(self):
        """Set ticks and their labels."""
        if self.xlim is not None:
            self.ax.set_xlim(self.xlim)
        if self.xticks is not None:
            self.ax.set_xticks(self.xticks)
            if self.xticklabels is not None:
                options = (
                    {"rotation": -45, "ha": "left", "rotation_mode": "anchor"}
                    if self.xticklabels_tilted
                    else {}
                )
                self.ax.set_xticklabels(self.xticklabels, **options)
        if self.ylim is not None:
            self.ax.set_ylim(self.ylim)
        if self.yticks is not None:
            self.ax.set_yticks(self.yticks)
            if self.yticklabels is not None:
                self.ax.set_yticklabels(self.yticklabels)


class LinePlot(CartesianPlot):
    """This class draws a regular lines and points plot.

    :param x: data abscissa to plot
    :param y: data ordinates to plot
    :param xlim: limits used for `x` axis
    :param ylim: limits used for `y` axis
    :param xticks: ticks used for `x` axis
    :param yticks: ticks used for `y` axis
    :param xticklabels: labels used to replace numeric ticks for `x` axis
    :param yticklabels: labels used to replace numeric ticks for `y` axis
    :param xticklabels_tilted:
        if ``True`` `xticklabels` are tilted to better fit
    :param axis: subplot on which to be plotted
    :param label: label that will be displayed in the legend
    :param linestyle: linestyle of the line plotted
        =============    ===============================
        parameter        description
        =============    ===============================
        ``'-'``          solid line style
        ``'--'``         dashed line style
        ``'-.'``         dash-dot line style
        ``':'``          dotted line style
        =============    ===============================
    :param marker: marker style
        =============   ===============================
        parameter       description
        =============   ===============================
        ``'.'``         point marker
        ``','``         pixel marker
        ``'o'``         circle marker
        ``'v'``         triangle_down marker
        ``'^'``         triangle_up marker
        ``'<'``         triangle_left marker
        ``'>'``         triangle_right marker
        ``'1'``         tri_down marker
        ``'2'``         tri_up marker
        ``'3'``         tri_left marker
        ``'4'``         tri_right marker
        ``'8'``         octagon marker
        ``'s'``         square marker
        ``'p'``         pentagon marker
        ``'P'``         plus (filled) marker
        ``'*'``         star marker
        ``'h'``         hexagon1 marker
        ``'H'``         hexagon2 marker
        ``'+'``         plus marker
        ``'x'``         x marker
        ``'X'``         x (filled) marker
        ``'D'``         diamond marker
        ``'d'``         thin_diamond marker
        ``'|'``         vline marker
        ``'_'``         hline marker
        =============   ===============================
        Symbols `here <https://matplotlib.org/stable/api/markers_api.html>`__.
    :param color: color of the line plotted
        List of colors available `here <https://matplotlib.org/stable/gallery/color/named_colors.html>`__.
    :param alpha:
        if set, the line is colored with this transparency
    """  # noqa E501

    def __init__(
        self,
        x: List[NumericValue],
        y: List[NumericValue],
        xlim: Tuple[NumericValue, NumericValue] = None,
        ylim: Tuple[NumericValue, NumericValue] = None,
        xticks: List[NumericValue] = None,
        yticks: List[NumericValue] = None,
        xticklabels: List[str] = None,
        yticklabels: List[str] = None,
        xticklabels_tilted: bool = False,
        axis: Axis = None,
        label: str = None,
        linestyle: str = None,
        marker: str = None,
        color: str = None,
        alpha: float = None,
    ):
        CartesianPlot.__init__(
            self,
            x,
            y,
            xlim,
            ylim,
            xticks,
            yticks,
            xticklabels,
            yticklabels,
            xticklabels_tilted,
            axis,
            label,
        )
        self.linestyle = linestyle
        self.marker = marker
        self.color = color
        self.alpha = alpha

    def _draw(self):
        """Draw the lines and points regular plot."""
        self.ax.plot(
            self.x,
            self.y,
            linestyle=self.linestyle,
            marker=self.marker,
            color=self.color,
            alpha=self.alpha,
            label=self.label,
        )


class AreaPlot(CartesianPlot):
    """This class draws an line plot,
    where the area between the x axis and the line is filled.

    :param x: data abscissa to plot
    :param y: data ordinates to plot
    :param xlim: limits used for `x` axis
    :param ylim: limits used for `y` axis
    :param xticks: ticks used for `x` axis
    :param yticks: ticks used for `y` axis
    :param xticklabels: labels used to replace numeric ticks for `x` axis
    :param yticklabels: labels used to replace numeric ticks for `y` axis
    :param xticklabels_tilted:
        if ``True`` `xticklabels` are tilted to better fit
    :param axis: subplot on which to be plotted
    :param label: label that will be displayed in the legend
    :param color: color of the area and the line plotted
        List of colors available `here <https://matplotlib.org/stable/gallery/color/named_colors.html>`__.
    :param alpha:
        if set, the area is colored with this transparency
    :param strongline: if ``True`` the line is drawn without transparency
    """  # noqa E501

    def __init__(
        self,
        x: List[NumericValue],
        y: List[NumericValue],
        xlim: Tuple[NumericValue, NumericValue] = None,
        ylim: Tuple[NumericValue, NumericValue] = None,
        xticks: List[NumericValue] = None,
        yticks: List[NumericValue] = None,
        xticklabels: List[str] = None,
        yticklabels: List[str] = None,
        xticklabels_tilted: bool = False,
        axis: Axis = None,
        label: str = None,
        color: str = None,
        alpha: float = 1.0,
        strongline: bool = True,
    ):
        CartesianPlot.__init__(
            self,
            x,
            y,
            xlim,
            ylim,
            xticks,
            yticks,
            xticklabels,
            yticklabels,
            xticklabels_tilted,
            axis,
            label,
        )
        self.color = color
        self.alpha = alpha
        self.strongline = strongline

    def _draw(self):
        """Draw the area chart."""
        self.ax.fill_between(
            self.x,
            self.y,
            color=self.color,
            alpha=self.alpha,
            label=self.label,
        )
        if self.strongline:
            self.ax.plot(self.x, self.y, color=self.color)


class ParallelCoordinatesPlot(Plot):
    """This class draws a parallel coordinates chart.

    :param x: data abscissa to plot
    :param values: list of data values to plot for each line
    :param xlim: limits used for `x` axis
    :param ylim: limits used for `y` axis
    :param xticks: ticks used for `x` axis
    :param yticks: ticks used for `y` axis
    :param xticklabels: labels used to replace numeric ticks for `x` axis
    :param yticklabels: labels used to replace numeric ticks for `y` axis
    :param xticklabels_tilted:
        if ``True`` `xticklabels` are tilted to better fit
    :param axis: subplot on which to be plotted
    :param labels: labels of the lines that will be displayed in the legend
    :param linestyle: linestyle of the lines plotted
    :param marker: marker style of the lines plotted
    :param color: color of the lines plotted
        List of colors available `here <https://matplotlib.org/stable/gallery/color/named_colors.html>`_.
    :param alpha:
        if set, lines plotted are colored with this transparency
    """  # noqa E501

    def __init__(
        self,
        x: List[NumericValue],
        values: Union[List[List[NumericValue]], PerformanceTable],
        xlim: Tuple[NumericValue, NumericValue] = None,
        ylim: Tuple[NumericValue, NumericValue] = None,
        xticks: List[NumericValue] = None,
        yticks: List[NumericValue] = None,
        xticklabels: List[str] = None,
        yticklabels: List[str] = None,
        xticklabels_tilted: bool = False,
        axis: Axis = None,
        labels: Union[Sequence[Optional[str]], Index, Series] = None,
        linestyle: str = None,
        marker: str = None,
        color: str = None,
        alpha: float = None,
    ):
        Plot.__init__(self, axis)
        self.x = x
        values = np.array(values)
        labels = cast(Sequence[str], np.array(labels))
        if labels is None:
            labels = [None] * len(values)
        self.lines = []
        for i in range(len(values)):
            y = np.array(values[i])
            self.lines.append(
                LinePlot(
                    self.x,
                    y,
                    xlim,
                    ylim,
                    xticks,
                    yticks,
                    xticklabels,
                    yticklabels,
                    xticklabels_tilted,
                    axis,
                    labels[i],
                    linestyle,
                    marker,
                    color,
                    alpha,
                )
            )
        self.min = np.min(values)
        self.max = np.max(values)
        self.length = self.max - self.min

    def _pre_draw(self):
        """Prepare the parallel coordinates chart."""
        for line in self.lines:
            if line not in self.axis.plots:
                self.axis.add_plot(line)
        for i in self.x:
            self.axis.ax.arrow(
                i,
                self.min,
                0,
                1.05 * self.length,
                head_length=0.03 * self.length,
                head_width=0.02 * len(self.x),
                color="black",
            )


class StemPlot(CartesianPlot):
    """This class draws a stem plot.

    :param x: data abscissa to plot
    :param y: data ordinates to plot
    :param xlim: limits used for `x` axis
    :param ylim: limits used for `y` axis
    :param xticks: ticks used for `x` axis
    :param yticks: ticks used for `y` axis
    :param xticklabels: labels used to replace numeric ticks for `x` axis
    :param yticklabels: labels used to replace numeric ticks for `y` axis
    :param xticklabels_tilted:
        if ``True`` `xticklabels` are tilted to better fit
    :param axis: subplot on which to be plotted
    :param label: label that will be displayed in the legend
    """

    def _draw(self):
        """Draw the stem plot."""
        self.ax.stem(self.x, self.y, label=self.label)


class BarPlot(CartesianPlot):
    """This class draws a bar chart.

    :param x: data abscissa to plot
    :param y: data ordinates to plot
    :param xlim: limits used for `x` axis
    :param ylim: limits used for `y` axis
    :param xticks: ticks used for `x` axis
    :param yticks: ticks used for `y` axis
    :param xticklabels: labels used to replace numeric ticks for `x` axis
    :param yticklabels: labels used to replace numeric ticks for `y` axis
    :param xticklabels_tilted:
        if ``True`` `xticklabels` are tilted to better fit
    :param axis: subplot on which to be plotted
    :param label: label that will be displayed in the legend
    :param width: width of the bars plotted
    :param bottom: bottom values for each bar
    :param color: color of the bars plotted
        List of colors available `here <https://matplotlib.org/stable/gallery/color/named_colors.html>`__.
    :param alpha:
        if set, bars plotted are colored with this transparency
    """  # noqa E501

    def __init__(
        self,
        x: List[NumericValue],
        y: List[NumericValue],
        xlim: Tuple[NumericValue, NumericValue] = None,
        ylim: Tuple[NumericValue, NumericValue] = None,
        xticks: List[NumericValue] = None,
        yticks: List[NumericValue] = None,
        xticklabels: List[str] = None,
        yticklabels: List[str] = None,
        xticklabels_tilted: bool = False,
        axis: Axis = None,
        label: str = None,
        width: NumericValue = 0.8,
        bottom: List[NumericValue] = None,
        color: str = None,
        alpha: float = None,
    ):
        CartesianPlot.__init__(
            self,
            x,
            y,
            xlim,
            ylim,
            xticks,
            yticks,
            xticklabels,
            yticklabels,
            xticklabels_tilted,
            axis,
            label,
        )
        self.width = width
        self.bottom = bottom
        self.color = color
        self.alpha = alpha

    def _draw(self):
        """Draw the bar chart."""
        if self.bottom is not None:
            self.ax.bar(
                self.x,
                self.y,
                width=self.width,
                color=self.color,
                alpha=self.alpha,
                bottom=self.bottom,
                label=self.label,
            )
        else:
            self.ax.bar(
                self.x,
                self.y,
                width=self.width,
                color=self.color,
                alpha=self.alpha,
                label=self.label,
            )


class StackedBarPlot(Plot):
    """This class draws a stacked bar chart.

    :param x: data abscissa to plot
    :param values: list of data values to plot for each group
    :param xlim: limits used for `x` axis
    :param ylim: limits used for `y` axis
    :param xticks: ticks used for `x` axis
    :param yticks: ticks used for `y` axis
    :param xticklabels: labels used to replace numeric ticks for `x` axis
    :param yticklabels: labels used to replace numeric ticks for `y` axis
    :param xticklabels_tilted:
        if ``True`` `xticklabels` are tilted to better fit
    :param axis: subplot on which to be plotted
    :param labels: labels of the groups that will be displayed in the legend
    :param width: width of the bars plotted
    :param color: color of the bars plotted
        List of colors available `here <https://matplotlib.org/stable/gallery/color/named_colors.html>`__.
    :param alpha:
        if set, bars plotted are colored with this transparency
    """  # noqa E501

    def __init__(
        self,
        x: List[NumericValue],
        values: List[List[NumericValue]],
        xlim: Tuple[NumericValue, NumericValue] = None,
        ylim: Tuple[NumericValue, NumericValue] = None,
        xticks: List[NumericValue] = None,
        yticks: List[NumericValue] = None,
        xticklabels: List[str] = None,
        yticklabels: List[str] = None,
        xticklabels_tilted: bool = False,
        axis: Axis = None,
        labels: Union[List[Optional[str]], Index, Series] = None,
        width: NumericValue = 0.8,
        color: str = None,
        alpha: float = None,
    ):
        Plot.__init__(self, axis)
        values = np.array(values)
        if labels is None:
            labels = [None] * len(values)
        self.barplots = []
        bottom = np.full_like(x, 0, dtype=float)
        for i in range(len(values)):
            self.barplots.append(
                BarPlot(
                    x,
                    values[i],
                    xlim,
                    ylim,
                    xticks,
                    yticks,
                    xticklabels,
                    yticklabels,
                    xticklabels_tilted,
                    axis,
                    labels[i],
                    width,
                    bottom.copy(),
                    color,
                    alpha,
                )
            )
            bottom += values[i]

    def _pre_draw(self):
        """Prepare the stacked bar chart."""
        for barplot in self.barplots:
            if barplot not in self.axis.plots:
                self.axis.add_plot(barplot)


class HorizontalStripes(Plot):
    """This class draws horizontal stripes.

    :param stripeticks: `y` ticks separating horizontal stripes
    :param color: color of the stripes
        List of colors available `here <https://matplotlib.org/stable/gallery/color/named_colors.html>`__.
    :param alpha:
        if set, the stripes are colored with this transparency
    :param attach_yticks: if ``True`` `yticks` are `stripeticks`
    :param axis: subplot on which to be plotted
    """  # noqa E501

    def __init__(
        self,
        stripeticks: List[NumericValue] = None,
        color: str = None,
        alpha: float = None,
        attach_yticks: bool = False,
        axis: Axis = None,
    ):
        Plot.__init__(self, axis)
        self.stripeticks = stripeticks
        self.color = color
        self.alpha = alpha
        self.attach_yticks = attach_yticks

    def _draw(self):
        """Draw the horizontal stripes."""
        for i in range(0, len(self.stripeticks) - 1, 2):
            self.ax.axhspan(
                self.stripeticks[i],
                self.stripeticks[i + 1],
                color=self.color,
                alpha=self.alpha,
            )

    def _post_draw(self):
        """Set ticks."""
        if self.attach_yticks:
            self.ax.yaxis.set_minor_locator(FixedLocator(self.stripeticks))
            self.ax.tick_params(axis="y", which="major", left=False)


class VerticalStripes(Plot):
    """This class draws a vertical stripes.

    :param stripeticks: `x` ticks separating vertical stripes
    :param color: color of the stripes plotted
        List of colors available `here <https://matplotlib.org/stable/gallery/color/named_colors.html>`__.
    :param alpha:
        if set, the stripes are colored with this transparency
    :param attach_xticks: if ``True`` `xticks` are `stripeticks`
    :param axis: subplot on which to be plotted
    """  # noqa E501

    def __init__(
        self,
        stripeticks: List[NumericValue] = None,
        color: str = None,
        alpha: float = None,
        attach_xticks: bool = False,
        axis: Axis = None,
    ):
        Plot.__init__(self, axis)
        self.stripeticks = stripeticks
        self.color = color
        self.alpha = alpha
        self.attach_xticks = attach_xticks

    def _draw(self):
        """Draw the vertical stripes."""
        for i in range(0, len(self.stripeticks) - 1, 2):
            self.ax.axvspan(
                self.stripeticks[i],
                self.stripeticks[i + 1],
                color=self.color,
                alpha=self.alpha,
            )

    def _post_draw(self):
        """Set ticks."""
        if self.attach_xticks:
            self.ax.xaxis.set_minor_locator(FixedLocator(self.stripeticks))
            self.ax.tick_params(axis="x", which="major", bottom=False)


class PolarPlot(Plot):
    """This class represents polar plots.

    :param x: data labels to plot
    :param y: data values to plot
    :param axis: subplot on which to be plotted
    :param label: label that will be displayed in the legend
    """

    def __init__(
        self,
        x: List[str],
        y: List[NumericValue],
        axis: Axis = None,
        label: str = None,
    ):
        Plot.__init__(self, axis, label)
        self.x = x
        self.y = y


class PiePlot(PolarPlot):
    """This class draws a pie chart.

    :param x: data labels to plot
    :param y: data values to plot
    :param axis: subplot on which to be plotted
    """

    def _draw(self):
        """Draw the pie chart."""
        self.ax.pie(self.y, labels=self.x)


class RadarPlot(PolarPlot):
    """This class draws a radar chart (also called spider plot).

    :param x: data labels to plot
    :param y: data values to plot
    :param alpha:
        if set, surface under the plot is colored with this transparency
    :param axis: subplot on which to be plotted
    :param label: label that will be displayed in the legend
    :param rlimits: limits for radial axis

    .. warning::
        This type of plot must be used with a `radar` type projection.
        The projection must exist before drawing of this chart can occur.

    .. seealso::
        Function :func:`create_radar_projection`
            This function should be called before drawing this chart so the
            radar projection (with same number of variables) is already
            registered.
    """

    def __init__(
        self,
        x: List[str],
        y: List[NumericValue],
        alpha: float = None,
        axis: Axis = None,
        label: str = None,
        rlimits: List[NumericValue] = None,
    ):
        PolarPlot.__init__(self, x, y, axis, label)
        self.alpha = alpha
        self.rlimits = rlimits

    @property
    def default_axis(self) -> Axis:
        """Default subplot object on which to plot itself."""
        return Axis(projection=radar_projection_name(len(self.x)))

    def _draw(self):
        # calculate evenly-spaced axis angles
        theta = np.linspace(0, 2 * np.pi, len(self.x), endpoint=False)
        if self.rlimits is not None:
            self.ax.set_ylim(self.rlimits)
        self.ax.plot(theta, self.y, label=self.label)
        if self.alpha is not None:
            self.ax.fill(theta, self.y, alpha=self.alpha)

    def _post_draw(self):
        self.ax.set_varlabels(self.x)
        self.ax.set_rlabel_position(0)


class Text(Plot):
    """This class represents text plots.

    :param x: text abscissa
    :param y: text ordinate
    :param text: text to plot
    :param horizontal_alignement: text horizontal alignement
        Supported values: ``'center'``, ``'right'``, ``'left'``
    :param vertical_alignement: text vertical alignement
        Supported values: ``'center'``, ``'top'``, ``'bottom'``, ``'baseline'``, ``'center_baseline'``
    :param alpha:
        if set, the text background is colored with this transparency
    :param box:
        if ``True`` draw a box around the text
    :param axis: subplot on which to be plotted
    """  # noqa E501

    def __init__(
        self,
        x: NumericValue,
        y: NumericValue,
        text: str,
        horizontal_alignement: str = "left",
        vertical_alignement: str = "baseline",
        alpha: float = None,
        box: bool = False,
        axis: Axis = None,
    ):
        Plot.__init__(self, axis)
        self.x = x
        self.y = y
        self.text = text
        if alpha is not None:
            self.alpha = alpha
        elif box:
            self.alpha = 1
        else:
            self.alpha = 0
        self.horizontal_alignement = horizontal_alignement
        self.vertical_alignement = vertical_alignement
        self.box = box

    def _draw(self):
        """Draw the text."""
        if self.box:
            self.ax.text(
                self.x,
                self.y,
                self.text,
                ha=self.horizontal_alignement,
                va=self.vertical_alignement,
                bbox=dict(
                    boxstyle="round",
                    color="white",
                    alpha=self.alpha,
                    ec="0.8",
                ),
            )
        else:
            self.ax.text(
                self.x,
                self.y,
                self.text,
                ha=self.horizontal_alignement,
                va=self.vertical_alignement,
                bbox=dict(
                    boxstyle="round,pad=0",
                    color="white",
                    alpha=self.alpha,
                ),
            )


class Annotation(Text):
    """This class represents annotation plots.

    :param x: annotated point abscissa
    :param y: annotated point ordinate
    :param text: the text of the annotation
    :param xoffset: x-axis text offset (in points) from the annotated point
    :param yoffset: y-axis text offset (in points) from the annotated point
    :param horizontal_alignement: text horizontal alignement
        Supported values: ``'center'``, ``'right'``, ``'left'``
    :param vertical_alignement: text vertical alignement
        Supported values: ``'center'``, ``'top'``, ``'bottom'``, ``'baseline'``, ``'center_baseline'``
    :param alpha:
        if set, the text background is colored with this transparency
    :param box:
        if ``True`` draw a box around the text
    :param axis: subplot on which to be plotted
    """  # noqa E501

    def __init__(
        self,
        x: NumericValue,
        y: NumericValue,
        text: str,
        xoffset: NumericValue = 0,
        yoffset: NumericValue = 0,
        horizontal_alignement: str = "left",
        vertical_alignement: str = "baseline",
        alpha: float = None,
        box: bool = False,
        axis: Axis = None,
    ):
        Plot.__init__(self, axis)
        self.x = x
        self.y = y
        self.text = text
        self.xoffset = xoffset
        self.yoffset = yoffset
        if alpha is not None:
            self.alpha = alpha
        elif box:
            self.alpha = 1
        else:
            self.alpha = 0
        self.horizontal_alignement = horizontal_alignement
        self.vertical_alignement = vertical_alignement
        self.box = box

    def _draw(self):
        """Draw the text."""
        if self.box:
            self.ax.annotate(
                text=self.text,
                xy=(self.x, self.y),
                xytext=(self.xoffset, self.yoffset),
                textcoords="offset points",
                ha=self.horizontal_alignement,
                va=self.vertical_alignement,
                bbox=dict(
                    boxstyle="round",
                    color="white",
                    alpha=self.alpha,
                    ec="0.8",
                ),
            )
        else:
            self.ax.annotate(
                text=self.text,
                xy=(self.x, self.y),
                xytext=(self.xoffset, self.yoffset),
                textcoords="offset points",
                ha=self.horizontal_alignement,
                va=self.vertical_alignement,
                bbox=dict(
                    boxstyle="round,pad=0",
                    color="white",
                    alpha=self.alpha,
                ),
            )


def plot_outranking(
    outranking_matrix: PerformanceTable,
    edge_label: bool = False,
    transitive_reduction_: bool = True,
) -> Digraph:
    """Create a graph for outranking matrix.

    This function creates a Graph using graphviz and display it.

    :param outranking_matrix: the matrix to display
    :param edge_label: (optional) parameter to display the value of edges.
    :param transitive_reduction_: (optional) enable transitive reduction
    """

    matrix = (
        transitive_reduction_matrix(outranking_matrix)
        if transitive_reduction_
        else outranking_matrix
    )
    graph = graphviz.Digraph("graph", strict=True)
    graph.attr("node", shape="box")

    for a in matrix.index.tolist():
        for b in matrix.columns.tolist():
            if matrix.loc[matrix.index == a, matrix.columns == b].all(None):
                graph.edge(
                    str(a),
                    str(b),
                    label=str(
                        matrix.loc[matrix.index == a, matrix.columns == b]
                    )
                    if edge_label
                    else "",
                )
    graph.render()
    return graph


def indifference_group(
    relation_list: List[Relation],
    alternative_dict: Dict[str, List[str]],
) -> Dict[str, List[str]]:
    """Associate every key of indifference alternatives

    This function is used to make a proper dictionnary with associating the
    alternatives which are indifferent

    :param relation_list: the list of relation
    :param alternative_dict: the dictionnary of every alternatives
    """
    for a, b, r in relation_list:
        if r == RelationType.INDIFFERENCE and a != b:
            for element in alternative_dict[a]:
                if b not in alternative_dict[element]:
                    alternative_dict[element] = list(
                        set(alternative_dict[element] + alternative_dict[b])
                    )
                alternative_dict[element].sort()
            for element in alternative_dict[b]:
                alternative_dict[element] = alternative_dict[a]
    return alternative_dict


def get_names(alternative_dict: Dict[str, List[str]]) -> Dict[str, str]:
    """Create a dictionary with the names of alternatives and their indexes.

    This function is used to make a proper dictionary with associating the
    right combination of alternatives names

    :param alternative_dict: the dictionary with the right key
    """
    new_dict = {}
    for key, value in alternative_dict.items():
        temp = ""
        for element in value:
            if temp == "":
                temp = f"{element}"
            else:
                temp = f"{temp}, {element}"
        new_dict[key] = temp
    return new_dict


def plot_relation(
    relation_list: List[Relation],
    relation_types: List[RelationType] = None,
) -> Digraph:
    """Create a graph for list of relation.

    This function creates a Graph using graphviz and display it.

    :param relation_list: the list of relation to display
    :param relation_types: types of relations to plot
    """

    relation_types = (
        [RelationType.PREFERENCE, RelationType.INDIFFERENCE]
        if relation_types is None
        else relation_types
    )
    relation_graph = graphviz.Digraph("relation", strict=True)
    relation_graph.attr("node", shape="box")
    for a, b, _ in relation_list:
        relation_graph.node(str(a))
        relation_graph.node(str(b))
    for a, b, r in relation_list:
        if r not in relation_types:
            continue
        if r == RelationType.PREFERENCE:
            relation_graph.edge(
                str(a),
                str(b),
            )
        elif r == RelationType.INDIFFERENCE:
            relation_graph.edge(
                str(a),
                str(b),
                arrowhead="none",
            )
        else:
            relation_graph.edge(
                str(a),
                str(b),
                style="dotted",
                arrowhead="none",
            )
    relation_graph.render()
    return relation_graph


def plot_linear_ranking(
    alternatives_list: Series,
):
    """Create a graph for list of alternatives.

    This function creates a Graph using graphviz and display it.

    :param alternatives_list: the alternatives number with the rank
    """

    _alternatives_list = alternatives_list.copy()
    _alternatives_list.index = _alternatives_list.index.astype("string")
    rank_unique = _alternatives_list.drop_duplicates()
    alternatives_same_rank = rank_unique.apply(
        lambda x: ", ".join(_alternatives_list.index[_alternatives_list == x])
    )
    _alternatives_list = rank_unique.set_axis(alternatives_same_rank)
    _alternatives_list = _alternatives_list.sort_values(ascending=False)
    relation_graph = graphviz.Digraph("relation", strict=True)
    relation_graph.attr("node", shape="box")
    prev_alt = ""
    for alt in _alternatives_list.index.tolist():
        label = ""
        relation_graph.node(alt)
        if prev_alt != "":
            relation_graph.edge(
                prev_alt,
                alt,
                label=label,
            )
        prev_alt = alt
    relation_graph.render()
    return relation_graph
