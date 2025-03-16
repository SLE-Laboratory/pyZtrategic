from pyztrategic.zipper import Zipper
from typing import Callable

class StrategicError(Exception):
    pass

#############################################

def idTP[T](f: Zipper[T]) -> Zipper[T]:
    return f


def failTP[T](f: T) -> None:
    raise StrategicError


def adhocTP[T](f: Callable[[Zipper[T]], Zipper[T]], g: Callable[[T], T], z: Zipper[T]) -> Zipper[T]:
    try:
        return z.trans(g)
    except (StrategicError, ValueError, AttributeError):
        return f(z)


def adhocTPZ[T](f: Callable[[Zipper[T]], Zipper[T]], g: Callable[[T, Zipper[T]], T], z: Zipper[T]) -> Zipper[T]:
    try:
        return z.transZ(g)
    except (StrategicError, ValueError, AttributeError):
        return f(z)


def seqTP[T](f: Callable[[Zipper[T]], Zipper[T]], g: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    return g(f(z))


def choiceTP[T](f: Callable[[Zipper[T]], Zipper[T]], g: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    try:
        return f(z)
    except StrategicError:
        return g(z)


def tryTP[T](f: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    return choiceTP(f, idTP, z)


def repeatTP[T](f: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    return tryTP(lambda x: seqTP(f, lambda y: repeatTP(f, y), x), z)


def allTPright[T](f: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    try:
        return f(z.right()).left()
    except (StrategicError, AttributeError):
        return z


def allTPdown[T](f: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    try:
        return f(z.down()).up()
    except (StrategicError, AttributeError):
        return z


def oneTPright[T](f: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    try:
        return f(z.right()).left()
    except (StrategicError, AttributeError) as e:
        raise e


def oneTPdown[T](f: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    try:
        return f(z.down()).up()
    except (StrategicError, AttributeError) as e:
        raise e


def full_tdTP[T](f: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    def down(x: Zipper[T]) -> Zipper[T]:
        return allTPdown(lambda y: full_tdTP(f, y), x)
    def right(w: Zipper[T]) -> Zipper[T]:
        return allTPright(lambda k: full_tdTP(f, k), w)
    def downRight(i: Zipper[T]) -> Zipper[T]:
        return seqTP(down, right, i)
    return seqTP(f, downRight,  z)


# def full_tdTP(f, z):
#     return seqTP(f, lambda i: seqTP(lambda x: allTPdown(lambda y: full_tdTP(f, y), x), lambda w: allTPright(lambda k: full_tdTP(f, k), w), i), z)


def full_buTP[T](f: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    def down(x: Zipper[T]) -> Zipper[T]:
        return allTPdown(lambda y: full_buTP(f, y), x)
    def right(w: Zipper[T]) -> Zipper[T]:
        return allTPright(lambda k: full_buTP(f, k), w)
    def downF(i: Zipper[T]) -> Zipper[T]:
        return seqTP(down, f, i)
    return seqTP(right, downF, z)


def once_tdTP[T](f: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    def down(x: Zipper[T]) -> Zipper[T]:
        return oneTPdown(lambda y: once_tdTP(f, y), x)
    def right(w: Zipper[T]) -> Zipper[T]:
        return oneTPright(lambda k: once_tdTP(f, k), w)
    def downRight(i: Zipper[T]) -> Zipper[T]:
        return choiceTP(down, right, i)
    return choiceTP(f, downRight, z)


def once_buTP[T](f: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    def down(x: Zipper[T]) -> Zipper[T]:
        return oneTPdown(lambda y: once_buTP(f, y), x)
    def right(w: Zipper[T]) -> Zipper[T]:
        return oneTPright(lambda k: once_buTP(f, k), w)
    def downF(i: Zipper[T]) -> Zipper[T]:
        return choiceTP(down, f, i)
    return choiceTP(right, downF, z)


def innermost[T](f: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    def down(x: Zipper[T]) -> Zipper[T]:
        return allTPdown(lambda y: innermost(f, y), x)
    def right(w: Zipper[T]) -> Zipper[T]:
        return allTPright(lambda k: innermost(f, k), w)
    def t(j: Zipper[T]) -> Zipper[T]:
        return seqTP(f, lambda n: innermost(f, n), j)
    def tryT(i: Zipper[T]) -> Zipper[T]:
        return tryTP(t, i)
    def downT(m: Zipper[T]) -> Zipper[T]:
        return seqTP(down, tryT, m)
    return seqTP(right, downT, z)


# def innermost(f, z):
#     return seqTP(lambda w: allTPright(lambda k: innermost(f, k), w), lambda m: seqTP(lambda x: allTPdown(lambda y: innermost(f, y), x), lambda i: tryTP(lambda j: seqTP(f, lambda n: innermost(f, n), j), i), m), z)


# broken
def innermostt[T](f: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    return repeatTP(lambda x: once_buTP(f, x), z)


def outermost[T](f: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    def down(x: Zipper[T]) -> Zipper[T]:
        return allTPdown(lambda y: outermost(f, y), x)
    def right(w: Zipper[T]) -> Zipper[T]:
        return allTPright(lambda k: outermost(f, k), w)
    def t(j: Zipper[T]) -> Zipper[T]:
        return seqTP(f, lambda n: outermost(f, n), j)
    def tryT(i: Zipper[T]) -> Zipper[T]:
        return tryTP(t, i)
    def downRight(m: Zipper[T]) -> Zipper[T]:
        return seqTP(down, right, m)
    return seqTP(tryT, downRight, z)


# broken
def outermostt[T](f: Callable[[Zipper[T]], Zipper[T]], z: Zipper[T]) -> Zipper[T]:
    return repeatTP(lambda x: once_tdTP(f, x), z)


##########
####
# TU
####
##########


def idTU[T](f: Zipper[T]) -> list[T]:
    return [f.node()]


def failTU[T](f: Zipper[T]) -> list:
    return []


def constTU[T](f: Zipper[T]) -> Zipper[T]:
    return f


def adhocTU[T](f: Callable[[Zipper[T]], list], g: Callable[[T], list], z: Zipper[T]) -> list:
    try:
        return g(z.node())
    except (StrategicError, AttributeError, TypeError):
        return f(z)


def adhocTUZ[T](f: Callable[[Zipper[T]], list], g: Callable[[T, Zipper[T]], list], z: Zipper[T]) -> list:
    try:
        return g(z.node(), z)
    except (StrategicError, AttributeError, TypeError):
        return f(z)


def seqTU[T](f: Callable[[Zipper[T]], list], g: Callable[[Zipper[T]], list], z: Zipper[T]) -> list:
    return f(z) + g(z)


def choiceTU[T](f: Callable[[Zipper[T]], list], g: Callable[[Zipper[T]], list], z: Zipper[T]) -> list:
    try:
        return f(z)
    except (StrategicError, AttributeError, TypeError):
        return g(z)


def allTUright[T](f: Callable[[Zipper[T]], list], z: Zipper[T]) -> list:
    try:
        return f(z.right())
    except (StrategicError, AttributeError, TypeError):
        return []


def allTUdown[T](f: Callable[[Zipper[T]], list], z: Zipper[T]) -> list:
    try:
        return f(z.down())
    except (StrategicError, AttributeError, TypeError):
        return []


def full_tdTU[T](f: Callable[[Zipper[T]], list], z: Zipper[T]) -> list:
    def down(x: Zipper[T]) -> list:
        return allTUdown(lambda y: full_tdTU(f, y), x)
    def right(w: Zipper[T]) -> list:
        return allTUright(lambda k: full_tdTU(f, k), w)
    def downRight(i: Zipper[T]) -> Zipper[T]:
        return seqTU(down, right, i)
    return seqTU(f, downRight,  z)


def full_buTU[T](f: Callable[[Zipper[T]], list], z: Zipper[T]) -> list:
    def down(x: Zipper[T]) -> list:
        return allTUdown(lambda y: full_buTU(f, y), x)
    def right(w: Zipper[T]) -> list:
        return allTUright(lambda k: full_buTU(f, k), w)
    def downF(i: Zipper[T]) -> list:
        return seqTU(down, f, i)
    return seqTU(right, downF, z)
