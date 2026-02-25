# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
from frappe import _


def get_data():
	return {
		"fieldname": "cost_center",
		"reports": [{"label": _("Reports"), "items": ["Budget Variance Report", "General Ledger"]}],
	}
