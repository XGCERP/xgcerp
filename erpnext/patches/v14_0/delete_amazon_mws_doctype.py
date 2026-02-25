# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	frappe.delete_doc("DocType", "Amazon MWS Settings", ignore_missing=True)
