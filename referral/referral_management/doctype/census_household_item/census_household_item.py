# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class CensusHouseholdItem(Document):
	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		item: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data

	pass
