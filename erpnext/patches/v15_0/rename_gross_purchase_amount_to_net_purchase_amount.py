# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
from frappe.model.utils.rename_field import rename_field


def execute():
	rename_field("Asset", "gross_purchase_amount", "net_purchase_amount")
	rename_field("Asset Depreciation Schedule", "gross_purchase_amount", "net_purchase_amount")
