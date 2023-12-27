import zipper as zp
import strategy as st
from adt import adt, Case

import sys


@adt
class Tree:
    ROOT: Case["Tree"]
    FORK: Case["Tree", "Tree"]
    LEAF: Case[int]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.match(
            root=lambda l: "Root " + str(l),
            fork=lambda l, r: "Fork " + str(l) + str(r),
            leaf=lambda l: "Leaf " + str(l)
        )


class Constructor:
    CRoot = "CRoot"
    CFork = "CFork"
    CLeaf = "CLeaf"


def constructor(ag):
    return ag.node().match(
        root=lambda x: Constructor.CRoot,
        fork=lambda x, y: Constructor.CFork,
        leaf=lambda x: Constructor.CLeaf
    )


def lexeme(ag):
    return ag.node().match(
        root=lambda x: None,
        fork=lambda x, y: None,
        leaf=lambda x: x
    )


def globmin(z):
    match constructor(z):
        case Constructor.CRoot:
            return locmin(z.z_dollar(1))
        case Constructor.CLeaf:
            return globmin(z.up())
        case Constructor.CFork:
            return globmin(z.up())


def locmin(z):
    match constructor(z):
        case Constructor.CLeaf:
            return lexeme(z)
        case Constructor.CFork:
            return min(locmin(z.z_dollar(1)), locmin(z.z_dollar(2)))


def replace(z):
    match constructor(z):
        case Constructor.CRoot:
            return Tree.ROOT(replace(z.z_dollar(1)))
        case Constructor.CLeaf:
            return Tree.LEAF(globmin(z))
        case Constructor.CFork:
            return Tree.FORK(replace(z.z_dollar(1)), replace(z.z_dollar(2)))


def repminAG(t):
    return replace(zp.obj(t))


def repminZtrategic(t):
    def aux(exp, z):
        x = exp.match(
            leaf=lambda x: Tree.LEAF(globmin(z)),
            fork=lambda x, y: st.StrategicError,
            root=lambda x: st.StrategicError,
        )
        if x is st.StrategicError:
            raise x
        else:
            return x

    return st.full_tdTP(lambda x: st.adhocTPZ(st.idTP, aux, x), t).node()


def minimumValue(t):
    def nodeVal(exp):
        z = exp.match(
            leaf=lambda x: [x],
            fork=lambda x, y: st.StrategicError,
            root=lambda x: st.StrategicError,
        )
        if z is st.StrategicError:
            raise z
        else:
            return z

    return min(st.full_tdTU(lambda x: st.adhocTU(st.failTU, nodeVal, x), t))


def replaceTree(i, t):
    def replaceTP(i, exp):
        x = exp.match(
            leaf=lambda x: Tree.LEAF(i),
            fork=lambda x, y: st.StrategicError,
            root=lambda x: st.StrategicError,
        )
        if x is st.StrategicError:
            raise x
        else:
            return x

    return st.full_tdTP(lambda x: st.adhocTP(st.idTP, lambda y: replaceTP(i, y), x), t).node()


def repmin(t):
    return replaceTree(minimumValue(t), t)

#########################################
# generator


def testTree(n):
    return Tree.ROOT(build_tree(list(range(1, n+1))))


def build_tree(lst):
    n = len(lst)
    if n == 2:
        return Tree.FORK(Tree.LEAF(lst[0]), Tree.LEAF(lst[1]))
    elif n == 3:
        return Tree.FORK(Tree.FORK(Tree.LEAF(lst[0]), Tree.LEAF(lst[1])), Tree.LEAF(lst[2]))
    else:
        half = n // 2
        left_subtree = build_tree(lst[:half])
        right_subtree = build_tree(lst[half:])
        return Tree.FORK(left_subtree, right_subtree)


#########################################

def sumTree(t):
    return t.match(
        root=lambda r: sumTree(r),
        fork=lambda l, r: sumTree(l) + sumTree(r),
        leaf=lambda l: l
    )


##########################################


def main():

    i = int(sys.argv[1])

    print(sumTree(repmin(zp.obj(testTree(i)))))


if __name__ == "__main__":
    main()
