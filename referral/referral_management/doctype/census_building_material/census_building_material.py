# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class CensusBuildingMaterial(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		material_code: DF.Link
		material_name: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		material: DF.Link
		material_type: DF.Literal["Wall", "Roof", "Floor"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data

	pass
