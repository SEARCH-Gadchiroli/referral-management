# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class CasteMaster(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		caste_code: DF.Int
		caste_name: DF.Data
		category: DF.Data | None
		is_tribal: DF.Check
	# end: auto-generated types

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		caste_code: DF.Int
		caste_name: DF.Data
		category: DF.Data | None
		is_tribal: DF.Check

	pass
