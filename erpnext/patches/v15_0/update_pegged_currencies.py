# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe

from erpnext.setup.install import update_pegged_currencies


def execute():
	update_pegged_currencies()
