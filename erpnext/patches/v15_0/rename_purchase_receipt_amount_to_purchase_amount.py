# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe
from frappe.model.utils.rename_field import rename_field


def execute():
	frappe.reload_doc("assets", "doctype", "asset")
	if frappe.db.has_column("Asset", "purchase_receipt_amount"):
		rename_field("Asset", "purchase_receipt_amount", "purchase_amount")
