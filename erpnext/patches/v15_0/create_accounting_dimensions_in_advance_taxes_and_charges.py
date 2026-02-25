# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	create_accounting_dimensions_for_doctype,
)


def execute():
	create_accounting_dimensions_for_doctype(doctype="Advance Taxes and Charges")
