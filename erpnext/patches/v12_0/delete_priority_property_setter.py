# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	frappe.db.sql(
		"""
		DELETE FROM `tabProperty Setter`
		WHERE `tabProperty Setter`.doc_type='Issue'
			AND `tabProperty Setter`.field_name='priority'
			AND `tabProperty Setter`.property='options'
	"""
	)
