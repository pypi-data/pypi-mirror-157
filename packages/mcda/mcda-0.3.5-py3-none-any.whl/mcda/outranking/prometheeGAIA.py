""" This module implements the graphic display of the GAIA plane

Implementations naming conventions are taken from
:cite:p:`figueira2005mcda`
"""

from typing import Dict

import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

from mcda.core.aliases import (  # Cannot do from ..core.aliases
    NumericValue,
    PerformanceTable,
)
from mcda.outranking.promethee_common import (
    PreferenceFunction,
    preference_degree_calculation,
)


def unicriterion_net_flow(
    alternative: str,
    criterion: str,
    performance_table: PerformanceTable,
    preference_functions: Dict[str, PreferenceFunction],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    standard_deviations: Dict[str, NumericValue],
) -> NumericValue:
    """Computes the single criterion net flow of an alternative
    considering only a criterion.

    :param alternative: label of the alternative
    :param criterion: label of the criterion
    :param performance_table:
    :param preference_functions: preference function for each criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :return: net flow
    """
    net_flow = 0.0
    for i in performance_table.index.tolist():
        net_flow += preference_degree_calculation(
            preference_functions[criterion],
            preference_thresholds[criterion],
            indifference_thresholds[criterion],
            standard_deviations[criterion],
            performance_table.loc[alternative, criterion],
            performance_table.loc[i, criterion],
        ) - preference_degree_calculation(
            preference_functions[criterion],
            preference_thresholds[criterion],
            indifference_thresholds[criterion],
            standard_deviations[criterion],
            performance_table.loc[i, criterion],
            performance_table.loc[alternative, criterion],
        )
    return net_flow


def unicriterion_flow_matrix(
    performance_table: PerformanceTable,
    preference_functions: Dict[str, PreferenceFunction],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    standard_deviations: Dict[str, NumericValue],
) -> PerformanceTable:
    """Computes the whole matrix M of single criterion net flows.

    :param performance_table:
    :param preference_functions: preference function for each criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :return: net flow matrix
    """
    unicrit_flows = PerformanceTable(
        0, index=performance_table.index, columns=performance_table.columns
    )
    for act in performance_table.index.tolist():
        for cri in performance_table.columns.tolist():
            unicrit_flows.loc[act, cri] = unicriterion_net_flow(
                act,
                cri,
                performance_table,
                preference_functions,
                preference_thresholds,
                indifference_thresholds,
                standard_deviations,
            )
    return unicrit_flows


def gaia(
    performance_table: PerformanceTable,
    preference_functions: Dict[str, PreferenceFunction],
    preference_thresholds: Dict[str, NumericValue],
    indifference_thresholds: Dict[str, NumericValue],
    standard_deviations: Dict[str, NumericValue],
    criteria_weights: Dict[str, NumericValue],
):
    """Plots the GAIA plane and displays in the top-left corner
    the ratio of saved information by the PCA, delta.

    :param performance_table: performance table
    :param preference_functions: preference function for each criterion
    :param preference_thresholds: preference threshold for each criterion
    :param indifference_thresholds: indifference threshold for each criterion
    :param standard_deviations: standard deviation for each criterion
    :param criteria_weights: weight of each criterion
    """
    net_flows = unicriterion_flow_matrix(
        performance_table,
        preference_functions,
        preference_thresholds,
        indifference_thresholds,
        standard_deviations,
    )

    pca = PCA(n_components=2)
    pca.fit(net_flows)
    delta = pca.explained_variance_ratio_[0] + pca.explained_variance_ratio_[1]
    alternative_vectors = pca.transform(net_flows)
    criterions = PerformanceTable(
        [
            [1 if i == j else 0 for j in range(len(performance_table.columns))]
            for i in range(len(performance_table.columns))
        ],
        index=performance_table.columns,
        columns=performance_table.columns,
    )
    criterion_vectors = pca.transform(criterions)
    S = sum(criteria_weights.values())
    pi = [0, 0]
    for i, criterion in enumerate(performance_table.columns.tolist()):
        pi[0] += criterion_vectors[i][0] * criteria_weights[criterion] / S
        pi[1] += criterion_vectors[i][1] * criteria_weights[criterion] / S

    plt.figure(figsize=[10, 10])

    for i, alternative in enumerate(performance_table.index.tolist()):
        plt.scatter(
            alternative_vectors[i][0],
            alternative_vectors[i][1],
            s=100,
            label=alternative,
        )
    for i, criterion in enumerate(performance_table.columns.tolist()):
        plt.text(
            criterion_vectors[i][0],
            criterion_vectors[i][1],
            criterion,
            ha="center",
        )
        plt.arrow(0, 0, criterion_vectors[i][0], criterion_vectors[i][1])

    plt.arrow(0, 0, pi[0], pi[1])
    plt.scatter(pi[0], pi[1], s=150, marker="*", label=r"$\pi$")

    ax = plt.gca()
    xmin, _ = ax.get_xlim()
    _, ymax = ax.get_ylim()

    plt.text(
        xmin, ymax, r"$\delta$ = %.3f" % delta, bbox=dict(boxstyle="round")
    )

    plt.legend()
    plt.plot()
    plt.show()
