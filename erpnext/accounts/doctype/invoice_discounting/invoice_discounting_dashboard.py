# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
from frappe import _


def get_data():
	return {
		"fieldname": "reference_name",
		"internal_links": {"Sales Invoice": ["invoices", "sales_invoice"]},
		"transactions": [
			{"label": _("Reference"), "items": ["Sales Invoice"]},
			{"label": _("Payment"), "items": ["Payment Entry", "Journal Entry"]},
		],
	}
