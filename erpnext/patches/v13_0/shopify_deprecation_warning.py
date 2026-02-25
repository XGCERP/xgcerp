# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import click


def execute():
	click.secho(
		"Shopify Integration is moved to a separate app and will be removed from XGCERP in version-14.
"
		"Please install the app to continue using the integration: https://github.com/frappe/ecommerce_integrations",
		fg="yellow",
	)
