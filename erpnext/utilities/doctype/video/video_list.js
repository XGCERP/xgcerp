/* Copyright (c) 2026 XGC CORP. Created by Daniel Brody. All rights reserved. */
frappe.listview_settings["Video"] = {
	onload: (listview) => {
		listview.page.add_menu_item(__("Video Settings"), function () {
			frappe.set_route("Form", "Video Settings", "Video Settings");
		});
	},
};
