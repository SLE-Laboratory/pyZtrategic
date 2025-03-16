from pyztrategic.zipper import Zipper, obj
import pyztrategic.strategy as st

from repmin_data import *
from repmin_ag import gm


def repminZtrategic(t: Zipper[Tree]) -> Tree:
    def aux(exp: Tree, z: Zipper[Tree]) -> Tree:
        match(exp):
            case Leaf():
                return Leaf(gm(z))
            case _:
                raise st.StrategicError

    return st.full_tdTP(lambda x: st.adhocTPZ(st.idTP, aux, x), t).node()


def minimumValue(t: Zipper[Tree]) -> int:
    def nodeVal(exp: Tree) -> list[int]:
        match(exp):
            case Leaf(x):
                return [x]
            case _:
                raise st.StrategicError

    return min(st.full_tdTU(lambda x: st.adhocTU(st.failTU, nodeVal, x), t))


def replaceTree(i: int, t: Tree) -> Tree:
    def replaceTP(i: int, exp: Tree) -> Tree:
        match(exp):
            case Leaf():
                return Leaf(i)
            case _:
                raise st.StrategicError

    return st.full_tdTP(lambda x: st.adhocTP(st.idTP, lambda y: replaceTP(i, y), x), t).node()


def repmin(t: Tree) -> Tree:
    return replaceTree(minimumValue(t), t)
