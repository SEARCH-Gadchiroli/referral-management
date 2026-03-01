# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class GenderMaster(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		gender_code: DF.Int
		gender_name: DF.Data | None
	# end: auto-generated types

	pass
