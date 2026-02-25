# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
from frappe import _


def get_data():
	return {
		"fieldname": "share_type",
		"transactions": [{"label": _("References"), "items": ["Share Transfer", "Shareholder"]}],
	}
