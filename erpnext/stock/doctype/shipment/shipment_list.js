/* Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved. */
frappe.listview_settings["Shipment"] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (doc.status == "Booked") {
			return [__("Booked"), "green"];
		}
	},
};
