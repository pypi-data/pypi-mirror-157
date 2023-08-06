"""This module implements the SRMP algorithm.

Implementation and naming conventions are taken from
:cite:p:`olteanu2022preference`.
"""
from typing import Dict, List, Tuple, cast

import numpy as np
from pandas import Series, concat

from mcda.plot.plot import (
    Annotation,
    AreaPlot,
    Axis,
    BarPlot,
    Figure,
    HorizontalStripes,
    LinePlot,
    ParallelCoordinatesPlot,
    StackedBarPlot,
    Text,
)

from ..core.aliases import Function, NumericValue, PerformanceTable
from ..core.performance_table import (
    apply_criteria_functions,
    apply_criteria_weights,
    normalize,
    normalize_without_scales,
    transform,
)
from ..core.scales import (
    PreferenceDirection,
    QualitativeScale,
    QuantitativeScale,
    Scale,
    is_better_or_equal,
)


def preference_relation(
    profile: Series,
    performance_table: PerformanceTable,
    criteria_weights: Dict[str, NumericValue],
    scales: Dict[str, QuantitativeScale],
) -> PerformanceTable:
    """Define a preference relation related to a profile

    :param profile:
    :param performance_table:
    :param criteria_weights:
    :param scales:
    :return: preference matrix
    """
    functions = {
        criterion: (
            cast(
                Function,
                lambda x, c=criterion: is_better_or_equal(
                    x, profile[c], scales[c]
                ),
            )
        )  # https://bugs.python.org/issue13652
        for criterion in scales.keys()
    }

    conditional_weighted_sum = apply_criteria_weights(
        apply_criteria_functions(performance_table, functions),
        criteria_weights,
    ).sum(1)

    return PerformanceTable(
        [
            [
                conditional_weighted_sum[ai] >= conditional_weighted_sum[aj]
                for aj in performance_table.index
            ]
            for ai in performance_table.index
        ],
        index=performance_table.index,
        columns=performance_table.index,
        dtype="int64",
    )


def ranking(
    relations: List[PerformanceTable],
    lexicographic_order: List[int],
) -> Series:
    """Rank alternatives

    :param relations: list of preference relations
    :param lexicographic_order: profile indices used sequentially to rank
    :return: the outranking total order
    """
    relations_ordered = [relations[i] for i in lexicographic_order]
    n = len(relations_ordered)
    score = sum(
        [
            PerformanceTable(2 ** (n - 1 - i) * relations_ordered[i])
            for i in range(n)
        ],
        PerformanceTable(
            0,
            index=relations_ordered[0].index,
            columns=relations_ordered[0].columns,
        ),
    )
    outranking_matrix = score - score.transpose() >= 0
    return outranking_matrix.sum(1)


def srmp(
    performance_table: PerformanceTable,
    criteria_weights: Dict[str, NumericValue],
    scales: Dict[str, QuantitativeScale],
    profiles: PerformanceTable,
    lexicographic_order: List[int],
) -> Series:
    """Compute the SRMP algorithm

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param profiles:
    :param lexicographic_order: profile indices used sequentially to rank
    :return: the outranking total order
    """
    relations = profiles.apply(
        preference_relation,
        1,
        performance_table=performance_table,
        criteria_weights=criteria_weights,
        scales=scales,
    ).tolist()
    return ranking(relations, lexicographic_order)


