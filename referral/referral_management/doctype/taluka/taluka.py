# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Taluka(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		district: DF.Link
		state: DF.Link | None
		taluka_code: DF.Data | None
		taluka_name: DF.Data
	# end: auto-generated types

	def validate(self):
		"""Auto-fetch state from district"""
		if self.district and not self.state:
			district_doc = frappe.get_doc("District", self.district)
			self.state = district_doc.state