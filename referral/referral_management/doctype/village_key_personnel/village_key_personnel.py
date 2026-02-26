# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class VillageKeyPersonnel(Document):
	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		mobile_number: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		person_name: DF.Data | None
		role: DF.Link

	pass
