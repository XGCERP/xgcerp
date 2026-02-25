# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	items = []
	items = frappe.db.sql(
		"""select item_code from `tabItem` group by item_code having count(*) > 1""", as_dict=True
	)
	if items:
		for item in items:
			frappe.db.sql("""update `tabItem` set item_code=name where item_code = %s""", (item.item_code))
