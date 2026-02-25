# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	if frappe.db.exists("Page", "point-of-sale"):
		frappe.rename_doc("Page", "pos", "point-of-sale", 1, 1)
