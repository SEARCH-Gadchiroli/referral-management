# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class CensusOccupation(Document):
	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		occupation: DF.Link
		occupation_type: DF.Literal["Main", "Secondary 1", "Secondary 2", "Secondary 3"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data

	pass
