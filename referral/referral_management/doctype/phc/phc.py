# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PHC(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		code: DF.Data
		district: DF.Link
		phc_name: DF.Data
		state: DF.Link
		taluka: DF.Link | None
	# end: auto-generated types

	def validate(self):
		"""Auto-fetch state from district if not set"""
		if self.district and not self.state:
			district_doc = frappe.get_doc("District", self.district)
			self.state = district_doc.state