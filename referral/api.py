import frappe

VALID_DEPARTMENTS = ["Orthopedics", "Spine", "Gynaecology", "Cardiology", "Mental Health", "General Surgeon", "Cataract Surgery", "Others"]


@frappe.whitelist(allow_guest=False)
def create_referral(
    contact_phone: str,
    selected_phc: str = "",
    patient_name_raw: str = "",
    father_name_raw: str = "",
    gender_raw: str = "",
    age_raw: str = "",
    village_raw: str = "",
    departments_raw: str = "",
    additional_notes_raw: str = "",
    referrer_latitude: str = "",
    referrer_longitude: str = "",
    latitude: str = "",
    longitude: str = "",
    patient_phone_raw: str = ""
) -> dict:
    try:
        actual_lat = referrer_latitude or latitude
        actual_lon = referrer_longitude or longitude

        # Save raw data
        raw_doc = frappe.get_doc({
            "doctype": "Raw Patient Referral Data",
            "glific_contact_id": contact_phone,
            "received_at": frappe.utils.now(),
            "selected_phc": selected_phc,
            "referrer_latitude": actual_lat,
            "referrer_longitude": actual_lon,
            "patient_name_raw": patient_name_raw,
            "father_name_raw": father_name_raw,
            "gender_raw": gender_raw,
            "age_raw": age_raw,
            "village_raw": village_raw,
            "patient_phone_raw": patient_phone_raw,
            "departments_raw": departments_raw,
            "additional_notes_raw": additional_notes_raw,
        })
        raw_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Resolve referrer by phone, fallback to first
        referrer = frappe.db.get_value("Referrer", {"phone": contact_phone}, "name") \
                   or frappe.db.get_value("Referrer", {}, "name")

        # Resolve PHC
        phc = frappe.db.get_value("PHC", {"phc_name": selected_phc}, "name") \
              or frappe.db.get_value("PHC", {}, "name")

        # Resolve patient village
        patient_village = frappe.db.get_value(
            "Village Profile", {"village_name": village_raw}, "name"
        ) or frappe.db.get_value("Village Profile", {}, "name")

        # Normalize gender
        gender_map = {"male": "Male", "female": "Female", "other": "Other"}
        patient_gender = gender_map.get(gender_raw.lower().strip(), "Other")

        # Parse age
        try:
            patient_age = int(age_raw)
        except Exception:
            patient_age = 0

        # Single OPD department
        opd_dept = departments_raw.strip() if departments_raw.strip() in VALID_DEPARTMENTS else "Other"

        # Create Patient Referral
        referral_doc = frappe.get_doc({
            "doctype": "Patient Referral",
            "referral_date": frappe.utils.today(),
            "status": "Pending",
            "referrer": referrer,
            "referrer_phone": contact_phone,
            "referrer_latitude": actual_lat,
            "referrer_longitude": actual_lon,
            "phc": phc,
            "patient_name": patient_name_raw,
            "patient_father_name": father_name_raw,
            "patient_gender": patient_gender,
            "patient_age": patient_age,
            "patient_village": patient_village,
            "patient_phone": patient_phone_raw,
            "additional_notes": additional_notes_raw,
            "opd_departments": opd_dept,
            "raw_patient_data": raw_doc.name,
        })
        referral_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Link raw doc back
        raw_doc.patient_referral = referral_doc.name
        raw_doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "reference_number": referral_doc.reference_number
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_referral API Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist(allow_guest=False)
def get_referral(reference_number: str) -> dict:
    try:
        if not frappe.db.exists("Patient Referral", reference_number):
            return {
                "success": False,
                "error": f"Referral {reference_number} not found"
            }

        doc = frappe.get_doc("Patient Referral", reference_number)

        # Get related field values
        phc_name = frappe.db.get_value("PHC", doc.phc, "phc_name") if doc.phc else ""
        patient_village_name = frappe.db.get_value(
            "Village Profile", doc.patient_village, "village_name"
        ) if doc.patient_village else ""
        referrer_name = frappe.db.get_value(
            "Referrer", doc.referrer, "full_name"
        ) if doc.referrer else ""

        return {
            "success": True,
            "referral": {
                "reference_number": doc.reference_number,
                "referral_date": str(doc.referral_date),
                "status": doc.status,
                "referrer_name": referrer_name,
                "referrer_phone": doc.referrer_phone,
                "phc": phc_name,
                "patient_name": doc.patient_name,
                "patient_father_name": doc.patient_father_name,
                "patient_gender": doc.patient_gender,
                "patient_age": doc.patient_age,
                "patient_village": patient_village_name,
                "patient_phone": doc.patient_phone or "",
                "opd_department": doc.opd_departments,
                "additional_notes": doc.additional_notes or "",
                "match_status": doc.match_status,
                "tribal_classification": doc.tribal_classification or "",
            }
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_referral API Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist(allow_guest=False)
def update_registration(
    reference_number: str,
    hospital_registration_number: str = "",
    visit_date: str = ""
) -> dict:
    try:
        if not frappe.db.exists("Patient Referral", reference_number):
            return {
                "success": False,
                "error": f"Referral {reference_number} not found"
            }

        doc = frappe.get_doc("Patient Referral", reference_number)
        doc.status = "Visited"
        doc.hospital_registration_number = hospital_registration_number
        doc.visit_date = visit_date or frappe.utils.today()
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": f"Referral {reference_number} updated to Visited"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "update_registration API Error")
        return {
            "success": False,
            "error": str(e)
        }
