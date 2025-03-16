from pyztrategic.zipper import Zipper

from typing import Optional
from dataclasses import dataclass

from enum import StrEnum, auto


type Lets = Root | Let | List | Exp

type List = NestedLet | Assign | Empty

type Exp = Add | Sub | Neg | Var | Const

type Env = list[tuple[str, int, Optional[Exp]]]

type EnvBlock = list[tuple[str, Optional[Exp]]]

@dataclass
class Let:
    lst: List
    exp: Exp

    def __repr__(self):
        return str(self)

    def __str__(self):
        match self:
            case Let(lst, exp):
                return "let " + str(lst) + "in " + str(exp) + "\n"

@dataclass
class Root:
    let: Let

    def __repr__(self):
        return str(self)

    def __str__(self):
        match self:
            case Root(let):
                return str(let)

@dataclass
class NestedLet:
    name: str
    let: Let
    lst: List

    def __repr__(self):
        return str(self)

    def __str__(self):
        match self:
            case NestedLet(name, let, lst):
                return name + " = " + str(let) + str(lst)

@dataclass
class Assign:
    name: str
    exp: Exp
    lst: List

    def __repr__(self):
        return str(self)

    def __str__(self):
        match self:
            case Assign(name, exp, lst):
                return name + " = " + str(exp) + "\n" + str(lst)

@dataclass
class Empty:
    pass

    def __repr__(self):
        return str(self)

    def __str__(self):
        match self:
            case Empty():
                return ""

@dataclass
class Add:
    x: Exp
    y: Exp

    def __repr__(self):
        return str(self)

    def __str__(self):
        match self:
            case Add(x, y):
                return str(x) + " + " + str(y)

@dataclass
class Sub:
    x: Exp
    y: Exp

    def __repr__(self):
        return str(self)

    def __str__(self):
        match self:
            case Sub(x, y):
                return str(x) + " - " + str(y)

@dataclass
class Neg:
    x: Exp

    def __repr__(self):
        return str(self)

    def __str__(self):
        match self:
            case Neg(x):
                return "-" + str(x)

@dataclass
class Var:
    name: str

    def __repr__(self):
        return str(self)

    def __str__(self):
        match self:
            case Var(name):
                return name

@dataclass
class Const:
    value: int

    def __repr__(self):
        return str(self)

    def __str__(self):
        match self:
            case Const(value):
                return str(value)


class Constructor(StrEnum):
    CRoot = auto()
    CLet = auto()
    CNestedLet = auto()
    CAssign = auto()
    CEmpty = auto()
    CAdd = auto()
    CSub = auto()
    CNeg = auto()
    CConst = auto()
    CVar = auto()


def constructor(ag: Zipper[Lets]) -> Constructor:
    match ag.node():
        case Root():
            return Constructor.CRoot
        case Let():
            return Constructor.CLet
        case NestedLet():
            return Constructor.CNestedLet
        case Assign():
            return Constructor.CAssign
        case Empty():
            return Constructor.CEmpty
        case Add():
            return Constructor.CAdd
        case Sub():
            return Constructor.CSub
        case Neg():
            return Constructor.CNeg
        case Var():
            return Constructor.CVar
        case Const():
            return Constructor.CConst


def lexeme_Name(ag: Zipper[Lets]) -> str:
    match ag.node():
        case NestedLet(x,_,_):
            return x
        case Assign(x,_,_):
            return x
        case Var(x):
            return x


def lexeme_Exp(ag: Zipper[Lets]) -> Exp:
    match ag.node():
        case Assign(_,y,_):
            return y