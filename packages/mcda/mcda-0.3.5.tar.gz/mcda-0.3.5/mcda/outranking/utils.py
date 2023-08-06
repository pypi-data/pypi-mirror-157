"""This module implements utils function for outranking algorithms.

Implementation and naming conventions are taken from
:cite:p:`vincke1998electre`.
"""
from itertools import product
from typing import Dict, List

from deprecated.sphinx import deprecated
from scipy.sparse.csgraph import connected_components

import mcda.core.relations as crelations
from mcda.core.aliases import PerformanceTable


def dijskstra(graph: Dict[str, List[str]], x: str, y: str) -> List[str]:
    """Return the longest path from an action to another

    :param graph: graph
    :param x: initial action
    :param y: final action
    :return: the longest path"""
    verteces = [x]
    distances = {x: 0}
    tracks: Dict[str, List[str]] = {x: []}
    while verteces:
        point = verteces.pop(0)  # or we can use deque
        for voisin in graph[point]:
            new_track = tracks[point] + [voisin]
            verteces.append(voisin)
            new_dist = distances[point] + 1
            if voisin not in distances or new_dist > distances[voisin]:
                distances[voisin] = new_dist
                tracks[voisin] = new_track
    return tracks[y]


def cycle_reduction_matrix(matrix: PerformanceTable) -> PerformanceTable:
    """Remove cycles from matrix

    :param matrix: outranking matrix
    :return: outranking matrix with no cycle
    """
    n_components, labels = connected_components(
        matrix.to_numpy(), connection="strong"
    )
    components = range(n_components)
    new_matrix = PerformanceTable(
        0, index=matrix.index, columns=matrix.columns
    )
    for component_a, component_b in product(components, components):
        if component_a != component_b:
            new_matrix.loc[labels == component_a, labels == component_b] = (
                matrix.loc[labels == component_a, labels == component_b]
                .to_numpy()
                .any()
            )
    return new_matrix.astype(int)


@deprecated(
    reason="This function has been moved to "
    ":func:`mcda.core.relations.relations_to_matrix`",
    version="0.3.4",
)
def relations_to_matrix(*args, **kwargs):  # pragma: nocover
    return crelations.relations_to_matrix(*args, **kwargs)


@deprecated(
    reason="This function has been moved to "
    ":func:`mcda.core.relations.matrix_to_relations`",
    version="0.3.4",
)
def matrix_to_relations(*args, **kwargs):  # pragma: nocover
    return crelations.matrix_to_relations(*args, **kwargs)
