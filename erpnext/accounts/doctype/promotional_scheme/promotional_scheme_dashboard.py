# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
from frappe import _


def get_data():
	return {
		"fieldname": "promotional_scheme",
		"transactions": [{"label": _("Reference"), "items": ["Pricing Rule"]}],
	}
