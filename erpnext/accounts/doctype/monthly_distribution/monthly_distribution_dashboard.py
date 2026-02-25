# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
from frappe import _


def get_data():
	return {
		"fieldname": "monthly_distribution",
		"non_standard_fieldnames": {
			"Sales Person": "distribution_id",
			"Territory": "distribution_id",
			"Sales Partner": "distribution_id",
		},
		"transactions": [
			{"label": _("Target Details"), "items": ["Sales Person", "Territory", "Sales Partner"]},
		],
	}
