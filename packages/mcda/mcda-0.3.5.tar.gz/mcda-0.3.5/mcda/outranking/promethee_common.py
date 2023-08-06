"""This module implements the common promethee methods.

Implementation and naming conventions are taken from
:cite:p:`vincke1998promethee1`.
"""

from enum import Enum
from math import exp
from typing import Dict, Tuple, cast

from pandas import Series

from mcda.core.aliases import (  # Cannot do from ..core.aliases
    NumericFunction,
    NumericValue,
    PerformanceTable,
)
from mcda.core.performance_table import transform

from ..core.scales import PreferenceDirection, QuantitativeScale, Scale


class PreferenceFunction(Enum):
    """Enumeration of the preference functions."""

    USUAL = 1
    U_SHAPE = 2
    V_SHAPE = 3
    LEVEL = 4
    LINEAR = 5
    GAUSSIAN = 6


def usual_function() -> NumericFunction:
    """Implements the usual function.

    :return: the result of the lambda variable on the usual function"""
    return lambda x: 1 if x > 0 else 0


def u_shape_function(q: NumericValue) -> NumericFunction:
    """Implements the u-shape function.

    :param q: the indifference threshold
    :return: the result of the lambda variable on the u-shape function"""
    return lambda x: 1 if x > q else 0


def v_shape_function(p: NumericValue) -> NumericFunction:
    """Implements the v-shape function.

    :param p: the preference threshold
    :return: the result of the lambda variable on the v-shape function"""
    return lambda x: 1 if x > p else abs(x) / p


def level_function(p: NumericValue, q: NumericValue) -> NumericFunction:
    """Implements the level function.

    :param p: the preference threshold
    :param q: the indifference threshold
    :return: the result of the lambda variable on the level function"""
    return lambda x: 1 if x > p else 1 / 2 if q < x else 0


def linear_function(p: NumericValue, q: NumericValue) -> NumericFunction:
    """Implements the linear function.

    :param p: the preference threshold
    :param q: the indifference threshold
    :return: the result of the lambda variable on the linear function"""
    return lambda x: 1 if x > p else (abs(x) - q) / (p - q) if q < x else 0


def gaussian_function(s: NumericValue) -> NumericFunction:
    """Implements the gaussian function.

    :param s: the standard deviation
    :return: the result of the lambda variable on the gaussian function"""
    return lambda x: 1 - exp(-(x ** 2) / (2 * s ** 2))


def preference_degree_calculation(
    pref_func: PreferenceFunction,
    p: NumericValue,
    q: NumericValue,
    s: NumericValue,
    ga: NumericValue,
    gb: NumericValue,
) -> NumericValue:
    """Compute the preference degree for the criterion of two alternatives.

    :param pref_func: the preference function for the criterion
    :param p: the preference threshold for the criterion
    :param q: the indifference threshold for the criterion
    :param s: the standard deviation for the criterion
    :param ga: value of the criterion for the first alternative
    :param gb: value of the criterion for the second alternative
    :return: the preference degree of the alternatives with the `pref_func`"""

    if ga - gb <= 0:
        return 0
    if pref_func is PreferenceFunction.USUAL:
        my_func = usual_function()
    elif pref_func is PreferenceFunction.U_SHAPE:
        my_func = u_shape_function(q)
    elif pref_func is PreferenceFunction.V_SHAPE:
        my_func = v_shape_function(p)
    elif pref_func is PreferenceFunction.LEVEL:
        if q > p:
            raise ValueError(
                "incorrect threshold : q "
                + str(q)
                + " greater than p "
                + str(p)
            )
        my_func = level_function(p, q)
    elif pref_func is PreferenceFunction.LINEAR:
        if q > p:
            raise ValueError(
                "incorrect threshold : q "
                + str(q)
                + " greater than p "
                + str(p)
            )
        my_func = linear_function(p, q)
    elif pref_func is PreferenceFunction.GAUSSIAN:
        my_func = gaussian_function(s)
    else:
        raise ValueError(
            "pref_func "
            + str(pref_func)
            + " is not known. \n See PreferenceFunction Enum"
        )
    pref_degree = my_func(ga - gb)
    return pref_degree


