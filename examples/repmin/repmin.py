from pyztrategic.zipper import obj
import pyztrategic.strategy as st


from repmin_data import Leaf, Fork

type Tree = Leaf | Fork


t1=Fork(Leaf(3), Fork(Leaf(2), Leaf(4)))


def tmin(t: Tree) -> int:
    match(t):
        case Leaf(n):
            return n
        case Fork(l,r):
            return min(tmin(l), tmin(r))
        
def replace(t: Tree, n: int) -> Tree:
    match(t):
        case Leaf(_):
            return Leaf(n)
        case Fork(l,r):
            return Fork(replace(l,n), replace(r,n))
        
def repmin(t: Tree) -> Tree:
    return replace(t, tmin(t))


# Properties for Repmin


def values(t: Tree) -> int:
    match(t):
        case Leaf(l):
            return 1
        case Fork(l,r):
            return values(l) + values(r)


def toList(t: Tree) -> list[int]:
    match(t):
        case Leaf(l):
            return [l]
        case Fork(l,r):
            return toList(l) + toList(r)



#prop_repmin1 t =  values t == values (repmin t)  
def prop_repmin1(t: Tree) -> bool:
    return values(t) == values(repmin(t))


#prop_repmin2 t = (values t) * (tmin t) == sum (toList (repmin t))
def prop_repmin2(t: Tree) -> bool:
    return (values(t) * tmin(t)) == sum(toList(repmin(t)))


# Strategies

def inc(t: Tree) -> Tree:
    def aux(tr: Tree) -> Tree:
        match(tr):
            case Leaf(l):
                return Leaf(l+1)
            case _:
                raise st.StrategicError
    return st.full_tdTP(lambda x: st.adhocTP(st.idTP, aux, x), obj(t)).node()


# innermost
# rule:   Fork (Leaf 0) (Leaf x)  -> Leaf x
#         Fork (Leaf x) (Leaf 0)  -> Leaf x


t2 = Fork(Fork(Leaf(2), Leaf(0)), Leaf(0))

def opt(t: Tree) -> Tree:
    def aux(tr: Tree) -> Tree:
        match(tr):
            case Fork(Leaf(0), Leaf(x)):
                return Leaf(x)
            case Fork(Leaf(x), Leaf(0)):
                return Leaf(x)
            case _:
                raise st.StrategicError
    return st.innermost(lambda x: st.adhocTP(st.failTP, aux, x), obj(t)).node()
    #return st.full_buTP(lambda x: st.adhocTP(st.idTP, aux, x), obj(t)).node()
    #return st.full_tdTP(lambda x: st.adhocTP(st.idTP, aux, x), obj(t)).node()


def valuesTU(t: Tree) -> int:
    def aux(tr: Tree) -> list[int]:
        match(tr):
            case Leaf(_):
                return [1]
            case _:
                return []
    return sum(st.full_tdTU(lambda x: st.adhocTU(st.failTU, aux, x), obj(t)))