# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	frappe.reload_doc("accounts", "doctype", "pos_closing_entry")

	frappe.db.sql("update `tabPOS Closing Entry` set `status` = 'Failed' where `status` = 'Queued'")
