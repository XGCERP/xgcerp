# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe
from frappe.query_builder import DocType


def execute():
	POSInvoice = DocType("POS Invoice")

	frappe.qb.update(POSInvoice).set(POSInvoice.status, "Cancelled").where(POSInvoice.docstatus == 2).run()
