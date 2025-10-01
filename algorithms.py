from typing import List

from edge import Edge
from graph import Graph

def _all_eq(ints:List[int]) -> bool:
    return all(x == ints[0] for x in ints)

def mst_prims(G:Graph):
    """
    Only for undirected graphs.
    """

    union = Union(len(G.V))
    edges = sorted(G.E, key=lambda e: e.weight, reverse=True)
    mst: List[Edge] = []

    for _ in range(len(G.V) - 1):

        smallest_edge = edges.pop()
        u = smallest_edge.a
        v = smallest_edge.b

        while union.get_representative(u.id) == union.get_representative(v.id):
            smallest_edge = edges.pop()
            u = smallest_edge.a
            v = smallest_edge.b

        union.union(u.id, v.id)
        mst.append(smallest_edge)

    return mst




# ------------------------------------
# --------- Data structures ----------
# ------------------------------------

class Union:
    def __init__(self, n:int) -> None:
        self._representatives: List[int] = list(range(n))

    def union(self, u:int, v:int) -> None:
        if u == v:
            return
        
        rep_u = self._representatives[u]
        rep_v = self._representatives[v]

        (new_rep, to_replace) = (rep_u, rep_v) if rep_u < rep_v else (rep_v, rep_u)

        for i in range(len(self._representatives)):
            if self._representatives[i] == to_replace:
                self._representatives[i] = new_rep

    def get_representative(self, idx:int) -> int:
        return self._representatives[idx]




