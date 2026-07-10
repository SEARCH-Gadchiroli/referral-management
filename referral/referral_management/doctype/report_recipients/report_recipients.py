# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class ReportRecipients(Document):
	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		recipient_name: DF.Data
		phone: DF.Data
		report_type: DF.Literal["", "Supervisor Briefing", "OPD Manifest"]
		is_active: DF.Check

	pass
