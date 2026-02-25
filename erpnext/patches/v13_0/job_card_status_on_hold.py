# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import frappe


def execute():
	job_cards = frappe.get_all(
		"Job Card",
		{"status": "On Hold", "docstatus": ("!=", 0)},
		pluck="name",
	)

	for idx, job_card in enumerate(job_cards):
		try:
			doc = frappe.get_doc("Job Card", job_card)
			doc.set_status()
			doc.db_set("status", doc.status, update_modified=False)
			if idx % 100 == 0:
				frappe.db.commit()
		except Exception:
			continue
