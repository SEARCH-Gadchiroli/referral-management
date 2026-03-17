import frappe
from frappe.model.document import Document
from frappe.utils import today


class PatientReferral(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        additional_notes: DF.TextEditor | None
        census_match: DF.Link | None
        hospital_registration_number: DF.Data | None
        match_confidence: DF.Float
        match_status: DF.Literal["Unmatched", "Auto-Matched", "Multiple Matches", "Manually Verified"]
        matched_member_age: DF.Int
        matched_member_name: DF.Data | None
        opd_departments: DF.Literal["OPD 1", "OPD 2", "OPD 3", "OPD 4", "OPD 5", "OPD 6", "OPD 7", "Other"]
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
        referrer_latitude: DF.Data | None
        referrer_longitude: DF.Data | None
        referrer_phone: DF.Data
        status: DF.Literal["Pending", "Visited", "No-Show", "Cancelled"]
        tribal_classification: DF.Literal["", "Tribal", "Non-Tribal"]
        visit_date: DF.Date | None
    # end: auto-generated types

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        additional_notes: DF.TextEditor | None
        census_match: DF.Link | None
        matched_member_name: DF.Data | None
        matched_member_age: DF.Int
        hospital_registration_number: DF.Data | None
        match_confidence: DF.Float
        match_status: DF.Literal["Unmatched", "Auto-Matched", "Multiple Matches", "Manually Verified"]
        opd_departments: DF.Literal["OPD 1", "OPD 2", "OPD 3", "OPD 4", "OPD 5", "OPD 6", "OPD 7", "Other"]
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
        referrer_latitude: DF.Data | None
        referrer_longitude: DF.Data | None
        status: DF.Literal["Pending", "Visited", "No-Show", "Cancelled"]
        tribal_classification: DF.Literal["", "Tribal", "Non-Tribal"]
        village_of_reference: DF.Link
        visit_date: DF.Date | None

    def before_insert(self):
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        if not self.referral_date:
            self.referral_date = today()

    def after_insert(self):
        self.match_with_census()

    def generate_reference_number(self):
        from frappe.utils import now_datetime

        referrer_id = "REF0"
        if self.referrer:
            referrer_doc = frappe.get_doc("Referrer", self.referrer)
            referrer_id = referrer_doc.referrer_id or "REF0"

        village_code = "VLG00"
        if self.patient_village:
            village_doc = frappe.get_doc("Village Profile", self.patient_village)
            if village_doc.village_number:
                village_code = f"V{str(village_doc.village_number).zfill(4)}"

        date_str = now_datetime().strftime("%y%m%d")
        sequence = self.get_daily_sequence(date_str)
        return f"{referrer_id}-{village_code}-{date_str}-{sequence:04d}"

    def get_daily_sequence(self, date_str):
        count = frappe.db.count(
            "Patient Referral",
            filters={"reference_number": ["like", f"%{date_str}%"]}
        )
        return count + 1

    def match_with_census(self):
        """
        Match patient against Census Family Member child table records.
        Steps:
        1. Find Census Households linked to patient_village
        2. Search Census Family Members by first name + gender
        3. Refine by father name (middle name of member_name)
        4. Save matched household + member details + tribal classification
        """
        if not self.patient_village or not self.patient_name:
            self._set_unmatched()
            return

        # Parse patient first name and father name
        name_parts = self.patient_name.strip().split()
        patient_first = name_parts[0] if name_parts else ""
        # Father name from dedicated field, fallback to middle name
        father_name = self.patient_father_name.strip() if self.patient_father_name else (
            name_parts[1] if len(name_parts) > 1 else ""
        )
        patient_father_first = father_name.split()[0].lower() if father_name else ""

        # Normalize gender for Census Family Member
        # Census uses Link to Gender Master
        gender_name = frappe.db.get_value(
            "Gender Master", {"gender_name": self.patient_gender}, "name"
        )

        # Find households in patient village
        households = frappe.get_all(
            "Census Household",
            filters={"village": self.patient_village},
            fields=["name", "caste_of_head"]
        )

        if not households:
            self._set_unmatched()
            return

        household_names = [h.name for h in households]
        household_caste_map = {h.name: h.caste_of_head for h in households}

        # Search family members by first name and gender
        query = """
            SELECT
                cfm.name,
                cfm.member_name,
                cfm.age,
                cfm.gender,
                cfm.parent as household
            FROM `tabCensus Family Member` cfm
            WHERE cfm.parent IN %(households)s
            AND cfm.member_name LIKE %(first_name)s
        """
        params = {
            "households": household_names,
            "first_name": f"{patient_first}%",
        }

        # Add gender filter if we have a valid gender
        if gender_name:
            query += " AND cfm.gender = %(gender)s"
            params["gender"] = gender_name

        matched_members = frappe.db.sql(query, params, as_dict=True)

        if not matched_members:
            self._set_unmatched()
            return

        # Refine by father name (middle name of member_name)
        if patient_father_first:
            refined = [
                m for m in matched_members
                if len(m.member_name.split()) > 1 and
                m.member_name.split()[1].lower() == patient_father_first
            ]
            # If refined matches found use them, otherwise use broader matches
            final_matches = refined if refined else matched_members
        else:
            final_matches = matched_members

        # Exact match logic (First name, father name, age)
        # Note: Gender is already filtered in the SQL query
        exact_match = None
        for match in final_matches:
            m_first_name = match.member_name.split()[0].lower() if match.member_name else ""
            m_father_name = match.member_name.split()[1].lower() if len(match.member_name.split()) > 1 else ""
            
            if (
                m_first_name == patient_first.lower() and
                m_father_name == patient_father_first and
                match.age == self.patient_age
            ):
                exact_match = match
                break
        
        if exact_match:
            final_matches = [exact_match]

        if len(final_matches) == 1:
            match = final_matches[0]
            m_first_name = match.member_name.split()[0].lower() if match.member_name else ""
            m_father_name = match.member_name.split()[1].lower() if len(match.member_name.split()) > 1 else ""
            
            is_exact = (
                m_first_name == patient_first.lower() and
                m_father_name == father_name.lower() and
                match.age == self.patient_age
            )

            if is_exact:
                confidence = 100.0
                frappe.msgprint("Patient is a citizen already (Exact Census match found).", alert=True)
            else:
                confidence = 95.0 if (patient_father_first and len(
                    match.member_name.split()) > 1 and
                    match.member_name.split()[1].lower() == patient_father_first) else 70.0

            self.census_match = match.household
            self.matched_member_name = match.member_name
            self.matched_member_age = match.age or 0
            self.match_confidence = confidence
            self.match_status = "Auto-Matched"

            # Get tribal classification from caste
            caste = household_caste_map.get(match.household)
            if caste:
                is_tribal = frappe.db.get_value("Caste Master", caste, "is_tribal")
                self.tribal_classification = "Tribal" if is_tribal else "Non-Tribal"

            self.save()

        elif len(final_matches) > 1:
            self.match_status = "Multiple Matches"
            self.save()

        else:
            self._set_unmatched()

    def _set_unmatched(self):
        self.match_status = "Unmatched"
        self.save()
