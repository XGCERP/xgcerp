# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe
from frappe.query_builder import DocType


def execute():
	POSOpeningEntry = DocType("POS Opening Entry")
	POSClosingEntry = DocType("POS Closing Entry")

	frappe.qb.update(POSOpeningEntry).set(POSOpeningEntry.status, "Cancelled").where(
		POSOpeningEntry.docstatus == 2
	).run()
	frappe.qb.update(POSClosingEntry).set(POSClosingEntry.status, "Cancelled").where(
		POSClosingEntry.docstatus == 2
	).run()
