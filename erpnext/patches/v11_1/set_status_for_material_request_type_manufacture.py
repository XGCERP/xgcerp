# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	frappe.db.sql(
		"""
		update `tabMaterial Request`
		set status='Manufactured'
		where docstatus=1 and material_request_type='Manufacture' and per_ordered=100 and status != 'Stopped'
	"""
	)
