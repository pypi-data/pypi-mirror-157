"""This module implements the promethee 2 algorithm.

Implementation and naming conventions are taken from
:cite:p:`vincke1998promethee1`.
"""


from typing import Dict

from pandas import Series

from mcda.core.aliases import (  # Cannot do from ..core.aliases
    NumericValue,
    PerformanceTable,
)
from mcda.outranking.promethee_common import (
    PreferenceFunction,
    outranking_flow_calculation,
    scale_performance_table,
)

from ..core.scales import QuantitativeScale


def total_order(
    performance_table: PerformanceTable,
    preference_functions: Dict[str, PreferenceFunction],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    standard_deviations: Dict[str, NumericValue],
    criteria_weights: Dict[str, NumericValue],
) -> Series:
    """Compute the total order list.

    :param performance_table:
    :param preference_functions: preference function for each criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :param criteria_weights: weight of each criterion
    :return: the outranking total order of the performance table"""

    pos_flow, neg_flow = outranking_flow_calculation(
        performance_table,
        preference_functions,
        preference_thresholds,
        indifference_thresholds,
        standard_deviations,
        criteria_weights,
    )

    return pos_flow - neg_flow


def promethee2(
    performance_table: PerformanceTable,
    preference_functions: Dict[str, PreferenceFunction],
    scales: Dict[str, QuantitativeScale],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    standard_deviations: Dict[str, NumericValue],
    criteria_weights: Dict[str, NumericValue],
) -> Series:
    """Compute the outranking algorithm promethee2 with the total order.

    :param performance_table:
    :param preference_functions: preference function for each criterion
    :param scales: scale for each criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :param criteria_weights: weight of each criterion
    :return: the outranking total order of the performance table"""

    scaled_performance_table = scale_performance_table(
        performance_table, scales
    )

    return total_order(
        scaled_performance_table,
        preference_functions,
        preference_thresholds,
        indifference_thresholds,
        standard_deviations,
        criteria_weights,
    )
