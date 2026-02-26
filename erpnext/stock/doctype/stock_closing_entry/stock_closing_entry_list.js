/* Copyright (c) 2026 XGC CORP. Created by Daniel Brody. All rights reserved. */
frappe.listview_settings["Stock Closing Entry"] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		return [__(doc.status), frappe.utils.guess_colour(doc.status), "status,=," + doc.status];
	},
};
