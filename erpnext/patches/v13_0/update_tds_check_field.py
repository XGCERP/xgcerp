# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	if frappe.db.has_table("Tax Withholding Category") and frappe.db.has_column(
		"Tax Withholding Category", "round_off_tax_amount"
	):
		frappe.db.sql(
			"""
			UPDATE `tabTax Withholding Category` set round_off_tax_amount = 0
			WHERE round_off_tax_amount IS NULL
		"""
		)
