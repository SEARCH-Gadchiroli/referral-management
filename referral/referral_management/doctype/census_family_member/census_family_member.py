# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class CensusFamilyMember(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		age: DF.Int
		birth_date: DF.Data | None
		birth_id_number: DF.Data | None
		currently_studying: DF.Literal["0", "1", "2"]
		date_in_migration: DF.Date | None
		date_of_death: DF.Data | None
		date_out_migration: DF.Date | None
		education: DF.Link | None
		family_planning_operation: DF.Literal["0", "1", "2"]
		gender: DF.Literal["1", "2"]
		identification_number: DF.Int
		marital_status: DF.Link | None
		member_name: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		age: DF.Int
		birth_date: DF.Date | None
		birth_id_number: DF.Data | None
		currently_studying: DF.Literal["0", "1", "2"]
		date_in_migration: DF.Date | None
		date_of_death: DF.Date | None
		date_out_migration: DF.Date | None
		education: DF.Link | None
		family_planning_operation: DF.Literal["0", "1", "2"]
		gender: DF.Literal["Male", "Female"]
		identification_number: DF.Int
		marital_status: DF.Link | None
		member_name: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data

	pass
