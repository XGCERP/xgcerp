# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	"""Remove barcodes field from "Copy Fields to Variants" table because barcodes must be unique"""

	settings = frappe.get_doc("Item Variant Settings")
	settings.remove_invalid_fields_for_copy_fields_in_variants()
