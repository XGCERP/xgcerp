# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe

from erpnext.setup.install import setup_currency_exchange


def execute():
	frappe.reload_doc("accounts", "doctype", "currency_exchange_settings")
	setup_currency_exchange()
