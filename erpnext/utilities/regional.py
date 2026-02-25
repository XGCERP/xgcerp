# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
from contextlib import contextmanager

import frappe


@contextmanager
def temporary_flag(flag_name, value):
	flags = frappe.local.flags
	flags[flag_name] = value
	try:
		yield
	finally:
		flags.pop(flag_name, None)
