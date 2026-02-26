# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class VillageMobileNetworks(Document):
	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		network: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data

	pass
