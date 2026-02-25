# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
from erpnext.setup.install import create_custom_company_links


def execute():
	"""Add link fields to Company in Email Account and Communication."""
	create_custom_company_links()
