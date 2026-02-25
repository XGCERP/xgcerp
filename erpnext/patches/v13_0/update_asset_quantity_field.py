# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	if frappe.db.count("Asset"):
		frappe.reload_doc("assets", "doctype", "Asset")
		asset = frappe.qb.DocType("Asset")
		frappe.qb.update(asset).set(asset.asset_quantity, 1).run()
