import frappe
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

VALID_DEPARTMENTS = [
    "Orthopedics", "Spine", "Gynaecology", "Cardiology",
    "Mental Health", "General Surgeon", "Cataract Surgery", "Others"
]

# Hindi/Marathi keywords → English OPD department mapping
DEPARTMENT_KEYWORDS = {
    # Marathi / Hindi terms
    "स्त्रीरोग": "Gynaecology",
    "स्त्री रोग": "Gynaecology",
    "गायनेकॉलॉजी": "Gynaecology",
    "प्रसूती": "Gynaecology",
    "प्रसूतिशास्त्र": "Gynaecology",
    "हाडरोग": "Orthopedics",
    "अस्थिरोग": "Orthopedics",
    "ऑर्थोपेडिक्स": "Orthopedics",
    "हड्डी": "Orthopedics",
    "पाठीचा कणा": "Spine",
    "स्पाइन": "Spine",
    "मणका": "Spine",
    "रीढ़": "Spine",
    "हृदयरोग": "Cardiology",
    "कार्डिओलॉजी": "Cardiology",
    "हृदय": "Cardiology",
    "दिल": "Cardiology",
    "मानसिक आरोग्य": "Mental Health",
    "मानसिक": "Mental Health",
    "मनोविकार": "Mental Health",
    "सर्जन": "General Surgeon",
    "शल्यचिकित्सक": "General Surgeon",
    "सर्जरी": "General Surgeon",
    "जनरल सर्जन": "General Surgeon",
    "मोतीबिंदू": "Cataract Surgery",
    "मोतियाबिंद": "Cataract Surgery",
    "नेत्र": "Cataract Surgery",
    "डोळा": "Cataract Surgery",
    "इतर": "Others",
    "अन्य": "Others",
}


def is_devanagari(text: str) -> bool:
    """Check if text contains Devanagari script"""
    return any("\u0900" <= c <= "\u097F" for c in (text or ""))


def _iast_to_english(iast_text: str) -> str:
    """
    Convert IAST transliteration to common English spellings.
    Handles digraph mappings and Hindi/Marathi schwa deletion.
    Key: schwa deletion runs BEFORE vowel normalization so only
    implicit 'a' (schwa) is removed, not explicit 'ā' (long a).
    """
    import unicodedata

    # Step 1: Hindi/Marathi schwa deletion on IAST text
    # Remove trailing implicit 'a' (schwa) but NOT 'ā', 'ī', 'ū' etc.
    # In IAST: implicit schwa = 'a', explicit long vowel = 'ā'
    words = iast_text.split()
    cleaned = []
    for w in words:
        if len(w) > 1 and w[-1] == 'a' and w[-2] not in 'aeiouāīūṛ':
            w = w[:-1]
        cleaned.append(w)
    result = ' '.join(cleaned)

    # Step 2: Apply multi-char IAST → English mappings
    replacements = [
        ("kṣ", "ksh"), ("ṣ", "sh"), ("ś", "sh"),
        ("ch", "chh"), ("c", "ch"),   # IAST 'c' = ch sound
        ("jñ", "gya"),
        ("ṭ", "t"), ("ḍ", "d"), ("ṇ", "n"), ("ṅ", "ng"),
        ("ñ", "n"),
        ("ṃ", "m"), ("ḥ", "h"),
        ("ā", "a"), ("ī", "i"), ("ū", "u"),
        ("ṛ", "ri"),
        ("ai", "ai"), ("au", "au"),
        ("ē", "e"), ("ō", "o"),
    ]
    for old, new in replacements:
        result = result.replace(old, new)

    # Step 3: Remove any remaining diacritics
    normalized = unicodedata.normalize('NFD', result)
    result = ''.join(
        c for c in normalized
        if unicodedata.category(c) != 'Mn'
    )

    return result


def transliterate_to_roman(text: str) -> str:
    """
    Transliterate Devanagari text to Roman English using indic-transliteration.
    This does script-to-script conversion (preserves names like साक्षी → Sakshi)
    instead of translating meaning (which would give 'Witness').
    Falls back to original text if transliteration fails.
    """
    if not text or not is_devanagari(text):
        return text

    try:
        iast = transliterate(text, sanscript.DEVANAGARI, sanscript.IAST)
        result = _iast_to_english(iast).strip().title()
        frappe.logger().info(
            f"Transliterated '{text}' → '{result}'"
        )
        return result if result else text

    except Exception as e:
        frappe.log_error(
            f"Transliteration failed for '{text}': {str(e)}",
            "Transliteration Error"
        )
        return text


def translate_to_english(text: str) -> str:
    """
    Translate Devanagari text to English using deep-translator.
    Used for additional notes where we want meaning not transliteration.
    Falls back to original text if translation fails.
    """
    if not text or not is_devanagari(text):
        return text

    try:
        translated = GoogleTranslator(source="auto", target="en").translate(text)
        result = translated.strip() if translated else text
        frappe.logger().info(
            f"Translated '{text}' → '{result}'"
        )
        return result if result else text

    except Exception as e:
        frappe.log_error(
            f"Translation failed for '{text}': {str(e)}",
            "Translation Error"
        )
        return text


