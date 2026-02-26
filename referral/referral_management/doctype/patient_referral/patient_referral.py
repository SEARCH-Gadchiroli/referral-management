# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class PatientReferral(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from referral_management.referral_management.doctype.referral_opd_department.referral_opd_department import ReferralOPDDepartment

		additional_notes: DF.TextEditor | None
		census_match: DF.Link | None
		hospital_registration_number: DF.Data | None
		match_confidence: DF.Float
		match_status: DF.Literal["Unmatched", "Auto-Matched", "Multiple-Matches", "Manually-Verified"]
		opd_departments: DF.Table[ReferralOPDDepartment]
		patient_age: DF.Int
		patient_father_name: DF.Data
		patient_gender: DF.Literal["Male", "Female", "Other"]
		patient_name: DF.Data
		patient_phone: DF.Data | None
		patient_village: DF.Link
		phc: DF.Link
		raw_patient_data: DF.Link | None
		reference_number: DF.Data
		referral_date: DF.Date
		referrer: DF.Link
		referrer_phone: DF.Data
		status: DF.Literal["Pending", "Visited", "No-Show", "Cancelled"]
		tribal_classification: DF.Literal["Tribal", "Non-Tribal"]
		village_of_reference: DF.Link
		visit_date: DF.Date | None
	# end: auto-generated types

	def before_insert(self):
		"""Generate reference number if not provided"""
		if not self.reference_number:
			self.reference_number = self.generate_reference_number()
		
		# Set default referral date
		if not self.referral_date:
			self.referral_date = today()
	
	def after_insert(self):
		"""Attempt census matching after creation"""
		self.match_with_census()
	
	def generate_reference_number(self):
		"""
		Generate reference number in format:
		[REFERRER_ID]-[VILLAGE_CODE]-[YYMMDD]-[SEQUENCE]
		Example: REF1-VNO01-260127-0023
		"""
		from frappe.utils import now_datetime
		
		# Get referrer ID (use first 4 chars of user name)
		referrer_id = "REF1"  # Default, can be customized based on User
		
		# Get village code
		village_code = "VNO01"  # Default
		if self.village_of_reference:
			village_doc = frappe.get_doc("Village", self.village_of_reference)
			if village_doc.code:
				village_code = village_doc.code[:5]  # Limit to 5 chars
		
		# Get date in YYMMDD format
		date_str = now_datetime().strftime("%y%m%d")
		
		# Get daily sequence number
		sequence = self.get_daily_sequence(date_str)
		
		return f"{referrer_id}-{village_code}-{date_str}-{sequence:04d}"
	
	def get_daily_sequence(self, date_str):
		"""Get next sequence number for today"""
		count = frappe.db.count(
			"Patient Referral",
			filters={
				"reference_number": ["like", f"%{date_str}%"]
			}
		)
		return count + 1
	
	def match_with_census(self):
		"""
		Attempt to match patient with census data
		Matching criteria:
		1. Exact match: Village + Full Name + Father's Name + Gender
		2. Fuzzy match: Levenshtein distance >= 85%
		"""
		if not self.patient_village or not self.patient_name:
			return
		
		# Try exact match first
		exact_matches = frappe.get_all(
			"Census Data",
			filters={
				"village": self.patient_village,
				"full_name": self.patient_name,
				"father_name": self.patient_father_name,
				"gender": self.patient_gender
			},
			fields=["name", "tribal_status"]
		)
		
		if len(exact_matches) == 1:
			# Single exact match found
			self.census_match = exact_matches[0].name
			self.match_confidence = 100.0
			self.match_status = "Auto-Matched"
			if exact_matches[0].tribal_status:
				self.tribal_classification = exact_matches[0].tribal_status
			self.save()
			return
		
		elif len(exact_matches) > 1:
			# Multiple matches - flag for manual verification
			self.match_status = "Multiple Matches"
			self.save()
			return
		
		# If no exact match, try fuzzy matching (implement later if needed)
		self.match_status = "Unmatched"
		self.save()