def plot_input_data(
    performance_table: PerformanceTable,
    scales: Dict[str, QuantitativeScale],
    criteria_weights: Dict[str, NumericValue] = None,
    profiles: PerformanceTable = None,
    lexicographic_order: List[int] = None,
    annotations: bool = False,
    annotations_alpha: float = 0.5,
    scales_boundaries: bool = False,
    figsize: Tuple[float, float] = None,
    xticklabels_tilted: bool = False,
):
    """Visualize input data
    For each criterion, the arrow indicates the preference direction.
    The criteria weights are displayed as a bar plot,
    and their values are written in parentheses

    :param performance_table:
    :param scales:
    :param criteria_weights:
    :param profiles:
    :param lexicographic_order: profile indices used sequentially to rank
    :param annotations:
        if ``True`` every point is annotated with its value
    :param annotations_alpha: annotations white box transparency
    :param scales_boundaries:
        if ``True`` the criteria boundaries are the scales boundaries,
        else they are computed from the data
    :param figsize: figure size in inches as a tuple (`width`, `height`)
    :param xticklabels_tilted:
        if ``True`` `xticklabels` are tilted to better fit
    """
    # Reorder scales and criteria_weights
    scales = {crit: scales[crit] for crit in performance_table.columns}
    if criteria_weights is not None:
        criteria_weights = {
            crit: criteria_weights[crit] for crit in performance_table.columns
        }

    # Transform to quantitative scales
    quantitative_scales = {}
    for key, scale in scales.items():
        if isinstance(scale, QualitativeScale):
            quantitative_scales[key] = scale.quantitative
        else:
            quantitative_scales[key] = scale

    # Normalize data
    if profiles is not None:
        df = concat([performance_table, profiles])
    else:
        df = performance_table.copy()
    df = transform(
        df,
        cast(Dict[str, Scale], scales),
        cast(Dict[str, Scale], quantitative_scales),
    )
    if scales_boundaries:
        df = normalize(df, cast(Dict[str, Scale], quantitative_scales))
    else:
        df = normalize_without_scales(df)
        for key, scale in quantitative_scales.items():
            if scale.preference_direction == PreferenceDirection.MIN:
                df[key] = 1 - df[key]

    # Create constants
    nb_alt = len(performance_table)
    if profiles is not None:
        nb_profiles = len(profiles)

    # Create figure and axis
    fig = Figure(figsize=figsize)
    ax = fig.create_add_axis()

    # Axis parameters
    x = cast(List[float], range(len(performance_table.columns)))
    xticks = cast(List[float], (range(len(performance_table.columns))))
    if criteria_weights is not None:
        xticklabels = [
            f"{crit}\n({weight})" for crit, weight in criteria_weights.items()
        ]
    else:
        xticklabels = [f"{crit}" for crit in performance_table.columns]

    # Criteria weights
    if criteria_weights is not None:
        weights = np.array([*criteria_weights.values()])
        weights_normalized = weights / weights.sum()
        ax.add_plot(
            BarPlot(
                x,
                weights_normalized,
                xticks=xticks,
                yticks=[],
                xticklabels=xticklabels,
                xticklabels_tilted=xticklabels_tilted,
                width=0.1,
                alpha=0.5,
            )
        )

    # Plotted annotations' coordinates
    annotations_coord: List[Tuple[float, float]] = []

    # Profiles
    if profiles is not None:
        for profile in range(nb_alt, nb_alt + nb_profiles):
            ax.add_plot(
                AreaPlot(
                    x,
                    df.iloc[profile],
                    xticks=xticks,
                    yticks=[],
                    xticklabels=xticklabels,
                    xticklabels_tilted=xticklabels_tilted,
                    color="black",
                    alpha=0.1,
                    strongline=False,
                )
            )
            ax.add_plot(
                Annotation(
                    0,
                    df.iloc[profile, 0],
                    f"$P^{profile-nb_alt}$",
                    -1,
                    0,
                    "right",
                    "center",
                )
            )

    # Alternatives
    values = df[:nb_alt]
    labels = df[:nb_alt].index
    ax.add_plot(
        ParallelCoordinatesPlot(
            x,
            values,
            xticks=xticks,
            yticks=[],
            xticklabels=xticklabels,
            xticklabels_tilted=xticklabels_tilted,
            labels=labels,
            linestyle="-.",
        )
    )
    # Legend
    ax.add_legend(title="Alternatives :", location="right")

    fig.draw()
    assert ax.ax is not None  # to comply with mypy

    # Annotations
    if annotations:
        if profiles is not None:
            for profile in range(nb_alt, nb_alt + nb_profiles):
                for i in x:
                    xy = (i, df.iloc[profile, i])
                    overlap = False
                    for (xc, yc) in annotations_coord:
                        if (xc == i) and (
                            abs(
                                ax.ax.transData.transform(xy)[1]
                                - ax.ax.transData.transform((xc, yc))[1]
                            )
                            < 10
                        ):
                            # if current annotation overlaps
                            # already plotted annotations
                            overlap = True
                            break

                    if not overlap:
                        annotation = Annotation(
                            i,
                            df.iloc[profile, i],
                            profiles.iloc[profile - nb_alt, i],
                            2,
                            0,
                            "left",
                            "center",
                            annotations_alpha,
                        )
                        ax.add_plot(annotation)
                        annotations_coord.append((i, df.iloc[profile, i]))

        for alt in range(nb_alt):
            for i in x:
                xy = (i, df.iloc[alt, i])
                overlap = False
                for (xc, yc) in annotations_coord:
                    if (xc == i) and (
                        abs(
                            ax.ax.transData.transform(xy)[1]
                            - ax.ax.transData.transform((xc, yc))[1]
                        )
                        < 10
                    ):
                        # if current annotation overlaps
                        # already plotted annotations
                        overlap = True
                        break

                if not overlap:
                    annotation = Annotation(
                        i,
                        df.iloc[alt, i],
                        performance_table.iloc[alt, i],
                        2,
                        0,
                        "left",
                        "center",
                        annotations_alpha,
                    )
                    ax.add_plot(annotation)
                    annotations_coord.append((i, df.iloc[alt, i]))

    # Lexicographic order
    if lexicographic_order is not None:
        text = Text(
            0,
            1.2,
            "Lexicographic order : $"
            + r" \rightarrow ".join(
                [f"P^{profile}" for profile in lexicographic_order]
            )
            + "$",
            box=True,
        )
        ax.add_plot(text)
    fig.draw()


