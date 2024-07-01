from hypothesis import given
from hypothesis.strategies import integers, from_regex, composite, one_of, sampled_from, builds, deferred

from strategy import *
from let import Root, Let, List, Exp, dclBlock, env
from zipper import obj


# -- --------
# -- --
# -- - Generator for Let expressions
# -- --
# -- --------



@composite
def genExp(draw, names):
    add = builds(Exp.ADD, deferred(lambda: exp), deferred(lambda: exp))
    sub = builds(Exp.SUB, deferred(lambda: exp), deferred(lambda: exp))
    neg = builds(Exp.NEG, deferred(lambda: exp))
    const = builds(Exp.CONST, integers(min_value=1))
    if not names:
        exp = deferred(lambda: one_of(const, neg, add, sub))
        return draw(exp)
    else:
        var = builds(Exp.VAR, sampled_from(names))
        exp = deferred(lambda: one_of(const, var, neg, add, sub))
        return draw(exp)

@composite
def genAssign(draw, names, n):
    name = draw(genName())
    while name in names:
        name = draw(genName())
    nExp = draw(genExp(names))
    newNames, lst = draw(genList([name] + names, n-1))
    return newNames, List.ASSIGN(name, nExp, lst)


@composite
def genNestedLet(draw, names, n):
    name = draw(genName())
    nLet = draw(genLet(names, n))
    newNames, lst = draw(genList([name] + names, n-1))
    return newNames, List.NESTEDLET(name, nLet, lst)


@composite
def genList(draw, names, n):
    if n == 0:
        return names, List.EMPTY()
    else:
        return draw(one_of([genNestedLet(names, n), genAssign(names, n)]))


@composite
def genLet(draw, names, n):
    listSize = draw(integers(min_value=1, max_value=n+1))
    (newNames, lst) = draw(genList(names, listSize))
    expr = draw(genExp(newNames))
    return Let.LET(lst, expr)


@composite
def genName(draw):
    return draw(from_regex(r'^[a-z]$', fullmatch=True))


@composite
def genRoot(draw):
    return Root.ROOT(draw(genLet([], draw(integers(min_value=1)))))


###########

@given(genRoot())
def testPropLocInGlobal(i):
    assert all(full_tdTU(lambda x: adhocTUZ(failTU, localInGlobal, x), obj(i)))



def localInGlobal(t, z):
    return containedIn(dclBlock(z), env(z))


def containedIn(b, e):
    eNoLevels = [(x, z) for x, y, z in e]
    set1 = set(b)
    set2 = set(eNoLevels)
    intersection = set1.intersection(set2)
    return list(intersection) == b
