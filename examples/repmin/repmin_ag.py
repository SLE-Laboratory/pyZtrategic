from pyztrategic.zipper import Zipper, obj
import pyztrategic.strategy as st

from repmin_data import *

# Repmin Embedded AG

def gm(z: Zipper[Tree]) -> int:
    match constructor(z):
        case Constructor.CRoot:
            return lm(z.z_dollar(1))
        case Constructor.CLeaf:
            return gm(z.up())
        case Constructor.CFork:
            return gm(z.up())


def lm(z: Zipper[Tree]) -> int:
    match constructor(z):
        case Constructor.CLeaf:
            return lexeme(z)
        case Constructor.CFork:
            return min(lm(z.z_dollar(1)), lm(z.z_dollar(2)))
        case _:
            raise st.StrategicError


def nt(z: Zipper[Tree]) -> Tree:
    match constructor(z):
        case Constructor.CRoot:
            return Root(nt(z.z_dollar(1)))
        case Constructor.CLeaf:
            return Leaf(gm(z))
        case Constructor.CFork:
            return Fork(nt(z.z_dollar(1)), nt(z.z_dollar(2)))
        

def repminAG(t: Tree) -> Tree:
    return nt(obj(t))