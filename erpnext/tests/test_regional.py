import unittest

import frappe

import erpnext
from erpnext.tests.utils import XGCERPTestSuite


@erpnext.allow_regional
def test_method():
	return "original"


class TestInit(XGCERPTestSuite):
	def test_regional_overrides(self):
		frappe.flags.country = "Maldives"
		self.assertEqual(test_method(), "original")
