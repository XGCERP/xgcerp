# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	asset = frappe.qb.DocType("Asset")
	frappe.qb.update(asset).set(asset.asset_quantity, 1).where(asset.asset_quantity == 0).run()
