# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
from frappe import _


def get_data():
	return {
		"fieldname": "payment_request",
		"internal_links": {
			"Payment Entry": ["references", "payment_request"],
			"Payment Order": ["references", "payment_order"],
		},
		"transactions": [
			{"label": _("Payment"), "items": ["Payment Entry", "Payment Order"]},
		],
	}
