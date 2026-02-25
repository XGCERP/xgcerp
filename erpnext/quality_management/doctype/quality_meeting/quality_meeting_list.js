/* Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved. */
frappe.listview_settings["Quality Meeting"] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (doc.status == "Open") {
			return [__("Open"), "red", "status=,Open"];
		} else if (doc.status == "Close") {
			return [__("Close"), "green", ",status=,Close"];
		}
	},
};
