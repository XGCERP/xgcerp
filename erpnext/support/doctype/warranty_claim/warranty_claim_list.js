/* Copyright (c) 2026 XGC CORP. Created by Daniel Brody. All rights reserved. */
frappe.listview_settings["Warranty Claim"] = {
	add_fields: ["status", "customer", "item_code"],
	filters: [["status", "=", "Open"]],
};
