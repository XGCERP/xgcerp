# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	company = frappe.get_all("Company", filters={"country": "Italy"})
	if not company:
		return

	custom_fields = {
		"Sales Invoice": [
			dict(
				fieldname="type_of_document",
				label="Type of Document",
				fieldtype="Select",
				insert_after="customer_fiscal_code",
				options="
TD01
TD02
TD03
TD04
TD05
TD06
TD16
TD17
TD18
TD19
TD20
TD21
TD22
TD23
TD24
TD25
TD26
TD27",
			),
		]
	}

	create_custom_fields(custom_fields, update=True)
