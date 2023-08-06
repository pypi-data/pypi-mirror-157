"""This module implements the Electre I algorithm.

Implementation and naming conventions are taken from
:cite:p:`vincke1998electre`.
"""

from typing import Dict

from pandas import Series

from ..core.aliases import NumericValue, PerformanceTable
from ..core.scales import PreferenceDirection, QuantitativeScale


def delta_calculation(
    performance_table: PerformanceTable,
) -> NumericValue:
    """Compute delta for discordance.

    :param performance_table:
    :return: the value of the discordance's delta"""
    return max(performance_table.apply(lambda x: max(x) - min(x)))


def pairwise_concordance(
    alternative_values1: Series,
    alternative_values2: Series,
    criteria_weights: Dict[str, NumericValue],
    scales: Dict[str, QuantitativeScale],
) -> NumericValue:
    """Compute the concordance comparison of 2 alternatives.

    :param alternative_values1:
    :param alternative_values2:
    :param criteria_weights:
    :param scales:
    :return: concordance index"""
    concordance_value = 0.0
    for k in alternative_values1.index:
        concordance_value = (
            concordance_value + criteria_weights[k]
            if (
                alternative_values1[k] >= alternative_values2[k]
                and scales[k].preference_direction == PreferenceDirection.MAX
            )
            or (
                alternative_values1[k] <= alternative_values2[k]
                and scales[k].preference_direction == PreferenceDirection.MIN
            )
            else concordance_value
        )
    concordance_value = concordance_value / sum(criteria_weights.values())
    assert concordance_value >= 0
    return concordance_value


def concordance(
    performance_table: PerformanceTable,
    criteria_weights: Dict[str, NumericValue],
    scales: Dict[str, QuantitativeScale],
) -> PerformanceTable:
    """Compute the concordance matrix.

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :return: concordance matrix"""
    return PerformanceTable(
        [
            [
                pairwise_concordance(
                    performance_table.loc[ai],
                    performance_table.loc[aj],
                    criteria_weights,
                    scales,
                )
                for aj in performance_table.index
            ]
            for ai in performance_table.index
        ],
        index=performance_table.index,
        columns=performance_table.index,
    )


def pairwise_discordance(
    alternative_values1: Series,
    alternative_values2: Series,
    scales: Dict[str, QuantitativeScale],
    delta: NumericValue,
) -> NumericValue:
    """Compute the discordance comparison of 2 alternatives.

    :param alternative_values1:
    :param alternative_values2:
    :param scales: criteria scales
    :param delta: discordance delta
    :return: discordance index"""
    res = alternative_values2 - alternative_values1
    for i, scale in scales.items():
        if scale.preference_direction == PreferenceDirection.MIN:
            res[i] *= -1
    return max(res) / delta


def discordance(
    performance_table: PerformanceTable, scales: Dict[str, QuantitativeScale]
) -> PerformanceTable:
    """Compute the discordance matrix.

    :param performance_table:
    :param scales: criteria scales
    :return: discordance matrix"""
    delta = delta_calculation(performance_table)
    return PerformanceTable(
        [
            [
                pairwise_discordance(
                    performance_table.loc[ai],
                    performance_table.loc[aj],
                    scales,
                    delta,
                )
                for aj in performance_table.index
            ]
            for ai in performance_table.index
        ],
        index=performance_table.index,
        columns=performance_table.index,
    )


def outranking(
    concordance_: PerformanceTable,
    discordance_: PerformanceTable,
    c_hat: NumericValue,
    d_hat: NumericValue,
) -> PerformanceTable:
    """Compute the outranking matrix.

    :param discordance_: discordance matrix
    :param concordance_: concordance matrix
    :param c_hat: concordance threshold
    :param d_hat: discordance threshold
    :return: the outranking matrix of the performance table"""
    ones = PerformanceTable(
        1, index=concordance_.index, columns=concordance_.columns
    )
    return ones[(concordance_ >= c_hat) & (discordance_ <= d_hat)].fillna(0)


def electre1(
    performance_table: PerformanceTable,
    criteria_weights: Dict[str, NumericValue],
    scales: Dict[str, QuantitativeScale],
    c_hat: NumericValue,
    d_hat: NumericValue,
    concordance_matrix: PerformanceTable = None,
    discordance_matrix: PerformanceTable = None,
) -> PerformanceTable:
    """Compute the outranking matrix using Electre I method.

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param c_hat: concordance threshold
    :param d_hat: discordance threshold
    :param concordance_matrix: concordance matrix
    :param discordance_matrix: discordance matrix
    :return: the outranking matrix of the performance table"""
    concordance_matrix = (
        concordance(performance_table, criteria_weights, scales)
        if concordance_matrix is None
        else concordance_matrix
    )
    discordance_matrix = (
        discordance(performance_table, scales)
        if discordance_matrix is None
        else discordance_matrix
    )
    return outranking(concordance_matrix, discordance_matrix, c_hat, d_hat)
