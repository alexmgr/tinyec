# -*- coding: utf-8 -*-

import unittest
import tinyec.ec as ec


class TestCurve(unittest.TestCase):

    def setUp(self):
        self.field = ec.SubGroup(23, (1, 2), 5, 1)
        super(TestCurve, self).setUp()

    def test_when_specific_a_and_b_are_used_then_curve_is_singular(self):
        self.assertTrue(ec.Curve(0, 0, self.field).is_singular())
        self.assertTrue(ec.Curve(-3, 2, self.field).is_singular())
        self.assertFalse(ec.Curve(-3, 1, self.field).is_singular())
        self.assertFalse(ec.Curve(2, 2, self.field).is_singular())


class TestPoint(unittest.TestCase):
    def setUp(self):
        self.field = ec.SubGroup(97, (1, 2), 5, 1)
        self.curve = ec.Curve(2, 3, self.field)
        super(TestPoint, self).setUp()

    def test_when_point_are_on_curve_then_add_result_is_on_curve(self):
        p1 = ec.Point(self.curve, 22, 5)
        p2 = ec.Point(self.curve, 95, 31)
        self.assertEqual(ec.Point(self.curve, 29, 43), p1 + p2)
        p1 = ec.Point(self.curve, 24, 2)
        p2 = ec.Point(self.curve, 96, 0)
        self.assertEqual(ec.Point(self.curve, 38, 90), p1 + p2)

    def test_when_point_is_not_on_curve_then_warning_is_raised(self):
        import warnings
        p1 = ec.Point(self.curve, 22, 5)
        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            with self.assertRaises(UserWarning):
                ec.Point(self.curve, 94, 31)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            p2 = ec.Point(self.curve, 94, 31)
        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            with self.assertRaises(UserWarning):
                p1 + p2

    def test_when_point_is_added_to_infinity_then_point_is_returned(self):
        p1 = ec.Point(self.curve, 22, 5)
        p2 = ec.Inf(self.curve)
        self.assertEqual(p1, p1 + p2)
        self.assertEqual(p1, p2 + p1)

    def test_when_same_points_are_added_then_result_is_on_curve(self):
        p1 = ec.Point(self.curve, 24, 2)
        self.assertEqual(ec.Point(self.curve, 65, 65), p1 + p1)

    def test_when_points_have_opposite_ordinates_then_result_is_infinite(self):
        p1 = ec.Point(self.curve, 12, 3)
        p2 = ec.Point(self.curve, 12, 94)
        self.assertEqual(ec.Inf(self.curve), p1 + p2)

    def test_when_point_is_substracted_from_infinity_then_point_is_returned(self):
        p1 = ec.Point(self.curve, 22, 5)
        p2 = ec.Inf(self.curve)
        self.assertEqual(p1, p1 - p2)
        self.assertEqual(p1, p2 - p1)

    def test_when_point_are_on_curve_then_substracted_result_is_on_curve(self):
        p1 = ec.Point(self.curve, 22, 5)
        p2 = ec.Point(self.curve, 95, 66)
        # -31 % 97 == 66
        p3 = ec.Point(self.curve, 95, 31)
        self.assertEqual(p1 + p2, p1 - p3)

    def test_when_point_is_scalar_multiplied_then_point_is_in_subgroup(self):
        p1 = ec.Point(self.curve, 3, 6)
        self.assertEqual(ec.Point(self.curve, 3, 6), p1 * 1)
        self.assertEqual(ec.Point(self.curve, 80, 10), 2 * p1 * 1)
        self.assertEqual(ec.Point(self.curve, 3, 91), 2 * p1 * 2)
        self.assertEqual(ec.Point(self.curve, 80, 10), p1 * -3)
        self.assertEqual(ec.Inf(self.curve), p1 * 10)

    def test_when_point_is_not_multiplied_by_an_int_then_error_is_raised(self):
        p1 = ec.Point(self.curve, 3, 6)
        with self.assertRaises(TypeError):
            p1 * p1
