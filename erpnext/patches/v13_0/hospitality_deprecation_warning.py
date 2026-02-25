# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import click


def execute():
	click.secho(
		"Hospitality domain is moved to a separate app and will be removed from XGCERP in version-14.
"
		"When upgrading to XGCERP version-14, please install the app to continue using the Hospitality domain: https://github.com/frappe/hospitality",
		fg="yellow",
	)
