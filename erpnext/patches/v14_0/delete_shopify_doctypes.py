# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	frappe.delete_doc("DocType", "Shopify Settings", ignore_missing=True)
	frappe.delete_doc("DocType", "Shopify Log", ignore_missing=True)
