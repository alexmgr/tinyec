# -*- coding: utf-8 -*-

import warnings


def egcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = egcd(b % a, a)
        return g, x - (b // a) * y, y


def modinv(a, p):
    if a < 0:
        return p - modinv(-a, p)
    g, x, y = egcd(a, p)
    if g != 1:
        raise ArithmeticError("Modular inverse does not exist")
    else:
        return x % p


class Curve(object):
    def __init__(self, a, b, field, name="undefined"):
        self.name = name
        self.a = a
        self.b = b
        self.field = field
        self.g = Point(self, self.field.g[0], self.field.g[1])

    def is_singular(self):
        return (4 * self.a**3 + 27 * self.b**2) % self.field.p == 0

    def on_curve(self, x, y):
        return (y**2 - x**3 - self.a * x - self.b) % self.field.p == 0

    def __eq__(self, other):
        if not isinstance(other, Curve):
            return False
        return self.a == other.a and self.b == other.b and self.field == other.field

    def __str__(self):
        return "%s => y^2 = x^3 + %dx + %d (mod %d)" % (self.name, self.a, self.b, self.field.p)


class SubGroup(object):
    def __init__(self, p, g, n, h):
        self.p = p
        self.g = g
        self.n = n
        self.h = h

    def __eq__(self, other):
        if not isinstance(other, SubGroup):
            return False
        return self.p == other.p and self.g == other.g and self.n == other.n and self.h == other.h

    def __ne__(self, other):
        return self.__eq__(other)

    def __str__(self):
        return "Subgroup => generator %s, order: %d, cofactor: %d on Field => prime %d" % (self.g, self.n,
                                                                                           self.h, self.p)

    def __repr__(self):
        return self.__str__()


class Inf(object):
    def __init__(self, curve, x=None, y=None):
        self.x = x
        self.y = y
        self.curve = curve

    def __eq__(self, other):
        if not isinstance(other, Inf):
            return False
        return self.curve == other.curve

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        if isinstance(other, Inf):
            return Inf()
        if isinstance(other, Point):
            return other
        raise TypeError("Unsupported operand type(s) for +: '%s' and '%s'" % (q.__class__.__name__,
                                                                                  self.__class__.__name__))

    def __sub__(self, other):
        if isinstance(other, Inf):
            return Inf()
        if isinstance(other, Point):
            return other
        raise TypeError("Unsupported operand type(s) for +: '%s' and '%s'" % (q.__class__.__name__,
                                                                                  self.__class__.__name__))

    def __str__(self):
        return "%s on %s" % (self.__class__.__name__, self.curve)

    def __repr__(self):
        return self.__str__()


class Point(object):
    def __init__(self, curve, x, y):
        self.curve = curve
        self.x = x
        self.y = y
        self.p = self.curve.field.p
        self.on_curve = True
        if not self.curve.on_curve(self.x, self.y):
            warnings.warn("Point (%d, %d) is not on curve %s" % (self.x, self.y, self.curve))
            self.on_curve = False

    def __m(self, p, q):
        if p.x == q.x:
            return (3 * p.x**2 + self.curve.a) * modinv(2 * p.y, self.p)
        else:
            return (p.y - q.y) * modinv(p.x - q.x, self.p)

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y and self.curve == other.curve

    def __ne__(self, other):
        return self.__eq__(other)

    def __add__(self, other):
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

    def __sub__(self, other):
        if isinstance(other, Inf):
            return self.__add__(other)
        if isinstance(other, Point):
            return self.__add__(Point(self.curve, other.x, -other.y % self.p))
        else:
            raise TypeError("Unsupported operand type(s) for -: '%s' and '%s'" % (other.__class__.__name__,
                                                                                  self.__class__.__name__))

    def __mul__(self, other):
        if isinstance(other, Inf) or other % self.curve.field.n == 0:
            return Inf(self.curve)
        if isinstance(other, int):
            # Broken, should be -other * -self
            if other < 0:
                addend = Point(self.curve, self.x, -self.y % self.p)
            else:
                addend = self
            result = Inf(self.curve)
            # Iterate over all bits starting by the LSB
            for bit in reversed([int(i) for i in bin(abs(other))[2:]]):
                if bit == 1:
                    result += addend
                addend += addend
            return result
        else:
            raise TypeError("Unsupported operand type(s) for *: '%s' and '%s'" % (other.__class__.__name__,
                                                                                  self.__class__.__name__))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __str__(self):
        return "(%d, %d) on %s" % (self.x, self.y, self.curve)

    def __repr__(self):
        return self.__str__()
