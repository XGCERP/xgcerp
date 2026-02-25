# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
from frappe import qb


def execute():
	"""
	Clear `tabSingles` and Payment Reconciliation tables of values
	"""
	singles = qb.DocType("Singles")
	qb.from_(singles).delete().where(singles.doctype == "Payment Reconciliation").run()
	doctypes = [
		"Payment Reconciliation Invoice",
		"Payment Reconciliation Payment",
		"Payment Reconciliation Allocation",
	]
	for x in doctypes:
		dt = qb.DocType(x)
		qb.from_(dt).delete().run()
