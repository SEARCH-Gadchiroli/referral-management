# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class SupervisorVisit(Document):
	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		visit_number: DF.Int
		visit_date: DF.Date
		patient_visited: DF.Check
		facility_visited: DF.Literal["", "SEARCH", "Government", "Other"]
		confirmation_date: DF.Date | None
		non_visit_reason_code: DF.Literal["", "NV-01", "NV-02", "NV-03", "NV-04", "NV-05", "NV-06", "NV-07", "NV-08"]
		non_visit_reason_text: DF.SmallText | None
		observations: DF.SmallText | None
		supervisor_phone: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data

	pass
