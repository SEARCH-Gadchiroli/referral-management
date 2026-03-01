# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CowshedLocationMaster(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		cowshed_location_code: DF.Int
		cowshed_location_name: DF.Data | None
	# end: auto-generated types

	pass
