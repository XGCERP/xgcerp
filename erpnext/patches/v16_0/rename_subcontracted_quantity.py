# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe
from frappe.model.utils.rename_field import rename_field


def execute():
	if frappe.db.has_column("Purchase Order Item", "subcontracted_quantity"):
		rename_field("Purchase Order Item", "subcontracted_quantity", "subcontracted_qty")
