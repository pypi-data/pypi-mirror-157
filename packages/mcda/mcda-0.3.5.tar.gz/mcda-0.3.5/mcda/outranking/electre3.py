"""This module implements the Electre 3 algorithm.

Implementation and naming conventions are taken from
:cite:p:`vincke1998electre`.
"""
from typing import Any, Dict, List

from pandas import Series

from ..core.aliases import NumericValue, PerformanceTable
from ..core.scales import PreferenceDirection, QuantitativeScale
from .electre2 import categories_to_outranking, final_ranking


def concordance_index(
    ga: NumericValue,
    gb: NumericValue,
    pga: NumericValue,
    qga: NumericValue,
    preference_direction: PreferenceDirection,
) -> NumericValue:
    """Compute the concordance index between two alternatives wrt a criterion.

    :param ga: preference function of first alternative wrt criterion
    :param gb: preference function of second alternative wrt criterion
    :param pga: preference threshold for the criterion
    :param qga: indifference threshold for the criterion
    :param preference_direction:
    :return: concordance index value"""
    if pga < qga:
        raise ValueError(
            "Indifference value cannot be greater than preference value"
        )
    if (
        gb > (ga + pga) and preference_direction == PreferenceDirection.MAX
    ) or (gb < (ga - pga) and preference_direction == PreferenceDirection.MIN):
        return 0
    if (
        gb <= (ga + qga) and preference_direction == PreferenceDirection.MAX
    ) or (
        gb >= (ga - qga) and preference_direction == PreferenceDirection.MIN
    ):
        return 1
    return (
        (ga + pga - gb) / (pga - qga)
        if preference_direction == PreferenceDirection.MAX
        else (-ga + pga + gb) / (pga - qga)
    )


def pairwise_concordance(
    alternative_values1: Series,
    alternative_values2: Series,
    criteria_weights: Dict[str, NumericValue],
    scales: Dict[str, QuantitativeScale],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
) -> NumericValue:
    """Compute the pairwise concordance between two alternatives.

    :param alternative_values1:
    :param alternative_values2:
    :param criteria_weights:
    :param scales:
    :param preference_thresholds:
    :param indifference_thresholds:
    :return: pairwise concordance value
    """

    return (
        sum(
            criteria_weights[i]
            * concordance_index(
                alternative_values1[i],
                alternative_values2[i],
                preference_thresholds[i],
                indifference_thresholds[i],
                scales[i].preference_direction,
            )
            for i in criteria_weights
        )
        / sum(criteria_weights.values())
    )


def discordance_index(
    ga: NumericValue,
    gb: NumericValue,
    pga: NumericValue,
    vga: NumericValue,
    preference_direction: PreferenceDirection,
) -> NumericValue:
    """Compute the discordance index between two alternatives wrt a criterion.

    :param ga: preference function of first alternative wrt the criterion
    :param gb: preference function of second alternative wrt the criterion
    :param pga: preference threshold for the criterion
    :param vga:
        veto threshold for the criterion. ``None`` for the highest value
    :param preference_direction:
    :return: discordance index value"""
    if vga is not None and pga > vga:
        raise ValueError("Preference value cannot be greater than Veto value")
    if (
        vga is None
        or (
            gb <= (ga + pga)
            and preference_direction == PreferenceDirection.MAX
        )
        or (
            gb >= (ga - pga)
            and preference_direction == PreferenceDirection.MIN
        )
    ):
        return 0
    elif (
        gb > (ga + vga) and preference_direction == PreferenceDirection.MAX
    ) or (gb < (ga - vga) and preference_direction == PreferenceDirection.MIN):
        return 1
    else:
        return (
            (gb - pga - ga) / (vga - pga)
            if preference_direction == PreferenceDirection.MAX
            else (-gb - pga + ga) / (vga - pga)
        )


def pairwise_credibility_index(
    pairwise_concordance_: NumericValue,
    pairwise_discordance_: Series,
) -> NumericValue:
    """Compute the credibility index between two alternatives.

    :pairwise_concordance_:
        concordance value for criterion between both alternatives
    :pairwise_discordance_:
        discordance serie for criterion between both alternatives
    :return: pairwise credibility index"""
    sup_discordance = pairwise_discordance_[
        pairwise_discordance_ > pairwise_concordance_
    ]
    S_ab = pairwise_concordance_
    if len(sup_discordance) > 0:
        for Di_ab in sup_discordance:
            S_ab = S_ab * (1 - Di_ab) / (1 - pairwise_concordance_)
    return S_ab


