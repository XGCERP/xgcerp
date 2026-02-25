/* Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved. */
// Copyright (c) 2016, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Party Type", {
	setup: function (frm) {
		frm.fields_dict["party_type"].get_query = function (frm) {
			return {
				filters: {
					istable: 0,
					is_submittable: 0,
				},
			};
		};
	},
});
