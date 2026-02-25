# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
def get_data():
	return {
		"fieldname": "shareholder",
		"non_standard_fieldnames": {"Share Transfer": "to_shareholder"},
		"transactions": [{"items": ["Share Transfer"]}],
	}