def plot_concordance_index(
    performance_table: PerformanceTable,
    scales: Dict[str, QuantitativeScale],
    criteria_weights: Dict[str, NumericValue],
    profiles: PerformanceTable,
    lexicographic_order: List[int],
    figsize: Tuple[float, float] = None,
    ncols: int = 0,
    nrows: int = 0,
    xlabels_tilted: bool = False,
):
    """Visualize concordance index between alternatives and profiles

    :param performance_table:
    :param scales:
    :param criteria_weights:
    :param profiles:
    :param lexicographic_order: profile indices used sequentially to rank
    :param figsize: figure size in inches as a tuple (`width`, `height`)
    :param xlabels_tilted:
        if ``True`` `xlabels` are tilted to better fit
    """
    # Create constants
    nb_alt = len(performance_table)
    nb_profiles = len(profiles)
    weights_sum = sum(criteria_weights.values())

    # Create figure and axes
    fig = Figure(figsize=figsize, ncols=ncols, nrows=nrows)

    for ind_alt in range(nb_alt):
        ax = Axis(
            xlabel=f"{performance_table.index[ind_alt]}",
            xlabel_tilted=xlabels_tilted,
        )
        # Axis properties
        x = cast(List[float], range(nb_profiles))
        xticks = cast(List[float], range(nb_profiles))
        xticklabels = [f"$P^{profile}$" for profile in lexicographic_order]
        ylim = (0.0, 1.0)

        values = []
        # Draw the stacked barplot
        for ind_crit, crit in enumerate(performance_table.columns):
            crit_values = np.array(
                [
                    criteria_weights[crit] / weights_sum
                    if is_better_or_equal(
                        performance_table.iloc[ind_alt, ind_crit],
                        profiles.iloc[profile, ind_crit],
                        scales[crit],
                    )
                    else 0
                    for profile in lexicographic_order
                ]
            )
            values.append(crit_values)
        ax.add_plot(
            StackedBarPlot(
                x,
                values,
                ylim=ylim,
                xticks=xticks,
                xticklabels=xticklabels,
                labels=performance_table.columns,
            )
        )
        fig.add_axis(ax)
    ax.add_legend(title="Criteria :", location="right")
    fig.draw()


