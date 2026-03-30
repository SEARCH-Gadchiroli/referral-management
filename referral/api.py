import frappe
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

VALID_DEPARTMENTS = [
    "Orthopedics", "Spine", "Surgery", "Medicine",
    "Gynaecology", "Oncology", "Sickle Cell", "Diabetology",
    "Cardiology", "ENT", "Head & Neck", "Gastrology",
    "Dermatology", "Psychiatry", "Mental Health Clinic", "Dental",
    "Cataract Surgery", "Ophthalmology", "Rheumatology", "Epilepsy",
    "Neurology", "Urology", "Plastic Surgery", "Pulmonology",
    "Others"
]

# Hindi/Marathi keywords → English OPD department mapping
DEPARTMENT_KEYWORDS = {
    # Gynaecology
    "स्त्रीरोग": "Gynaecology",
    "स्त्री रोग": "Gynaecology",
    "गायनेकॉलॉजी": "Gynaecology",
    "प्रसूती": "Gynaecology",
    "प्रसूतिशास्त्र": "Gynaecology",
    # Orthopedics
    "हाडरोग": "Orthopedics",
    "अस्थिरोग": "Orthopedics",
    "ऑर्थोपेडिक्स": "Orthopedics",
    "हड्डी": "Orthopedics",
    # Spine
    "पाठीचा कणा": "Spine",
    "स्पाइन": "Spine",
    "मणका": "Spine",
    "रीढ़": "Spine",
    # Cardiology
    "हृदयरोग": "Cardiology",
    "कार्डिओलॉजी": "Cardiology",
    "हृदय": "Cardiology",
    "दिल": "Cardiology",
    # Mental Health Clinic
    "मानसिक आरोग्य": "Mental Health Clinic",
    "मानसिक": "Mental Health Clinic",
    "मनोविकार": "Mental Health Clinic",
    # Surgery
    "सर्जन": "Surgery",
    "शल्यचिकित्सक": "Surgery",
    "सर्जरी": "Surgery",
    "जनरल सर्जन": "Surgery",
    "शस्त्रक्रिया": "Surgery",
    # Cataract Surgery
    "मोतीबिंदू": "Cataract Surgery",
    "मोतियाबिंद": "Cataract Surgery",
    # Ophthalmology
    "नेत्र": "Ophthalmology",
    "डोळा": "Ophthalmology",
    "नेत्रविज्ञान": "Ophthalmology",
    # ENT
    "कान नाक घसा": "ENT",
    "कान": "ENT",
    # Dermatology
    "त्वचा": "Dermatology",
    "त्वचारोग": "Dermatology",
    "चर्मरोग": "Dermatology",
    # Dental
    "दंत": "Dental",
    "दात": "Dental",
    "दंतचिकित्सा": "Dental",
    # Psychiatry
    "मानसोपचार": "Psychiatry",
    "मनोचिकित्सा": "Psychiatry",
    # Oncology
    "कर्करोग": "Oncology",
    "ऑन्कोलॉजी": "Oncology",
    # Sickle Cell
    "सिकल सेल": "Sickle Cell",
    "विकृतिरक्तकोशिका": "Sickle Cell",
    # Diabetology
    "मधुमेह": "Diabetology",
    # Gastrology
    "पोट": "Gastrology",
    "जठर": "Gastrology",
    "पोटरोग": "Gastrology",
    # Pulmonology
    "फुफ्फुस": "Pulmonology",
    "श्वसन": "Pulmonology",
    # Head & Neck
    "डोके आणि मान": "Head & Neck",
    # Rheumatology
    "संधिवात": "Rheumatology",
    "सांधेदुखी": "Rheumatology",
    # Epilepsy
    "अपस्मार": "Epilepsy",
    "मिरगी": "Epilepsy",
    "फेफरे": "Epilepsy",
    # Neurology
    "मज्जातंतू": "Neurology",
    "न्यूरोलॉजी": "Neurology",
    # Urology
    "मूत्ररोग": "Urology",
    "यूरोलॉजी": "Urology",
    # Plastic Surgery
    "प्लास्टिक सर्जरी": "Plastic Surgery",
    # Medicine
    "औषध": "Medicine",
    "मेडिसिन": "Medicine",
    # Others
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
    Tries: original text, Marathi name, transliterated, case-insensitive, fuzzy.
    Returns None if no match found (never falls back to a random village).
    """
    if not village_raw:
        frappe.logger().warning("Village name is empty — leaving unset")
        return None

    village_raw = village_raw.strip()
    frappe.logger().info(f"[resolve_village] Starting search for: '{village_raw}'")

    # Try original text exact match (English or Marathi)
    village = frappe.db.get_value(
        "Village Profile", {"village_name": village_raw}, "name"
    )
    if village:
        frappe.logger().info(f"[resolve_village] Exact English match found: {village}")
        return village

    # Try by Marathi name if input is Devanagari
    if is_devanagari(village_raw):
        village = frappe.db.get_value(
            "Village Profile", {"village_name_marathi": village_raw}, "name"
        )
        if village:
            frappe.logger().info(f"[resolve_village] Exact Marathi match found: {village}")
            return village

    # Try case-insensitive match on English name
    village = frappe.db.sql("""
        SELECT name FROM `tabVillage Profile`
        WHERE LOWER(village_name) = LOWER(%(name)s)
        LIMIT 1
    """, {"name": village_raw}, as_dict=True)
    if village:
        frappe.logger().info(f"[resolve_village] Case-insensitive English match found: {village[0].name}")
        return village[0].name

    # Try transliterated version
    if is_devanagari(village_raw):
        transliterated = transliterate_to_roman(village_raw)
        frappe.logger().info(f"[resolve_village] Transliterated to: '{transliterated}'")
        if transliterated:
            village = frappe.db.get_value(
                "Village Profile", {"village_name": transliterated}, "name"
            )
            if village:
                frappe.logger().info(f"[resolve_village] Transliterated exact match found: {village}")
                return village

            # Case-insensitive on transliterated
            village = frappe.db.sql("""
                SELECT name FROM `tabVillage Profile`
                WHERE LOWER(village_name) = LOWER(%(name)s)
                LIMIT 1
            """, {"name": transliterated}, as_dict=True)
            if village:
                frappe.logger().info(f"[resolve_village] Transliterated case-insensitive match found: {village[0].name}")
                return village[0].name

            # Bidirectional fuzzy: transliterated starts with village OR village starts with transliterated
            # Also require minimum 3 chars to avoid over-matching
            if len(transliterated) >= 3:
                village = frappe.db.sql("""
                    SELECT name, village_name FROM `tabVillage Profile`
                    WHERE LOWER(village_name) LIKE CONCAT(LOWER(%(name)s), '%%')
                       OR LOWER(%(name)s) LIKE CONCAT(LOWER(village_name), '%%')
                    ORDER BY
                        ABS(CHAR_LENGTH(village_name) - CHAR_LENGTH(%(name)s)) ASC
                    LIMIT 1
                """, {"name": transliterated}, as_dict=True)
                if village:
                    frappe.logger().info(
                        f"[resolve_village] Fuzzy match: '{village_raw}' → '{transliterated}' → '{village[0].village_name}'"
                    )
                    return village[0].name

    # No match found — log available villages and return None
    all_villages = frappe.db.get_list("Village Profile", fields=["name", "village_name"])
    village_names = [v.get("village_name", v.get("name")) for v in all_villages]
    frappe.logger().warning(
        f"No village match found for '{village_raw}' (transliterated: '{transliterate_to_roman(village_raw) if is_devanagari(village_raw) else 'N/A'}') — leaving unset for manual correction. Available villages: {village_names[:10]}"
    )
    return None


def resolve_phc(phc_raw: str) -> str | None:
    """
    Resolve PHC name to PHC record.
    Tries: original text, Marathi name, transliterated, case-insensitive, fuzzy.
    Returns None if no match found (never falls back to a random PHC).
    """
    if not phc_raw:
        frappe.logger().warning("PHC name is empty — leaving unset")
        return None

    phc_raw = phc_raw.strip()
    frappe.logger().info(f"[resolve_phc] Starting search for: '{phc_raw}'")

    # Try original exact match (English or Marathi)
    phc = frappe.db.get_value("PHC", {"phc_name": phc_raw}, "name")
    if phc:
        frappe.logger().info(f"[resolve_phc] Exact English match found: {phc}")
        return phc

    # Try by Marathi name if input is Devanagari
    if is_devanagari(phc_raw):
        phc = frappe.db.get_value(
            "PHC", {"phc_name_marathi": phc_raw}, "name"
        )
        if phc:
            frappe.logger().info(f"[resolve_phc] Exact Marathi match found: {phc}")
            return phc

    # Try case-insensitive on English name
    phc = frappe.db.sql("""
        SELECT name FROM `tabPHC`
        WHERE LOWER(phc_name) = LOWER(%(name)s)
        LIMIT 1
    """, {"name": phc_raw}, as_dict=True)
    if phc:
        frappe.logger().info(f"[resolve_phc] Case-insensitive English match found: {phc[0].name}")
        return phc[0].name

    # Try transliterated version
    if is_devanagari(phc_raw):
        transliterated = transliterate_to_roman(phc_raw)
        frappe.logger().info(f"[resolve_phc] Transliterated to: '{transliterated}'")
        if transliterated:
            phc = frappe.db.get_value("PHC", {"phc_name": transliterated}, "name")
            if phc:
                frappe.logger().info(f"[resolve_phc] Transliterated exact match found: {phc}")
                return phc

            phc = frappe.db.sql("""
                SELECT name FROM `tabPHC`
                WHERE LOWER(phc_name) = LOWER(%(name)s)
                LIMIT 1
            """, {"name": transliterated}, as_dict=True)
            if phc:
                frappe.logger().info(f"[resolve_phc] Transliterated case-insensitive match found: {phc[0].name}")
                return phc[0].name

            # Bidirectional fuzzy match
            if len(transliterated) >= 3:
                phc = frappe.db.sql("""
                    SELECT name FROM `tabPHC`
                    WHERE LOWER(phc_name) LIKE CONCAT(LOWER(%(name)s), '%%')
                       OR LOWER(%(name)s) LIKE CONCAT(LOWER(phc_name), '%%')
                    ORDER BY
                        ABS(CHAR_LENGTH(phc_name) - CHAR_LENGTH(%(name)s)) ASC
                    LIMIT 1
                """, {"name": transliterated}, as_dict=True)
                if phc:
                    frappe.logger().info(
                        f"[resolve_phc] Fuzzy match: '{phc_raw}' → '{transliterated}' → '{phc[0].phc_name}'"
                    )
                    return phc[0].name

    # No match found — log available PHCs and return None
    all_phcs = frappe.db.get_list("PHC", fields=["name", "phc_name"])
    phc_names = [p.get("phc_name", p.get("name")) for p in all_phcs]
    frappe.logger().warning(
        f"No PHC match found for '{phc_raw}' (transliterated: '{transliterate_to_roman(phc_raw) if is_devanagari(phc_raw) else 'N/A'}') — leaving unset for manual correction. Available PHCs: {phc_names}"
    )
    return None


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

        # Normalize gender — supports English, Marathi, Hindi
        gender_map = {
            # English
            "male": "Male", "female": "Female", "other": "Other",
            "m": "Male", "f": "Female",
            # Marathi / Hindi
            "पुरुष": "Male", "पु": "Male",
            "स्त्री": "Female", "महिला": "Female",
            "इतर": "Other", "अन्य": "Other",
        }
        gender_clean = gender_raw.strip()
        patient_gender = gender_map.get(gender_clean.lower(), None)
        if not patient_gender:
            # Try the raw string as-is (may be Devanagari not lowerable meaningfully)
            patient_gender = gender_map.get(gender_clean, None)
        if not patient_gender:
            # Try transliterating Devanagari to English and re-matching
            if is_devanagari(gender_clean):
                gender_transliterated = transliterate_to_roman(gender_clean).lower()
                patient_gender = gender_map.get(gender_transliterated, "Other")
            else:
                patient_gender = "Other"

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
            "phc": phc or "",
            "patient_name": patient_name,
            "patient_father_name": father_name,
            "patient_gender": patient_gender,
            "patient_age": patient_age,
            "patient_village": patient_village or "",
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


@frappe.whitelist()
def translate_villages_to_marathi():
    """
    Translate all Village Profile names from English to Marathi using Google Translate.
    Requires System Manager role.
    """
    frappe.only_for("System Manager")
    
    print("\n" + "="*70)
    print("TRANSLATING VILLAGES TO MARATHI")
    print("="*70 + "\n")
    
    try:
        # Get all villages
        villages = frappe.db.get_list("Village Profile", fields=["name", "village_name"])
        total = len(villages)
        
        if total == 0:
            print("No villages found in the database.")
            return {"success": True, "message": "No villages found"}
        
        print(f"Found {total} villages to translate.\n")
        
        translated = 0
        failed = 0
        skipped = 0
        results = []
        
        for idx, v in enumerate(villages, 1):
            try:
                village_name = v.get("village_name")
                existing_marathi = frappe.db.get_value(
                    "Village Profile", 
                    v.get("name"), 
                    "village_name_marathi"
                )
                
                # Skip if already has Marathi translation
                if existing_marathi:
                    msg = f"[{idx}/{total}] {village_name}: SKIPPED (already has Marathi)"
                    print(msg)
                    results.append(msg)
                    skipped += 1
                    continue
                
                # Translate to Marathi
                try:
                    marathi = GoogleTranslator(source="en", target="mr").translate(village_name)
                except Exception as trans_err:
                    msg = f"[{idx}/{total}] {village_name}: TRANSLATION ERROR - {str(trans_err)}"
                    print(msg)
                    results.append(msg)
                    failed += 1
                    continue
                
                if marathi and marathi != village_name:
                    # Update the village
                    frappe.db.set_value(
                        "Village Profile", 
                        v.get("name"), 
                        "village_name_marathi", 
                        marathi
                    )
                    msg = f"[{idx}/{total}] {village_name:30} → {marathi}"
                    print(msg)
                    results.append(msg)
                    translated += 1
                else:
                    msg = f"[{idx}/{total}] {village_name}: FAILED (translation same as input)"
                    print(msg)
                    results.append(msg)
                    failed += 1
                    
            except Exception as e:
                msg = f"[{idx}/{total}] {village_name}: ERROR - {str(e)}"
                print(msg)
                results.append(msg)
                failed += 1
        
        # Commit all changes
        frappe.db.commit()
        
        summary = f"\n{'='*70}\nTRANSLATION COMPLETE\n{'='*70}\n  Translated: {translated}\n  Skipped: {skipped}\n  Failed: {failed}\n  Total: {total}\n"
        print(summary)
        results.append(summary)
        
        return {
            "success": True,
            "translated": translated,
            "skipped": skipped,
            "failed": failed,
            "total": total,
            "results": results
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Village Translation Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def add_phcs_with_marathi():
    """
    Add new PHCs (Murumgaon, Rangi, Karwafa, Pendhri, Godalwahi, Other) with Marathi names.
    Requires System Manager role.
    """
    frappe.only_for("System Manager")
    
    print("\n" + "="*70)
    print("ADDING NEW PHCs")
    print("="*70 + "\n")
    
    phcs_data = [
        {
            "phc_name": "Murumgaon",
            "phc_name_marathi": "मुरुमगाव",
            "code": "PHC_001"
        },
        {
            "phc_name": "Rangi",
            "phc_name_marathi": "रंगी",
            "code": "PHC_002"
        },
        {
            "phc_name": "Karwafa",
            "phc_name_marathi": "करवाफा",
            "code": "PHC_003"
        },
        {
            "phc_name": "Pendhri",
            "phc_name_marathi": "पेंढरी",
            "code": "PHC_004"
        },
        {
            "phc_name": "Godalwahi",
            "phc_name_marathi": "गोदलवाही",
            "code": "PHC_005"
        },
        {
            "phc_name": "Other",
            "phc_name_marathi": "इतर",
            "code": "PHC_006"
        }
    ]
    
    results = []
    added = 0
    skipped = 0
    failed = 0
    
    try:
        for idx, phc_data in enumerate(phcs_data, 1):
            try:
                # Check if PHC already exists
                existing = frappe.db.get_value("PHC", {"phc_name": phc_data["phc_name"]})
                if existing:
                    msg = f"[{idx}/{len(phcs_data)}] {phc_data['phc_name']}: SKIPPED (already exists)"
                    print(msg)
                    results.append(msg)
                    skipped += 1
                    continue
                
                # Create new PHC  
                phc_doc = frappe.get_doc({
                    "doctype": "PHC",
                    "phc_name": phc_data["phc_name"],
                    "phc_name_marathi": phc_data["phc_name_marathi"],
                    "code": phc_data["code"],
                    "state": "Maharashtra",
                    "district": "Gadchiroli"
                })
                phc_doc.insert(ignore_permissions=True)
                msg = f"[{idx}/{len(phcs_data)}] {phc_data['phc_name']:20} → {phc_data['phc_name_marathi']:15} ✓"
                print(msg)
                results.append(msg)
                added += 1
                
            except Exception as e:
                msg = f"[{idx}/{len(phcs_data)}] {phc_data['phc_name']}: ERROR - {str(e)}"
                print(msg)
                results.append(msg)
                failed += 1
        
        frappe.db.commit()
        
        summary = f"\n{'='*70}\nPHCS ADDED SUCCESSFULLY\n{'='*70}\n  Added: {added}\n  Skipped: {skipped}\n  Failed: {failed}\n  Total: {len(phcs_data)}\n"
        print(summary)
        results.append(summary)
        
        return {
            "success": True,
            "added": added,
            "skipped": skipped,
            "failed": failed,
            "total": len(phcs_data),
            "results": results
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Add PHCs Error")
        return {
            "success": False,
            "error": str(e)
        }
