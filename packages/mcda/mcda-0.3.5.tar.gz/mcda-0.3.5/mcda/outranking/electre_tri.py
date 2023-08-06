"""This module implements the Electre-TRI B algorithm.

Implementation and naming conventions are taken from
:cite:p:`vincke1998electreTRI`.
"""

from collections import defaultdict
from typing import Dict, List, Tuple

from mcda.core.relations import Relation, RelationType

from ..core.aliases import NumericValue, PerformanceTable
from ..core.scales import QuantitativeScale
from .electre3 import concordance, credibility, discordance


def outrank(
    credibility_mat: PerformanceTable,
    alternative: int,
    category_profile: int,
    lambda_: NumericValue,
) -> Relation:
    """Compute relation between two actions based on credibility matrix.

    :param credibility_mat:
        credibility matrix of concatenated performance table / category
        profiles
    :param alternative:
    :param category_profile:
    :param lambda_: cut level
    :return: relationship between both actions

    .. todo::
        * change name?
    """
    aSb = credibility_mat.loc[alternative, category_profile]
    bSa = credibility_mat.loc[category_profile, alternative]
    if aSb >= lambda_ and bSa >= lambda_:
        return alternative, category_profile, RelationType.INDIFFERENCE
    elif aSb >= lambda_ > bSa:
        return alternative, category_profile, RelationType.PREFERENCE
    elif aSb < lambda_ <= bSa:
        return category_profile, alternative, RelationType.PREFERENCE
    return alternative, category_profile, RelationType.INCOMPARABLE


def exploitation_procedure(
    performance_table: PerformanceTable,
    category_profiles: PerformanceTable,
    criteria_weights: Dict[str, NumericValue],
    scales: Dict[str, QuantitativeScale],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    veto_thresholds: Dict[str, NumericValue],
    lambda_: NumericValue = 0.75,
    concordance_function=None,
    discordance_function=None,
    credibility_function=None,
    pessimistic: bool = False,
) -> Dict[int, List[str]]:
    """Compute the exploitation procedure (either optimistically or
    pessimistically).

    In the output ranking, class -1 means incomparable class

    :param performance_table:
    :param category_profiles: profil
    :param criteria_weights:
    :param scales: Scaling List
    :param preference_thresholds:
    :param indifference_thresholds:
    :param veto_thresholds:
    :param lambda_: cut level
    :param concordance_function: function used to calculate concordance matrix
    :param discordance_function: function used to calculate discordance matrix
    :param credibility_function: function used to calculate credibility matrix
    :param pessimistic: if ``True`` performs procedure pessimistically
    :return: categories
    """
    concordance_function = (
        concordance if concordance_function is None else concordance_function
    )

    discordance_function = (
        discordance if discordance_function is None else discordance_function
    )

    credibility_function = (
        credibility if credibility_function is None else credibility_function
    )

    # Concatenate performance table and category profile
    # Replace indexes so no chance of same id category profile alternative
    altered_performance_table = PerformanceTable(
        performance_table.values.tolist() + category_profiles.values.tolist()
    )
    nb_actions = len(performance_table.index)
    nb_classes = len(category_profiles.index)

    credibility_mat = credibility_function(
        altered_performance_table,
        criteria_weights,
        scales,
        preference_thresholds,
        indifference_thresholds,
        veto_thresholds,
        concordance_function,
        discordance_function,
    )

    classes = defaultdict(list)
    rest = [*range(nb_actions)]
    for i in (
        range(nb_classes - 1, -1, -1) if pessimistic else range(nb_classes)
    ):
        class_ = []
        for action in rest:
            a, b, relation = outrank(
                credibility_mat,
                action,
                i + nb_actions,
                lambda_,
            )
            if relation == RelationType.PREFERENCE:
                if a == action and pessimistic:
                    class_.append(action)
                    classes[i + 1].append(performance_table.iloc[action].name)
                elif a != action and not pessimistic:
                    class_.append(action)
                    classes[i].append(performance_table.iloc[action].name)
        for a in class_:
            rest.remove(a)
    if len(rest) > 0:
        for action in rest:
            a, b, relation = outrank(
                credibility_mat,
                nb_actions if pessimistic else action,
                action if pessimistic else nb_actions + nb_classes - 1,
                lambda_,
            )
            if relation == RelationType.INCOMPARABLE:
                classes[-1].append(performance_table.iloc[action].name)
            elif b == action and pessimistic:
                classes[0].append(performance_table.iloc[action].name)
            elif a == action and not pessimistic:
                classes[nb_classes].append(performance_table.iloc[action].name)
            else:
                classes[-1].append(
                    performance_table.iloc[action].name
                )  # pragma: nocover
    return classes


def electre_tri(
    performance_table: PerformanceTable,
    category_profiles: PerformanceTable,
    criteria_weights: Dict[str, NumericValue],
    scales: Dict[str, QuantitativeScale],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    veto_thresholds: Dict[str, NumericValue],
    lambda_: NumericValue,
    concordance_function=None,
    discordance_function=None,
    credibility_function=None,
) -> Tuple[Dict[int, List[str]], Dict[int, List[str]]]:
    """Compute the electre_tri algorithm.

    In the output ranking, class -1 means incomparable class

    :param performance_table:
    :param category_profiles:
    :param criteria_weights:
    :param scales:
    :param preference_thresholds:
    :param indifference_thresholds:
    :param veto_thresholds:
    :param lambda_: cut level
    :param concordance_function: function used to calculate concordance matrix
    :param discordance_function: function used to calculate discordance matrix
    :param credibility_function: function used to calculate credibility matrix
    :return: optimistic ranking, pessimistic ranking"""
    concordance_function = (
        concordance if concordance_function is None else concordance_function
    )

    discordance_function = (
        discordance if discordance_function is None else discordance_function
    )

    credibility_function = (
        credibility if credibility_function is None else credibility_function
    )
    optimistic = exploitation_procedure(
        performance_table,
        category_profiles,
        criteria_weights,
        scales,
        preference_thresholds,
        indifference_thresholds,
        veto_thresholds,
        lambda_,
        concordance_function,
        discordance_function,
        credibility_function,
    )
    pessimistic = exploitation_procedure(
        performance_table,
        category_profiles,
        criteria_weights,
        scales,
        preference_thresholds,
        indifference_thresholds,
        veto_thresholds,
        lambda_,
        concordance_function,
        discordance_function,
        credibility_function,
        pessimistic=True,
    )
    return optimistic, pessimistic
