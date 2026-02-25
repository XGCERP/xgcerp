# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	if not frappe.db.get_single_value("POS Settings", "invoice_type"):
		frappe.db.set_single_value("POS Settings", "invoice_type", "POS Invoice")
