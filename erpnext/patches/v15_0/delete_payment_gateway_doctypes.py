# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	for dt in ("GoCardless Settings", "GoCardless Mandate", "Mpesa Settings"):
		frappe.delete_doc("DocType", dt, ignore_missing=True)
