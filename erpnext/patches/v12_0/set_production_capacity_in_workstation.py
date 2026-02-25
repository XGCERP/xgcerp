# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	frappe.reload_doc("manufacturing", "doctype", "workstation")

	frappe.db.sql(
		""" UPDATE `tabWorkstation`
        SET production_capacity = 1 """
	)