def multicriteria_preference_degree_calculation(
    alternative_values1: Series,
    alternative_values2: Series,
    preference_functions: Dict[str, PreferenceFunction],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    standard_deviations: Dict[str, NumericValue],
    criteria_weights: Dict[str, NumericValue],
) -> NumericValue:
    """Compute the multicriteria preference degree of two alternatives.

    :param alternative_values1: criteria values for one alternative
    :param alternative_values2: criteria values for the second alternative
    :param preference_functions: preference function for each criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :param criteria_weights: weight of each criterion
    :return: the multicriteria preference degree for the alternatives"""

    multi_pref_degree = 0.0
    for i in alternative_values1.index.tolist():
        multi_pref_degree += criteria_weights[
            i
        ] * preference_degree_calculation(
            preference_functions[i],
            preference_thresholds[i],
            indifference_thresholds[i],
            standard_deviations[i],
            alternative_values1[i],
            alternative_values2[i],
        )
    multi_pref_degree /= sum(criteria_weights.values())
    return multi_pref_degree


def positive_preference_flow_calculation(
    alternative_values: Series,
    other_alternatives_values: PerformanceTable,
    preference_functions: Dict[str, PreferenceFunction],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    standard_deviations: Dict[str, NumericValue],
    criteria_weights: Dict[str, NumericValue],
) -> NumericValue:
    """Compute the positive preference flow of an alternative.

    :param alternative_values: criteria values for the alternative
    :param other_alternatives_values:
        criteria values for the other alternatives
    :param preference_functions: preference function for each criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :param criteria_weights: weight of each criterion
    :return: the positive preference flow of the alternative"""

    positive_pref_flow = 0.0
    for j in other_alternatives_values.index.tolist():
        positive_pref_flow += multicriteria_preference_degree_calculation(
            alternative_values,
            other_alternatives_values.loc[j],
            preference_functions,
            preference_thresholds,
            indifference_thresholds,
            standard_deviations,
            criteria_weights,
        )
    return positive_pref_flow


def negative_preference_flow_calculation(
    alternative_values: Series,
    other_alternatives_values: PerformanceTable,
    preference_functions: Dict[str, PreferenceFunction],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    standard_deviations: Dict[str, NumericValue],
    criteria_weights: Dict[str, NumericValue],
) -> NumericValue:
    """Compute the negative preference flow of an alternative.

    :param alternative_values: criteria values for one alternative
    :param other_alternatives_values:
        criteria values for the other alternatives
    :param preference_functions: preference function for each criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :param criteria_weights: weight of each criterion
    :return: the negative preference flow calculation for the alternative"""

    negative_pref_flow = 0.0
    for j in other_alternatives_values.index.tolist():
        negative_pref_flow += multicriteria_preference_degree_calculation(
            other_alternatives_values.loc[j],
            alternative_values,
            preference_functions,
            preference_thresholds,
            indifference_thresholds,
            standard_deviations,
            criteria_weights,
        )
    return negative_pref_flow


def outranking_flow_calculation(
    performance_table: PerformanceTable,
    preference_functions: Dict[str, PreferenceFunction],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    standard_deviations: Dict[str, NumericValue],
    criteria_weights: Dict[str, NumericValue],
) -> Tuple[Series, Series]:
    """Compute the outranking flow.

    :param performance_table:
    :param preference_functions: preference function for each criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :param criteria_weights: weight of each criterion
    :return: positive and negative outranking flows"""

    pos_pref_flow = performance_table.apply(
        lambda x: positive_preference_flow_calculation(
            x,
            performance_table.drop(x.name),
            preference_functions,
            preference_thresholds,
            indifference_thresholds,
            standard_deviations,
            criteria_weights,
        ),
        axis=1,
    )
    neg_pref_flow = performance_table.apply(
        lambda x: negative_preference_flow_calculation(
            x,
            performance_table.drop(x.name),
            preference_functions,
            preference_thresholds,
            indifference_thresholds,
            standard_deviations,
            criteria_weights,
        ),
        axis=1,
    )
    return cast(Series, pos_pref_flow), cast(Series, neg_pref_flow)


def scale_performance_table(
    performance_table: PerformanceTable, scales: Dict[str, QuantitativeScale]
) -> PerformanceTable:
    """Rearrange the performance table if there are criteria to minimize

    :param performance_table:
    :param scales: the scale for each criterion
    :return: the scaled performance table
    """

    return transform(
        performance_table,
        cast(Dict[str, Scale], scales),
        {
            i: cast(
                Scale,
                QuantitativeScale(v.dmin, v.dmax, PreferenceDirection.MAX),
            )
            for i, v in scales.items()
        },
    )