def plot_progressive_ranking(
    performance_table: PerformanceTable,
    scales: Dict[str, QuantitativeScale],
    criteria_weights: Dict[str, NumericValue],
    profiles: PerformanceTable,
    lexicographic_order: List[int],
    figsize: Tuple[float, float] = None,
):
    """Visualize ranking progressively according to the lexicographic order

    :param performance_table:
    :param scales:
    :param criteria_weights:
    :param profiles:
    :param lexicographic_order: profile indices used sequentially to rank
    :param figsize: figure size in inches as a tuple (`width`, `height`)
    """
    # Create constants
    nb_alt = len(performance_table)
    nb_profiles = len(lexicographic_order)

    # Compute rankings progressively
    relations = profiles.apply(
        preference_relation,
        1,
        performance_table=performance_table,
        criteria_weights=criteria_weights,
        scales=scales,
    ).tolist()
    rankings = PerformanceTable(
        [
            ranking(relations, lexicographic_order[:stop])
            for stop in range(1, nb_profiles + 1)
        ]
    )

    # Create figure and axes
    fig = Figure(figsize=figsize)
    ax = Axis(xlabel="Profiles", ylabel="Rank")
    fig.add_axis(ax)

    # Axis parameters
    xticks = cast(List[float], range(nb_profiles))
    xticklabels = [f"$P^{profile}$" for profile in lexicographic_order]
    ylim = (0.5, nb_alt + 0.5)
    yticks = cast(List[float], range(1, nb_alt + 1))
    yminorticks = np.arange(1, nb_alt + 2) - 0.5
    yticklabels = cast(List[str], range(nb_alt, 0, -1))

    # Draw horizontal striped background
    ax.add_plot(
        HorizontalStripes(
            yminorticks, color="black", alpha=0.1, attach_yticks=True
        )
    )

    # Number of alternatives for each rank (depending on the profile)
    rank_counts = PerformanceTable(
        [
            dict(zip(*np.unique(rankings.loc[profile], return_counts=True)))
            for profile in rankings.index
        ],
        columns=range(1, nb_alt + 1),
    ).fillna(0)
    # Offsets' width for each rank (depending on the profile)
    offsets_width = 1 / (rank_counts + 1)
    # Offsets to apply to current alternative's ranks
    offsets = [0.5] * nb_profiles
    # Alternatives sorted according to the final ranking
    final_ranking_sorted = rankings.iloc[-1].sort_values(ascending=False).index
    # Previous alternative's ranks
    previous_ranks = [nb_alt + 1] * nb_profiles

    for alt in final_ranking_sorted:
        # Current alternative's ranks
        ranks = rankings[alt]
        # Update offsets (return to 0.5 if it's a new rank)
        offsets = np.where(ranks == previous_ranks, offsets, 0.5)
        offsets = [
            offsets[profile] - offsets_width.loc[profile, ranks[profile]]
            for profile in range(nb_profiles)
        ]
        x = cast(List[float], range(nb_profiles))
        y = ranks + offsets
        ax.add_plot(
            LinePlot(
                x,
                y,
                xticks=xticks,
                xticklabels=xticklabels,
                ylim=ylim,
                yticks=yticks,
                yticklabels=yticklabels,
                marker="o",
            )
        )
        ax.add_plot(
            Annotation(
                nb_profiles - 1,
                ranks.iloc[-1] + offsets[-1],
                str(alt),
                10,
                0,
                vertical_alignement="center",
                box=True,
            )
        )
        previous_ranks = ranks
    fig.draw()
