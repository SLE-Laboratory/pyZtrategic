from repmin_data import Tree, Root, Leaf, Fork
from hypothesis.strategies import integers, composite, one_of


#########################################
# Hypothesis generator

@composite
def genLeaf(draw) -> Leaf:
    i = draw(integers(min_value=1))
    return Leaf(i)

@composite
def genFork(draw) -> Fork:
    return Fork(draw(genTree()), draw(genTree()))

@composite
def genTree(draw) -> Tree:
    return draw(one_of([genLeaf(), genFork()]))


@composite
def genTreeRoot(draw) -> Root:
    x = Root(draw(genTree()))
    return x


#########################################
# Normal generator


def testTree(n: int) -> Tree:
    return Root(build_tree(list(range(1, n+1))))


def build_tree(lst: list[int]) -> Tree:
    n = len(lst)
    if n == 2:
        return Fork(Leaf(lst[0]), Leaf(lst[1]))
    elif n == 3:
        return Fork(Fork(Leaf(lst[0]), Leaf(lst[1])), Leaf(lst[2]))
    else:
        half = n // 2
        left_subtree = build_tree(lst[:half])
        right_subtree = build_tree(lst[half:])
        return Fork(left_subtree, right_subtree)


#########################################
