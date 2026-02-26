# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class RawPatientReferralData(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		additional_notes_raw: DF.LongText | None
		age_raw: DF.Data | None
		departments_raw: DF.Link | None
		father_name_raw: DF.Data | None
		gender_raw: DF.Data | None
		glific_contact_id: DF.Data | None
		patient_name_raw: DF.Data | None
		patient_referral: DF.Link | None
		received_at: DF.Datetime | None
		referrer_village: DF.Data | None
		selected_phc: DF.Data | None
		village_raw: DF.Data | None
	# end: auto-generated types

	pass
