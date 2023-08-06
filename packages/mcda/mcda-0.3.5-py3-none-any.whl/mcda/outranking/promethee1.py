"""This module implements the Promethee I algorithm.

Implementation and naming conventions are taken from
:cite:p:`vincke1998promethee1`.
"""

from typing import Dict, List

from mcda.core.aliases import (  # Cannot do from ..core.aliases
    NumericValue,
    PerformanceTable,
)
from mcda.core.relations import Relation, RelationType
from mcda.outranking.promethee_common import (
    PreferenceFunction,
    outranking_flow_calculation,
    scale_performance_table,
)

from ..core.scales import QuantitativeScale


def partial_order(
    performance_table: PerformanceTable,
    preference_functions: Dict[str, PreferenceFunction],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    standard_deviations: Dict[str, NumericValue],
    criteria_weights: Dict[str, NumericValue],
) -> List[Relation]:
    """Compute the partial order list.

    :param performance_table:
    :param preference_functions: preference function for each criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :param criteria_weights: weight of each criterion
    :return: preference relations between each pair of alternatives
    """

    pos_flow, neg_flow = outranking_flow_calculation(
        performance_table,
        preference_functions,
        preference_thresholds,
        indifference_thresholds,
        standard_deviations,
        criteria_weights,
    )

    relations: List[Relation] = list()

    for ii, i in enumerate(performance_table.index.tolist()):
        for j in performance_table.index.tolist()[ii + 1 :]:
            relations.append(
                flow_intersection(
                    i,
                    j,
                    pos_flow[i],
                    pos_flow[j],
                    neg_flow[i],
                    neg_flow[j],
                )
            )

    return relations


def flow_intersection(
    a: str,
    b: str,
    pos_flow_a: NumericValue,
    pos_flow_b: NumericValue,
    neg_flow_a: NumericValue,
    neg_flow_b: NumericValue,
) -> Relation:
    """Compute the positive and negative flow intersection.

    :param a: first alternative
    :param b: second alternative
    :param pos_flow_a: the positive flow of first alternative
    :param pos_flow_b: the positive flow of second alternative
    :param neg_flow_a: the negative flow of first alternative
    :param neg_flow_b: the negative flow of second alternative
    :return: the comparison of the two alternatives in a relation"""

    if pos_flow_a == pos_flow_b and neg_flow_a == neg_flow_b:
        return a, b, RelationType.INDIFFERENCE
    if pos_flow_a >= pos_flow_b and neg_flow_a <= neg_flow_b:
        return a, b, RelationType.PREFERENCE
    if pos_flow_b >= pos_flow_a and neg_flow_b <= neg_flow_a:
        return b, a, RelationType.PREFERENCE
    return a, b, RelationType.INCOMPARABLE


def promethee1(
    performance_table: PerformanceTable,
    preference_functions: Dict[str, PreferenceFunction],
    scales: Dict[str, QuantitativeScale],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    standard_deviations: Dict[str, NumericValue],
    criteria_weights: Dict[str, NumericValue],
) -> List[Relation]:
    """Compute the outranking algorithm promethee1 with the partial order.

    :param performance_table:
    :param preference_functions: preference function for each criterion
    :param scales: scale for each criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :param criteria_weights: weight of each criterion
    :return: the outranking partial order of the performance table"""

    scaled_performance_table = scale_performance_table(
        performance_table, scales
    )
    return partial_order(
        scaled_performance_table,
        preference_functions,
        preference_thresholds,
        indifference_thresholds,
        standard_deviations,
        criteria_weights,
    )
