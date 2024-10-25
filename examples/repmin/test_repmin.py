from hypothesis import given
from hypothesis.strategies import integers, composite, one_of

from pyztrategic import strategy as st
from pyztrategic import zipper as zp
from repmin import Tree, locmin, globmin, repminAG


@composite
def genLeaf(draw):
    i = draw(integers(min_value=1))
    return Tree.LEAF(i)



@composite
def genFork(draw):
    return Tree.FORK(draw(genTree1()), draw(genTree1()))

@composite
def genTree1(draw):
    return draw(one_of([genLeaf(), genFork()]))


@composite
def genTreeRoot(draw):
    x = Tree.ROOT(draw(genTree1()))
    return x



@given(genTreeRoot())
def testPropLocMin(i):
    assert all(st.full_tdTU(lambda x: st.adhocTUZ(st.failTU, validateLocMin, x), zp.obj(i)))



def validateLocMin(t, z):
    x = t.match(
        leaf=lambda l: [l >= globmin(z)],
        fork=lambda l, r: [locmin(z) >= globmin(z)],
        root=lambda r: []
    )
    return x


@given(genTreeRoot())
def testPropGlobMin(i):
    assert all(st.full_tdTU(lambda x: st.adhocTUZ(st.failTU, globminIsSmaller, x), zp.obj(i)))


def globminIsSmaller(t, z):
    x = t.match(
        leaf=lambda l: [globmin(z) <= l],
        fork=lambda l, r: [],
        root=lambda r: []
    )
    return x


@given(genTreeRoot())
def testResultingInOriginal(t):
    assert all(st.full_tdTU(lambda x: st.adhocTUZ(st.failTU, intInOriginal, x), repminAG(t)))


def intInOriginal(i):
    def equal(n):
        return i == n
    return any(st.full_tdTU(lambda x: st.adhocTUZ(st.failTU, equal, x), zp.obj(i)))


@given(genTreeRoot())
def testNumberLeaves(t):
    assert(countLeaves(t) == countLeaves(repminAG(t)))


def countLeaves(t):
    return t.match(
        root=lambda r: countLeaves(r),
        fork=lambda l, r: countLeaves(l) + countLeaves(r),
        leaf=lambda l: 1
    )

@given(genTreeRoot())
def testIsomorphic(t):
    assert isIsomorphic(t, repminAG(t))

def isIsomorphic(t1, t2):
    return t1.match(
        root=lambda l1: t2.match(
            root=lambda l2: isIsomorphic(l1, l2),
            fork=lambda l2, r2: False,
            leaf=lambda l2: False
        ),
        fork=lambda l1, r1: t2.match(
            root=lambda l2: False,
            fork=lambda l2, r2: isIsomorphic(l1, l2) and isIsomorphic(r1, r2),
            leaf=lambda l2: False
        ),
        leaf=lambda l1: t2.match(
            root=lambda l2: False,
            fork=lambda l2, r2: False,
            leaf=lambda l2: True
        )
    )


@given(genTreeRoot())
def testGlobminPreserved(t):
    zt = zp.obj(t)
    assert globmin(zt) == globmin(zp.obj(repminAG(t)))
