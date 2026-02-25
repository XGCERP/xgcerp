# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	frappe.reload_doc("stock", "doctype", "bin")

	frappe.db.sql(
		"""
        UPDATE `tabBin` b
        INNER JOIN `tabWarehouse` w ON b.warehouse = w.name
        SET b.company = w.company
        WHERE b.company IS NULL OR b.company = ''
    """
	)
