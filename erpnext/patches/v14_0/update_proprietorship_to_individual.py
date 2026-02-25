# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	for doctype in ["Customer", "Supplier"]:
		field = doctype.lower() + "_type"
		frappe.db.set_value(doctype, {field: "Proprietorship"}, field, "Individual")
