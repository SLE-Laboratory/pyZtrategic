from hypothesis import given
from hypothesis.strategies import integers, composite, one_of

from pyztrategic import strategy as st
from pyztrategic.zipper import Zipper, obj
from repmin_data import Tree, Root, Leaf, Fork
from repmin_ag import gm, lm, repminAG
from repmin_generator import genTreeRoot



@given(genTreeRoot())
def testPropLocMin(i):
    assert all(st.full_tdTU(lambda x: st.adhocTUZ(st.failTU, validateLocMin, x), obj(i)))



def validateLocMin(t: Tree, z: Zipper[Tree]) -> list[bool]:
    match(t):
        case Leaf(l):
            return [l >= gm(z)]
        case Fork():
            return [lm(z) >= gm(z)]
        case Root():
            return []


@given(genTreeRoot())
def testPropGlobMin(i):
    assert all(st.full_tdTU(lambda x: st.adhocTUZ(st.failTU, globminIsSmaller, x), obj(i)))


def globminIsSmaller(t: Tree, z: Zipper[Tree]) -> list[bool]:
    match(t):
        case Leaf(l):
            return [gm(z) <= l]
        case _:
            return []


@given(genTreeRoot())
def testResultingInOriginal(t):
    assert all(st.full_tdTU(lambda x: st.adhocTUZ(st.failTU, intInOriginal, x), repminAG(t)))


def intInOriginal(i: int) -> bool:
    def equal(n: int) -> list[bool]:
        return [i == n]
    return any(st.full_tdTU(lambda x: st.adhocTU(st.failTU, equal, x), obj(i)))


@given(genTreeRoot())
def testNumberLeaves(t):
    assert(countLeaves(t) == countLeaves(repminAG(t)))


def countLeaves(t: Tree) -> int:
    match(t):
        case Root(r):
            return countLeaves(r)
        case Fork(l, r):
            return countLeaves(l) + countLeaves(r)
        case Leaf():
            return 1

# @given(genTreeRoot())
# def testIsomorphic(t):
#     assert isIsomorphic(t, repminAG(t))

# def isIsomorphic(t1, t2):
#     return t1.match(
#         root=lambda l1: t2.match(
#             root=lambda l2: isIsomorphic(l1, l2),
#             fork=lambda l2, r2: False,
#             leaf=lambda l2: False
#         ),
#         fork=lambda l1, r1: t2.match(
#             root=lambda l2: False,
#             fork=lambda l2, r2: isIsomorphic(l1, l2) and isIsomorphic(r1, r2),
#             leaf=lambda l2: False
#         ),
#         leaf=lambda l1: t2.match(
#             root=lambda l2: False,
#             fork=lambda l2, r2: False,
#             leaf=lambda l2: True
#         )
#     )


@given(genTreeRoot())
def testGlobminPreserved(t):
    assert gm(obj(t)) == gm(obj(repminAG(t)))
