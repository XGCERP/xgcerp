# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	frappe.db.set_value("Report", "Gross Profit", "add_total_row", 0)
