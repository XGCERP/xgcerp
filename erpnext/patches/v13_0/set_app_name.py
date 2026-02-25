# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	frappe.reload_doctype("System Settings")
	settings = frappe.get_doc("System Settings")
	settings.db_set("app_name", "XGCERP", commit=True)