def resolve_village(village_raw: str) -> str | None:
    """
    Resolve village name to Village Profile record.
    Tries original text first, then transliterated version.
    """
    if not village_raw:
        return frappe.db.get_value("Village Profile", {}, "name")

    # Try original text exact match
    village = frappe.db.get_value(
        "Village Profile", {"village_name": village_raw}, "name"
    )
    if village:
        return village

    # Try case-insensitive match
    village = frappe.db.sql("""
        SELECT name FROM `tabVillage Profile`
        WHERE LOWER(village_name) = LOWER(%(name)s)
        LIMIT 1
    """, {"name": village_raw}, as_dict=True)
    if village:
        return village[0].name

    # Try transliterated version
    if is_devanagari(village_raw):
        transliterated = transliterate_to_roman(village_raw)
        village = frappe.db.get_value(
            "Village Profile", {"village_name": transliterated}, "name"
        )
        if village:
            return village

        # Case-insensitive on transliterated
        village = frappe.db.sql("""
            SELECT name FROM `tabVillage Profile`
            WHERE LOWER(village_name) = LOWER(%(name)s)
            LIMIT 1
        """, {"name": transliterated}, as_dict=True)
        if village:
            return village[0].name

        # Fuzzy match: schwa deletion may strip trailing 'a'/'aa'
        # so try LIKE match (e.g. "Girol" matches "Girola")
        village = frappe.db.sql("""
            SELECT name FROM `tabVillage Profile`
            WHERE LOWER(village_name) LIKE CONCAT(LOWER(%(name)s), '%%')
            LIMIT 1
        """, {"name": transliterated}, as_dict=True)
        if village:
            return village[0].name

    # Fallback to first village
    return frappe.db.get_value("Village Profile", {}, "name")


def resolve_phc(phc_raw: str) -> str | None:
    """
    Resolve PHC name to PHC record.
    Tries original text first, then transliterated version.
    """
    if not phc_raw:
        return frappe.db.get_value("PHC", {}, "name")

    # Try original exact match
    phc = frappe.db.get_value("PHC", {"phc_name": phc_raw}, "name")
    if phc:
        return phc

    # Try case-insensitive
    phc = frappe.db.sql("""
        SELECT name FROM `tabPHC`
        WHERE LOWER(phc_name) = LOWER(%(name)s)
        LIMIT 1
    """, {"name": phc_raw}, as_dict=True)
    if phc:
        return phc[0].name

    # Try transliterated version
    if is_devanagari(phc_raw):
        transliterated = transliterate_to_roman(phc_raw)
        phc = frappe.db.get_value("PHC", {"phc_name": transliterated}, "name")
        if phc:
            return phc

        phc = frappe.db.sql("""
            SELECT name FROM `tabPHC`
            WHERE LOWER(phc_name) = LOWER(%(name)s)
            LIMIT 1
        """, {"name": transliterated}, as_dict=True)
        if phc:
            return phc[0].name

        # Fuzzy match for schwa deletion (e.g. "Dhanor" matches "Dhanora")
        phc = frappe.db.sql("""
            SELECT name FROM `tabPHC`
            WHERE LOWER(phc_name) LIKE CONCAT(LOWER(%(name)s), '%%')
            LIMIT 1
        """, {"name": transliterated}, as_dict=True)
        if phc:
            return phc[0].name

    return frappe.db.get_value("PHC", {}, "name")


def resolve_department(dept_raw: str) -> str:
    """
    Resolve OPD department from any script to valid English option.
    Tries direct match first, then transliteration.
    """
    if not dept_raw:
        return "Others"

    cleaned = dept_raw.strip()

    # Direct match
    if cleaned in VALID_DEPARTMENTS:
        return cleaned

    # Case-insensitive match
    for dept in VALID_DEPARTMENTS:
        if dept.lower() == cleaned.lower():
            return dept

    # Check Hindi/Marathi keyword mapping
    if cleaned in DEPARTMENT_KEYWORDS:
        return DEPARTMENT_KEYWORDS[cleaned]

    # Case-insensitive keyword match
    cleaned_lower = cleaned.lower()
    for keyword, dept in DEPARTMENT_KEYWORDS.items():
        if keyword.lower() == cleaned_lower:
            return dept

    # Partial keyword match (input contains a known keyword)
    for keyword, dept in DEPARTMENT_KEYWORDS.items():
        if keyword in cleaned or cleaned in keyword:
            return dept

    # Transliterate and try again
    if is_devanagari(cleaned):
        transliterated = transliterate_to_roman(cleaned)
        if transliterated in VALID_DEPARTMENTS:
            return transliterated
        for dept in VALID_DEPARTMENTS:
            if dept.lower() == transliterated.lower():
                return dept

    return "Others"


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

        # Save raw data exactly as received (original script preserved)
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

        # Resolve referrer
        referrer = frappe.db.get_value("Referrer", {"phone": contact_phone}, "name") \
                   or frappe.db.get_value("Referrer", {}, "name")

        # Resolve PHC — handles Devanagari input
        phc = resolve_phc(selected_phc)

        # Resolve patient village — handles Devanagari input
        patient_village = resolve_village(village_raw)

        # Normalize gender
        gender_map = {"male": "Male", "female": "Female", "other": "Other"}
        patient_gender = gender_map.get(gender_raw.lower().strip(), "Other")

        # Parse age
        try:
            patient_age = int(age_raw)
        except Exception:
            patient_age = 0

        # Resolve OPD department — handles Devanagari input
        opd_dept = resolve_department(departments_raw)

        # Transliterate names to Roman English
        patient_name = transliterate_to_roman(patient_name_raw)
        father_name = transliterate_to_roman(father_name_raw)

        # Translate additional notes to English (meaning, not transliteration)
        additional_notes = translate_to_english(additional_notes_raw)

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
            "patient_name": patient_name,
            "patient_father_name": father_name,
            "patient_gender": patient_gender,
            "patient_age": patient_age,
            "patient_village": patient_village,
            "patient_phone": patient_phone_raw,
            "additional_notes": additional_notes,
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
