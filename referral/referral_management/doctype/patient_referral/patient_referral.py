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
        census_member_id: DF.Data | None
        hospital_registration_number: DF.Data | None
        match_confidence: DF.Float
        match_status: DF.Literal["Unmatched", "Auto-Matched", "Multiple Matches", "Manually Verified"]
        matched_member_age: DF.Int
        matched_member_name: DF.Data | None
        mmu_patient_record: DF.Link | None
        opd_category: DF.Literal["", "Regular OPD", "Specialist OPD", "Cataract Surgery"]
        opd_departments: DF.Literal["Medicine", "Gynaecology", "Orthopedics", "Spine", "Surgery", "Dental", "Mental Health Clinic", "Rheumatology OPD", "Cardiology", "Dermatology", "Diabetology", "ENT", "Gastrology", "Head & Neck", "Neurology + Epilepsy", "Oncology", "Pulmonology", "Sickle Cell", "Cataract Surgery", "Ophthalmology", "Plastic Surgery", "Urology", "Pain Management OPD"]
        patient_age: DF.Int
        patient_father_name: DF.Data
        patient_gender: DF.Literal["Male", "Female", "Other"]
        patient_name: DF.Data
        patient_phone: DF.Data | None
        patient_taluka: DF.Link
        patient_village: DF.Link | None
        phc: DF.Link | None
        raw_patient_data: DF.Link | None
        reference_number: DF.Data
        referral_date: DF.Date
        referred_by_who: DF.Literal["", "MMU Doctor", "MHD counsellor", "Muktipath Karyakarta", "ASHA", "CHW", "Supervisor", "Optometrist", "MPU Physiotherapist"]
        referred_doctor: DF.Literal[
            "",
            "Dr Kunal Vidhale",
            "Dr Adhya Dubey",
            "Dr Sanjeev Kumar",
            "Dr Ashwini Shinde",
            "Dr Mrunali Chaudhari",
            "Dr Shrirang Pathak",
            "Dr Pritam Dorlikar",
            "Dr Rohini Wankhede",
            "Dr Aditya Agrawal",
            "Dr Ganesh Kudmethe",
            "Other",
        ]
        referring_doctor: DF.Data | None
        referrer: DF.Link
        referrer_latitude: DF.Data | None
        referrer_longitude: DF.Data | None
        referrer_phone: DF.Data
        status: DF.Literal["Pending", "Follow-up In Progress", "Visited", "Closed - Not Visited", "No-Show", "Cancelled"]
        tribal_classification: DF.Literal["", "Tribal", "Non-Tribal"]
        visit_date: DF.Date | None
        service_facility_type: DF.Literal["SEARCH", "Government", "Other"]
        other_facility_name: DF.Data | None
        supervisor_visits: DF.Table
        visit_count: DF.Int
        facility_visited: DF.Literal["", "SEARCH", "Government", "Other"]
    # end: auto-generated types

    def validate(self):
        if self.service_facility_type == "SEARCH" and not self.opd_departments:
            frappe.throw("OPD Department is required for SEARCH referrals")

    def before_insert(self):
        if not self.referral_date:
            self.referral_date = today()
        if not self.referral_recorded_date:
            self.referral_recorded_date = today()
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()

    def after_insert(self):
        """Preliminary auto-match on creation — exact matches get auto-saved,
        multiple matches are flagged for admin review. Also links matching MMU visits."""
        self.match_with_census()
        self.link_matching_mmu_visit()

    def generate_reference_number(self):
        from frappe.utils import getdate, today
        ref_date = getdate(self.referral_date) if self.referral_date else getdate(today())
        date_str = ref_date.strftime("%d%m%y")
        sequence = self.get_daily_sequence(date_str)
        candidate = f"{date_str}-{sequence}"
        while frappe.db.exists("Patient Referral", candidate) or frappe.db.exists("Patient Referral", {"reference_number": candidate}):
            sequence += 1
            candidate = f"{date_str}-{sequence}"
        return candidate

    def get_daily_sequence(self, date_str):
        count = frappe.db.count(
            "Patient Referral",
            filters={"reference_number": ["like", f"{date_str}-%"]}
        )
        return count + 1

    def _get_census_matches(self):
        """
        Core matching logic: find Census Family Member records matching patient.
        Returns a list of match dicts with confidence scores.
        Does NOT save anything — caller decides what to do with results.
        """
        if not self.patient_village or not self.patient_name:
            return []

        # Parse patient first name and father name
        name_parts = self.patient_name.strip().split()
        patient_first = name_parts[0] if name_parts else ""
        # Father name from dedicated field, fallback to middle name
        father_name = self.patient_father_name.strip() if self.patient_father_name else (
            name_parts[1] if len(name_parts) > 1 else ""
        )
        patient_father_first = father_name.split()[0].lower() if father_name else ""

        # Normalize gender for Census Family Member (Census uses Link to Gender Master)
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
            return []

        household_names = [h.name for h in households]
        household_caste_map = {h.name: h.caste_of_head for h in households}

        # Search family members by first name and gender
        query = """
            SELECT
                cfm.name,
                cfm.identification_number,
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
            return []

        # Compute confidence for each match
        results = []
        for m in matched_members:
            m_parts = m.member_name.split() if m.member_name else []
            m_first = m_parts[0].lower() if m_parts else ""
            m_father = m_parts[1].lower() if len(m_parts) > 1 else ""

            # Get gender display name
            gender_display = ""
            if m.gender:
                gender_display = frappe.db.get_value("Gender Master", m.gender, "gender_name") or ""

            # Get caste info
            caste = household_caste_map.get(m.household, "")

            # Compute Member ID (e.g. HH-44-149-149-1)
            id_num = m.identification_number or 1
            member_id = f"{m.household}-{id_num}"

            # Compute confidence
            first_match = (m_first == patient_first.lower())
            father_match = (patient_father_first and m_father == patient_father_first)
            age_match = (m.age == self.patient_age)

            if first_match and father_match and age_match:
                confidence = 100.0
            elif first_match and father_match:
                confidence = 95.0
            elif first_match and age_match:
                confidence = 80.0
            elif first_match:
                confidence = 70.0
            else:
                confidence = 50.0

            results.append({
                "household": m.household,
                "member_id": member_id,
                "identification_number": id_num,
                "member_name": m.member_name,
                "member_first_name": m_first.title(),
                "member_father_name": m_father.title(),
                "age": m.age or 0,
                "gender": gender_display,
                "confidence": confidence,
                "caste": caste,
            })

        # Sort by confidence descending
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results

    def match_with_census(self):
        """
        Preliminary auto-match on insert.
        - Exact match (100% confidence) → auto-save as Auto-Matched
        - Multiple matches → flag as Multiple Matches for admin review
        - No matches → Unmatched
        """
        matches = self._get_census_matches()

        if not matches:
            self._set_unmatched()
            return

        # Check for exact match (100% confidence)
        exact_matches = [m for m in matches if m["confidence"] == 100.0]

        if len(exact_matches) == 1:
            match = exact_matches[0]
            self.census_match = match["household"]
            self.census_member_id = match.get("member_id") or f"{match['household']}-{match.get('identification_number', 1)}"
            self.matched_member_name = match["member_name"]
            self.matched_member_age = match["age"]
            self.match_confidence = match["confidence"]
            self.match_status = "Auto-Matched"
            frappe.msgprint("Patient is a citizen already (Exact Census match found).", alert=True)
            self.save()

        elif len(matches) == 1:
            # Single non-exact match — auto-save but with lower confidence
            match = matches[0]
            self.census_match = match["household"]
            self.census_member_id = match.get("member_id") or f"{match['household']}-{match.get('identification_number', 1)}"
            self.matched_member_name = match["member_name"]
            self.matched_member_age = match["age"]
            self.match_confidence = match["confidence"]
            self.match_status = "Auto-Matched"
            self.save()

        else:
            # Multiple matches — flag for admin review
            self.match_status = "Multiple Matches"
            self.save()

    def _set_unmatched(self):
        self.match_status = "Unmatched"
        self.census_member_id = None
        self.save()

    def link_matching_mmu_visit(self):
        """
        Cross-links this referral with an MMU Patient Record encounter.
        Searches tabMMU Patient Record in the same village for this patient/census member
        within a 30-day window around the referral date.
        """
        if getattr(self, "mmu_patient_record", None):
            return

        patient_village = getattr(self, "patient_village", None)
        if not patient_village:
            return

        from frappe.utils import getdate, add_days, today
        referral_date = getattr(self, "referral_date", None)
        ref_date = getdate(referral_date) if referral_date else getdate(today())
        start_date = add_days(ref_date, -30)
        end_date = add_days(ref_date, 7)

        matched_mmu = None

        # 1. Search by census_member_id if available
        census_member_id = getattr(self, "census_member_id", None)
        if census_member_id:
            matched_mmu = frappe.db.sql("""
                SELECT name FROM `tabMMU Patient Record`
                WHERE census_member_id = %s
                  AND date_of_visit BETWEEN %s AND %s
                ORDER BY date_of_visit DESC LIMIT 1
            """, (census_member_id, start_date, end_date), as_dict=True)

        # 2. Search by census_match household if available
        census_match = getattr(self, "census_match", None)
        if not matched_mmu and census_match:
            matched_mmu = frappe.db.sql("""
                SELECT name FROM `tabMMU Patient Record`
                WHERE census_match = %s
                  AND date_of_visit BETWEEN %s AND %s
                ORDER BY date_of_visit DESC LIMIT 1
            """, (census_match, start_date, end_date), as_dict=True)

        # 3. Search by village and patient first name
        patient_name = getattr(self, "patient_name", None)
        if not matched_mmu and patient_name:
            patient_first = patient_name.strip().split()[0]
            matched_mmu = frappe.db.sql("""
                SELECT name FROM `tabMMU Patient Record`
                WHERE village_name = %s
                  AND patient_name LIKE %s
                  AND date_of_visit BETWEEN %s AND %s
                ORDER BY date_of_visit DESC LIMIT 1
            """, (patient_village, f"%{patient_first}%", start_date, end_date), as_dict=True)

        if matched_mmu:
            mmu_name = matched_mmu[0].name
            self.mmu_patient_record = mmu_name
            try:
                self.db_set("mmu_patient_record", mmu_name, update_modified=False)
                frappe.db.set_value("MMU Patient Record", mmu_name, "patient_referral", self.name, update_modified=False)
            except Exception:
                pass


@frappe.whitelist()
def search_census_matches(referral_name: str) -> dict:
    """
    Whitelisted API for admin to search census matches for a referral.
    Returns all potential matches for the user to choose from.
    """
    try:
        doc = frappe.get_doc("Patient Referral", referral_name)
        matches = doc._get_census_matches()

        return {
            "success": True,
            "matches": matches,
            "patient_info": {
                "name": doc.patient_name,
                "father_name": doc.patient_father_name,
                "age": doc.patient_age,
                "gender": doc.patient_gender,
                "village": doc.patient_village,
            }
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "search_census_matches Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def confirm_census_match(
    referral_name: str,
    household: str,
    member_name: str,
    member_age: int = 0,
    confidence: float = 100.0,
    member_id: str | None = None
) -> dict:
    """
    Whitelisted API for admin to confirm a selected census match.
    Sets match_status to 'Manually Verified' and computes census_member_id.
    """
    try:
        doc = frappe.get_doc("Patient Referral", referral_name)
        doc.census_match = household
        doc.matched_member_name = member_name
        doc.matched_member_age = int(member_age)
        doc.match_confidence = float(confidence)
        doc.match_status = "Manually Verified"

        if member_id:
            doc.census_member_id = member_id
        elif household and member_name:
            member = frappe.db.get_value(
                "Census Family Member",
                {"parent": household, "member_name": member_name},
                ["identification_number"],
                as_dict=True
            )
            id_num = member.identification_number if member and member.identification_number else 1
            doc.census_member_id = f"{household}-{id_num}"

        doc.save()
        doc.link_matching_mmu_visit()
        frappe.db.commit()

        return {
            "success": True,
            "message": f"Census match confirmed for {referral_name}",
            "census_member_id": doc.census_member_id
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "confirm_census_match Error")
        return {"success": False, "error": str(e)}

