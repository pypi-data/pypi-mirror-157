"""This module implements the Electre II algorithm.

Implementation and naming conventions are taken from
:cite:p:`vincke1998electre`.
"""
from typing import Dict, List

from mcda.core.aliases import NumericValue, PerformanceTable
from mcda.core.scales import QuantitativeScale
from mcda.outranking.electre1 import concordance, discordance
from mcda.outranking.utils import cycle_reduction_matrix


def outranking(
    concordance_: PerformanceTable,
    discordance_: PerformanceTable,
    c_hat: NumericValue,
    d_hat: NumericValue,
) -> PerformanceTable:
    """Calculate the outranking matrix according to given thresholds.

    :param concordance_: concordance matrix
    :param discordance_: discordance matrix
    :param c_hat: concordance threshold
    :param d_hat: discordance threshold
    :return: outranking matrix
    """
    ones = PerformanceTable(
        1, index=concordance_.index, columns=concordance_.columns
    )
    return ones[
        (concordance_ >= concordance_.T)
        & (concordance_ >= c_hat)
        & (discordance_ <= d_hat)
    ].fillna(0)


def categories_to_outranking(categories: List[List[str]]) -> PerformanceTable:
    """Convert a ranking of categories of alternatives into an outranking
    matrix.

    :param categories:
        the ranked categories (each category is a list of alternatives)
    :return: outranking matrix

    .. todo:: reposition function?
    """

    alternatives = [a for ll in categories for a in ll]
    res = PerformanceTable(0, index=alternatives, columns=alternatives)
    for category in categories:
        res.loc[category, category] = 1
        res.loc[
            category, alternatives[alternatives.index(category[-1]) + 1 :]
        ] = 1
    return res


def distillation(
    strong_outranking_matrix: PerformanceTable,
    weak_outranking_matrix: PerformanceTable,
    ascending: bool = False,
) -> List[List[str]]:
    """Compute distillation.

    :param strong_outranking_matrix:
    :param weak_outranking_matrix:
    :param ascending: if ``True`` distillation is done in ascending direction
    :return: ranking of categories
    """
    axis = 1 if ascending else 0
    distillate = []
    rest = weak_outranking_matrix.index.tolist()
    strong_outranking_matrix = cycle_reduction_matrix(strong_outranking_matrix)
    weak_outranking_matrix = cycle_reduction_matrix(weak_outranking_matrix)
    while len(rest) > 0:
        outranked = strong_outranking_matrix.loc[rest, rest].apply(
            sum, axis=axis
        )
        B = outranked[outranked == 0].index.tolist()
        outranked = weak_outranking_matrix.loc[B, B].apply(sum, axis=axis)
        A = outranked[outranked == 0].index.tolist()
        for i in A:
            rest.remove(i)
        distillate.append(A)
    return distillate[::-1] if ascending else distillate


def final_ranking(
    ascending_distillation: PerformanceTable,
    descending_distillation: PerformanceTable,
) -> PerformanceTable:
    """Compute the final ranking by combining the
    ascending and descending distillation.

    :param ascending_distillation: ascending distillation outranking matrix
    :param descending_distillation: descending distillation outranking matrix
    :return: final outranking matrix
    """

    return ascending_distillation * descending_distillation


def electre_ii(
    performance_table: PerformanceTable,
    criteria_weights: Dict[str, NumericValue],
    scales: Dict[str, QuantitativeScale],
    c_hat_sup: NumericValue,
    c_hat_inf: NumericValue,
    d_hat_sup: NumericValue,
    d_hat_inf: NumericValue,
    concordance_matrix: PerformanceTable = None,
    discordance_matrix: PerformanceTable = None,
) -> PerformanceTable:
    """Compute final outranking matrix for Electre II.

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param c_hat_sup: higher concordance threshold
    :param c_hat_inf: lower concordance threshold
    :param d_hat_sup: higher discordance threshold
    :param d_hat_inf: lower discordance threshold
    :param concordance_matrix:
    :param discordance_matrix:
    :return: final outranking matrix
    """
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
    s_dominance_matrix = outranking(
        concordance_matrix, discordance_matrix, c_hat_sup, d_hat_inf
    )
    w_dominance_matrix = outranking(
        concordance_matrix, discordance_matrix, c_hat_inf, d_hat_sup
    )
    ascending_distillate = distillation(
        s_dominance_matrix,
        w_dominance_matrix,
        ascending=True,
    )
    descending_distillate = distillation(
        s_dominance_matrix,
        w_dominance_matrix,
    )
    final_rank = final_ranking(
        categories_to_outranking(ascending_distillate),
        categories_to_outranking(descending_distillate),
    )
    return final_rank
