from typing import Any, Dict, List, cast

import numpy as np
from pandas import Series

from ..core.aliases import NumericValue, PerformanceTable
from ..core.scales import NominalScale, QualitativeScale, Scale
from .plot import BarPlot, Figure


def plot_performance_table(
    performance_table: PerformanceTable,
    criteria_scales: Dict[str, Scale],
    plot: Any = None,
) -> Figure:
    """Create figure with all criterion values plotted in their own subplot.

    :param performance_table:
    :param criteria_scales:
    :param plot: class chosen to plot each criterion values
    :return: figure created
    """
    plot = BarPlot if plot is None else plot
    fig = Figure(
        ncols=2, nrows=int(np.ceil(len(performance_table.columns) / 2))
    )
    x = [*range(len(performance_table.index))]
    xticks = x
    xticklabels = performance_table.index.tolist()
    for _c, values in performance_table.items():
        c = cast(str, _c)
        ax = fig.create_add_axis()
        ax.title = c
        yticks = None
        yticklabels = None
        y = values
        if isinstance(criteria_scales[c], QualitativeScale):
            y = cast(Series, values.apply(criteria_scales[c].transform_to))
            yticklabels = criteria_scales[c].range()
            yticks = [
                criteria_scales[c].transform_to(yy) for yy in yticklabels
            ]
        elif isinstance(criteria_scales[c], NominalScale):
            yticklabels = criteria_scales[c].range()
            yticks = [*range(len(yticklabels))]
            y = cast(Series, values.apply(yticklabels.index))
        ax.add_plot(
            plot(
                x,
                cast(List[NumericValue], y),
                xticks=cast(List[NumericValue], xticks),
                yticks=cast(List[NumericValue], yticks),
                xticklabels=cast(List[str], xticklabels),
                yticklabels=cast(List[str], yticklabels),
            )
        )
    return fig
