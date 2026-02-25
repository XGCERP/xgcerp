# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	if frappe.get_all("Company", filters={"country": "India"}, limit=1):
		frappe.db.set_single_value("Stock Settings", "allow_existing_serial_no", 1)
