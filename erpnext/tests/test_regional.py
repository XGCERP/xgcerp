# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import unittest

import frappe
from frappe.tests import IntegrationTestCase

import erpnext


@erpnext.allow_regional
def test_method():
	return "original"


class TestInit(IntegrationTestCase):
	def test_regional_overrides(self):
		frappe.flags.country = "Maldives"
		self.assertEqual(test_method(), "original")