def concordance(
    performance_table: PerformanceTable,
    criteria_weights: Dict[str, NumericValue],
    scales: Dict[str, QuantitativeScale],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
) -> PerformanceTable:
    """Compute the concordance matrix.

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param preference_thresholds:
    :param indifference_thresholds:
    :return: concordance matrix"""

    return PerformanceTable(
        [
            [
                pairwise_concordance(
                    performance_table.loc[i],
                    performance_table.loc[j],
                    criteria_weights,
                    scales,
                    preference_thresholds,
                    indifference_thresholds,
                )
                for j in performance_table.index
            ]
            for i in performance_table.index
        ],
        index=performance_table.index,
        columns=performance_table.index,
    )


def discordance(
    performance_table: PerformanceTable,
    scales: Dict[str, QuantitativeScale],
    preference_thresholds: Dict[str, NumericValue],
    veto_thresholds: Dict[str, NumericValue],
) -> PerformanceTable:
    """Compute the discordance matrix.

    :param performance_table:
    :param scales:
    :param preference_thresholds:
    :param veto_thresholds:
    :return: discordance matrix"""

    return PerformanceTable(
        [
            [
                Series(
                    {
                        j: discordance_index(
                            performance_table.loc[k, j],
                            performance_table.loc[i, j],
                            preference_thresholds[j],
                            veto_thresholds[j],
                            scales[j].preference_direction,
                        )
                        for j in performance_table.columns
                    }
                )
                for i in performance_table.index
            ]
            for k in performance_table.index
        ],
        index=performance_table.index,
        columns=performance_table.index,
    )


def credibility(
    performance_table: PerformanceTable,
    criteria_weights: Dict[str, NumericValue],
    scales: Dict[str, QuantitativeScale],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    veto_thresholds: Dict[str, NumericValue],
    concordance_function=None,
    discordance_function=None,
) -> PerformanceTable:
    """Compute the credibility matrix.

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param preference_thresholds:
    :param indifference_thresholds:
    :param veto_thresholds:
    :param concordance_function: function used to calculate concordance matrix
    :param discordance_function: function used to calculate discordance matrix
    :return: credibility matrix
    """
    concordance_function = (
        concordance if concordance_function is None else concordance_function
    )

    discordance_function = (
        discordance if discordance_function is None else discordance_function
    )
    concordance_matrix = concordance_function(
        performance_table,
        criteria_weights,
        scales,
        preference_thresholds,
        indifference_thresholds,
    )
    discordance_matrix = discordance_function(
        performance_table, scales, preference_thresholds, veto_thresholds
    )
    return PerformanceTable(
        [
            [
                pairwise_credibility_index(
                    concordance_matrix.loc[i, j],
                    discordance_matrix.loc[i, j],
                )
                for j in performance_table.index
            ]
            for i in performance_table.index
        ],
        index=performance_table.index,
        columns=performance_table.index,
    )


def qualification(
    performance_table: PerformanceTable,
    criteria_weights: Dict[str, NumericValue],
    scales: Dict[str, QuantitativeScale],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    veto_thresholds: Dict[str, NumericValue],
    concordance_function=None,
    discordance_function=None,
    credibility_function=None,
    alpha: NumericValue = 0.30,
    beta: NumericValue = -0.15,
) -> Series:
    """Compute the qualification for each pair of alternatives a and b.

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param preference_thresholds:
    :param indifference_thresholds:
    :param veto_thresholds:
    :param concordance_function: function used to calculate concordance matrix
    :param discordance_function: function used to calculate discordance matrix
    :param credibility_function: function used to calculate credibility matrix
    :param alpha: preset up values of distillation coefficients
    :param beta: preset up values of distillation coefficients
    :return: qualifications"""
    concordance_function = (
        concordance if concordance_function is None else concordance_function
    )

    discordance_function = (
        discordance if discordance_function is None else discordance_function
    )

    credibility_function = (
        credibility if credibility_function is None else credibility_function
    )
    assert (
        len(performance_table) > 0
    ), "Please be sure to have correctly implemented the performance matrix"

    credibility_mat = credibility_function(
        performance_table,
        criteria_weights,
        scales,
        preference_thresholds,
        indifference_thresholds,
        veto_thresholds,
        concordance_function,
        discordance_function,
    )
    lambda_max = max(credibility_mat.apply(max))
    lambda_ = lambda_max - (alpha + beta * lambda_max)

    lambda_strengths = Series(
        {
            i: sum(
                (
                    credibility_mat.loc[i, j] > lambda_
                    and credibility_mat.loc[i, j] > credibility_mat.loc[j, i]
                )
                for j in performance_table.index
            )
            for i in performance_table.index
        }
    )

    lambda_weakness = Series(
        {
            j: sum(
                (
                    credibility_mat.loc[i, j] > lambda_
                    and credibility_mat.loc[i, j] > credibility_mat.loc[j, i]
                )
                for i in performance_table.index
            )
            for j in performance_table.index
        }
    )

    return lambda_strengths - lambda_weakness


