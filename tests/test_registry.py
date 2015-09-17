# -*- coding: utf-8 -*-

import unittest

import tinyec.ec as ec
import tinyec.registry as reg


class TestGetCurve(unittest.TestCase):
    def test_when_invalid_curve_name_is_provided_then_exception_is_raised(self):
        with self.assertRaises(ValueError):
            reg.get_curve("abcd")

    def test_when_valid_curve_name_is_provided_then_curve_object_is_built(self):
        curve_name = "brainpoolP160r1"
        curve = reg.get_curve(curve_name)
        self.assertIsInstance(curve, ec.Curve)
        self.assertEqual(curve_name, curve.name)
        self.assertEqual(reg.EC_CURVE_REGISTRY[curve_name]["n"], curve.field.n)
