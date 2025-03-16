from pyztrategic.zipper import Zipper
import pyztrategic.strategy as st

from dataclasses import dataclass
from enum import StrEnum, auto


type Tree = Root | Fork | Leaf

@dataclass
class Root:
    tree: Tree

@dataclass
class Fork:
    left: Tree
    right: Tree

@dataclass
class Leaf:
    leaf: int


class Constructor(StrEnum):
    CRoot = auto()
    CFork = auto()
    CLeaf = auto()


def constructor(ag: Zipper[Tree]) -> Constructor:
    match ag.node():
        case Root():
            return Constructor.CRoot
        case Fork():
            return Constructor.CFork
        case Leaf():
            return Constructor.CLeaf


def lexeme(ag: Zipper[Tree]) -> int:
    match ag.node():
        case Leaf(x):
            return x
        case _:
            raise st.StrategicError


def sumTree(t: Tree) -> int:
    match(t):
        case Root(r):
            return sumTree(r)
        case Fork(l,r):
            return sumTree(l) + sumTree(r)
        case Leaf(l):
            return l