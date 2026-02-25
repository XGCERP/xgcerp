# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
from frappe import _


def get_data():
	return {
		"fieldname": "production_plan",
		"non_standard_fieldnames": {
			"Stock Reservation Entry": "voucher_no",
		},
		"transactions": [
			{"label": _("Transactions"), "items": ["Work Order", "Material Request"]},
			{"label": _("Subcontract"), "items": ["Purchase Order"]},
			{"label": _("Reservation"), "items": ["Stock Reservation Entry"]},
		],
	}
