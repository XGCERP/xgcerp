# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe
from frappe.model.utils.rename_field import rename_field


def execute():
	if frappe.db.has_column("Material Request", "price_list"):
		rename_field(
			"Material Request",
			"price_list",
			"buying_price_list",
		)
