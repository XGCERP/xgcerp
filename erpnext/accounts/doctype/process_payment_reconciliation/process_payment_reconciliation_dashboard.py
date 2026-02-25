# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
from frappe import _


def get_data():
	return {
		"fieldname": "process_pr",
		"transactions": [
			{
				"label": _("Reconciliation Logs"),
				"items": [
					"Process Payment Reconciliation Log",
				],
			},
		],
	}
