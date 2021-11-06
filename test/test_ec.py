# -*- coding: utf-8 -*-

import unittest

import tinyec.ec as ec
import tinyec.registry as reg


class TestCurve(unittest.TestCase):

    def setUp(self):
        self.field = ec.SubGroup(23, (1, 2), 5, 1)
        self.curve = reg.get_curve("brainpoolP384r1")
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

    def test_python3_compat_when_point_is_not_multiplied_by_int_or_point_then_error_is_raised(self):
        p1 = ec.Point(self.curve, 3, 6)
        with self.assertRaises(TypeError):
            p1 * 5.6

class TestKeyPair(unittest.TestCase):
    def setUp(self):
        self.curve = reg.get_curve("brainpoolP160r1")
        super(TestKeyPair, self).setUp()

    def test_when_keypair_is_generated_then_public_key_is_on_curve(self):
        keypair = ec.make_keypair(self.curve)
        self.assertTrue(1 <= keypair.priv <= self.curve.field.n)
        self.assertTrue(self.curve.on_curve(keypair.pub.x, keypair.pub.y))

    def test_when_no_keys_are_provided_then_error_is_raised(self):
        with self.assertRaises(ValueError):
            ec.Keypair(self.curve, None, None)

    def test_when_no_public_key_is_provided_then_it_is_calculated_from_private_key(self):
        keypair = ec.make_keypair(self.curve)
        keys = ec.Keypair(self.curve, keypair.priv)
        self.assertEqual(keypair.pub, keys.pub)
        self.assertTrue(keys.can_encrypt)
        self.assertTrue(keys.can_sign)


class TestECDH(unittest.TestCase):
    def setUp(self):
        self.curve = reg.get_curve("secp384r1")
        super(TestECDH, self).setUp()

    def test_when_dh_secret_is_generated_then_it_matches_on_both_keypairs(self):
        keypair1 = ec.make_keypair(self.curve)
        keypair2 = ec.make_keypair(self.curve)
        self.assertNotEqual(keypair1.priv, keypair2.priv)
        self.assertNotEqual(keypair1.pub, keypair2.pub)
        ecdh1 = ec.ECDH(keypair1)
        ecdh2 = ec.ECDH(keypair2)
        self.assertEqual(ecdh1.get_secret(keypair2), ecdh2.get_secret(keypair1))
        # Test that secret computation works without priv key
        keypair3 = ec.Keypair(self.curve, pub=keypair1.pub)
        ecdh3 = ec.ECDH(keypair3)
        self.assertEqual(ecdh3.get_secret(keypair2), ecdh2.get_secret(keypair3))
