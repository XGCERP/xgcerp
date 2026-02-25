# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
from frappe import _


def get_data():
	return {
		"fieldname": "operation",
		"transactions": [{"label": _("Manufacture"), "items": ["BOM", "Work Order", "Job Card"]}],
	}
