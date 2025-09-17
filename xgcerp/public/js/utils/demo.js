frappe.provide("xgcerp.demo");

$(document).on("toolbar_setup", function () {
	if (frappe.boot.sysdefaults.demo_company) {
		render_clear_demo_action();
	}
});

function render_clear_demo_action() {
	let demo_action = $(
		`<a class="dropdown-item" onclick="return xgcerp.demo.clear_demo()">
			${__("Clear Demo Data")}
		</a>`
	);

	demo_action.appendTo($("#toolbar-user"));
}

xgcerp.demo.clear_demo = function () {
	frappe.confirm(__("Are you sure you want to clear all demo data?"), () => {
		frappe.call({
			method: "xgcerp.setup.demo.clear_demo_data",
			freeze: true,
			freeze_message: __("Clearing Demo Data..."),
			callback: function (r) {
				frappe.ui.toolbar.clear_cache();
				frappe.show_alert({
					message: __("Demo data cleared"),
					indicator: "green",
				});
			},
		});
	});
};
