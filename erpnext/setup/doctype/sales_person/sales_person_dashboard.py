# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
from frappe import _


def get_data():
	return {
		"heatmap": True,
		"heatmap_message": _(
			"This is based on transactions against this Sales Person. See timeline below for details"
		),
		"fieldname": "sales_person",
		"transactions": [
			{"label": _("Sales"), "items": ["Sales Order", "Delivery Note", "Sales Invoice"]},
		],
	}
