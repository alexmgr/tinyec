import random
from typing import Any, Optional, Tuple, Union

import warnings

def egcd(a: int, b: int) -> Tuple[int, int, int]:
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = egcd(b % a, a)
        return g, x - (b // a) * y, y


def mod_inv(a: int, p: int) -> int:
    if a < 0:
        return p - mod_inv(-a, p)
    g, x, y = egcd(a, p)
    if g != 1:
        raise ArithmeticError("Modular inverse does not exist")
    else:
        return x % p


class SubGroup:
    def __init__(self, p: int, g: Tuple[int, int], n: int, h:int):
        self.p = p
        self.g = g
        self.n = n
        self.h = h

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SubGroup):
            return False
        return self.p == other.p and self.g == other.g and self.n == other.n and self.h == other.h

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return "Subgroup => generator %s, order: %d, cofactor: %d on Field => prime %d" % (self.g, self.n,
                                                                                           self.h, self.p)

    def __repr__(self) -> str:
        return self.__str__()


class Curve:
    def __init__(self, a: int, b: int, field: SubGroup, name:str="undefined"):
        self.name = name
        self.a = a
        self.b = b
        self.field = field
        self.g = Point(self, self.field.g[0], self.field.g[1])

    def is_singular(self) -> bool:
        return (4 * self.a**3 + 27 * self.b**2) % self.field.p == 0

    def on_curve(self, x: int, y: int) -> bool:
        return (y**2 - x**3 - self.a * x - self.b) % self.field.p == 0

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Curve):
            return False
        return self.a == other.a and self.b == other.b and self.field == other.field

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return "\"%s\" => y^2 = x^3 + %dx + %d (mod %d)" % (self.name, self.a, self.b, self.field.p)


class Inf:
    def __init__(self, curve: Curve, x: Optional[int]=None, y: Optional[int]=None):
        self.x = x
        self.y = y
        self.curve = curve

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Inf):
            return False
        return self.curve == other.curve

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __add__(self, other: Any) -> Union["Inf", "Point"]:
        if isinstance(other, Inf):
            return Inf(self.curve)
        if isinstance(other, Point):
            return other
        raise TypeError("Unsupported operand type(s) for +: '%s' and '%s'" % (other.__class__.__name__,
                                                                                  self.__class__.__name__))

    def __sub__(self, other: Any) -> Union["Inf", "Point"]:
        if isinstance(other, Inf):
            return Inf(self.curve)
        if isinstance(other, Point):
            return other
        raise TypeError("Unsupported operand type(s) for +: '%s' and '%s'" % (other.__class__.__name__,
                                                                                  self.__class__.__name__))

    def __str__(self) -> str:
        return "%s on %s" % (self.__class__.__name__, self.curve)

    def __repr__(self) -> str:
        return self.__str__()


class Point:
    def __init__(self, curve: Curve, x: int, y: int):
        self.curve = curve
        self.x = x
        self.y = y
        self.p = self.curve.field.p
        self.on_curve = True
        if not self.curve.on_curve(self.x, self.y):
            warnings.warn("Point (%d, %d) is not on curve \"%s\"" % (self.x, self.y, self.curve))
            self.on_curve = False

    def __m(self, p: "Point", q: "Point") -> int:
        if p.x == q.x:
            return (3 * p.x**2 + self.curve.a) * mod_inv(2 * p.y, self.p)
        else:
            return (p.y - q.y) * mod_inv(p.x - q.x, self.p)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y and self.curve == other.curve

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __add__(self, other: Any) -> Union[Inf, "Point"]:
        if isinstance(other, Inf):
            return self
        if isinstance(other, Point):
            if self.x == other.x and self.y != other.y:
                return Inf(self.curve)
            elif self.curve == other.curve:
                m = self.__m(self, other)
                x_r = (m**2 - self.x - other.x) % self.p
                y_r = -(self.y + m * (x_r - self.x)) % self.p
                return Point(self.curve, x_r, y_r)
            else:
                raise ValueError("Cannot add points belonging to different curves")
        else:
            raise TypeError("Unsupported operand type(s) for +: '%s' and '%s'" % (other.__class__.__name__,
                                                                                  self.__class__.__name__))

    def __sub__(self, other: Any) -> Union[Inf, "Point"]:
        if isinstance(other, Inf):
            return self.__add__(other)
        if isinstance(other, Point):
            return self.__add__(Point(self.curve, other.x, -other.y % self.p))
        else:
            raise TypeError("Unsupported operand type(s) for -: '%s' and '%s'" % (other.__class__.__name__,
                                                                                  self.__class__.__name__))

    def __mul__(self, other: Any) -> Union[Inf, "Point"]:
        if isinstance(other, Inf):
            return Inf(self.curve)
        if not isinstance(other, int):
            raise TypeError("Unsupported operand type(s) for *: '%s' and '%s'" % (other.__class__.__name__,
                                                                                  self.__class__.__name__))
        if other % self.curve.field.n == 0:
            return Inf(self.curve)
        addend: Union[Inf, Point] = Point(self.curve, self.x, -self.y % self.p) if other < 0 else self
        result: Union[Inf, Point] = Inf(self.curve)
        # Iterate over all bits starting by the LSB
        for bit in reversed([int(i) for i in bin(abs(other))[2:]]):
            if bit == 1:
                result += addend
            addend += addend
        return result

    def __rmul__(self, other: Any) -> Union[Inf, "Point"]:
        return self.__mul__(other)

    def __str__(self) -> str:
        return "(%d, %d) %s %s" % (self.x, self.y, "on" if self.on_curve else "off", self.curve)

    def __repr__(self) -> str:
        return self.__str__()


class Keypair:
    def __init__(self, curve: Curve, priv: Optional[int]=None, pub: Optional[Point]=None):
        self.curve = curve
        self.can_sign = True
        self.can_encrypt = True
        self.priv: Optional[int] = priv
        if priv is None:
            self.can_sign = False
            if pub is None:
                raise ValueError("At least one of private or public key must be provided.")
            self.pub = pub
        else:
            self.can_sign = True
            if pub is None:
                self.pub = self._generate_pub(priv)
            else:
                self.pub = pub

    def _generate_pub(self, priv: int) -> Point:
        result = self.priv * self.curve.g
        if isinstance(result, Inf):
            raise ValueError("Generated public value at infinity point.")
        return result


class ECDH:
    def __init__(self, keypair: Keypair):
        self.keypair = keypair

    def get_secret(self, other: Keypair) -> Point:
        # Don't check if both keypairs are on the same curve. Should raise a warning only
        if self.keypair.priv is not None and self.keypair.can_sign and other.can_encrypt:
            secret = self.keypair.priv * other.pub
        elif self.keypair.can_encrypt and other.can_sign and other.priv is not None:
            secret = self.keypair.pub * other.priv
        else:
            raise ValueError("Missing crypto material to generate DH secret")
        if isinstance(secret, Inf):
            raise ValueError("Got a secret that is at the infinite point")
        return secret


def make_keypair(curve: Curve) -> Keypair:
    priv = random.randint(1, curve.field.n)
    pub = priv * curve.g
    if isinstance(pub, Inf):
        raise RuntimeError("Created infinite public key")
    return Keypair(curve, priv, pub)
