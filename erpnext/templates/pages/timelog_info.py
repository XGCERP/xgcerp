# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def get_context(context):
	context.no_cache = 1

	timelog = frappe.get_doc("Time Log", frappe.form_dict.timelog)

	context.doc = timelog