def distillation(
    performance_table: PerformanceTable,
    criteria_weights: Dict[str, NumericValue],
    scales: Dict[str, QuantitativeScale],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    veto_thresholds: Dict[str, NumericValue],
    concordance_function=None,
    discordance_function=None,
    credibility_function=None,
    alpha: NumericValue = 0.30,
    beta: NumericValue = -0.15,
    ascending: bool = False,
) -> List[List[Any]]:
    """Compute the descending distillation between two actions a and b.

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param preference_thresholds:
    :param indifference_thresholds:
    :param veto_thresholds:
    :param concordance_function: function used to calculate concordance matrix
    :param discordance_function: function used to calculate discordance matrix
    :param credibility_function: function used to calculate credibility matrix
    :param alpha:  preset up values of distillation coefficients
    :param beta: preset up values of distillation coefficients
    :param ascending: if ``True`` distillation is performed in ascension
    :return: list distillation"""
    comp = min if ascending else max
    concordance_function = (
        concordance if concordance_function is None else concordance_function
    )

    discordance_function = (
        discordance if discordance_function is None else discordance_function
    )

    credibility_function = (
        credibility if credibility_function is None else credibility_function
    )

    rest = performance_table.index.tolist()
    distillate = []
    while len(rest) > 0:
        updated_performance_table = performance_table.loc[rest]
        qualifications = qualification(
            updated_performance_table,
            criteria_weights,
            scales,
            preference_thresholds,
            indifference_thresholds,
            veto_thresholds,
            concordance_function,
            discordance_function,
            credibility_function,
            alpha,
            beta,
        )

        maxes = qualifications[qualifications == comp(qualifications)]
        if len(maxes) > 1:
            updated_performance_table = updated_performance_table.loc[
                maxes.index
            ]
            qualifications = qualification(
                updated_performance_table,
                criteria_weights,
                scales,
                preference_thresholds,
                indifference_thresholds,
                veto_thresholds,
                concordance_function,
                discordance_function,
                credibility_function,
                alpha,
                beta,
            )
            maxes = qualifications[qualifications == comp(qualifications)]
        distillate.append(maxes.index.tolist())
        for i in maxes.index.tolist():
            rest.remove(i)
    return distillate[::-1] if ascending else distillate


def electre_iii(
    performance_table: PerformanceTable,
    criteria_weights: Dict[str, NumericValue],
    scales: Dict[str, QuantitativeScale],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    veto_thresholds: Dict[str, NumericValue],
    concordance_function=None,
    discordance_function=None,
    credibility_function=None,
    alpha: NumericValue = 0.30,
    beta: NumericValue = -0.15,
) -> PerformanceTable:
    """Compute the complete electreIII algorithm

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param preference_thresholds:
    :param indifference_thresholds:
    :param veto_thresholds:
    :param alpha:  preset up values of distillation coefficients
    :param beta: preset up values of distillation coefficients
    :param concordance_function: function used to calculate concordance matrix
    :param discordance_function: function used to calculate discordance matrix
    :param credibility_function: function used to calculate credibility matrix
    :return: final ranking of Electre III"""
    concordance_function = (
        concordance if concordance_function is None else concordance_function
    )

    discordance_function = (
        discordance if discordance_function is None else discordance_function
    )

    credibility_function = (
        credibility if credibility_function is None else credibility_function
    )

    ascending_distillate = distillation(
        performance_table,
        criteria_weights,
        scales,
        preference_thresholds,
        indifference_thresholds,
        veto_thresholds,
        concordance_function,
        discordance_function,
        credibility_function,
        alpha,
        beta,
        ascending=True,
    )
    descending_distillate = distillation(
        performance_table,
        criteria_weights,
        scales,
        preference_thresholds,
        indifference_thresholds,
        veto_thresholds,
        concordance_function,
        discordance_function,
        credibility_function,
        alpha,
        beta,
    )
    final_matrix = final_ranking(
        categories_to_outranking(ascending_distillate),
        categories_to_outranking(descending_distillate),
    )
    return final_matrix
