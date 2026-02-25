# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
# Copyright (c) 2019


import frappe


def execute():
	frappe.delete_doc("Page", "medical_record")
