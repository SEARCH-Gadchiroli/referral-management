import frappe
from collections import defaultdict
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from frappe.utils import getdate, today, cint
from frappe import _

VALID_DEPARTMENTS = [
    "Medicine", "Gynaecology", "Orthopedics", "Spine",
    "Surgery", "Dental", "Mental Health Clinic", "Rheumatology OPD",
    "Cardiology", "Dermatology", "Diabetology", "ENT",
    "Gastrology", "Head & Neck", "Neurology + Epilepsy", "Oncology",
    "Pulmonology", "Sickle Cell", "Cataract Surgery", "Ophthalmology",
    "Plastic Surgery", "Urology", "Pain Management OPD", "Physiotherapy",
    "Others", "Other"
]

REGULAR_OPD_DEPTS = ["Medicine", "Gynaecology", "Orthopedics", "Spine", "Surgery", "Dental", "Mental Health Clinic", "Pain Management OPD", "Rheumatology OPD", "Physiotherapy", "Others", "Other"]
SPECIALIST_OPD_DEPTS = ["Cardiology", "Dermatology", "Diabetology", "ENT", "Gastrology", "Head & Neck", "Neurology + Epilepsy", "Oncology", "Pulmonology", "Sickle Cell", "Plastic Surgery", "Urology", "Pain Management OPD", "Rheumatology OPD", "Others", "Other"]
CATARACT_SURGERY_DEPTS = ["Cataract Surgery", "Ophthalmology", "Plastic Surgery", "Urology", "Pain Management OPD", "Others", "Other"]
SURGICAL_OPD_DEPTS = CATARACT_SURGERY_DEPTS  # Backward compatibility alias

# Hindi/Marathi keywords → English OPD department mapping
DEPARTMENT_KEYWORDS = {
    # Backward-compatible English aliases
    "Epilepsy": "Neurology + Epilepsy",
    "Neurology": "Neurology + Epilepsy",
    "Psychiatry": "Mental Health Clinic",
    "Mental Health Clinic": "Mental Health Clinic",
    "Pain Clinic": "Pain Management OPD",
    "Pain Management": "Pain Management OPD",
    "Pain Management OPD": "Pain Management OPD",
    "Rheumatology": "Rheumatology OPD",
    "Rheumatology OPD": "Rheumatology OPD",
    "Gastroenterology": "Gastrology",
    # Gynaecology
    "स्त्रीरोग": "Gynaecology",
    "स्त्री रोग": "Gynaecology",
    "गायनेकॉलॉजी": "Gynaecology",
    "प्रसूती": "Gynaecology",
    "प्रसूतिशास्त्र": "Gynaecology",
    "प्रसूतिशास्र": "Gynaecology",
    "प्रसूति शास्त्र": "Gynaecology",
    "स्त्रीरोगशास्त्र": "Gynaecology",
    # Orthopedics
    "हाडरोग": "Orthopedics",
    "अस्थिरोग": "Orthopedics",
    "ऑर्थोपेडिक्स": "Orthopedics",
    "हड्डी": "Orthopedics",
    "हड्डी रोग": "Orthopedics",
    # Spine
    "पाठीचा कणा": "Spine",
    "स्पाइन": "Spine",
    "मणका": "Spine",
    "रीढ़": "Spine",
    "रीढ़ की हड्डी": "Spine",
    # Cardiology
    "हृदयरोग": "Cardiology",
    "कार्डिओलॉजी": "Cardiology",
    "हृदय": "Cardiology",
    "दिल": "Cardiology",
    "हृदयरोगशास्त्र": "Cardiology",
    "कार्डियलजी": "Cardiology",
    # Mental Health / Psychiatry
    "मानसिक आरोग्य": "Mental Health Clinic",
    "मानसिक": "Mental Health Clinic",
    "मनोविकार": "Mental Health Clinic",
    "मानसोपचार": "Mental Health Clinic",
    "मनोचिकित्सा": "Mental Health Clinic",
    "मानसिक आरोग्य (२ दिवस)": "Mental Health Clinic",
    "मानसिक आरोग्य (2 दिवस)": "Mental Health Clinic",
    "मानसिक स्वास्थ्य (2 दिन)": "Mental Health Clinic",
    "मानसिक स्वास्थ्य (२ दिन)": "Mental Health Clinic",
    "मानसिक स्वास्थ्य": "Mental Health Clinic",
    # Surgery
    "सर्जन": "Surgery",
    "शल्यचिकित्सक": "Surgery",
    "सर्जरी": "Surgery",
    "जनरल सर्जन": "Surgery",
    "शस्त्रक्रिया": "Surgery",
    "शल्य चिकित्सा": "Surgery",
    # Cataract Surgery
    "मोतीबिंदू": "Cataract Surgery",
    "मोतियाबिंद": "Cataract Surgery",
    "मोतीबिंदू शस्त्रक्रिया": "Cataract Surgery",
    "मोतियाबिंद सर्जरी": "Cataract Surgery",
    # Ophthalmology
    "नेत्र": "Ophthalmology",
    "डोळा": "Ophthalmology",
    "नेत्रविज्ञान": "Ophthalmology",
    # ENT
    "कान नाक घसा": "ENT",
    "कान": "ENT",
    "ईएनटी": "ENT",
    # Dermatology
    "त्वचा": "Dermatology",
    "त्वचारोग": "Dermatology",
    "चर्मरोग": "Dermatology",
    "त्वचा विज्ञान": "Dermatology",
    # Dental
    "दंत": "Dental",
    "दात": "Dental",
    "दंतचिकित्सा": "Dental",
    "दंतचिकित्सा (३ दिवस)": "Dental",
    "दंतचिकित्सा (3 दिवस)": "Dental",
    "दंत चिकित्सा (3 दिन)": "Dental",
    "दंत चिकित्सा (३ दिन)": "Dental",
    "दंत चिकित्सा": "Dental",
    # Oncology
    "कर्करोग": "Oncology",
    "ऑन्कोलॉजी": "Oncology",
    "कैंसर विज्ञान": "Oncology",
    # Sickle Cell
    "सिकल सेल": "Sickle Cell",
    "सिकल सेल ओपीडी": "Sickle Cell",
    "सिकल सेल opd": "Sickle Cell",
    "सिकलसेल ओपीडी": "Sickle Cell",
    "सिकलसेल": "Sickle Cell",
    "sickle cell opd": "Sickle Cell",
    "sickle cell": "Sickle Cell",
    "विकृतिरक्तकोशिका": "Sickle Cell",
    # Diabetology
    "मधुमेह": "Diabetology",
    "डायाबैटोलोजी": "Diabetology",
    "मधुमेहशास्त्र": "Diabetology",
    # Gastrology
    "पोट": "Gastrology",
    "जठर": "Gastrology",
    "पोटरोग": "Gastrology",
    "गॅस्ट्रोएन्टेरोलॉजी": "Gastrology",
    "गैस्ट्रोएंटरोलॉजी": "Gastrology",
    # Pulmonology
    "फुफ्फुस": "Pulmonology",
    "श्वसन": "Pulmonology",
    "फुफ्फुसशास्त्र": "Pulmonology",
    "फुफ्फुसविज्ञान": "Pulmonology",
    # Head & Neck
    "डोके आणि मान": "Head & Neck",
    "सिर और गर्दन": "Head & Neck",
    # Rheumatology
    "संधिवात": "Rheumatology OPD",
    "सांधेदुखी": "Rheumatology OPD",
    "रुमॅटोलॉजी": "Rheumatology OPD",
    "रुमॅटोलॉजी ओपीडी": "Rheumatology OPD",
    "संधिवातीयशास्त्र": "Rheumatology OPD",
    "रुमेटोलॉजी ओपीडी": "Rheumatology OPD",
    # Neurology + Epilepsy
    "अपस्मार": "Neurology + Epilepsy",
    "मिरगी": "Neurology + Epilepsy",
    "फेफरे": "Neurology + Epilepsy",
    "मज्जातंतू": "Neurology + Epilepsy",
    "न्यूरोलॉजी": "Neurology + Epilepsy",
    "तंत्रिका विज्ञान + मिर्ग": "Neurology + Epilepsy",
    "न्यूरोलॉजी + एपिलेप्सी": "Neurology + Epilepsy",
    # Urology
    "मूत्ररोग": "Urology",
    "यूरोलॉजी": "Urology",
    "उरोलोजि": "Urology",
    "मूत्रविज्ञान": "Urology",
    # Plastic Surgery
    "प्लास्टिक सर्जरी": "Plastic Surgery",
    # Pain Management
    "वेदना": "Pain Management OPD",
    "दुखणे": "Pain Management OPD",
    "दर्द": "Pain Management OPD",
    "पेन": "Pain Management OPD",
    "वेदना व्यवस्थापन": "Pain Management OPD",
    "वेदना व्यवस्थापन ओपीडी": "Pain Management OPD",
    "दर्द प्रबंधन": "Pain Management OPD",
    "दर्द प्रबंधन ओपीडी": "Pain Management OPD",
    "Physiotherapy": "Physiotherapy",
    "फिजिओथेरपी": "Physiotherapy",
    "फिजियोथेरेपी": "Physiotherapy",
    # Medicine
    "औषध": "Medicine",
    "मेडिसिन": "Medicine",
    "दवा": "Medicine",
    # Others
    "इतर": "Others",
    "अन्य": "Others",
}


VILLAGE_MATCH_CACHE_TTL_SECONDS = 600

VILLAGE_MESSAGES = {
    "village_empty": {
        "en": "Village name cannot be empty. Please try again.",
        "hi": "गाँव का नाम खाली नहीं हो सकता। कृपया पुनः प्रयास करें।",
        "mr": "गावाचे नाव रिकामे असू शकत नाही. कृपया पुन्हा प्रयत्न करा.",
    },
    "resolved": {
        "en": "Village confirmed: {name}",
        "hi": "गाँव की पुष्टि हुई: {name}",
        "mr": "गाव निश्चित केले: {name}",
    },
    "no_match_in_taluka": {
        "en": "No matching village found under this taluka. Please type the village name again:",
        "hi": "इस तालुका में यह नाम वाला कोई गाँव नहीं मिला। कृपया गाँव का नाम दोबारा टाइप करें:",
        "mr": "तुमच्या तालुक्यात या नावाचे गाव आढळले नाही. कृपया गावाचे नाव पुन्हा एकदा टाईप करा:",
    },
    "did_you_mean": {
        "en": "Do you mean one of these villages? Please reply with the correct option number:",
        "hi": "क्या आपका मतलब इनमें से कोई गाँव है? कृपया सही विकल्प नंबर के साथ जवाब दें:",
        "mr": "मला खालीलपैकी एक गाव वाटते का? कृपया योग्य पर्याय क्रमांक निवडून पाठवा:",
    },
    "none_of_these": {
        "en": "None of these - Type again",
        "hi": "इनमें से कोई नहीं - दोबारा टाइप करें",
        "mr": "यापैकी काहीही नाही (पुन्हा टाईप करा)",
    },
    "session_expired": {
        "en": "Your village list has expired. Please type the village name again.",
        "hi": "आपकी गाँव सूची समाप्त हो गई है। कृपया गाँव का नाम फिर से टाइप करें।",
        "mr": "तुमची गाव यादी कालबाह्य झाली आहे. कृपया गावाचे नाव पुन्हा टाईप करा.",
    },
}


GENDER_TRANSLATIONS = {
    "mr": {
        "Female": "स्त्री",
        "Male": "पुरुष",
        "Other": "इतर",
        "स्त्री": "स्त्री",
        "महिला": "स्त्री",
        "पुरुष": "पुरुष",
        "इतर": "इतर",
    },
    "hi": {
        "Female": "महिला",
        "Male": "पुरुष",
        "Other": "अन्य",
        "स्त्री": "महिला",
        "महिला": "महिला",
        "पुरुष": "पुरुष",
        "इतर": "अन्य",
    },
    "en": {
        "Female": "Female",
        "Male": "Male",
        "Other": "Other",
        "स्त्री": "Female",
        "महिला": "Female",
        "पुरुष": "Male",
        "इतर": "Other",
    }
}

OPD_TRANSLATIONS = {
    "mr": {
        "Medicine": "औषधशास्त्र",
        "Gynaecology": "स्त्रीरोग व प्रसूती",
        "Orthopedics": "अस्थिरोग",
        "Spine": "मणकारोग",
        "Surgery": "शस्त्रक्रिया",
        "Dental": "दंतचिकित्सा",
        "Mental Health Clinic": "मानसिक आरोग्य क्लिनिक",
        "Psychiatry": "मानसोपचार",
        "Rheumatology OPD": "संधिवात",
        "Rheumatology": "संधिवात",
        "Cardiology": "हृदयरोग",
        "Dermatology": "त्वचारोग",
        "Diabetology": "मधुमेह",
        "ENT": "कान, नाक, घसा",
        "Gastrology": "पोट व जठररोग",
        "Head & Neck": "डोके आणि मान",
        "Neurology + Epilepsy": "मेंदू व मज्जातंतू / अपस्मार",
        "Neurology": "मेंदू व मज्जातंतू",
        "Epilepsy": "अपस्मार",
        "Oncology": "कर्करोग",
        "Pulmonology": "फुफ्फुस व श्वसनरोग",
        "Sickle Cell": "सिकलसेल",
        "Cataract Surgery": "मोतीबिंदू शस्त्रक्रिया",
        "Ophthalmology": "नेत्ररोग",
        "Plastic Surgery": "प्लास्टिक सर्जरी",
        "Urology": "मूत्ररोग",
        "Pain Management OPD": "वेदना व्यवस्थापन",
        "Pain Management": "वेदना व्यवस्थापन",
        "Physiotherapy": "फिजिओथेरपी",
        "Regular OPD": "नियमित ओपीडी",
        "Specialist OPD": "तज्ञ ओपीडी",
        "Surgical OPD": "शस्त्रक्रिया ओपीडी",
        "Others": "इतर",
        "Other": "इतर"
    },
    "hi": {
        "Medicine": "औषधशास्त्र",
        "Gynaecology": "स्त्री रोग व प्रसूति",
        "Orthopedics": "हड्डी रोग",
        "Spine": "रीढ़ की हड्डी",
        "Surgery": "शल्य चिकित्सा",
        "Dental": "दंत चिकित्सा",
        "Mental Health Clinic": "मानसिक स्वास्थ्य क्लिनिक",
        "Psychiatry": "मानसिक स्वास्थ्य",
        "Rheumatology OPD": "संधिवात",
        "Rheumatology": "संधिवात",
        "Cardiology": "हृदय रोग",
        "Dermatology": "त्वचा रोग",
        "Diabetology": "मधुमेह",
        "ENT": "कान, नाक, गला",
        "Gastrology": "पेट व जठर रोग",
        "Head & Neck": "सिर और गर्दन",
        "Neurology + Epilepsy": "तंत्रिका विज्ञान / मिर्गी",
        "Neurology": "तंत्रिका विज्ञान",
        "Epilepsy": "मिर्गी",
        "Oncology": "कैंसर",
        "Pulmonology": "फेफड़े व श्वसन रोग",
        "Sickle Cell": "सिकल सेल",
        "Cataract Surgery": "मोतियाबिंद सर्जरी",
        "Ophthalmology": "नेत्र रोग",
        "Plastic Surgery": "प्लास्टिक सर्जरी",
        "Urology": "मूत्र रोग",
        "Pain Management OPD": "दर्द प्रबंधन",
        "Pain Management": "दर्द प्रबंधन",
        "Physiotherapy": "फिजियोथेरेपी",
        "Regular OPD": "नियमित ओपीडी",
        "Specialist OPD": "विशेषज्ञ ओपीडी",
        "Surgical OPD": "सर्जिकल ओपीडी",
        "Others": "अन्य",
        "Other": "अन्य"
    }
}

FACILITY_TRANSLATIONS = {
    "mr": {
        "SEARCH": "सर्च रुग्णालय",
        "SEARCH Hospital": "सर्च रुग्णालय",
        "Government Hospital": "शासकीय रुग्णालय",
        "Taluka MH Clinic": "तालुका मानसिक आरोग्य क्लिनिक",
        "Village MH Clinic": "गाव मानसिक आरोग्य क्लिनिक",
        "Other": "इतर रुग्णालय",
    },
    "hi": {
        "SEARCH": "सर्च अस्पताल",
        "SEARCH Hospital": "सर्च अस्पताल",
        "Government Hospital": "सरकारी अस्पताल",
        "Taluka MH Clinic": "तालुका मानसिक स्वास्थ्य क्लिनिक",
        "Village MH Clinic": "गाँव मानसिक स्वास्थ्य क्लिनिक",
        "Other": "अन्य अस्पताल",
    },
    "en": {
        "SEARCH": "SEARCH Hospital",
        "SEARCH Hospital": "SEARCH Hospital",
        "Government Hospital": "Government Hospital",
        "Taluka MH Clinic": "Taluka MH Clinic",
        "Village MH Clinic": "Village MH Clinic",
        "Other": "Other Hospital",
    }
}

REFERRED_BY_WHO_TRANSLATIONS = {
    "mr": {
        "MMU Doctor": "एमएमयू डॉक्टर",
        "Arogyadoot": "आरोग्यदूत",
        "ASHA": "आशा",
        "Muktipath Karyakarta": "मुक्तिपथ कार्यकर्ता",
        "MHD counsellor": "एमएचडी समुपदेशक",
        "Supervisor": "सुपरवायझर",
        "Optometrist": "नेत्र तपासणी अधिकारी",
        "MPU Physiotherapist": "फिजिओथेरपिस्ट",
        "CHW": "आरोग्यदूत",
    },
    "hi": {
        "MMU Doctor": "एमएमयू डॉक्टर",
        "Arogyadoot": "आरोग्यदूत",
        "ASHA": "आशा",
        "Muktipath Karyakarta": "मुक्तिपथ कार्यकर्ता",
        "MHD counsellor": "एमएचडी परामर्शदाता",
        "Supervisor": "सुपरवाइजर",
        "Optometrist": "नेत्र जांच अधिकारी",
        "MPU Physiotherapist": "फिजियोथेरेपिस्ट",
        "CHW": "आरोग्यदूत",
    },
    "en": {
        "MMU Doctor": "MMU Doctor",
        "Arogyadoot": "Arogyadoot",
        "ASHA": "ASHA",
        "Muktipath Karyakarta": "Muktipath Karyakarta",
        "MHD counsellor": "MHD counsellor",
        "Supervisor": "Supervisor",
        "Optometrist": "Optometrist",
        "MPU Physiotherapist": "MPU Physiotherapist",
        "CHW": "CHW",
    }
}


def village_msg(key: str, lang: str, **kwargs) -> str:
    lang = lang if lang in ("en", "hi", "mr") else "en"
    template = VILLAGE_MESSAGES[key][lang]
    return template.format(**kwargs) if kwargs else template


def village_display_name(village_name: str, lang: str) -> str:
    """Single-language display name for a Village Profile record."""
    if lang == "mr":
        v_mr = frappe.db.get_value("Village Profile", village_name, "village_name_marathi")
        return v_mr or village_name
    return village_name


def format_patient_name(name: str, raw_name: str = None, lang: str = "mr") -> str:
    """Returns patient name formatted for target language (Devanagari if mr/hi, English if en)."""
    if not name and not raw_name:
        return ""
    
    val = name or raw_name
    if lang == "en":
        if is_devanagari(val):
            return transliterate_to_roman(val)
        return val

    # Target is Devanagari (mr or hi)
    if raw_name and is_devanagari(raw_name):
        return raw_name.strip()
    if is_devanagari(val):
        return val.strip()

    # If name is in Roman script, translate/transliterate to Devanagari
    # Fallback chain: Google Translate → Google Input Tools → ITRANS (lowercased)
    try:
        translated = GoogleTranslator(source="en", target=lang).translate(val)
        if translated and translated.strip():
            return translated.strip()
    except Exception:
        pass

    # Google Input Tools — phonetically accurate for Indian names
    try:
        git_result = google_input_transliterate(val, target_lang=lang)
        if git_result:
            return git_result
    except Exception:
        pass

    # Last resort: ITRANS with lowercased input to avoid uppercase letter bugs
    # (uppercase M = anusvara, I = ī, R = ṝ in ITRANS)
    try:
        return transliterate(val.lower(), sanscript.ITRANS, sanscript.DEVANAGARI)
    except Exception:
        return val


def format_gender(gender: str, lang: str = "mr") -> str:
    """Returns localized gender string."""
    if not gender:
        return ""
    g_map = GENDER_TRANSLATIONS.get(lang, {})
    return g_map.get(str(gender).strip(), str(gender).strip())


def format_opd(opd: str, lang: str = "mr") -> str:
    """Returns localized OPD department / category name."""
    if not opd:
        return ""
    if lang == "en":
        return opd
    opd_map = OPD_TRANSLATIONS.get(lang, {})
    return opd_map.get(str(opd).strip(), str(opd).strip())


def format_facility(facility: str, other_name: str = None, lang: str = "mr") -> str:
    """Returns localized hospital / facility name."""
    if not facility:
        return other_name or ""
    if facility == "Other" and other_name:
        return other_name
    if lang == "en":
        return "SEARCH Hospital" if facility == "SEARCH" else (other_name or facility)
    fac_map = FACILITY_TRANSLATIONS.get(lang, {})
    return fac_map.get(str(facility).strip(), other_name or facility)


def format_referred_by_who(role: str, lang: str = "mr") -> str:
    """Returns localized referred_by_who role string."""
    if not role:
        return ""
    if lang == "en":
        return role
    role_map = REFERRED_BY_WHO_TRANSLATIONS.get(lang, {})
    return role_map.get(str(role).strip(), str(role).strip())


def format_age_display(age) -> str:
    """Formats age without trailing decimals (e.g. 40.0 -> '40')."""
    if age is None or age == "":
        return ""
    try:
        val = float(age)
        if val.is_integer():
            return str(int(val))
        return str(val)
    except Exception:
        return str(age)


def is_devanagari(text: str) -> bool:
    """Check if text contains Devanagari script"""
    return any("\u0900" <= c <= "\u097F" for c in (text or ""))


def google_input_transliterate(text: str, target_lang: str = "mr") -> str | None:
    """
    Use Google Input Tools API for phonetically accurate Roman → Devanagari
    transliteration. Unlike ITRANS (which treats uppercase letters as special
    diacritical markers), this handles natural English spellings of Indian names
    correctly — e.g. "Manasvini" → "मनस्विनी", "Sakshi" → "साक्षी".

    Fetches top candidates (num=8) and verifies phonetic alignment to prevent
    overzealous dictionary auto-corrections (e.g. 'maniram' -> 'मंदिरं', 'nuruti' -> 'निऋती').
    """
    import requests

    if not text or not text.strip():
        return None

    url = "https://inputtools.google.com/request"
    words = text.strip().split()
    transliterated_words = []

    for word in words:
        # Skip words that are already Devanagari
        if is_devanagari(word):
            transliterated_words.append(word)
            continue

        # Skip very short non-alpha tokens (numbers, punctuation)
        if len(word) <= 1 and not word.isalpha():
            transliterated_words.append(word)
            continue

        params = {
            "text": word.lower(),
            "itc": f"{target_lang}-t-i0-und",
            "num": 8,
            "cp": 0,
            "cs": 1,
            "ie": "utf-8",
            "oe": "utf-8",
        }
        try:
            response = requests.get(url, params=params, timeout=3)
            data = response.json()
            if data[0] == "SUCCESS" and data[1] and data[1][0] and data[1][0][1]:
                candidates = data[1][0][1]
                selected = candidates[0]
                if len(candidates) > 1:
                    try:
                        from rapidfuzz import fuzz
                        c0_roman = transliterate_to_roman(candidates[0]).lower().replace(" ", "")
                        c0_sim = fuzz.ratio(word.lower(), c0_roman)
                        # If top candidate is a solid phonetic match (>= 88%), trust Google's language model
                        if c0_sim < 88:
                            best_sim = c0_sim
                            for cand in candidates[1:]:
                                cand_roman = transliterate_to_roman(cand).lower().replace(" ", "")
                                sim = fuzz.ratio(word.lower(), cand_roman)
                                if sim > best_sim:
                                    best_sim = sim
                                    selected = cand
                    except Exception:
                        pass
                transliterated_words.append(selected)
            else:
                transliterated_words.append(word)
        except Exception:
            transliterated_words.append(word)

    result = " ".join(transliterated_words).strip()
    return result if result and is_devanagari(result) else None


def _iast_to_english(iast_text: str) -> str:
    """
    Convert IAST transliteration to common English spellings.
    Handles digraph mappings and Hindi/Marathi schwa deletion.
    Key: schwa deletion runs BEFORE vowel normalization so only
    implicit 'a' (schwa) is removed, not explicit 'ā' (long a).
    """
    import re
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

    # Convert anusvara 'ṃ' to 'm' before labials (p, b, ph, bh, v, m), otherwise 'n'
    result = re.sub(r"ṃ(?=[pbvm]|ph|bh)", "m", result)
    result = result.replace("ṃ", "n")

    # Step 2: Apply multi-char IAST → English mappings
    replacements = [
        ("kṣ", "ksh"), ("ṣ", "sh"), ("ś", "sh"),
        ("ch", "chh"), ("c", "ch"),   # IAST 'c' = ch sound
        ("jñ", "gya"),
        ("ṭ", "t"), ("ḍ", "d"), ("ṇ", "n"), ("ṅ", "ng"),
        ("ñ", "n"),
        ("ḥ", "h"),
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
    This does script-to-script conversion (preserves names like साक्षी → Sakshi).
    Ensures doctor prefix is formatted as 'Dr.'.
    """
    if not text:
        return text

    import re
    dr_pattern = r'^(dr\.|dr|da[ăāॅॉ\u0945\u0949\u0306\u0902]?\.|da[ăāॅॉ\u0945\u0949\u0306\u0902]?|डॉक्टर|डाक्टर|डॉ\.|डॉ|डाॅ\.|डाॅ|डा\.|डा|डाॉ\.|डाॉ)\s*'
    has_dr_prefix = bool(re.search(dr_pattern, text.strip(), flags=re.IGNORECASE))
    clean_name = re.sub(dr_pattern, '', text.strip(), flags=re.IGNORECASE).strip()

    if is_devanagari(clean_name):
        try:
            iast = transliterate(clean_name, sanscript.DEVANAGARI, sanscript.IAST)
            result = _iast_to_english(iast).strip().title()
        except Exception as e:
            frappe.log_error(
                f"Transliteration failed for '{clean_name}': {str(e)}",
                "Transliteration Error"
            )
            result = clean_name
    else:
        result = clean_name

    if has_dr_prefix and result:
        result = f"Dr. {result}"

    return result if result else text


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


def devanagari_skeleton(text: str) -> str:
    """
    Normalizes a Devanagari string to a phonetic skeleton for robust search matching:
    - Normalizes Marathi 'ळ' to 'ल' (common keyboard substitution)
    - Normalizes 'ष' to 'श'
    - Normalizes short/long vowels: ी/ि -> ि, ू/ु -> ु, े/ै/ो/ौ -> standardized
    - Strips anusvara (ं), visarga (ः), nukta (़), virama (्), and aa-matra (ा)
    """
    if not text:
        return ""
    t = text.replace("ळ", "ल").replace("ष", "श")
    t = t.replace("ी", "ि").replace("ू", "ु").replace("े", "ि").replace("ै", "ि").replace("ो", "ु").replace("ौ", "ु")
    for ch in ("ं", "ः", "़", "्", "ा"):
        t = t.replace(ch, "")
    return t.strip()


def resolve_village(village_raw: str, taluka: str = None) -> str | None:
    """
    Resolve village name to Village Profile record.
    Tries: original text, Marathi name, transliterated, case-insensitive, fuzzy.
    Handles both Devanagari input (from Glific chatbot) and Roman input.
    If taluka is provided, prioritizes villages in that taluka.
    Returns None if no match found (never falls back to a random village).
    """
    if not village_raw:
        frappe.logger().warning("Village name is empty — leaving unset")
        return None

    village_raw = village_raw.strip()
    frappe.logger().info(f"[resolve_village] Starting search for: '{village_raw}' (taluka: {taluka})")

    # 1. Try exact match in specified taluka first (if provided)
    if taluka:
        village = frappe.db.get_value(
            "Village Profile", {"village_name": village_raw, "taluka": taluka}, "name"
        )
        if village:
            frappe.logger().info(f"[resolve_village] Exact English match in taluka {taluka} found: {village}")
            return village

        if is_devanagari(village_raw):
            village = frappe.db.get_value(
                "Village Profile", {"village_name_marathi": village_raw, "taluka": taluka}, "name"
            )
            if village:
                frappe.logger().info(f"[resolve_village] Exact Marathi match in taluka {taluka} found: {village}")
                return village

        # Case-insensitive in specified taluka
        village = frappe.db.sql("""
            SELECT name FROM `tabVillage Profile`
            WHERE LOWER(village_name) = LOWER(%(name)s) AND taluka = %(taluka)s
            LIMIT 1
        """, {"name": village_raw, "taluka": taluka}, as_dict=True)
        if village:
            frappe.logger().info(f"[resolve_village] Case-insensitive match in taluka {taluka} found: {village[0].name}")
            return village[0].name

    # 2. Try original text exact match (English or Marathi) across all talukas
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

    # 3. Fuzzy LIKE matching on Marathi name (for Devanagari input from Glific)
    # Handles partial/variant spellings — e.g. "मेंढा" matching "मेंढाटोला"
    if is_devanagari(village_raw) and len(village_raw) >= 2:
        # Try substring match: input contained in village_name_marathi OR vice versa
        fuzzy_query = """
            SELECT name, village_name, village_name_marathi FROM `tabVillage Profile`
            WHERE village_name_marathi LIKE %(pattern)s
               OR %(raw)s LIKE CONCAT('%%', village_name_marathi, '%%')
        """
        params = {"pattern": f"%{village_raw}%", "raw": village_raw}

        if taluka:
            fuzzy_query += " AND taluka = %(taluka)s"
            params["taluka"] = taluka

        fuzzy_query += """
            ORDER BY
                CASE
                    WHEN village_name_marathi = %(raw)s THEN 0
                    WHEN village_name_marathi LIKE CONCAT(%(raw)s, '%%') THEN 1
                    WHEN village_name_marathi LIKE CONCAT('%%', %(raw)s, '%%') THEN 2
                    ELSE 3
                END,
                ABS(CHAR_LENGTH(village_name_marathi) - CHAR_LENGTH(%(raw)s)) ASC
            LIMIT 1
        """
        village = frappe.db.sql(fuzzy_query, params, as_dict=True)
        if village:
            frappe.logger().info(
                f"[resolve_village] Fuzzy Marathi match: '{village_raw}' → '{village[0].village_name}' (marathi: '{village[0].village_name_marathi}')"
            )
            return village[0].name

    # 4. Try transliterated version (Devanagari → Roman → match English village_name)
    if is_devanagari(village_raw):
        transliterated = transliterate_to_roman(village_raw)
        frappe.logger().info(f"[resolve_village] Transliterated to: '{transliterated}'")
        if transliterated:
            if taluka:
                village = frappe.db.get_value(
                    "Village Profile", {"village_name": transliterated, "taluka": taluka}, "name"
                )
                if village:
                    frappe.logger().info(f"[resolve_village] Transliterated match in taluka {taluka} found: {village}")
                    return village

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

    # 5. For Roman-script input: try Google Input Tools to get Devanagari, then match on Marathi name
    if not is_devanagari(village_raw) and len(village_raw) >= 3:
        try:
            devanagari_name = google_input_transliterate(village_raw, target_lang="mr")
            if devanagari_name:
                frappe.logger().info(f"[resolve_village] Google Input transliterated to: '{devanagari_name}'")
                # Exact Marathi match
                village = frappe.db.get_value(
                    "Village Profile", {"village_name_marathi": devanagari_name}, "name"
                )
                if village:
                    frappe.logger().info(f"[resolve_village] Google Input Marathi exact match found: {village}")
                    return village

                # Fuzzy Marathi LIKE match
                village = frappe.db.sql("""
                    SELECT name, village_name, village_name_marathi FROM `tabVillage Profile`
                    WHERE village_name_marathi LIKE %(pattern)s
                    ORDER BY ABS(CHAR_LENGTH(village_name_marathi) - CHAR_LENGTH(%(name)s)) ASC
                    LIMIT 1
                """, {"pattern": f"%{devanagari_name}%", "name": devanagari_name}, as_dict=True)
                if village:
                    frappe.logger().info(
                        f"[resolve_village] Google Input fuzzy Marathi match: '{village_raw}' → '{devanagari_name}' → '{village[0].village_name}'"
                    )
                    return village[0].name
        except Exception as e:
            frappe.logger().info(f"[resolve_village] Google Input Tools failed: {e}")

    # No match found — log available villages and return None
    all_villages = frappe.get_all("Village Profile", fields=["name", "village_name"], limit=15)
    village_names = [v.get("village_name", v.get("name")) for v in all_villages]
    frappe.logger().warning(
        f"No village match found for '{village_raw}' (transliterated: '{transliterate_to_roman(village_raw) if is_devanagari(village_raw) else 'N/A'}') — leaving unset for manual correction. Sample villages: {village_names[:10]}"
    )
    return None


def resolve_phc(phc_raw: str) -> str | None:
    """
    Resolve PHC name to PHC record.
    Tries: original text, Marathi name, transliterated, case-insensitive, fuzzy.
    If 'NA' or 'no PHC' variation, returns None.
    If 'Other' variation or no match is found for other PHC name, returns 'Other'.
    """
    if not phc_raw:
        frappe.logger().warning("PHC name is empty — leaving unset")
        return None

    phc_raw = phc_raw.strip()
    phc_lower = phc_raw.lower()
    frappe.logger().info(f"[resolve_phc] Starting search for: '{phc_raw}'")

    # 1. Handle "NA" / "No PHC" responses
    na_keywords = {
        "na", "n/a", "none", "nil", "no", "not applicable", "not available",
        "नाही", "नाही आहे", "एनए", "एन/ए"
    }
    if phc_lower in na_keywords:
        frappe.logger().info(f"[resolve_phc] Input '{phc_raw}' resolved as NA/None")
        return None

    # 2. Handle explicit "Other" / "इतर" responses
    other_keywords = {
        "other", "other phc", "इतर", "इतर पीएचसी", "इतर पी.एच.सी.", "इतर पी. एच. सी."
    }
    if phc_lower in other_keywords:
        frappe.logger().info(f"[resolve_phc] Input '{phc_raw}' resolved as 'Other'")
        return "Other"

    # 3. Try original exact match (English or Marathi)
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

    # 4. Fallback: If no match is found, but the input is not NA, it is an "Other PHC"
    if frappe.db.exists("PHC", "Other"):
        frappe.logger().info(f"[resolve_phc] No match found for '{phc_raw}'. Falling back to 'Other'")
        return "Other"

    # If even "Other" is missing from the database
    frappe.logger().warning(f"[resolve_phc] No match found and 'Other' PHC record does not exist.")
    return None


def resolve_department(dept_raw: str, opd_category: str = None) -> str | None:
    """
    Resolve OPD department from any script to valid English option.
    Tries direct match first, then transliteration.
    """
    if not dept_raw:
        return None

    cleaned = dept_raw.strip()

    resolved = None
    # Direct match
    if cleaned in VALID_DEPARTMENTS:
        resolved = cleaned

    if not resolved:
        # Case-insensitive match
        for dept in VALID_DEPARTMENTS:
            if dept.lower() == cleaned.lower():
                resolved = dept
                break

    if not resolved:
        # Check Hindi/Marathi keyword mapping
        if cleaned in DEPARTMENT_KEYWORDS:
            resolved = DEPARTMENT_KEYWORDS[cleaned]

    if not resolved:
        # Case-insensitive keyword match
        cleaned_lower = cleaned.lower()
        for keyword, dept in DEPARTMENT_KEYWORDS.items():
            if keyword.lower() == cleaned_lower:
                resolved = dept
                break

    if not resolved:
        # Partial keyword match (input contains a known keyword)
        for keyword, dept in DEPARTMENT_KEYWORDS.items():
            if keyword in cleaned or cleaned in keyword:
                resolved = dept
                break

    if not resolved:
        # Transliterate and try again
        if is_devanagari(cleaned):
            transliterated = transliterate_to_roman(cleaned)
            if transliterated in VALID_DEPARTMENTS:
                resolved = transliterated
            else:
                for dept in VALID_DEPARTMENTS:
                    if dept.lower() == transliterated.lower():
                        resolved = dept
                        break

    # Validate against OPD category if provided
    if resolved and opd_category:
        valid_depts = []
        if opd_category == "Regular OPD":
            valid_depts = REGULAR_OPD_DEPTS
        elif opd_category == "Specialist OPD":
            valid_depts = SPECIALIST_OPD_DEPTS
        elif opd_category in ("Cataract Surgery", "Surgical OPD"):
            valid_depts = CATARACT_SURGERY_DEPTS
        
        if resolved not in valid_depts:
            frappe.logger().warning(f"Resolved department '{resolved}' does not match category '{opd_category}'")
            return None

    return resolved


def resolve_opd_category(category_raw: str) -> str:
    if not category_raw:
        return ""

    cleaned = category_raw.strip().lower()
    
    # Check for Marathi/English keywords
    if "नियमित" in cleaned or "regular" in cleaned:
        return "Regular OPD"
    if "तज्ञ" in cleaned or "विशेषज्ञ" in cleaned or "specialist" in cleaned:
        return "Specialist OPD"
    if "मोतीबिंदू" in cleaned or "मोतियाबिंद" in cleaned or "cataract" in cleaned or "शस्त्रक्रिया" in cleaned or "surgical" in cleaned:
        return "Cataract Surgery"

    category_map = {
        "regular": "Regular OPD",
        "regular opd": "Regular OPD",
        "specialist": "Specialist OPD",
        "specialist opd": "Specialist OPD",
        "cataract": "Cataract Surgery",
        "cataract surgery": "Cataract Surgery",
        "surgical": "Cataract Surgery",
        "surgical opd": "Cataract Surgery",
    }
    return category_map.get(cleaned, category_raw.strip())


def resolve_referred_by_who(role_raw: str) -> str:
    if not role_raw:
        return ""
    
    cleaned = role_raw.strip().lower()
    
    # Check for keywords in Marathi/Hindi/English
    if "mmu" in cleaned or "doctor" in cleaned or "docter" in cleaned or "डॉक्टर" in cleaned:
        return "MMU Doctor"
    if "counsellor" in cleaned or "समुपदेशक" in cleaned or "परामर्शदाता" in cleaned or "mhd" in cleaned:
        return "MHD counsellor"
    if "muktipath" in cleaned or "मुक्तिपथ" in cleaned:
        return "Muktipath Karyakarta"
    if "asha" in cleaned or "आशा" in cleaned:
        return "ASHA"
    if "arogyadoot" in cleaned or "आरोग्यदूत" in cleaned:
        return "Arogyadoot"
    if "chw" in cleaned:
        return "CHW"
    if "supervisor" in cleaned or "सुपरवायझर" in cleaned or "सुपरवाइजर" in cleaned:
        return "Supervisor"
    if "optometrist" in cleaned or "ऑप्टोमेट्रिस्ट" in cleaned or "नेत्र" in cleaned:
        return "Optometrist"
    if "mpu" in cleaned or "physiotherap" in cleaned or "फिजिओथेरपिस्ट" in cleaned or "फिजियो" in cleaned:
        return "MPU Physiotherapist"
        
    return role_raw.strip()


VALID_DOCTORS = [
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
    "Other"
]


def resolve_referred_doctor(doctor_raw: str) -> str:
    if not doctor_raw:
        return ""
    
    cleaned = doctor_raw.strip()
    if is_devanagari(cleaned):
        cleaned = transliterate_to_roman(cleaned)

    cleaned_lower = cleaned.lower()
    import re
    dr_stripped = re.sub(r'^(dr\.|dr|da[ăāॅॉ\u0945\u0949\u0306\u0902]?\.|da[ăāॅॉ\u0945\u0949\u0306\u0902]?|डॉक्टर|डाक्टर|डॉ\.|डॉ|डाॅ\.|डाॅ|डा\.|डा|डाॉ\.|डाॉ)\s*', '', cleaned_lower, flags=re.IGNORECASE).strip()

    doctor_keywords = {
        "kunal": "Dr Kunal Vidhale",
        "vidhale": "Dr Kunal Vidhale",
        "adhya": "Dr Adhya Dubey",
        "dubey": "Dr Adhya Dubey",
        "sanjeev": "Dr Sanjeev Kumar",
        "kumar": "Dr Sanjeev Kumar",
        "ashwini": "Dr Ashwini Shinde",
        "shinde": "Dr Ashwini Shinde",
        "mrunali": "Dr Mrunali Chaudhari",
        "chaudhari": "Dr Mrunali Chaudhari",
        "shrirang": "Dr Shrirang Pathak",
        "pathak": "Dr Shrirang Pathak",
        "pritam": "Dr Pritam Dorlikar",
        "dorlikar": "Dr Pritam Dorlikar",
        "rohini": "Dr Rohini Wankhede",
        "wankhede": "Dr Rohini Wankhede",
        "aditya": "Dr Aditya Agrawal",
        "agrawal": "Dr Aditya Agrawal",
        "ganesh": "Dr Ganesh Kudmethe",
        "kudmethe": "Dr Ganesh Kudmethe",
        "other": "Other",
        "इतर": "Other"
    }

    for doc in VALID_DOCTORS:
        if cleaned_lower == doc.lower() or cleaned_lower == doc.lower().replace("dr ", "dr. "):
            return doc

    for kw, doc in doctor_keywords.items():
        if kw in dr_stripped or kw in cleaned_lower:
            return doc

    return "Other" if cleaned_lower in ("other", "इतर") else (f"Dr. {dr_stripped.title()}" if dr_stripped else doctor_raw.strip())


def resolve_taluka(taluka_raw: str) -> str | None:
    """
    Resolve a Glific taluka value to the Taluka doctype.
    Accepts taluka name, taluka code, or an existing document name.
    """
    if not taluka_raw:
        return None

    cleaned = taluka_raw.strip().lower()
    if not cleaned:
        return None

    # Strict map of valid Gadchiroli talukas (with English, Hindi, Marathi variants and common typos)
    taluka_map = {
        # Gadchiroli
        "gadchiroli": "Gadchiroli", "गडचिरोली": "Gadchiroli", "गड़चिरोली": "Gadchiroli",
        # Dhanora
        "dhanora": "Dhanora", "dhanura": "Dhanora", "धानोरा": "Dhanora",
        # Chamorshi
        "chamorshi": "Chamorshi", "chamorshee": "Chamorshi", "चामोर्शी": "Chamorshi",
        # Mulchera
        "mulchera": "Mulchera", "मुलचेरा": "Mulchera", "मूलचेरा": "Mulchera",
        # Desaiganj / Wadsa
        "desaiganj (wadsa)": "Desaiganj", "desaiganj(wadsa)": "Desaiganj",
        "देसाईगंज (वडसा)": "Desaiganj", "देसाईगंज(वडसा)": "Desaiganj",
        "desaiganj": "Desaiganj", "देसाईगंज": "Desaiganj", "warsa": "Desaiganj", 
        "wadsa": "Desaiganj", "वडसा": "Desaiganj", "वडसा-देसाईगंज": "Desaiganj",
        # Armori
        "armori": "Armori", "आरमोरी": "Armori",
        # Kurkheda
        "kurkheda": "Kurkheda", "कुरखेडा": "Kurkheda", "कुरखेड़ा": "Kurkheda",
        # Korchi
        "korchi": "Korchi", "कोरची": "Korchi",
        # Aheri
        "aheri": "Aheri", "अहेरी": "Aheri",
        # Sironcha
        "sironcha": "Sironcha", "सिरोंचा": "Sironcha",
        # Etapalli
        "etapalli": "Etapalli", "एटापल्ली": "Etapalli",
        # Bhamragad
        "bhamragad": "Bhamragad", "भामरागड": "Bhamragad", "भामरागढ़": "Bhamragad"
    }

    resolved = taluka_map.get(cleaned)
    if not resolved:
        # Try transliterated key lookup
        if is_devanagari(taluka_raw):
            transliterated = transliterate_to_roman(taluka_raw).strip().lower()
            resolved = taluka_map.get(transliterated)

    if resolved:
        return resolved

    # Fallback to direct DB checks (only for backward compatibility)
    if frappe.db.exists("Taluka", taluka_raw.strip()):
        return taluka_raw.strip()
    
    taluka_db = frappe.db.get_value("Taluka", {"taluka_name": taluka_raw.strip()}, "name")
    if taluka_db:
        return taluka_db

    return None


def clean_glific_value(val):
    if not val:
        return None
    val_str = str(val).strip()
    val_lower = val_str.lower()
    
    # Check for common Glific/RapidPro unresolved variable patterns
    if (
        val_lower.startswith("@contact") or 
        val_lower.startswith("contact.") or 
        val_lower.startswith("@results") or 
        val_lower.startswith("results.") or
        "contact.fields" in val_lower or
        "results." in val_lower or
        "{{" in val_str or
        "}}" in val_str
    ):
        return None
    return val_str


def parse_date(date_str):
    """Handle DD/MM/YYYY from Glific and YYYY-MM-DD from Frappe"""
    cleaned = clean_glific_value(date_str)
    if not cleaned:
        return None

    # Handle "today" / "aaj" / "आज" sent literally by Glific
    if cleaned.lower().strip() in ("today", "aaj", "आज"):
        from frappe.utils import today as frappe_today
        return getdate(frappe_today())

    # DD/MM/YYYY format from Glific
    if "/" in cleaned:
        from datetime import datetime
        try:
            return datetime.strptime(cleaned, "%d/%m/%Y").date()
        except ValueError:
            pass
            
    # DD-MM-YYYY format from Glific
    if "-" in cleaned and len(cleaned.split("-")[0]) == 2:
        from datetime import datetime
        try:
            return datetime.strptime(cleaned, "%d-%m-%Y").date()
        except ValueError:
            pass
            
    # Standard YYYY-MM-DD
    try:
        return getdate(cleaned)
    except Exception:
        return None


def parse_referral_date(date_str):
    """
    Parses the referral date received from Glific.

    Accepts:
      - 'आज' / 'aaj' / 'today'
      - ISO format (YYYY-MM-DD)
      - DD/MM/YYYY or DD-MM-YYYY — sent when referrer types an explicit date

    Raises frappe.ValidationError on invalid input.
    """
    if not date_str or date_str.strip().lower() in ("आज", "aaj", "today"):
        return getdate(today())

    date_str = date_str.strip()
    parsed = parse_date(date_str)
    if not parsed:
        frappe.throw("तारीख अवैध आहे. कृपया DD/MM/YYYY या स्वरूपात टाका.")

    return parsed


def resolve_referrer(phone_raw: str) -> str | None:
    """
    Resolve referrer by phone number, handling various formats (with/without prefix).
    Tries: 
    1. Exact match.
    2. Normalize and match last 10 digits.
    3. Return None if no match found (avoiding random fallback).
    """
    if not phone_raw:
        return None

    # 1. Exact match on raw input (preserves underscores, suffixes, etc.)
    referrer = frappe.db.get_value("Referrer", {"phone": phone_raw}, "name")
    if referrer:
        return referrer

    # Remove all non-numeric characters
    phone_clean = "".join(filter(str.isdigit, str(phone_raw)))
    if not phone_clean:
        return None

    # 2. Exact match on cleaned digits
    referrer = frappe.db.get_value("Referrer", {"phone": phone_clean}, "name")
    if referrer:
        return referrer

    # 2. Normalize to 10 digits (last 10)
    if len(phone_clean) >= 10:
        ten_digit = phone_clean[-10:]
        # Try finding a referrer whose phone is exactly these 10 digits
        referrer = frappe.db.get_value("Referrer", {"phone": ten_digit}, "name")
        if referrer:
            return referrer
            
        # Try finding a referrer whose phone ends with these 10 digits 
        # (covers cases like '91' prefix in DB or '+91' prefix in input)
        referrer = frappe.db.get_value("Referrer", {"phone": ["like", f"%{ten_digit}"]}, "name")
        if referrer:
            return referrer

    return None


def resolve_non_visit_reason(reason_input: str) -> str | None:
    if not reason_input:
        return None
    
    reason_clean = reason_input.strip()
    
    # Mapping dictionary from code/text to the standard select option
    mapping = {
        "NV-01": "Financial Constraints",
        "Financial Constraints": "Financial Constraints",
        "पैशांची अडचण": "Financial Constraints",
        "पैसे नाही": "Financial Constraints",
        "आर्थिक अडचण": "Financial Constraints",
        "आर्थिक कारण": "Financial Constraints",
        "पैसे नसणे": "Financial Constraints",
        "आर्थिक मर्यादा": "Financial Constraints",
        "वित्तीय बाधाएं": "Financial Constraints",
        
        "NV-02": "Transport Unavailable",
        "Transport Unavailable": "Transport Unavailable",
        "वाहतूक उपलब्ध नाही": "Transport Unavailable",
        "गाडी नाही": "Transport Unavailable",
        "गाडीची सोय नाही": "Transport Unavailable",
        "वाहतूक नाही": "Transport Unavailable",
        "प्रवासाची अडचण": "Transport Unavailable",
        "परिवहन अनुपलब्ध": "Transport Unavailable",
        
        "NV-03": "Fear or Anxiety",
        "Fear or Anxiety": "Fear or Anxiety",
        "भीती वाटणे": "Fear or Anxiety",
        "भीती": "Fear or Anxiety",
        "घाबरणे": "Fear or Anxiety",
        "घाबरत आहे": "Fear or Anxiety",
        "भीती किंवा चिंता": "Fear or Anxiety",
        "डर या चिंता": "Fear or Anxiety",
        
        "NV-04": "Feeling Better",
        "Feeling Better": "Feeling Better",
        "बरे वाटत आहे": "Feeling Better",
        "बरे वाटणे": "Feeling Better",
        "तब्बेत सुधारली": "Feeling Better",
        "तब्येत सुधारली": "Feeling Better",
        "आता बरे वाटत आहे": "Feeling Better",
        "सुधारणा झाली": "Feeling Better",
        "अच्छा लगना": "Feeling Better",
        
        "NV-05": "Unaware of Appointment",
        "Unaware of Appointment": "Unaware of Appointment",
        "अपॉइंटमेंट माहित नव्हती": "Unaware of Appointment",
        "माहित नव्हते": "Unaware of Appointment",
        "माहिती नव्हती": "Unaware of Appointment",
        "तारीख माहित नव्हती": "Unaware of Appointment",
        "भेटीची माहिती नाही": "Unaware of Appointment",
        "नियुक्ति से अनभिज्ञ": "Unaware of Appointment",
        
        "NV-06": "Family Objection",
        "Family Objection": "Family Objection",
        "कुटुंबाचा विरोध": "Family Objection",
        "घरी विरोध": "Family Objection",
        "घरच्यांचा विरोध": "Family Objection",
        "घरचे नाही म्हणतात": "Family Objection",
        "कौटुंबिक आक्षेप": "Family Objection",
        "पारिवारिक आपत्ति": "Family Objection",
        
        "NV-07": "Distance Too Far",
        "Distance Too Far": "Distance Too Far",
        "खूप लांब आहे": "Distance Too Far",
        "अंतर जास्त आहे": "Distance Too Far",
        "खूप लांब": "Distance Too Far",
        "जास्त अंतर": "Distance Too Far",
        "अंतर खूप जास्त आहे": "Distance Too Far",
        "दूरी बहुत अधिक है": "Distance Too Far",
        
        "NV-09": "No Time",
        "No Time": "No Time",
        "Lack of Time": "No Time",
        "No time": "No Time",
        "वेळ नाही": "No Time",
        "वेळ मिळाला नाही": "No Time",
        "वेळेचा अभाव": "No Time",
        "कामामुळे वेळ नाही": "No Time",
        "वेळ": "No Time",
        "समय नहीं": "No Time",
        "समय का अभाव": "No Time",
        "समय नहीं मिला": "No Time",
        "समय": "No Time",

        "NV-08": "Other",
        "Other": "Other",
        "Other (Specify)": "Other",
        "Other Reason": "Other",
        "इतर": "Other",
        "अन्य": "Other",
        "इतर (नमूद करा)": "Other",
        "अन्य (निर्दिष्ट करें)": "Other",
        "इतर कारण": "Other",
        "अन्य कारण": "Other"
    }
    
    # Try direct mapping
    if reason_clean in mapping:
        return mapping[reason_clean]
        
    # Try mapping by splitting by colon (e.g. "NV-01: Financial Constraints")
    if ":" in reason_clean:
        parts = [p.strip() for p in reason_clean.split(":")]
        for part in parts:
            if part in mapping:
                return mapping[part]
                
    # If no mapping found, search case-insensitively or check substring
    for key, val in mapping.items():
        if key.lower() in reason_clean.lower():
            return val
            
    # Default non-empty input to Other
    return "Other"


def resolve_patient_health_status(status_input: str) -> str | None:
    if not status_input:
        return None
        
    clean_val = status_input.strip()
    
    mapping = {
        "Fully Recovered/Cured": "Fully Recovered/Cured",
        "Fully Recovered": "Fully Recovered/Cured",
        "Cured": "Fully Recovered/Cured",
        "पूर्ण बरे झाले": "Fully Recovered/Cured",
        "बरे झाले": "Fully Recovered/Cured",
        "पूर्णपणे बरे झाले": "Fully Recovered/Cured",
        "पूर्ण बरे": "Fully Recovered/Cured",
        "बरे": "Fully Recovered/Cured",
        "पूरी तरह से ठीक हो गया": "Fully Recovered/Cured",
        
        "Under Treatment (Ongoing)": "Under Treatment (Ongoing)",
        "Under Treatment(Ongoing)": "Under Treatment (Ongoing)",
        "Under Treatment": "Under Treatment (Ongoing)",
        "Ongoing Treatment": "Under Treatment (Ongoing)",
        "उपचार सुरू आहेत": "Under Treatment (Ongoing)",
        "उपचार चालू आहेत": "Under Treatment (Ongoing)",
        "उपचार सुरू": "Under Treatment (Ongoing)",
        "चालू उपचार": "Under Treatment (Ongoing)",
        "उपचार चालू": "Under Treatment (Ongoing)",
        "उपचार सुरू आहे": "Under Treatment (Ongoing)",
        "इलाज जारी है (जारी)": "Under Treatment (Ongoing)",
        
        "Needs Further Treatment": "Needs Further Treatment",
        "Further Treatment": "Needs Further Treatment",
        "पुढील उपचारांची गरज आहे": "Needs Further Treatment",
        "पुढील उपचार": "Needs Further Treatment",
        "आणखी उपचारांची गरज": "Needs Further Treatment",
        "पुढील गरज": "Needs Further Treatment",
        "आगे के उपचार की आवश्यकता": "Needs Further Treatment",
        
        "Condition Worsened": "Condition Worsened",
        "Worsened": "Condition Worsened",
        "तब्बेत बिघडली": "Condition Worsened",
        "तब्येत बिघडली": "Condition Worsened",
        "अवस्था बिघडली": "Condition Worsened",
        "प्रकृती बिघडली": "Condition Worsened",
        "परिस्थिति अधिकच बिघडली": "Condition Worsened",
        "स्थिति और बिगड़ गई": "Condition Worsened"
    }
    
    # Try case-insensitive matching
    for key, val in mapping.items():
        if key.lower().replace(" ", "") == clean_val.lower().replace(" ", ""):
            return val
            
    # Substring check
    for key, val in mapping.items():
        if key.lower() in clean_val.lower() or clean_val.lower() in key.lower():
            return val
            
    return mapping.get(clean_val, None)


def resolve_facility_type(facility_input: str) -> str | None:
    if not facility_input:
        return None
    facility_clean = facility_input.strip().lower()
    
    if "सर्च" in facility_clean or "search" in facility_clean:
        return "SEARCH"
    if (
        "village mh" in facility_clean or 
        "village mental health" in facility_clean or 
        "गाव" in facility_clean or 
        "व्हिलेज" in facility_clean or
        "विलेज" in facility_clean
    ):
        return "Village MH Clinic"
    if "taluka mh" in facility_clean or "taluka mental health" in facility_clean or "तालुका" in facility_clean:
        return "Taluka MH Clinic"
    if "शासकीय" in facility_clean or "सरकारी" in facility_clean or "government" in facility_clean or "सरकार" in facility_clean:
        return "Government Hospital"
    if "इतर" in facility_clean or "अन्य" in facility_clean or "other" in facility_clean:
        return "Other"
        
    facility_type_map = {
        "सर्च": "SEARCH",
        "search": "SEARCH",
        "village mh clinic": "Village MH Clinic",
        "taluka mh clinic": "Taluka MH Clinic",
        "तालुका mh क्लिनिक": "Taluka MH Clinic",
        "तालुका एमएच क्लिनिक": "Taluka MH Clinic",
        "तालुका क्लिनिक": "Taluka MH Clinic",
        "गाव mh क्लिनिक": "Village MH Clinic",
        "गावातील mh क्लिनिक": "Village MH Clinic",
        "गाव क्लिनिक": "Village MH Clinic",
        "विलेज एमएच क्लिनिक": "Village MH Clinic",
        "व्हिलेज एमएच क्लिनिक": "Village MH Clinic",
        "शासकीय": "Government Hospital",
        "शासकीय रुग्णालय": "Government Hospital",
        "सरकारी": "Government Hospital",
        "सरकारी रुग्णालय": "Government Hospital",
        "सरकारी दवाखाना": "Government Hospital",
        "government hospital": "Government Hospital",
        "government": "Government Hospital",
        "इतर": "Other",
        "अन्य": "Other",
        "other": "Other",
    }
    for key, val in facility_type_map.items():
        if key.lower() == facility_clean:
            return val
    return facility_type_map.get(facility_clean, None)


transliterate_if_devanagari = transliterate_to_roman


def send_patient_notification(patient_phone: str, patient_name: str, reference_number: str, opd_department: str) -> None:
    """
    Sends referral ID notification to the patient's WhatsApp number via Glific HSM template.
    Called internally by create_referral() after successful save.
    Fails silently — patient notification failure should NOT block referral creation.
    """
    try:
        import requests
        
        glific_api_url = frappe.conf.get("glific_api_url", "https://search.glific.com/api")
        glific_api_token = frappe.conf.get("glific_api_token")
        hsm_template_id = frappe.conf.get("patient_notification_hsm_id")
        
        if not glific_api_token or not hsm_template_id:
            frappe.logger().warning("Glific API token or HSM template ID not configured. Skipping patient notification.")
            return
        
        # Ensure phone number has country code
        phone = patient_phone.strip()
        if not phone.startswith("+") and not phone.startswith("91"):
            phone = "91" + phone
        
        headers = {
            "Authorization": glific_api_token,
            "Content-Type": "application/json",
        }
        
        # Step 1: Create or find contact in Glific by phone
        create_contact_query = """
        mutation createContact($input: ContactInput!) {
          createContact(input: $input) {
            contact { id }
          }
        }
        """
        
        # Step 2: Send HSM template message to the contact
        send_hsm_query = """
        mutation sendHsmMessage($templateId: ID!, $receiverId: ID!, $parameters: [String]!) {
          sendHsmMessage(templateId: $templateId, receiverId: $receiverId, parameters: $parameters) {
            message { id }
          }
        }
        """
        
        # Parameters for the HSM template
        parameters = [patient_name, reference_number, opd_department or "SEARCH Hospital"]
        
        # Execute create contact first
        contact_res = requests.post(
            glific_api_url,
            json={"query": create_contact_query, "variables": {"input": {"phone": phone}}},
            headers=headers,
            timeout=10
        )
        contact_res.raise_for_status()
        contact_data = contact_res.json()
        
        contact_id = None
        try:
            contact_id = contact_data["data"]["createContact"]["contact"]["id"]
        except (KeyError, TypeError):
            # If create contact failed because it exists, query contact by phone
            search_query = """
            query contact($phone: String!) {
              contact(phone: $phone) { id }
            }
            """
            search_res = requests.post(
                glific_api_url,
                json={"query": search_query, "variables": {"phone": phone}},
                headers=headers,
                timeout=10
            )
            search_res.raise_for_status()
            search_data = search_res.json()
            try:
                contact_id = search_data["data"]["contact"]["id"]
            except (KeyError, TypeError):
                frappe.logger().error(f"Could not find or create Glific contact for phone {phone}")
                return
                
        if contact_id:
            hsm_res = requests.post(
                glific_api_url,
                json={
                    "query": send_hsm_query,
                    "variables": {
                        "templateId": hsm_template_id,
                        "receiverId": contact_id,
                        "parameters": parameters
                    }
                },
                headers=headers,
                timeout=10
            )
            hsm_res.raise_for_status()
            frappe.logger().info(f"Patient notification sent to {phone} for referral {reference_number}")
        
    except Exception as e:
        frappe.logger().error(f"Failed to send patient notification: {str(e)}")


@frappe.whitelist(allow_guest=True)
def create_referral(
    contact_phone: str = "",
    referral_date_raw: str = "",
    referral_date: str = "",
    date_of_referral_raw: str = "",
    date_of_referral: str = "",
    selected_phc: str = "",
    patient_name_raw: str = "",
    father_name_raw: str = "",
    gender_raw: str = "",
    age_raw: str = "",
    village_raw: str = "",
    patient_taluka_raw: str = "",
    patient_taluka: str = "",
    taluka_raw: str = "",
    service_facility_type: str = "",
    opd_category_raw: str = "",
    opd_category: str = "",
    departments_raw: str = "",
    opd_department_raw: str = "",
    opd_department: str = "",
    other_facility_raw: str = "",
    referring_doctor_raw: str = "",
    referred_doctor_raw: str = "",
    referred_doctor: str = "",
    additional_notes_raw: str = "",
    referrer_latitude: str = "",
    referrer_longitude: str = "",
    latitude: str = "",
    longitude: str = "",
    patient_phone_raw: str = "",
    referred_by_who: str = "",
    language: str = None,
    **kwargs
) -> dict:
    try:
        # Fallback / Comprehensive JSON body parsing for all parameters
        if frappe.request:
            try:
                import json
                raw_data = frappe.request.get_data(as_text=True)
                if raw_data:
                    data = json.loads(raw_data)
                    if isinstance(data, dict):
                        contact_phone = contact_phone or data.get("contact_phone") or data.get("phone") or ""
                        referral_date_raw = referral_date_raw or data.get("referral_date_raw") or data.get("date_of_referral_raw") or data.get("referral_date") or data.get("date_of_referral") or data.get("date") or data.get("date_raw") or ""
                        referral_date = referral_date or data.get("referral_date") or ""
                        date_of_referral_raw = date_of_referral_raw or data.get("date_of_referral_raw") or ""
                        date_of_referral = date_of_referral or data.get("date_of_referral") or ""
                        selected_phc = selected_phc or data.get("selected_phc") or data.get("phc") or ""
                        patient_name_raw = patient_name_raw or data.get("patient_name_raw") or data.get("patient_name") or ""
                        father_name_raw = father_name_raw or data.get("father_name_raw") or data.get("father_name") or ""
                        gender_raw = gender_raw or data.get("gender_raw") or data.get("patient_gender") or data.get("gender") or ""
                        age_raw = age_raw or data.get("age_raw") or data.get("patient_age") or data.get("age") or ""
                        village_raw = village_raw or data.get("village_raw") or data.get("patient_village") or data.get("village") or ""
                        patient_taluka_raw = patient_taluka_raw or data.get("patient_taluka_raw") or data.get("patient_taluka") or data.get("taluka_raw") or data.get("taluka") or ""
                        patient_taluka = patient_taluka or data.get("patient_taluka") or ""
                        taluka_raw = taluka_raw or data.get("taluka_raw") or ""
                        service_facility_type = service_facility_type or data.get("service_facility_type") or data.get("facility_type") or ""
                        opd_category_raw = opd_category_raw or data.get("opd_category_raw") or data.get("opd_category") or ""
                        opd_category = opd_category or data.get("opd_category") or ""
                        departments_raw = departments_raw or data.get("departments_raw") or data.get("opd_department_raw") or data.get("opd_department") or data.get("department") or ""
                        opd_department_raw = opd_department_raw or data.get("opd_department_raw") or ""
                        opd_department = opd_department or data.get("opd_department") or ""
                        other_facility_raw = other_facility_raw or data.get("other_facility_raw") or data.get("other_facility") or ""
                        referring_doctor_raw = referring_doctor_raw or data.get("referring_doctor_raw") or data.get("referred_doctor_raw") or data.get("referring_doctor") or data.get("referred_doctor") or ""
                        referred_doctor_raw = referred_doctor_raw or data.get("referred_doctor_raw") or ""
                        referred_doctor = referred_doctor or data.get("referred_doctor") or ""
                        additional_notes_raw = additional_notes_raw or data.get("additional_notes_raw") or data.get("additional_notes") or data.get("notes") or ""
                        referrer_latitude = referrer_latitude or data.get("referrer_latitude") or data.get("latitude") or ""
                        referrer_longitude = referrer_longitude or data.get("referrer_longitude") or data.get("longitude") or ""
                        latitude = latitude or data.get("latitude") or ""
                        longitude = longitude or data.get("longitude") or ""
                        patient_phone_raw = patient_phone_raw or data.get("patient_phone_raw") or data.get("patient_phone") or ""
                        referred_by_who = referred_by_who or data.get("referred_by_who") or ""
                        language = language or data.get("language") or ""
            except Exception as e:
                frappe.log_error(f"Fallback JSON parsing failed: {str(e)}", "create_referral JSON Fallback Error")

        if not contact_phone:
            frappe.throw("contact_phone is required")

        # Clean all parameters first
        contact_phone = clean_glific_value(contact_phone)
        selected_phc = clean_glific_value(selected_phc)
        patient_name_raw = clean_glific_value(patient_name_raw)
        father_name_raw = clean_glific_value(father_name_raw)
        gender_raw = clean_glific_value(gender_raw) or ""
        age_raw = clean_glific_value(age_raw)
        village_raw = clean_glific_value(village_raw)
        patient_taluka_raw = clean_glific_value(patient_taluka_raw)
        patient_taluka = clean_glific_value(patient_taluka)
        taluka_raw = clean_glific_value(taluka_raw)
        service_facility_type = clean_glific_value(service_facility_type)
        opd_category_raw = clean_glific_value(opd_category_raw)
        opd_category = clean_glific_value(opd_category)
        departments_raw = clean_glific_value(departments_raw)
        opd_department_raw = clean_glific_value(opd_department_raw)
        opd_department = clean_glific_value(opd_department)
        other_facility_raw = clean_glific_value(other_facility_raw)
        referring_doctor_raw = clean_glific_value(referring_doctor_raw)
        referred_doctor_raw = clean_glific_value(referred_doctor_raw)
        referred_doctor = clean_glific_value(referred_doctor)
        additional_notes_raw = clean_glific_value(additional_notes_raw)
        patient_phone_raw = clean_glific_value(patient_phone_raw)
        referred_by_who = clean_glific_value(referred_by_who)
        referrer_latitude = clean_glific_value(referrer_latitude)
        referrer_longitude = clean_glific_value(referrer_longitude)
        latitude = clean_glific_value(latitude)
        longitude = clean_glific_value(longitude)

        # Defaults to SEARCH hospital if not specified for backward compatibility
        facility_type = resolve_facility_type(service_facility_type) or "SEARCH"

        valid_facilities = ["SEARCH", "Government Hospital", "Other", "Village MH Clinic", "Taluka MH Clinic"]
        if facility_type not in valid_facilities:
            frappe.throw(f"Invalid service facility type: {facility_type}")

        actual_lat = referrer_latitude or latitude
        actual_lon = referrer_longitude or longitude
        referral_date_input = (
            referral_date_raw or referral_date or date_of_referral_raw or date_of_referral or kwargs.get("referral_date_raw") or kwargs.get("date_of_referral") or kwargs.get("date") or kwargs.get("referral_date") or kwargs.get("date_raw")
        )
        try:
            referral_date_value = parse_referral_date(referral_date_input)
        except frappe.ValidationError as e:
            # Keep HTTP status 200 so Glific's webhook routes to Success
            return {"success": False, "error": str(e)}
        patient_taluka_input = patient_taluka_raw or patient_taluka or taluka_raw
        
        # Only resolve category if facility is SEARCH
        opd_category_input = ""
        if facility_type == "SEARCH":
            opd_category_input = resolve_opd_category(opd_category_raw or opd_category)
            
        department_input = opd_department_raw or opd_department or departments_raw
        doctor_input = referring_doctor_raw or referred_doctor_raw or referred_doctor

        # Resolve referrer correctly by phone number
        referrer = resolve_referrer(contact_phone)

        # Fetch referrer details for denormalized fields
        referrer_full_name = ""
        referrer_department = ""
        if referrer:
            referrer_doc = frappe.get_doc("Referrer", referrer)
            referrer_full_name = referrer_doc.full_name or ""
            referrer_department = referrer_doc.department or ""

        # Resolve patient village, taluka and PHC using standard clean logic without dynamic creation of new profiles
        patient_village = resolve_village(village_raw)
        patient_taluka_resolved = resolve_taluka(patient_taluka_input)
        
        if not patient_taluka_resolved and patient_village:
            patient_taluka_resolved = frappe.db.get_value(
                "Village Profile", patient_village, "taluka"
            )
            
        phc = resolve_phc(selected_phc)

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

        # Parse age — supports "X months" (e.g. "7 months" -> 0.7 years, per spec)
        import re as _re
        age_clean = (age_raw or "").strip().lower()
        month_match = _re.search(r"(\d+(\.\d+)?)\s*(month|months|महिने|महिना|माह)", age_clean)
        try:
            if month_match:
                patient_age = round(float(month_match.group(1)) / 10, 1)
            else:
                patient_age = float(age_clean)
        except Exception:
            patient_age = 0.0

        # Resolve OPD department (SEARCH only)
        opd_dept = None
        if facility_type == "SEARCH":
            opd_dept = resolve_department(department_input, opd_category_input)

        # Transliterate names to Roman English
        patient_name = transliterate_to_roman(patient_name_raw)
        father_name = transliterate_to_roman(father_name_raw)

        # Translate additional notes to English (meaning, not transliteration)
        additional_notes = translate_to_english(additional_notes_raw)
        
        # Referring Doctor resolution
        referring_doctor = resolve_referred_doctor(doctor_input)
        
        # Resolve Referred By Who role (e.g. MMU Doctor, ASHA, etc.)
        referred_by_resolved = resolve_referred_by_who(referred_by_who)

        # Save raw data exactly as received
        raw_doc = frappe.get_doc({
            "doctype": "Raw Patient Referral Data",
            "glific_contact_id": contact_phone,
            "received_at": frappe.utils.now(),
            "referral_date_raw": referral_date_raw or referral_date_input or "",
            "selected_phc": selected_phc,
            "referrer_latitude": actual_lat,
            "referrer_longitude": actual_lon,
            "patient_name_raw": patient_name_raw,
            "father_name_raw": father_name_raw,
            "gender_raw": gender_raw,
            "age_raw": age_raw,
            "village_raw": village_raw,
            "patient_taluka_raw": patient_taluka_input,
            "patient_phone_raw": patient_phone_raw,
            "service_facility_type": facility_type,
            "opd_category_raw": opd_category_raw or opd_category,
            "referred_by_who": referred_by_who,
            "departments_raw": department_input,
            "other_facility_raw": other_facility_raw or "",
            "referring_doctor_raw": doctor_input,
            "referred_doctor_raw": doctor_input,
            "additional_notes_raw": additional_notes_raw,
            "glific_referrer_name": referrer_full_name,
        })
        raw_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Create Patient Referral
        referral_doc = frappe.get_doc({
            "doctype": "Patient Referral",
            "referral_date": referral_date_value,
            "referral_recorded_date": today(),
            "status": "Pending",
            "referrer": referrer,
            "referrer_name": referrer_full_name,
            "referrer_phone": contact_phone,
            "referrer_department": referrer_department,
            "referrer_latitude": actual_lat,
            "referrer_longitude": actual_lon,
            "referred_by_who": referred_by_resolved,
            "phc": phc or "",
            "patient_name": patient_name,
            "patient_father_name": father_name,
            "patient_gender": patient_gender,
            "patient_age": patient_age,
            "patient_village": patient_village or "",
            "patient_taluka": patient_taluka_resolved or "",
            "patient_phone": patient_phone_raw,
            "additional_notes": additional_notes,
            "service_facility_type": facility_type,
            "opd_category": opd_category_input or "",
            "opd_departments": opd_dept or "",
            "other_facility_name": other_facility_raw or "",
            "referring_doctor": referring_doctor,
            "referred_doctor": referring_doctor,
            "raw_patient_data": raw_doc.name,
        })
        referral_doc.flags.ignore_mandatory = True
        referral_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Link raw doc back
        raw_doc.patient_referral = referral_doc.name
        raw_doc.save(ignore_permissions=True)
        frappe.db.commit()

        # Send patient notification (fails silently)
        if referral_doc.patient_phone:
            facility_desc = referral_doc.opd_departments or referral_doc.other_facility_name or referral_doc.service_facility_type
            send_patient_notification(referral_doc.patient_phone, referral_doc.patient_name, referral_doc.reference_number, facility_desc)

        # Format date as dd-mm-yyyy
        from frappe.utils import getdate
        ref_date_str = ""
        if referral_doc.referral_date:
            try:
                ref_date_str = getdate(referral_doc.referral_date).strftime("%d-%m-%Y")
            except Exception:
                ref_date_str = str(referral_doc.referral_date)

        # Clean language parameter
        lang = (clean_glific_value(language) or "mr").strip().lower()
        if lang not in ("en", "hi", "mr"):
            lang = "mr"

        # Localized patient, facility, and OPD values
        patient_name_display = format_patient_name(referral_doc.patient_name, patient_name_raw, lang)
        patient_father_name_display = format_patient_name(referral_doc.patient_father_name, father_name_raw, lang)
        gender_display_val = format_gender(referral_doc.patient_gender, lang)
        facility_display = format_facility(referral_doc.service_facility_type, referral_doc.other_facility_name, lang)
        opd_raw_val = referral_doc.opd_departments or referral_doc.opd_category or "-"
        opd_display = format_opd(opd_raw_val, lang)
        village_display = village_display_name(referral_doc.patient_village, lang) if referral_doc.patient_village else (village_raw or "-")
        age_display = format_age_display(referral_doc.patient_age)
        referred_by_who_display = format_referred_by_who(referral_doc.referred_by_who, lang) or referral_doc.referred_by_who or ""

        patient_instruction = ""
        if referral_doc.service_facility_type == "SEARCH":
            if lang == "mr":
                patient_instruction = "कृपया SEARCH हॉस्पिटलमधील नोंदणी कक्षात रेफरल स्लिप दाखवा."
            elif lang == "hi":
                patient_instruction = "कृपया SEARCH अस्पताल के पंजीकरण काउंटर (Registration Desk) पर अपनी रेफरल पर्ची दिखाएं।"
            else:
                patient_instruction = "Please show your referral slip at the registration desk in SEARCH Hospital."

        # Format full informatory / confirmation message
        referred_by_line_mr = f"रेफर करणारे: {referred_by_who_display}\n" if referred_by_who_display else ""
        referred_by_line_hi = f"रेफर करने वाले: {referred_by_who_display}\n" if referred_by_who_display else ""
        referred_by_line_en = f"Referred By: {referred_by_who_display}\n" if referred_by_who_display else ""

        if lang == "mr":
            formatted_text = (
                f"✅ *रेफेरल ची नोंदणी यशस्वी झाली, धन्यवाद!*\n\n"
                f"संदर्भ क्रमांक: {referral_doc.reference_number}\n"
                f"रुग्णाचे नाव: {patient_name_display}\n"
                f"वय: {age_display}\n"
                f"लिंग: {gender_display_val}\n"
                f"रेफरलची तारीख: {ref_date_str}\n"
                f"रुग्णालय: {facility_display}\n"
                f"ओपीडी (OPD): {opd_display}\n"
                f"गावाचे नाव: {village_display}\n"
                f"{referred_by_line_mr}\n"
                f"{patient_instruction}"
            ).strip()
        elif lang == "hi":
            formatted_text = (
                f"✅ *रेफरल सफलतापूर्वक दर्ज किया गया!*\n\n"
                f"रेफरल नंबर: {referral_doc.reference_number}\n"
                f"मरीज का नाम: {patient_name_display}\n"
                f"उम्र: {age_display}\n"
                f"लिंग: {gender_display_val}\n"
                f"रेफरल तिथि: {ref_date_str}\n"
                f"अस्पताल: {facility_display}\n"
                f"ओपीडी (OPD): {opd_display}\n"
                f"गाँव का नाम: {village_display}\n"
                f"{referred_by_line_hi}\n"
                f"{patient_instruction}"
            ).strip()
        else:
            formatted_text = (
                f"✅ *Referral Registered Successfully!*\n\n"
                f"Reference Number: {referral_doc.reference_number}\n"
                f"Patient Name: {patient_name_display}\n"
                f"Age: {age_display}\n"
                f"Gender: {gender_display_val}\n"
                f"Referral Date: {ref_date_str}\n"
                f"Hospital: {facility_display}\n"
                f"OPD: {opd_display}\n"
                f"Village Name: {village_display}\n"
                f"{referred_by_line_en}\n"
                f"{patient_instruction}"
            ).strip()

        return {
            "success": True,
            "reference_number": referral_doc.reference_number,
            "patient_name": patient_name_display,
            "patient_father_name": patient_father_name_display,
            "patient_age": age_display,
            "age": age_display,
            "patient_gender": gender_display_val,
            "gender": gender_display_val,
            "patient_village": village_display,
            "village_name": village_display,
            "village": village_display,
            "referral_date": ref_date_str,
            "date": ref_date_str,
            "hospital": facility_display,
            "service_facility_type": facility_display,
            "opd": opd_display,
            "opd_department": opd_display,
            "referred_by_who": referred_by_who_display,
            "referredbywho": referred_by_who_display,
            "referred_by": referred_by_who_display,
            "patient_instruction": patient_instruction,
            "formatted_text": formatted_text,
            "summary_message": formatted_text,
            "message": {
                "reference_number": referral_doc.reference_number,
                "patient_name": patient_name_display,
                "patient_age": age_display,
                "patient_gender": gender_display_val,
                "hospital": facility_display,
                "opd": opd_display,
                "village_name": village_display,
                "referred_by_who": referred_by_who_display,
                "referredbywho": referred_by_who_display,
                "referred_by": referred_by_who_display,
                "formatted_text": formatted_text,
                "summary_message": formatted_text,
            }
        }

    except frappe.ValidationError:
        raise
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_referral API Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist(allow_guest=True)
def get_referral(
    referral_id: str = None,
    reference_number: str = None,
    supervisor_phone: str = None,
    language: str = None,
    **kwargs
) -> dict:
    """
    Look up a Patient Referral by reference_number, patient_name, or patient_phone.
    Supports guest access and returns flat and nested referral details in requested language.
    """
    try:
        # Check form_dict and kwargs
        if frappe.form_dict:
            referral_id = referral_id or frappe.form_dict.get("referral_id") or frappe.form_dict.get("reference_number") or frappe.form_dict.get("ref_id") or frappe.form_dict.get("ref_no") or frappe.form_dict.get("referral_number") or frappe.form_dict.get("id") or frappe.form_dict.get("text") or frappe.form_dict.get("search") or frappe.form_dict.get("search_term")
            reference_number = reference_number or frappe.form_dict.get("reference_number")
            language = language or frappe.form_dict.get("language")

        if kwargs:
            referral_id = referral_id or kwargs.get("referral_id") or kwargs.get("reference_number") or kwargs.get("ref_id") or kwargs.get("ref_no") or kwargs.get("referral_number") or kwargs.get("id") or kwargs.get("text") or kwargs.get("search") or kwargs.get("search_term")
            reference_number = reference_number or kwargs.get("reference_number")
            language = language or kwargs.get("language")

        # Fallback JSON parsing
        if frappe.request:
            try:
                import json
                raw_data = frappe.request.get_data(as_text=True)
                if raw_data:
                    data = json.loads(raw_data)
                    if isinstance(data, dict):
                        referral_id = referral_id or data.get("referral_id") or data.get("reference_number") or data.get("ref_id") or data.get("ref_no") or data.get("referral_number") or data.get("id") or data.get("text") or data.get("search") or data.get("search_term")
                        reference_number = reference_number or data.get("reference_number")
                        language = language or data.get("language")
            except Exception:
                pass

        ref_id = referral_id or reference_number
        if not ref_id:
            return {
                "success": False,
                "error": "Missing referral ID or reference number"
            }

        ref_id = clean_glific_value(ref_id).strip()
        clean_id = ref_id.lstrip("#").strip().rstrip(".")
        if clean_id.upper().startswith("REF:"):
            clean_id = clean_id[4:].strip()
        elif clean_id.upper().startswith("REF-"):
            clean_id = clean_id[4:].strip()

        referral = None
        # Try exact match on name (name in Frappe is the reference_number due to autonaming)
        # or direct search by reference_number field
        if frappe.db.exists("Patient Referral", ref_id):
            referral = frappe.get_doc("Patient Referral", ref_id)
        elif frappe.db.exists("Patient Referral", {"reference_number": ref_id}):
            referral = frappe.get_doc("Patient Referral", {"reference_number": ref_id})
        elif clean_id and frappe.db.exists("Patient Referral", clean_id):
            referral = frappe.get_doc("Patient Referral", clean_id)
        elif clean_id and frappe.db.exists("Patient Referral", {"reference_number": clean_id}):
            referral = frappe.get_doc("Patient Referral", {"reference_number": clean_id})
        else:
            # Try normalized slash vs dash (e.g. 040926/2 vs 040926-2)
            alt_id = clean_id.replace("/", "-")
            if frappe.db.exists("Patient Referral", alt_id):
                referral = frappe.get_doc("Patient Referral", alt_id)
            elif frappe.db.exists("Patient Referral", {"reference_number": alt_id}):
                referral = frappe.get_doc("Patient Referral", {"reference_number": alt_id})

        if not referral:
            # Fuzzy match on patient_name
            name_search = transliterate_to_roman(clean_id or ref_id)
            results = frappe.get_all("Patient Referral",
                filters={"patient_name": ["like", f"%{name_search}%"]},
                fields=["name"],
                order_by="referral_date desc",
                limit=1
            )
            if results:
                referral = frappe.get_doc("Patient Referral", results[0].name)

        if not referral:
            return {
                "success": False,
                "error": f"Referral {ref_id} not found"
            }

        lang = (clean_glific_value(language) or "mr").strip().lower()
        if lang not in ("en", "hi", "mr"):
            lang = "mr"

        raw_patient_name = None
        if getattr(referral, "raw_patient_data", None):
            if frappe.db.exists("DocType", "Raw Patient Referral Data"):
                raw_patient_name = frappe.db.get_value("Raw Patient Referral Data", referral.raw_patient_data, "patient_name_raw")
            elif frappe.db.exists("DocType", "Raw Patient Data"):
                raw_patient_name = frappe.db.get_value("Raw Patient Data", referral.raw_patient_data, "patient_name_raw")

        patient_name_display = format_patient_name(referral.patient_name, raw_patient_name, lang)
        gender_display = format_gender(referral.patient_gender, lang)
        age_display = format_age_display(referral.patient_age)
        village_display = village_display_name(referral.patient_village, lang) if referral.patient_village else ""
        facility_display = format_facility(referral.service_facility_type, referral.other_facility_name, lang)
        opd_display = format_opd(referral.opd_departments or referral.opd_category, lang)

        phc_name = frappe.db.get_value("PHC", referral.phc, "phc_name") if referral.phc else ""
        referrer_name = frappe.db.get_value(
            "Referrer", referral.referrer, "full_name"
        ) if referral.referrer else ""

        referred_by_who_display = format_referred_by_who(referral.referred_by_who, lang) or referral.referred_by_who or ""

        ref_date_display = ""
        if referral.referral_date:
            try:
                ref_date_display = getdate(referral.referral_date).strftime("%d-%m-%Y")
            except Exception:
                ref_date_display = str(referral.referral_date)

        referred_to_display = f"{facility_display} ({opd_display})" if opd_display and opd_display != facility_display else facility_display

        # Flat structure for Glific
        res = {
            "success": True,
            "patient_name": patient_name_display,
            "patient_age": age_display,
            "age": age_display,
            "patient_gender": gender_display,
            "gender": gender_display,
            "patient_village": village_display,
            "village_name": village_display,
            "village": village_display,
            "patient_taluka": referral.patient_taluka or "",
            "patient_phone": referral.patient_phone or "",
            "referral_date": ref_date_display,
            "referral_date_raw": str(referral.referral_date or ""),
            "hospital": facility_display,
            "facility": facility_display,
            "opd": opd_display,
            "opd_department": opd_display,
            "referred_to": referred_to_display,
            "referred_by_who": referred_by_who_display,
            "referredbywho": referred_by_who_display,
            "referred_by": referred_by_who_display,
            "reference_number": referral.reference_number,
            "referral_id": referral.reference_number,
            "visit_count": referral.visit_count or 0,
            "status": referral.status or "",
        }

        # Nested structure for backward compatibility and Glific message parsing
        res["message"] = {
            "success": True,
            "reference_number": referral.reference_number,
            "referral_id": referral.reference_number,
            "patient_name": patient_name_display,
            "patient_age": age_display,
            "age": age_display,
            "patient_gender": gender_display,
            "gender": gender_display,
            "patient_village": village_display,
            "village_name": village_display,
            "village": village_display,
            "referral_date": ref_date_display,
            "hospital": facility_display,
            "facility": facility_display,
            "opd": opd_display,
            "opd_department": opd_display,
            "referred_to": referred_to_display,
            "referred_by_who": referred_by_who_display,
            "referredbywho": referred_by_who_display,
            "referred_by": referred_by_who_display,
            "visit_count": referral.visit_count or 0,
            "status": referral.status or "",
        }

        res["referral"] = {
            "reference_number": referral.reference_number,
            "referral_id": referral.reference_number,
            "referral_date": ref_date_display,
            "status": referral.status or "",
            "referrer_name": referrer_name,
            "referrer_phone": referral.referrer_phone or "",
            "phc": phc_name,
            "patient_name": patient_name_display,
            "patient_father_name": format_patient_name(referral.patient_father_name, lang=lang),
            "patient_gender": gender_display,
            "patient_age": age_display,
            "patient_village": village_display,
            "patient_taluka": referral.patient_taluka or "",
            "patient_phone": referral.patient_phone or "",
            "hospital": facility_display,
            "facility": facility_display,
            "opd_category": referral.opd_category or "",
            "opd_department": opd_display,
            "opd": opd_display,
            "referred_to": referred_to_display,
            "referred_by_who": referred_by_who_display,
            "referredbywho": referred_by_who_display,
            "referred_by": referred_by_who_display,
            "referred_doctor": referral.referred_doctor or "",
            "additional_notes": referral.additional_notes or "",
            "match_status": referral.match_status or "",
            "tribal_classification": referral.tribal_classification or "",
            "visit_count": referral.visit_count or 0,
        }

        return res

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_referral API Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist(allow_guest=True)
def record_supervisor_visit(
    referral_id: str = None,
    supervisor_phone: str = None,
    visit_date: str = None,
    patient_visited: str = None,
    facility_visited: str = None,
    confirmation_date: str = None,
    patient_health_status: str = None,
    supervisor_name: str = None,
    non_visit_reason: str = None,
    other_non_visit_reason: str = None,
    non_visit_reason_text: str = None,
    other_reason: str = None,
    **kwargs
) -> dict:
    """
    Records a supervisor follow-up visit and updates the Patient Referral status.
    """
    try:
        # Try parsing JSON body if available (Glific uses POST)
        if frappe.request:
            try:
                import json
                raw_data = frappe.request.get_data(as_text=True)
                if raw_data:
                    data = json.loads(raw_data)
                    if isinstance(data, dict):
                        if not referral_id:
                            referral_id = data.get("referral_id") or data.get("reference_number")
                        if not supervisor_phone:
                            supervisor_phone = data.get("supervisor_phone") or data.get("contact_phone")
                        if not visit_date:
                            visit_date = data.get("visit_date") or data.get("date")
                        if not patient_visited:
                            patient_visited = data.get("patient_visited") or data.get("visited")
                        if not facility_visited:
                            facility_visited = data.get("facility_visited")
                        if not confirmation_date:
                            confirmation_date = data.get("confirmation_date")
                        if not patient_health_status:
                            patient_health_status = data.get("patient_health_status")
                        if not supervisor_name:
                            supervisor_name = data.get("supervisor_name")
                        if not non_visit_reason:
                            non_visit_reason = data.get("non_visit_reason")
                        if not other_non_visit_reason:
                            other_non_visit_reason = (
                                data.get("other_non_visit_reason")
                                or data.get("non_visit_reason_text")
                                or data.get("non_visit_reason_other")
                                or data.get("other_reason")
                                or data.get("other")
                            )
            except Exception:
                pass

        # Clean all input variables first (to handle unresolved Glific variables)
        referral_id = clean_glific_value(referral_id)
        supervisor_phone = clean_glific_value(supervisor_phone)
        visit_date = clean_glific_value(visit_date)
        patient_visited = clean_glific_value(patient_visited)
        facility_visited = clean_glific_value(facility_visited)
        confirmation_date = clean_glific_value(confirmation_date)
        patient_health_status = clean_glific_value(patient_health_status)
        supervisor_name = clean_glific_value(supervisor_name)
        non_visit_reason = clean_glific_value(non_visit_reason)
        other_non_visit_reason = clean_glific_value(
            other_non_visit_reason
            or non_visit_reason_text
            or other_reason
            or kwargs.get("other_non_visit_reason")
            or kwargs.get("non_visit_reason_text")
            or kwargs.get("other_reason")
        )

        if not referral_id:
            return {
                "success": False,
                "error": "Missing referral_id"
            }
        if not supervisor_phone:
            return {
                "success": False,
                "error": "Missing supervisor_phone"
            }
        if not visit_date:
            return {
                "success": False,
                "error": "Missing visit_date"
            }
        if not patient_visited:
            return {
                "success": False,
                "error": "Missing patient_visited"
            }

        # 1. Look up referral
        referral = None
        if frappe.db.exists("Patient Referral", referral_id):
            referral = frappe.get_doc("Patient Referral", referral_id)
        elif frappe.db.exists("Patient Referral", {"reference_number": referral_id}):
            referral = frappe.get_doc("Patient Referral", {"reference_number": referral_id})

        if not referral:
            return {
                "success": False,
                "error": f"Referral {referral_id} not found"
            }

        # 2. Validate status allows new visits
        if referral.status not in ("Pending", "Follow-up In Progress"):
            return {
                "success": False,
                "error": f"Referral {referral_id} has status '{referral.status}' and cannot accept new visits"
            }

        # 3. Validate visit count
        current_count = referral.visit_count or 0
        if current_count >= 3:
            return {
                "success": False,
                "error": f"Referral {referral_id} already has 3 visits recorded. No further visits allowed."
            }

        # 4. Parse and validate dates
        visit_date_parsed = parse_date(visit_date)
        if not visit_date_parsed:
            # Default to today if visit_date is missing/unresolved — supervisor records in real time
            frappe.logger().warning(
                f"[record_supervisor_visit] visit_date '{visit_date}' could not be parsed, defaulting to today"
            )
            visit_date_parsed = getdate(today())
            
        if visit_date_parsed > getdate(today()):
            return {
                "success": False,
                "error": "Visit date cannot be in the future"
            }
        if visit_date_parsed < getdate(referral.referral_date):
            return {
                "success": False,
                "error": "Visit date cannot be before referral date"
            }

        # 5. Create Supervisor Visit child record
        new_visit_number = current_count + 1
        # Support English, Marathi (होय/हो), Hindi (हाँ) affirmatives
        YES_VALUES = ("yes", "1", "true", "होय", "हो", "हाँ", "han", "hoy")
        is_visited = bool(patient_visited and patient_visited.strip().lower() in YES_VALUES)

        # Handle fields based on visited state
        if is_visited:
            confirmation_date_parsed = parse_date(confirmation_date)
            # If confirmation_date parsing failed, fallback to visit_date
            if not confirmation_date_parsed:
                confirmation_date_parsed = visit_date_parsed
                
            resolved_facility = resolve_facility_type(facility_visited)
            reason_code = None
            other_text = None
        else:
            confirmation_date_parsed = None
            resolved_facility = None
            
            reason_code = resolve_non_visit_reason(non_visit_reason)
            other_text = other_non_visit_reason or None
            
            # If user typed custom text in non_visit_reason directly, or selected Other
            if reason_code == "Other":
                if not other_text and non_visit_reason and non_visit_reason not in ("Other", "NV-08", "इतर", "अन्य", "Other (Specify)", "इतर (नमूद करा)", "अन्य (निर्दिष्ट करें)"):
                    other_text = non_visit_reason

        referral.append("supervisor_visits", {
            "visit_number": new_visit_number,
            "visit_date": visit_date_parsed,
            "patient_visited": 1 if is_visited else 0,
            "facility_visited": resolved_facility,
            "confirmation_date": confirmation_date_parsed,
            "patient_health_status": resolve_patient_health_status(patient_health_status) if is_visited else None,
            "non_visit_reason_code": reason_code if not is_visited else None,
            "non_visit_reason_text": other_text if (not is_visited and reason_code == "Other") else None,
            "supervisor_name": supervisor_name,
            "supervisor_phone": supervisor_phone,
        })

        # 6. Update referral status (state machine)
        if is_visited:
            referral.status = "Visited"
            referral.facility_visited = resolved_facility
            referral.visit_date = confirmation_date_parsed
        elif new_visit_number >= 3:
            referral.status = "Closed - Not Visited"
        else:
            referral.status = "Follow-up In Progress"

        # 7. Update visit count
        referral.visit_count = new_visit_number

        # Auto-heal legacy referrals: populate patient_taluka from village if missing
        if not referral.patient_taluka and referral.patient_village:
            referral.patient_taluka = frappe.db.get_value("Village Profile", referral.patient_village, "taluka")

        # 8. Save
        referral.flags.ignore_mandatory = True
        referral.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "status": referral.status,
            "visit_number": new_visit_number,
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "record_supervisor_visit API Error")
        return {
            "success": False,
            "error": str(e)
        }


MHD_INFO_SOURCE_MAP = {
    "patient": "Patient", "पेशंट": "Patient", "रुग्ण": "Patient",
    "relative": "Relative", "नातेवाईक": "Relative", "रिश्तेदार": "Relative",
    "neighbor": "Neighbor", "neighbour": "Neighbor", "शेजारी": "Neighbor", "पड़ोसी": "Neighbor",
    "other": "Other", "इतर": "Other", "अन्य": "Other",
}

MHD_DRINKING_PATTERN_MAP = {
    "regular": "Regular", "नियमित": "Regular",
    "binge on regular": "Binge on Regular", "नियमितपणे अति खाणे": "Binge on Regular",
    "binge": "Binge", "अति खाणे": "Binge", "बिंज": "Binge",
    "occasional": "Occasional", "अधूनमधून": "Occasional", "प्रासंगिक": "Occasional",
}

MHD_ALCOHOL_TYPE_MAP = {
    "country": "Country", "देशी": "Country",
    "imfl": "IMFL", "विदेशी (imfl)": "IMFL", "विदेशी": "IMFL",
    "moha / gul": "Moha / Gul", "moha/gul": "Moha / Gul", "मोहा / गुळ": "Moha / Gul", "मोहा / गुल": "Moha / Gul",
    "tadi / sindhi / gorga": "Tadi / Sindhi / Gorga", "ताडी / सिंधी / गोरगा": "Tadi / Sindhi / Gorga", "ताड़ी / सिंधी / गोरगा": "Tadi / Sindhi / Gorga",
    "none": "None", "काहीही नाही": "None", "कोई नहीं": "None",
}


def resolve_mhd_select(value_raw: str, mapping: dict) -> str | None:
    if not value_raw:
        return None
    return mapping.get(value_raw.strip().lower(), value_raw.strip())


@frappe.whitelist(allow_guest=True)
def record_mhd_followup(
    referral_id: str = None,
    mhd_counselor_phone: str = None,
    followup_day_offset: str = None,
    patient_info_source: str = None,
    days_drank_last_15: str = None,
    notable_incident: str = None,
    current_complaints: str = None,
    drinking_pattern: str = None,
    alcohol_type: str = None,
    quantity_ml_per_day: str = None,
    frequency_per_day: str = None,
    drank_today: str = None,
    family_opinion: str = None,
    counselor_observation: str = None,
    mhd_counselor_name: str = None,
    **kwargs
) -> dict:
    """
    Records an MHD counsellor follow-up (30/90-day addiction-management
    check-in) against a Patient Referral. Called by Glific's 'MHD Followup'
    flow, entered from the Supervisor Followup flow's MHD Followup branch.
    """
    try:
        import json
        if frappe.request:
            try:
                raw_data = frappe.request.get_data(as_text=True)
                if raw_data:
                    data = json.loads(raw_data)
                    if isinstance(data, dict):
                        referral_id = referral_id or data.get("referral_id")
                        mhd_counselor_phone = mhd_counselor_phone or data.get("mhd_counselor_phone")
                        followup_day_offset = followup_day_offset or data.get("followup_day_offset")
                        patient_info_source = patient_info_source or data.get("patient_info_source")
                        days_drank_last_15 = days_drank_last_15 or data.get("days_drank_last_15") or data.get("days_drank_last")
                        notable_incident = notable_incident or data.get("notable_incident")
                        current_complaints = current_complaints or data.get("current_complaints")
                        drinking_pattern = drinking_pattern or data.get("drinking_pattern")
                        alcohol_type = alcohol_type or data.get("alcohol_type")
                        quantity_ml_per_day = quantity_ml_per_day or data.get("quantity_ml_per_day") or data.get("quantity_ml")
                        frequency_per_day = frequency_per_day or data.get("frequency_per_day") or data.get("frequency")
                        drank_today = drank_today or data.get("drank_today")
                        family_opinion = family_opinion or data.get("family_opinion")
                        counselor_observation = counselor_observation or data.get("counselor_observation")
                        mhd_counselor_name = mhd_counselor_name or data.get("mhd_counselor_name")
            except Exception:
                pass

        referral_id = clean_glific_value(referral_id)
        mhd_counselor_phone = clean_glific_value(mhd_counselor_phone)
        mhd_counselor_name = clean_glific_value(mhd_counselor_name)
        followup_day_offset = clean_glific_value(followup_day_offset)
        patient_info_source = clean_glific_value(patient_info_source)
        days_drank_last_15 = clean_glific_value(days_drank_last_15)
        notable_incident = clean_glific_value(notable_incident)
        current_complaints = clean_glific_value(current_complaints)
        drinking_pattern = clean_glific_value(drinking_pattern)
        alcohol_type = clean_glific_value(alcohol_type)
        quantity_ml_per_day = clean_glific_value(quantity_ml_per_day)
        frequency_per_day = clean_glific_value(frequency_per_day)
        drank_today = clean_glific_value(drank_today)
        family_opinion = clean_glific_value(family_opinion)
        counselor_observation = clean_glific_value(counselor_observation)

        if not referral_id:
            return {"success": False, "error": "Missing referral_id"}
        if not mhd_counselor_phone:
            return {"success": False, "error": "Missing mhd_counselor_phone"}

        referral = None
        if frappe.db.exists("Patient Referral", referral_id):
            referral = frappe.get_doc("Patient Referral", referral_id)
        elif frappe.db.exists("Patient Referral", {"reference_number": referral_id}):
            referral = frappe.get_doc("Patient Referral", {"reference_number": referral_id})

        if not referral:
            return {"success": False, "error": f"Referral {referral_id} not found"}

        try:
            days_drank_int = int(days_drank_last_15) if days_drank_last_15 else 0
        except ValueError:
            days_drank_int = 0
        days_drank_int = max(0, min(15, days_drank_int))

        try:
            qty_ml_int = int(quantity_ml_per_day) if quantity_ml_per_day else 0
        except ValueError:
            qty_ml_int = 0

        try:
            freq_int = int(frequency_per_day) if frequency_per_day else 0
        except ValueError:
            freq_int = 0

        YES_VALUES = ("yes", "1", "true", "होय", "हो", "हाँ", "han", "hoy")
        drank_today_flag = 1 if (drank_today and drank_today.strip().lower() in YES_VALUES) else 0

        day_offset_clean = "90" if "90" in (followup_day_offset or "") else "30"

        referral.append("mhd_followups", {
            "followup_day_offset": day_offset_clean,
            "visit_date": getdate(today()),
            "patient_info_source": resolve_mhd_select(patient_info_source, MHD_INFO_SOURCE_MAP),
            "days_drank_last_15": days_drank_int,
            "notable_incident": notable_incident,
            "current_complaints": current_complaints,
            "drinking_pattern": resolve_mhd_select(drinking_pattern, MHD_DRINKING_PATTERN_MAP),
            "alcohol_type": resolve_mhd_select(alcohol_type, MHD_ALCOHOL_TYPE_MAP),
            "quantity_ml_per_day": qty_ml_int,
            "frequency_per_day": freq_int,
            "drank_today": drank_today_flag,
            "family_opinion": family_opinion,
            "counselor_observation": counselor_observation,
            "mhd_counselor_name": mhd_counselor_name,
            "mhd_counselor_phone": mhd_counselor_phone,
        })

        referral.visit_count = (referral.visit_count or 0) + 1

        referral.flags.ignore_mandatory = True
        referral.save(ignore_permissions=True)
        frappe.db.commit()

        return {"success": True, "followup_day_offset": day_offset_clean}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "record_mhd_followup API Error")
        return {"success": False, "error": str(e)}


def get_glific_contact_fields(phone: str) -> dict:
    try:
        import requests
        glific_api_url = frappe.conf.get("glific_api_url", "https://search.glific.com/api")
        glific_token = frappe.conf.get("glific_token")
        if not glific_token:
            return {}
            
        headers = {
            "Authorization": glific_token,
            "Content-Type": "application/json",
        }
        
        query = """
        query contact($phone: String!) {
          contact(phone: $phone) {
            id
            fields
          }
        }
        """
        res = requests.post(
            glific_api_url,
            json={"query": query, "variables": {"phone": phone}},
            headers=headers,
            timeout=10
        )
        res.raise_for_status()
        data = res.json()
        return data.get("data", {}).get("contact", {}).get("fields", {}) or {}
    except Exception as e:
        frappe.logger().error(f"Failed to fetch Glific contact fields: {str(e)}")
        return {}


@frappe.whitelist(allow_guest=True)
def get_pending_followups(
    supervisor_phone: str = None, 
    village_name: str = None, 
    taluka_name: str = None, 
    month: int = None, 
    year: int = None, 
    duration: str = None,
    followup_list_enter_date: str = None,
    date: str = None,
    specific_date: str = None,
    language: str = "mr",
    **kwargs
) -> dict:
    """
    Returns pending follow-up referrals formatted as a ready-to-send
    WhatsApp message, optionally filtered by village name, taluka name,
    specific date (DD/MM/YYYY), or duration,
    along with patients who visited SEARCH in the specified duration/date.

    Called by Glific 'Follow-up List' flow.
    """
    # Try parsing JSON body if available (Glific uses POST)
    if frappe.request:
        try:
            import json
            raw_data = frappe.request.get_data(as_text=True)
            if raw_data:
                data = json.loads(raw_data)
                if isinstance(data, dict):
                    if not supervisor_phone:
                        supervisor_phone = data.get("supervisor_phone")
                    if not village_name:
                        village_name = data.get("village") or data.get("village_name") or data.get("village_input")
                    if not taluka_name:
                        taluka_name = data.get("taluka") or data.get("taluka_name") or data.get("taluka_input")
                    if not month:
                        month = data.get("month")
                    if not year:
                        year = data.get("year")
                    if not duration:
                        duration = data.get("duration") or data.get("duration_months")
                    if not followup_list_enter_date:
                        followup_list_enter_date = (
                            data.get("followup_list_enter_date")
                            or data.get("followuplist_enter_date")
                            or data.get("date")
                            or data.get("specific_date")
                            or data.get("followup_date")
                        )
                    if not language:
                        language = data.get("language")
        except Exception:
            pass

    month = month or kwargs.get("month")
    year = year or kwargs.get("year")
    duration = duration or kwargs.get("duration") or kwargs.get("duration_months")
    language = language or kwargs.get("language")
    followup_list_enter_date = (
        followup_list_enter_date
        or date
        or specific_date
        or kwargs.get("followup_list_enter_date")
        or kwargs.get("followuplist_enter_date")
        or kwargs.get("date")
        or kwargs.get("specific_date")
        or kwargs.get("followup_date")
    )

    supervisor_phone = clean_glific_value(supervisor_phone)
    village_name = clean_glific_value(village_name)
    taluka_name = clean_glific_value(taluka_name)
    followup_list_enter_date = clean_glific_value(followup_list_enter_date)

    lang = (clean_glific_value(language) or "mr").strip().lower()
    if lang not in ("en", "hi", "mr"):
        lang = "mr"

    # If village_name or date is not provided in body, try querying Glific contact fields
    if supervisor_phone:
        if not village_name or not taluka_name or (not followup_list_enter_date and not duration):
            fields = get_glific_contact_fields(supervisor_phone)
            if not village_name:
                village_name = fields.get("followup_list_village_name")
            if not taluka_name:
                taluka_name = fields.get("followup_list_taluka_name")
            if not followup_list_enter_date and not duration:
                followup_list_enter_date = clean_glific_value(
                    fields.get("followup_list_enter_date") or fields.get("followuplist_enter_date")
                )
                if not followup_list_enter_date:
                    duration = fields.get("followup_list_duration")

    # 1. Calculate duration / specific date filters
    from frappe.utils import today, getdate, add_months
    import calendar

    now_date = getdate(today())
    start_date = None
    end_date = None
    duration_label_mr = "या महिन्यातील" if lang == "mr" else ("इस महीने" if lang == "hi" else "this month")

    # Priority 1: Check if specific date was provided (e.g. DD/MM/YYYY)
    parsed_specific_date = None
    if followup_list_enter_date:
        parsed_specific_date = parse_date(followup_list_enter_date)
        if not parsed_specific_date:
            err_msg = "❌ दिलेली तारीख योग्य नाही. कृपया DD/MM/YYYY स्वरूपात तारीख टाका (उदा. 15/08/2024)." if lang == "mr" else "❌ Invalid date format. Please enter date in DD/MM/YYYY format."
            return {
                "formatted_text": err_msg,
                "count": 0,
            }

    # Also check if duration itself was passed as a specific date string (e.g. "15/08/2024" or "2024-08-15")
    if not parsed_specific_date and duration:
        duration_candidate = clean_glific_value(duration)
        if duration_candidate and ("/" in duration_candidate or (("-" in duration_candidate) and len(duration_candidate) >= 8)):
            parsed_specific_date = parse_date(duration_candidate)

    if parsed_specific_date:
        start_date = parsed_specific_date
        end_date = parsed_specific_date
        duration_label_mr = f"{parsed_specific_date.strftime('%d/%m/%Y')} रोजी" if lang == "mr" else f"on {parsed_specific_date.strftime('%d/%m/%Y')}"
    else:
        # Clean duration input
        duration_clean = (clean_glific_value(duration) or "").strip().lower()
        
        # Check if duration input is an "Enter date" selection option
        if duration_clean in ("enter date", "enter_date", "तारीख प्रविष्ट करा", "तारीख टाका", "दिनांक टाका"):
            return {
                "formatted_text": "कृपया DD/MM/YYYY स्वरूपात तारीख टाका (उदा. 15/08/2024):",
                "count": 0,
                "requires_date_input": True
            }

        # Map Marathi & Hindi duration inputs to standard English values
        duration_map = {
            "या महिन्यात": "this_month",
            "चालू महिना": "this_month",
            "गेल्या महिन्यात": "last_month",
            "मागील महिना": "last_month",
            "गेल्या ३ महिन्यांत": "last_3_months",
            "मागील ३ महिने": "last_3_months",
            "गेल्या ६ महिन्यांत": "past_6_months",
            "मागील ६ महिने": "past_6_months",
            "सर्व काळ": "all_time",
            "सुरुवातीपासून": "all_time",
            "this month": "this_month",
            "last month": "last_month",
            "last 3 months": "last_3_months",
            "past 6 months": "past_6_months",
            "all time": "all_time",
            "इस महीने": "this_month",
            "पिछले महीने": "last_month",
            "पिछले 3 महीनों में": "last_3_months",
            "पिछले 6 महीनों में": "past_6_months",
            "सभी समय": "all_time",
            "शुरुआत से": "all_time"
        }

        if duration_clean in duration_map:
            duration_clean = duration_map[duration_clean]
        else:
            # Fallback substring checks for extra safety
            if "सर्व" in duration_clean or "सभी" in duration_clean:
                duration_clean = "all_time"
            elif "३" in duration_clean or "3" in duration_clean:
                duration_clean = "last_3_months"
            elif "६" in duration_clean or "6" in duration_clean:
                duration_clean = "past_6_months"
            elif "गेल्या" in duration_clean or "मागील" in duration_clean or "पिछले" in duration_clean or "पिछला" in duration_clean or "last" in duration_clean:
                duration_clean = "last_month"
            elif "या" in duration_clean or "चालू" in duration_clean or "इस" in duration_clean or "this" in duration_clean:
                duration_clean = "this_month"

        if duration_clean in ("this_month", "this month", "this"):
            start_date = getdate(f"{now_date.year}-{now_date.month:02d}-01")
            _, last_day = calendar.monthrange(now_date.year, now_date.month)
            end_date = getdate(f"{now_date.year}-{now_date.month:02d}-{last_day:02d}")
            duration_label_mr = "या महिन्यातील" if lang == "mr" else "this month"
            
        elif duration_clean in ("last_month", "last month", "last"):
            prev_date = add_months(now_date, -1)
            start_date = getdate(f"{prev_date.year}-{prev_date.month:02d}-01")
            _, last_day = calendar.monthrange(prev_date.year, prev_date.month)
            end_date = getdate(f"{prev_date.year}-{prev_date.month:02d}-{last_day:02d}")
            duration_label_mr = "गेल्या महिन्यातील" if lang == "mr" else "last month"
            
        elif duration_clean in ("last_3_months", "last 3 months", "3"):
            start_date = add_months(now_date, -3)
            end_date = now_date
            duration_label_mr = "गेल्या ३ महिन्यांतील" if lang == "mr" else "last 3 months"
            
        elif duration_clean in ("past_6_months", "past 6 months", "6"):
            start_date = add_months(now_date, -6)
            end_date = now_date
            duration_label_mr = "गेल्या ६ महिन्यांतील" if lang == "mr" else "past 6 months"
            
        elif duration_clean in ("all_time", "all time", "all"):
            start_date = None
            end_date = None
            duration_label_mr = "सर्व काळातील" if lang == "mr" else "all time"
        else:
            # Fallback to month/year if specifically provided as integers
            if month:
                target_year = year or now_date.year
                target_month = month
                try:
                    target_month = int(target_month)
                    target_year = int(target_year)
                except (ValueError, TypeError):
                    target_month = now_date.month
                    target_year = now_date.year
                if 1 <= target_month <= 12:
                    _, last_day = calendar.monthrange(target_year, target_month)
                    start_date = getdate(f"{target_year}-{target_month:02d}-01")
                    end_date = getdate(f"{target_year}-{target_month:02d}-{last_day:02d}")
                    month_names_mr = {
                        1: "जानेवारी", 2: "फेब्रुवारी", 3: "मार्च", 4: "एप्रिल",
                        5: "मे", 6: "जून", 7: "जुलै", 8: "ऑगस्ट",
                        9: "सप्टेंबर", 10: "ऑक्टोबर", 11: "नोव्हेंबर", 12: "डिसेंबर"
                    }
                    duration_label_mr = f"{month_names_mr.get(target_month, '')} {target_year} मधील"
            else:
                # Default to this month
                start_date = getdate(f"{now_date.year}-{now_date.month:02d}-01")
                _, last_day = calendar.monthrange(now_date.year, now_date.month)
                end_date = getdate(f"{now_date.year}-{now_date.month:02d}-{last_day:02d}")
                duration_label_mr = "या महिन्यातील"

    # Set up pending referrals filters
    filters = {"status": ["in", ["Pending", "Follow-up In Progress"]]}
    
    if start_date:
        if end_date:
            filters["referral_date"] = ["between", [start_date, end_date]]
        else:
            filters["referral_date"] = [">=", start_date]
    elif end_date:
        filters["referral_date"] = ["<=", end_date]

    resolved_taluka = None
    if taluka_name:
        resolved_taluka = resolve_taluka(taluka_name)
        if not resolved_taluka:
            return {
                "formatted_text": f"❌ तालुका '{taluka_name}' आढळला नाही. कृपया तालुका तपासा आणि पुन्हा प्रयत्न करा.",
                "count": 0,
            }
        filters["patient_taluka"] = resolved_taluka

    resolved_village_name_mr = None
    village_id = None
    if village_name:
        village_id = resolve_village(village_name, taluka=resolved_taluka)
        if not village_id:
            return {
                "formatted_text": f"❌ गाव '{village_name}' आढळले नाही. कृपया गावाचे नाव तपासा आणि पुन्हा प्रयत्न करा.",
                "count": 0,
            }
        
        # Get village profile info
        v_profile = frappe.db.get_value("Village Profile", village_id, ["village_name", "village_name_marathi"], as_dict=True) or {}
        v_name_eng = v_profile.get("village_name") or village_name
        v_name_mr = v_profile.get("village_name_marathi") or village_name
        resolved_village_name_mr = v_name_mr

        # Support querying by Village Profile document ID, English name, Marathi name, or raw input
        possible_village_keys = list({k for k in [village_id, v_name_eng, v_name_mr, village_name] if k})
        if len(possible_village_keys) == 1:
            filters["patient_village"] = possible_village_keys[0]
        else:
            filters["patient_village"] = ["in", possible_village_keys]

    # 1. Fetch pending referrals
    referrals = frappe.get_all(
        "Patient Referral",
        filters=filters,
        fields=[
            "reference_number",
            "patient_name",
            "patient_age",
            "patient_gender",
            "patient_village",
            "patient_taluka",
            "referral_date",
            "service_facility_type",
            "opd_departments",
            "opd_category",
            "other_facility_name",
            "visit_count",
            "raw_patient_data",
            "referred_by_who",
        ],
        order_by="referral_date asc, patient_village asc",
    )

    # 2. Fetch visited SEARCH referrals
    # Build visited query conditions dynamically based on filters
    query_conditions = [
        "pr.status = 'Visited'",
        "sv.facility_visited = 'SEARCH'",
        "sv.patient_visited = 1"
    ]
    query_args = []
    
    if start_date:
        query_conditions.append("sv.visit_date >= %s")
        query_args.append(start_date)
    if end_date:
        query_conditions.append("sv.visit_date <= %s")
        query_args.append(end_date)

    if village_id:
        if len(possible_village_keys) == 1:
            query_conditions.append("pr.patient_village = %s")
            query_args.append(possible_village_keys[0])
        else:
            query_conditions.append("pr.patient_village IN %s")
            query_args.append(tuple(possible_village_keys))
    elif resolved_taluka:
        query_conditions.append("pr.patient_taluka = %s")
        query_args.append(resolved_taluka)

    sql_query = f"""
        SELECT DISTINCT 
            pr.reference_number, pr.patient_name, pr.patient_age, pr.patient_gender,
            pr.patient_village, pr.patient_taluka, pr.referral_date, pr.service_facility_type,
            pr.opd_departments, pr.opd_category, pr.other_facility_name, pr.visit_count,
            pr.raw_patient_data, pr.referred_by_who, sv.visit_date
        FROM `tabPatient Referral` pr
        JOIN `tabSupervisor Visit` sv ON sv.parent = pr.name
        WHERE {" AND ".join(query_conditions)}
        ORDER BY sv.visit_date DESC
    """
    visited_referrals = []
    if village_id or resolved_taluka:
        visited_referrals = frappe.db.sql(sql_query, tuple(query_args), as_dict=True)

    if not referrals and not visited_referrals:
        if village_name:
            no_rec_txt = f"या गावात ({resolved_village_name_mr or village_name}), या कालावधीत कोणतेही रुग्ण रेफर केले नाहीत ✅" if lang == "mr" else f"No pending or visited patients found in {village_name} ✅"
            return {
                "formatted_text": no_rec_txt,
                "count": 0,
            }
        no_rec_txt = "सध्या कोणतेही प्रलंबित फॉलो-अप नाहीत ✅" if lang == "mr" else "No pending follow-ups currently ✅"
        return {
            "formatted_text": no_rec_txt,
            "count": 0,
        }

    # Resolve village links to display names
    village_names = {}
    all_village_ids = set()
    all_raw_ids = set()
    for r in referrals:
        if r.patient_village:
            all_village_ids.add(r.patient_village)
        if getattr(r, "raw_patient_data", None):
            all_raw_ids.add(r.raw_patient_data)
    for r in visited_referrals:
        if r.patient_village:
            all_village_ids.add(r.patient_village)
        if getattr(r, "raw_patient_data", None):
            all_raw_ids.add(r.raw_patient_data)

    if all_village_ids:
        for v in frappe.get_all(
            "Village Profile",
            filters={"name": ["in", list(all_village_ids)]},
            fields=["name", "village_name", "village_name_marathi"],
        ):
            if lang == "mr":
                village_names[v.name] = v.village_name_marathi or v.village_name
            else:
                village_names[v.name] = v.village_name or v.village_name_marathi

    raw_names = {}
    if all_raw_ids:
        raw_doctype = "Raw Patient Referral Data" if frappe.db.exists("DocType", "Raw Patient Referral Data") else "Raw Patient Data"
        for rp in frappe.get_all(
            raw_doctype,
            filters={"name": ["in", list(all_raw_ids)]},
            fields=["name", "patient_name_raw"],
        ):
            raw_names[rp.name] = rp.patient_name_raw

    if lang == "mr":
        lines = ["*रेफर सर्च — फॉलो-अप यादी* 📋", ""]
        age_label = "वय"
        dept_label = "विभाग"
        ref_by_label = "रेफर करणारे"
        visited_date_label = "भेट तारीख"
        next_visit_label = "पुढील भेट क्र."
    elif lang == "hi":
        lines = ["*रेफर सर्च — फॉलो-अप सूची* 📋", ""]
        age_label = "उम्र"
        dept_label = "विभाग"
        ref_by_label = "रेफर करने वाले"
        visited_date_label = "विज़िट तिथि"
        next_visit_label = "अगली विज़िट क्र."
    else:
        lines = ["*Referral SEARCH — Follow-up List* 📋", ""]
        age_label = "Age"
        dept_label = "Dept"
        ref_by_label = "Referred By"
        visited_date_label = "Visit Date"
        next_visit_label = "Next Visit #"

    # Format Pending Section
    if referrals:
        # Group by referral date, then village
        grouped = defaultdict(lambda: defaultdict(list))
        for r in referrals:
            date_str = r.referral_date.strftime("%d/%m/%y")
            village_display = village_names.get(r.patient_village, r.patient_village or ("गाव नोंद नाही" if lang == "mr" else "No Village"))
            grouped[date_str][village_display].append(r)

        for date_str in sorted(
            grouped.keys(),
            key=lambda d: frappe.utils.getdate("20" + d.split("/")[2] + "-" + d.split("/")[1] + "-" + d.split("/")[0]),
        ):
            villages = grouped[date_str]
            for village, patients in villages.items():
                lines.append(f"🟦 *{date_str}* ({village})")
                for i, p in enumerate(patients, 1):
                    raw_name = raw_names.get(p.raw_patient_data) if getattr(p, "raw_patient_data", None) else None
                    p_name = format_patient_name(p.patient_name, raw_name, lang)
                    p_age = format_age_display(p.patient_age)
                    p_gender = format_gender(p.patient_gender, lang)
                    hospital = format_facility(p.service_facility_type, p.other_facility_name, lang)
                    dept_display = format_opd(p.opd_departments or p.opd_category or "-", lang)
                    ref_by = format_referred_by_who(getattr(p, "referred_by_who", None), lang)

                    lines.append(f"{i}) *{p_name}*")
                    lines.append(f"{age_label}-{p_age}/{p_gender}")
                    lines.append(f"🏥 {hospital} | {dept_label}: {dept_display}")
                    if ref_by:
                        lines.append(f"🔹 {ref_by_label}: {ref_by}")
                    lines.append(f"🔖 {p.reference_number}")
                    if p.visit_count and p.visit_count > 0:
                        lines.append(f"{next_visit_label} {p.visit_count + 1}")
                    lines.append("──────────────────")
    else:
        if visited_referrals:
            if lang == "mr":
                lines.append("प्रलंबित फॉलो-अप: काहीही नाही ✅")
            elif lang == "hi":
                lines.append("लंबित फॉलो-अप: कोई नहीं ✅")
            else:
                lines.append("Pending follow-ups: None ✅")
            lines.append("──────────────────")

    # Format Visited Section
    if visited_referrals:
        if lang == "mr":
            lines.append(f"✅ *{duration_label_mr} SEARCH ला भेट दिलेले रुग्ण:*")
        elif lang == "hi":
            lines.append(f"✅ *{duration_label_mr} SEARCH अस्पताल आए हुए मरीज़:*")
        else:
            lines.append(f"✅ *Patients who visited SEARCH {duration_label_mr}:*")
        lines.append("")

        for i, p in enumerate(visited_referrals, 1):
            v_date_str = p.visit_date.strftime("%d/%m/%y") if p.visit_date else "-"
            village_display = village_names.get(p.patient_village, p.patient_village or ("गाव नोंद नाही" if lang == "mr" else "No Village"))
            raw_name = raw_names.get(p.raw_patient_data) if getattr(p, "raw_patient_data", None) else None
            p_name = format_patient_name(p.patient_name, raw_name, lang)
            p_age = format_age_display(p.patient_age)
            p_gender = format_gender(p.patient_gender, lang)
            ref_by = format_referred_by_who(getattr(p, "referred_by_who", None), lang)

            lines.append(f"{i}) *{p_name}* ({village_display})")
            lines.append(f"{age_label}-{p_age}/{p_gender}")
            lines.append(f"📅 {visited_date_label}: {v_date_str}")
            if ref_by:
                lines.append(f"🔹 {ref_by_label}: {ref_by}")
            lines.append(f"🔖 {p.reference_number}")
            lines.append("──────────────────")

    formatted = "\n".join(lines).strip()

    # WhatsApp message hard limit is 4096 chars. Truncate safely if huge.
    if len(formatted) > 3900:
        trunc_msg = "\n\n... यादी खूप मोठी आहे. कृपया प्रशासकाशी संपर्क साधा." if lang == "mr" else "\n\n... List is too long. Please contact admin."
        formatted = formatted[:3900] + trunc_msg

    return {"formatted_text": formatted, "count": len(referrals)}


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


@frappe.whitelist()
def insert_samples():
    print("Clearing existing referrals...")
    frappe.db.delete("Patient Referral")
    
    samples = [
        # Referral 1: Oldest date
        {
            "contact_phone": "9876543210",
            "patient_name_raw": "Ramesh Madavi",
            "father_name_raw": "Laxman",
            "gender_raw": "Male",
            "age_raw": "48",
            "village_raw": "Alaknar",
            "patient_taluka_raw": "Dhanora",
            "service_facility_type": "SEARCH",
            "opd_category_raw": "Regular OPD",
            "departments_raw": "Medicine",
            "referral_date_raw": "01/07/2026",
            "patient_phone_raw": "9100000001",
            "referring_doctor_raw": "Dr. Patil"
        },
        # Referral 2: Government facility
        {
            "contact_phone": "9876543210",
            "patient_name_raw": "Sunita Pudo",
            "father_name_raw": "Raju",
            "gender_raw": "Female",
            "age_raw": "35",
            "village_raw": "Ambezari",
            "patient_taluka_raw": "Dhanora",
            "service_facility_type": "Government Hospital",
            "referral_date_raw": "02/07/2026",
            "patient_phone_raw": "9100000002",
            "referring_doctor_raw": "Dr. Patil"
        },
        # Referral 3: Same date, village Arjuni (Patient A)
        {
            "contact_phone": "9876543210",
            "patient_name_raw": "Vilas Atram",
            "father_name_raw": "Sukhdeo",
            "gender_raw": "Male",
            "age_raw": "50",
            "village_raw": "Arjuni",
            "patient_taluka_raw": "Dhanora",
            "service_facility_type": "Other",
            "other_facility_raw": "Civil Hospital Nagpur",
            "referral_date_raw": "05/07/2026",
            "patient_phone_raw": "9100000003",
            "referring_doctor_raw": "Dr. Patil"
        },
        # Referral 4: Same date, village Arjuni (Patient B)
        {
            "contact_phone": "9876543210",
            "patient_name_raw": "Kamla Halami",
            "father_name_raw": "Devaji",
            "gender_raw": "Female",
            "age_raw": "60",
            "village_raw": "Arjuni",
            "patient_taluka_raw": "Dhanora",
            "service_facility_type": "SEARCH",
            "opd_category_raw": "Cataract Surgery",
            "departments_raw": "Ophthalmology",
            "referral_date_raw": "05/07/2026",
            "patient_phone_raw": "9100000004",
            "referring_doctor_raw": "Dr. Patil"
        },
        # Referral 5: Follow-up In Progress
        {
            "contact_phone": "9876543210",
            "patient_name_raw": "Devidas Usendi",
            "father_name_raw": "Kavdu",
            "gender_raw": "Male",
            "age_raw": "28",
            "village_raw": "Aswalpar",
            "patient_taluka_raw": "Dhanora",
            "service_facility_type": "SEARCH",
            "opd_category_raw": "Specialist OPD",
            "departments_raw": "Diabetology",
            "referral_date_raw": "07/07/2026",
            "patient_phone_raw": "9100000005",
            "referring_doctor_raw": "Dr. Patil"
        }
    ]
    
    for i, s in enumerate(samples, 1):
        res = create_referral(**s)
        if res.get("success"):
            ref_num = res.get("reference_number")
            print(f"Created referral {i}: {ref_num} for {s['patient_name_raw']}")
            
            # Record a visit for the last patient to set it to Follow-up In Progress
            if s["patient_name_raw"] == "Devidas Usendi":
                visit_res = record_supervisor_visit(
                    referral_id=ref_num,
                    supervisor_phone="9999999999",
                    visit_date="08-07-2026",
                    patient_visited="No",
                    non_visit_reason="NV-01: Financial Constraints"
                )
                if visit_res.get("success"):
                    print(f"Recorded follow-up visit for Devidas Usendi. Status: {visit_res.get('status')}")
        else:
            print(f"Failed to create referral {i}: {res.get('error')}")
            
    frappe.db.commit()
    return {"success": True}


# @frappe.whitelist()
def import_village_list() -> dict:
    """
    One-off import function to read 1500 villages from /Users/sakshi/Downloads/12 Taluka Village List (1500).xlsx
    and automatically translate village names into Marathi via deep_translator.
    """
    import openpyxl
    from deep_translator import GoogleTranslator

    file_path = "/Users/sakshi/Downloads/12 Taluka Village List (1500).xlsx"
    try:
        wb = openpyxl.load_workbook(file_path, read_only=True)
    except Exception as e:
        return {"success": False, "error": f"Failed to open workbook: {str(e)}"}

    if "1500 Village" not in wb.sheetnames:
        return {"success": False, "error": "Sheet '1500 Village' not found in workbook"}

    ws = wb["1500 Village"]
    rows = list(ws.iter_rows(values_only=True))

    count = 0
    skipped = 0
    translated = 0
    errors = 0

    # Get max village number to increment from
    max_num_list = frappe.get_all("Village Profile", fields=["village_number"], order_by="village_number desc", limit=1)
    current_num = max_num_list[0].village_number if max_num_list else 0
    if not isinstance(current_num, int):
        current_num = 0

    translator = GoogleTranslator(source="en", target="mr")

    for idx, r in enumerate(rows[2:], start=3):
        taluka_input, village_input = r[0], r[1]
        if not village_input:
            continue

        village_name = str(village_input).strip()
        taluka_clean = str(taluka_input).strip() if taluka_input else ""

        # Check if village already exists
        if frappe.db.exists("Village Profile", village_name):
            skipped += 1
            continue

        resolved_taluka = resolve_taluka(taluka_clean)
        if resolved_taluka and not frappe.db.exists("Taluka", resolved_taluka):
            try:
                t_doc = frappe.get_doc({
                    "doctype": "Taluka",
                    "taluka_name": resolved_taluka,
                    "taluka_code": resolved_taluka[:3].upper(),
                    "district": "Gadchiroli",
                    "state": "Maharashtra"
                })
                t_doc.insert(ignore_permissions=True)
            except Exception:
                pass

        # Translate to Marathi
        village_name_marathi = None
        try:
            marathi = translator.translate(village_name)
            if marathi and marathi != village_name:
                village_name_marathi = marathi
                translated += 1
        except Exception:
            errors += 1

        current_num += 1

        doc = frappe.get_doc({
            "doctype": "Village Profile",
            "village_name": village_name,
            "village_number": current_num,
            "taluka": resolved_taluka,
            "village_name_marathi": village_name_marathi
        })
        doc.insert(ignore_permissions=True)
        count += 1

        if count % 100 == 0:
            frappe.db.commit()

    frappe.db.commit()
    return {
        "success": True,
        "imported": count,
        "skipped": skipped,
        "translated": translated,
        "translation_errors": errors
    }


@frappe.whitelist(allow_guest=True)
def search_and_resolve_village(village_input: str = None, taluka: str = None, contact_phone: str = None, language: str = None, **kwargs) -> dict:
    import json

    # Glific POSTs JSON — fall back to parsing the raw body for keys that
    # don't match the function's parameter names exactly (e.g. the flow
    # sends "taluka_input" instead of "taluka").
    if frappe.request:
        try:
            raw_data = frappe.request.get_data(as_text=True)
            if raw_data:
                data = json.loads(raw_data)
                if isinstance(data, dict):
                    village_input = village_input or data.get("village_input")
                    taluka = taluka or data.get("taluka") or data.get("taluka_input")
                    contact_phone = contact_phone or data.get("contact_phone") or data.get("phone")
                    language = language or data.get("language")
        except Exception:
            pass

    village_clean = clean_glific_value(village_input)
    taluka_clean = clean_glific_value(taluka)
    contact_phone = clean_glific_value(contact_phone)
    lang = (clean_glific_value(language) or "mr").strip().lower()
    if is_devanagari(village_clean) and not language:
        lang = "mr"
    if lang not in ("en", "hi", "mr"):
        lang = "mr"

    if not village_clean:
        return {
            "success": False,
            "resolved": False,
            "village_name": None,
            "formatted_text": village_msg("village_empty", lang),
            "matches": []
        }

    # 1. Try exact match (English or Marathi) in specified taluka first
    # Auto-resolve ONLY on exact match. Partial inputs (e.g. 3-letter prefixes)
    # should show the candidate options list as designed.
    resolved_taluka = resolve_taluka(taluka_clean) if taluka_clean else None
    exact_village = None

    if resolved_taluka:
        exact_village = frappe.db.get_value(
            "Village Profile", {"village_name": village_clean, "taluka": resolved_taluka}, "name"
        )
        if not exact_village and is_devanagari(village_clean):
            exact_village = frappe.db.get_value(
                "Village Profile", {"village_name_marathi": village_clean, "taluka": resolved_taluka}, "name"
            )
        if not exact_village:
            # Case-insensitive English in taluka
            v_match = frappe.db.sql("""
                SELECT name FROM `tabVillage Profile`
                WHERE LOWER(village_name) = LOWER(%(name)s) AND taluka = %(taluka)s
                LIMIT 1
            """, {"name": village_clean, "taluka": resolved_taluka}, as_dict=True)
            if v_match:
                exact_village = v_match[0].name

    if not exact_village and len(village_clean) >= 4:
        # Full exact match across all talukas (only if 4+ characters)
        exact_village = frappe.db.get_value(
            "Village Profile", {"village_name": village_clean}, "name"
        )
        if not exact_village and is_devanagari(village_clean):
            exact_village = frappe.db.get_value(
                "Village Profile", {"village_name_marathi": village_clean}, "name"
            )

    if exact_village:
        display_name = village_display_name(exact_village, lang)
        return {
            "success": True,
            "resolved": True,
            "village_name": exact_village,
            "formatted_text": village_msg("resolved", lang, name=display_name),
            "matches": []
        }

    # 2. Multi-tier phonetic & fuzzy candidate search
    from rapidfuzz import fuzz

    query = village_clean.strip().lower()
    q_is_dev = is_devanagari(query)
    q_skel = devanagari_skeleton(query) if q_is_dev else ""
    q_roman = transliterate_to_roman(query).strip().lower() if q_is_dev else query

    def score_villages(village_list):
        scored = []
        for v in village_list:
            name_eng = (v.village_name or "").strip().lower()
            name_mr = (v.village_name_marathi or "").strip().lower()
            if not name_eng and not name_mr:
                continue

            mr_skel = devanagari_skeleton(name_mr) if name_mr else ""
            v_roman = transliterate_to_roman(name_mr).strip().lower() if name_mr else name_eng

            score = 0
            if query == name_eng or (name_mr and query == name_mr):
                score = 100
            elif name_mr and name_mr.startswith(query):
                score = 90
            elif name_eng and name_eng.startswith(query):
                score = 90
            elif q_skel and mr_skel and mr_skel.startswith(q_skel):
                score = 85
            elif name_mr and query in name_mr:
                score = 75
            elif name_eng and query in name_eng:
                score = 75
            elif q_skel and mr_skel and q_skel in mr_skel:
                score = 70
            elif (name_eng and name_eng.startswith(q_roman)) or (v_roman and v_roman.startswith(q_roman)):
                score = 65
            else:
                # Check if individual words inside multi-word English names start with q_roman (e.g. 'Amgaon' in 'Made Amgaon')
                matched_word = False
                if len(q_roman) >= 3:
                    for w in name_eng.split():
                        if w.startswith(q_roman):
                            score = 60
                            matched_word = True
                            break
                if not matched_word:
                    rf = max(
                        fuzz.ratio(q_roman, name_eng),
                        fuzz.ratio(q_roman, v_roman) if v_roman else 0
                    )
                    if rf >= 75:
                        score = rf * 0.6

            if score > 0:
                scored.append((score, v.name))
        return scored

    # Search in taluka first
    filters = {"taluka": resolved_taluka} if resolved_taluka else {}
    villages = frappe.get_all(
        "Village Profile",
        filters=filters,
        fields=["name", "village_name", "village_name_marathi"]
    )
    matches = score_villages(villages)

    # If no matches found in taluka, fallback to search across all talukas
    if not matches and resolved_taluka:
        all_villages = frappe.get_all(
            "Village Profile",
            fields=["name", "village_name", "village_name_marathi"]
        )
        matches = score_villages(all_villages)

    # Sort matches by score descending, then by length ascending (prefer direct concise names)
    matches.sort(key=lambda x: (x[0], -len(x[1])), reverse=True)

    unique_matches = []
    seen = set()
    for score, m_name in matches:
        if m_name not in seen:
            seen.add(m_name)
            unique_matches.append(m_name)
            if len(unique_matches) >= 5:
                break

    if not unique_matches:
        return {
            "success": True,
            "resolved": False,
            "village_name": None,
            "formatted_text": village_msg("no_match_in_taluka", lang),
            "matches": []
        }

    # Persist the candidate list server-side, keyed by the WhatsApp phone
    # number, so resolve_village_selection can retrieve it later without
    # needing the flow to hand the array back.
    if contact_phone:
        frappe.cache().set_value(
            f"village_matches:{contact_phone}",
            unique_matches,
            expires_in_sec=VILLAGE_MATCH_CACHE_TTL_SECONDS,
        )
    else:
        frappe.logger().warning(
            "[search_and_resolve_village] No contact_phone provided — cannot cache matches for later selection"
        )

    lines = [village_msg("did_you_mean", lang)]
    for i, m_name in enumerate(unique_matches):
        lines.append(f"{i + 1}. {village_display_name(m_name, lang)}")
    lines.append(f"{len(unique_matches) + 1}. {village_msg('none_of_these', lang)}")

    return {
        "success": True,
        "resolved": False,
        "village_name": None,
        "formatted_text": "\n".join(lines),
        "matches": unique_matches,
    }


@frappe.whitelist(allow_guest=True)
def resolve_village_selection(selection_input: str = None, contact_phone: str = None, language: str = None, **kwargs) -> dict:
    import json

    if frappe.request:
        try:
            raw_data = frappe.request.get_data(as_text=True)
            if raw_data:
                data = json.loads(raw_data)
                if isinstance(data, dict):
                    selection_input = selection_input or data.get("selection_input")
                    contact_phone = contact_phone or data.get("contact_phone") or data.get("phone")
                    language = language or data.get("language")
        except Exception:
            pass

    sel_clean = clean_glific_value(selection_input)
    contact_phone = clean_glific_value(contact_phone)
    lang = (clean_glific_value(language) or "mr").strip().lower()
    if lang not in ("en", "hi", "mr"):
        lang = "mr"

    if not sel_clean:
        return {"success": False, "resolved": False, "village_name": None}
    if not contact_phone:
        return {"success": False, "resolved": False, "village_name": None, "error": "Missing contact_phone"}

    num_map = {
        "१": 1, "२": 2, "३": 3, "४": 4, "५": 5, "६": 6, "७": 7, "८": 8, "९": 9, "०": 0
    }
    sel_str = sel_clean.strip()
    for dev_digit, eng_digit in num_map.items():
        sel_str = sel_str.replace(dev_digit, str(eng_digit))

    try:
        index = int(sel_str)
    except ValueError:
        return {"success": False, "resolved": False, "village_name": None}

    matches_list = frappe.cache().get_value(f"village_matches:{contact_phone}")
    if not matches_list:
        return {
            "success": False,
            "resolved": False,
            "village_name": None,
            "error": village_msg("session_expired", lang),
        }

    if index == len(matches_list) + 1:
        return {
            "success": True,
            "resolved": False,
            "village_name": None
        }

    if 1 <= index <= len(matches_list):
        selected_name = matches_list[index - 1]
        # Clear the cache entry once resolved
        frappe.cache().delete_value(f"village_matches:{contact_phone}")
        display_name = village_display_name(selected_name, lang)
        return {
            "success": True,
            "resolved": True,
            "village_name": selected_name,
            "formatted_text": village_msg("resolved", lang, name=display_name)
        }

    return {"success": False, "resolved": False, "village_name": None}


@frappe.whitelist()
def export_translated_villages():
    import json
    villages = frappe.get_all(
        "Village Profile",
        fields=["village_name", "village_name_marathi", "taluka", "village_number"]
    )
    with open("translated_villages.json", "w", encoding="utf-8") as f:
        json.dump(villages, f, ensure_ascii=False, indent=4)
    return {"success": True, "count": len(villages)}


@frappe.whitelist()
def import_translated_villages():
    import json
    import os
    
    file_path = "translated_villages.json"
    if not os.path.exists(file_path):
        return {"success": False, "error": f"{file_path} not found"}
        
    with open(file_path, "r", encoding="utf-8") as f:
        villages = json.load(f)
        
    count = 0
    skipped = 0
    
    for v in villages:
        village_name = v.get("village_name")
        if not village_name:
            continue
            
        if frappe.db.exists("Village Profile", village_name):
            skipped += 1
            continue
            
        taluka = v.get("taluka")
        if taluka and not frappe.db.exists("Taluka", taluka):
            try:
                t_doc = frappe.get_doc({
                    "doctype": "Taluka",
                    "taluka_name": taluka,
                    "taluka_code": taluka[:3].upper(),
                    "district": "Gadchiroli",
                    "state": "Maharashtra"
                })
                t_doc.insert(ignore_permissions=True)
            except Exception:
                pass
                
        doc = frappe.get_doc({
            "doctype": "Village Profile",
            "village_name": village_name,
            "village_number": v.get("village_number"),
            "taluka": taluka,
            "village_name_marathi": v.get("village_name_marathi")
        })
        doc.insert(ignore_permissions=True)
        count += 1
        
        if count % 100 == 0:
            frappe.db.commit()
            
    frappe.db.commit()
    return {"success": True, "imported": count, "skipped": skipped}


def _parse_multi_filter_values(val):
	"""
	Parse filter values that may be passed as:
	- a list or tuple
	- a JSON array string e.g. '["Pending", "Visited"]'
	- a comma-separated string e.g. 'Pending, Visited'
	- a single string e.g. 'Pending'
	Returns a list of cleaned, non-empty strings.
	"""
	if not val:
		return []
	if isinstance(val, (list, tuple, set)):
		return [str(v).strip() for v in val if str(v).strip()]
	
	val_str = str(val).strip()
	if not val_str:
		return []
	
	if val_str.startswith("[") and val_str.endswith("]"):
		try:
			import json
			parsed = json.loads(val_str)
			if isinstance(parsed, list):
				return [str(v).strip() for v in parsed if str(v).strip()]
		except Exception:
			pass
			
	return [p.strip() for p in val_str.split(",") if p.strip()]


def _apply_multi_filter(conditions, values, field_sql, param_name, raw_val):
	items = _parse_multi_filter_values(raw_val)
	if not items:
		return
	if len(items) == 1:
		conditions.append(f"{field_sql} = %({param_name})s")
		values[param_name] = items[0]
	else:
		conditions.append(f"{field_sql} IN %({param_name})s")
		values[param_name] = tuple(items)


def _get_filtered_referrals(form_dict):
	search = form_dict.get("search", "").strip()
	status = form_dict.get("status")
	village = form_dict.get("village")
	phc = form_dict.get("phc")
	opd_department = form_dict.get("opd_department")
	start_date = form_dict.get("start_date", "").strip()
	end_date = form_dict.get("end_date", "").strip()
	referred_by_who = form_dict.get("referred_by_who")
	taluka = form_dict.get("taluka")
	referring_doctor = form_dict.get("referring_doctor")
	referrer_name = form_dict.get("referrer_name")
	gender = form_dict.get("gender")
	min_age = form_dict.get("min_age", "").strip()
	max_age = form_dict.get("max_age", "").strip()
	opd_category = form_dict.get("opd_category")
	service_facility_type = form_dict.get("service_facility_type")
	facility_visited = form_dict.get("facility_visited")
	referrer_department = form_dict.get("referrer_department")
	tribal_classification = form_dict.get("tribal_classification")

	conditions = []
	values = {}

	if search:
		conditions.append("(reference_number LIKE %(search)s OR patient_name LIKE %(search)s OR patient_phone LIKE %(search)s OR referrer_name LIKE %(search)s)")
		values["search"] = f"%{search}%"

	_apply_multi_filter(conditions, values, "status", "status", status)
	_apply_multi_filter(conditions, values, "patient_village", "village", village)
	_apply_multi_filter(conditions, values, "patient_taluka", "taluka", taluka)
	_apply_multi_filter(conditions, values, "tribal_classification", "tribal_classification", tribal_classification)
	_apply_multi_filter(conditions, values, "phc", "phc", phc)
	_apply_multi_filter(conditions, values, "service_facility_type", "service_facility_type", service_facility_type)
	_apply_multi_filter(conditions, values, "opd_category", "opd_category", opd_category)
	_apply_multi_filter(conditions, values, "opd_departments", "opd_department", opd_department)
	_apply_multi_filter(conditions, values, "facility_visited", "facility_visited", facility_visited)
	_apply_multi_filter(conditions, values, "referred_by_who", "referred_by_who", referred_by_who)
	_apply_multi_filter(conditions, values, "referrer_name", "referrer_name", referrer_name)
	_apply_multi_filter(conditions, values, "referrer_department", "referrer_department", referrer_department)
	_apply_multi_filter(conditions, values, "patient_gender", "gender", gender)

	doc_items = _parse_multi_filter_values(referring_doctor)
	if doc_items:
		if len(doc_items) == 1:
			conditions.append("(referred_doctor = %(referring_doctor)s OR referred_doctor LIKE %(referring_doctor_like)s)")
			values["referring_doctor"] = doc_items[0]
			values["referring_doctor_like"] = f"%{doc_items[0]}%"
		else:
			doc_conds = []
			for idx, d_item in enumerate(doc_items):
				d_key = f"referring_doctor_{idx}"
				d_like_key = f"referring_doctor_like_{idx}"
				doc_conds.append(f"(referred_doctor = %({d_key})s OR referred_doctor LIKE %({d_like_key})s)")
				values[d_key] = d_item
				values[d_like_key] = f"%{d_item}%"
			conditions.append(f"({' OR '.join(doc_conds)})")

	if start_date:
		conditions.append("referral_date >= %(start_date)s")
		values["start_date"] = start_date
	if end_date:
		conditions.append("referral_date <= %(end_date)s")
		values["end_date"] = end_date
	if min_age:
		conditions.append("patient_age >= %(min_age)s")
		values["min_age"] = frappe.utils.cint(min_age)
	if max_age:
		conditions.append("patient_age <= %(max_age)s")
		values["max_age"] = frappe.utils.cint(max_age)

	where_clause = " AND ".join(conditions) if conditions else "1=1"

	query = f"""
		SELECT 
			name, reference_number, referral_date, referral_recorded_date, status,
			referrer, referrer_name, referrer_phone, referrer_department,
			patient_name, patient_father_name, patient_gender, patient_age,
			patient_village, patient_taluka, service_facility_type, opd_category,
			other_facility_name, patient_phone, phc, opd_departments, referred_doctor,
			referred_by_who, additional_notes, hospital_registration_number, visit_date, 
			facility_visited, tribal_classification, creation
		FROM `tabPatient Referral`
		WHERE {where_clause}
		ORDER BY referral_date DESC, creation DESC
	"""
	return frappe.db.sql(query, values, as_dict=True)


@frappe.whitelist()
def export_referrals_excel():
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication required"), frappe.PermissionError)
	if "System Manager" not in frappe.get_roles() and not frappe.has_permission("Patient Referral", "read"):
		frappe.throw(_("You do not have permission to export referrals."), frappe.PermissionError)

	from frappe.utils.xlsxutils import make_xlsx
	from frappe.utils import today, format_date

	referrals = _get_filtered_referrals(frappe.form_dict)

	data = [[
		"Reference Number", "Referral Date", "Recorded Date", "Status",
		"Point of Referral", "Referrer Name", "Referrer Phone", "Referrer Dept",
		"Patient Name", "Father's Name", "Gender", "Age", "Phone",
		"Village", "Taluka", "Tribal Classification", "Service Facility Type",
		"OPD Category", "OPD Department", "Referred Doctor", "PHC",
		"Facility Visited", "Hospital Reg No", "Visit Date", "Notes"
	]]

	for ref in referrals:
		data.append([
			ref.get("reference_number") or "",
			format_date(ref.get("referral_date")) if ref.get("referral_date") else "",
			format_date(ref.get("referral_recorded_date")) if ref.get("referral_recorded_date") else "",
			ref.get("status") or "",
			ref.get("referred_by_who") or "",
			ref.get("referrer_name") or "",
			ref.get("referrer_phone") or "",
			ref.get("referrer_department") or "",
			ref.get("patient_name") or "",
			ref.get("patient_father_name") or "",
			ref.get("patient_gender") or "",
			ref.get("patient_age") or "",
			ref.get("patient_phone") or "",
			ref.get("patient_village") or "",
			ref.get("patient_taluka") or "",
			ref.get("tribal_classification") or "",
			ref.get("service_facility_type") or "",
			ref.get("opd_category") or "",
			ref.get("opd_departments") or "",
			ref.get("referred_doctor") or "",
			ref.get("phc") or "",
			ref.get("facility_visited") or "",
			ref.get("hospital_registration_number") or "",
			format_date(ref.get("visit_date")) if ref.get("visit_date") else "",
			frappe.utils.strip_html(ref.get("additional_notes") or "") if ref.get("additional_notes") else ""
		])

	xlsx_file = make_xlsx(data, "Patient Referrals")
	frappe.response['filename'] = f"Patient_Referrals_{today()}.xlsx"
	frappe.response['filecontent'] = xlsx_file.getvalue()
	frappe.response['type'] = 'binary'


@frappe.whitelist()
def export_referrals_pdf():
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication required"), frappe.PermissionError)
	if "System Manager" not in frappe.get_roles() and not frappe.has_permission("Patient Referral", "read"):
		frappe.throw(_("You do not have permission to export referrals."), frappe.PermissionError)

	from frappe.utils.pdf import get_pdf
	from frappe.utils import today, format_date, now_datetime

	referrals = _get_filtered_referrals(frappe.form_dict)

	# Format dates
	for ref in referrals:
		if ref.get("referral_date"):
			ref["referral_date_formatted"] = format_date(ref["referral_date"])
		else:
			ref["referral_date_formatted"] = ""

	# Summary of active filters
	filter_summary = []
	for key, label in [
		("search", "Search"), ("status", "Status"), ("gender", "Gender"),
		("village", "Village"), ("taluka", "Taluka"), ("phc", "PHC"),
		("opd_department", "OPD Dept"), ("opd_category", "OPD Category"),
		("service_facility_type", "Service Facility"), ("facility_visited", "Facility Visited"),
		("referred_by_who", "Point of Referral"), ("referrer_name", "Referrer"),
		("referrer_department", "Referrer Dept"), ("referring_doctor", "Doctor"),
		("tribal_classification", "Tribal"), ("start_date", "From Date"), ("end_date", "To Date")
	]:
		val = frappe.form_dict.get(key, "").strip()
		if val:
			filter_summary.append(f"<b>{label}:</b> {val}")

	filter_summary_str = " | ".join(filter_summary) if filter_summary else "All Records (No active filters)"

	html = f"""
	<!DOCTYPE html>
	<html>
	<head>
		<meta charset="utf-8">
		<title>Patient Referrals Report</title>
		<style>
			body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 11px; color: #1e293b; margin: 0; padding: 0; }}
			.header {{ text-align: center; border-bottom: 2px solid #059669; padding-bottom: 10px; margin-bottom: 14px; }}
			.title {{ font-size: 20px; font-weight: bold; color: #059669; margin: 0 0 4px 0; }}
			.subtitle {{ font-size: 13px; color: #475569; margin: 0; }}
			.meta-bar {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 14px; margin-bottom: 14px; font-size: 10px; color: #475569; }}
			.meta-item {{ margin-bottom: 4px; }}
			table {{ width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 10px; }}
			th {{ background-color: #f1f5f9; color: #0f172a; font-weight: bold; text-transform: uppercase; padding: 8px 6px; border: 1px solid #cbd5e1; text-align: left; font-size: 9px; }}
			td {{ padding: 6px; border: 1px solid #e2e8f0; color: #334155; vertical-align: top; }}
			tr:nth-child(even) {{ background-color: #f8fafc; }}
			.footer {{ text-align: right; font-size: 9px; color: #94a3b8; margin-top: 20px; border-top: 1px solid #e2e8f0; padding-top: 8px; }}
		</style>
	</head>
	<body>
		<div class="header">
			<h1 class="title">SEARCH Gadchiroli</h1>
			<p class="subtitle">Patient Referrals Report</p>
		</div>

		<div class="meta-bar">
			<div class="meta-item"><b>Generated On:</b> {now_datetime().strftime("%d-%m-%Y %H:%M")} | <b>Total Records:</b> {len(referrals)}</div>
			<div class="meta-item"><b>Applied Filters:</b> {filter_summary_str}</div>
		</div>

		<table>
			<thead>
				<tr>
					<th style="width: 10%;">Ref No.</th>
					<th style="width: 9%;">Ref Date</th>
					<th style="width: 11%;">Status</th>
					<th style="width: 15%;">Patient Name</th>
					<th style="width: 8%;">Age/Gender</th>
					<th style="width: 10%;">Village</th>
					<th style="width: 12%;">Point of Referral</th>
					<th style="width: 12%;">Referrer Name</th>
					<th style="width: 13%;">OPD Department</th>
				</tr>
			</thead>
			<tbody>
	"""

	for ref in referrals:
		html += f"""
				<tr>
					<td style="font-weight: bold;">{ref.get('reference_number') or ''}</td>
					<td>{ref.get('referral_date_formatted') or ''}</td>
					<td>{ref.get('status') or ''}</td>
					<td style="font-weight: bold;">{ref.get('patient_name') or ''}</td>
					<td>{ref.get('patient_age') or '-'} / {ref.get('patient_gender') or '-'}</td>
					<td>{ref.get('patient_village') or '-'}</td>
					<td>{ref.get('referred_by_who') or '-'}</td>
					<td>{ref.get('referrer_name') or '-'}</td>
					<td>{ref.get('opd_departments') or '-'}</td>
				</tr>
		"""

	if not referrals:
		html += """
				<tr>
					<td colspan="9" style="text-align: center; padding: 20px; color: #64748b;">No referral records match the selected filters.</td>
				</tr>
		"""

	html += """
			</tbody>
		</table>
		<div class="footer">
			Generated via SEARCH Referral Management Portal
		</div>
	</body>
	</html>
	"""

	try:
		pdf_file = get_pdf(html, {"orientation": "Landscape", "page-size": "A4"})
		frappe.response['filename'] = f"Patient_Referrals_Report_{today()}.pdf"
		frappe.response['filecontent'] = pdf_file
		frappe.response['type'] = 'pdf'
	except Exception:
		# Fallback to returning standalone print-optimized HTML report page
		html_printable = html.replace("</body>", "<script>window.onload = function() { window.print(); };</script></body>")
		frappe.response['type'] = 'html'
		frappe.response['body'] = html_printable






@frappe.whitelist()
def get_portal_referral_filter_options() -> dict:
    """Fetch distinct filter options for the referral management portal."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required"), frappe.PermissionError)

    def get_distinct(field):
        rows = frappe.db.sql(f"SELECT DISTINCT {field} FROM `tabPatient Referral` WHERE {field} IS NOT NULL AND {field} != ''")
        return sorted([r[0] for r in rows if r[0]])

    return {
        "villages": get_distinct("patient_village"),
        "talukas": get_distinct("patient_taluka"),
        "tribal_classifications": get_distinct("tribal_classification"),
        "phcs": get_distinct("phc"),
        "service_facility_types": get_distinct("service_facility_type"),
        "opd_categories": get_distinct("opd_category"),
        "opd_departments": get_distinct("opd_departments"),
        "facilities_visited": get_distinct("facility_visited"),
        "referred_by_whos": get_distinct("referred_by_who"),
        "referrer_names": get_distinct("referrer_name"),
        "referrer_departments": get_distinct("referrer_department"),
        "referring_doctors": get_distinct("referred_doctor"),
        "genders": get_distinct("patient_gender"),
        "statuses": ["Pending", "Follow-up In Progress", "Visited", "Closed - Not Visited", "No-Show", "Cancelled"]
    }


@frappe.whitelist()
def get_portal_referrals(
    search: str = None,
    status: str = None,
    village: str = None,
    taluka: str = None,
    tribal_classification: str = None,
    phc: str = None,
    service_facility_type: str = None,
    opd_category: str = None,
    opd_department: str = None,
    facility_visited: str = None,
    referred_by_who: str = None,
    referrer_name: str = None,
    referrer_department: str = None,
    referring_doctor: str = None,
    gender: str = None,
    min_age: str = None,
    max_age: str = None,
    start_date: str = None,
    end_date: str = None,
    page: int = 1,
    page_size: int = 25
) -> dict:
    """Fetch paginated patient referrals with all filters for the portal."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required"), frappe.PermissionError)

    page = cint(page or 1)
    page_size = cint(page_size or 25)
    limit_start = (page - 1) * page_size

    conditions = []
    values = {}

    if search and str(search).strip():
        conditions.append("(reference_number LIKE %(search)s OR patient_name LIKE %(search)s OR patient_phone LIKE %(search)s OR referrer_name LIKE %(search)s OR referred_doctor LIKE %(search)s)")
        values["search"] = f"%{str(search).strip()}%"

    _apply_multi_filter(conditions, values, "status", "status", status)
    _apply_multi_filter(conditions, values, "patient_village", "village", village)
    _apply_multi_filter(conditions, values, "patient_taluka", "taluka", taluka)
    _apply_multi_filter(conditions, values, "tribal_classification", "tribal_classification", tribal_classification)
    _apply_multi_filter(conditions, values, "phc", "phc", phc)
    _apply_multi_filter(conditions, values, "service_facility_type", "service_facility_type", service_facility_type)
    _apply_multi_filter(conditions, values, "opd_category", "opd_category", opd_category)
    _apply_multi_filter(conditions, values, "opd_departments", "opd_department", opd_department)
    _apply_multi_filter(conditions, values, "facility_visited", "facility_visited", facility_visited)
    _apply_multi_filter(conditions, values, "referred_by_who", "referred_by_who", referred_by_who)
    _apply_multi_filter(conditions, values, "referrer_name", "referrer_name", referrer_name)
    _apply_multi_filter(conditions, values, "referrer_department", "referrer_department", referrer_department)
    _apply_multi_filter(conditions, values, "patient_gender", "gender", gender)

    doc_items = _parse_multi_filter_values(referring_doctor)
    if doc_items:
        if len(doc_items) == 1:
            conditions.append("(referred_doctor = %(referring_doctor)s OR referred_doctor LIKE %(referring_doctor_like)s)")
            values["referring_doctor"] = doc_items[0]
            values["referring_doctor_like"] = f"%{doc_items[0]}%"
        else:
            doc_conds = []
            for idx, d_item in enumerate(doc_items):
                d_key = f"referring_doctor_{idx}"
                d_like_key = f"referring_doctor_like_{idx}"
                doc_conds.append(f"(referred_doctor = %({d_key})s OR referred_doctor LIKE %({d_like_key})s)")
                values[d_key] = d_item
                values[d_like_key] = f"%{d_item}%"
            conditions.append(f"({' OR '.join(doc_conds)})")

    if min_age and str(min_age).strip():
        conditions.append("patient_age >= %(min_age)s")
        values["min_age"] = cint(min_age)
    if max_age and str(max_age).strip():
        conditions.append("patient_age <= %(max_age)s")
        values["max_age"] = cint(max_age)
    if start_date and str(start_date).strip():
        conditions.append("referral_date >= %(start_date)s")
        values["start_date"] = str(start_date).strip()
    if end_date and str(end_date).strip():
        conditions.append("referral_date <= %(end_date)s")
        values["end_date"] = str(end_date).strip()

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    total_count_query = f"SELECT COUNT(*) FROM `tabPatient Referral` WHERE {where_clause}"
    total_records = frappe.db.sql(total_count_query, values)[0][0]
    total_pages = (total_records + page_size - 1) // page_size

    query = f"""
        SELECT 
            name, reference_number, referral_date, referral_recorded_date, status,
            referrer, referrer_name, referrer_phone, referrer_department,
            patient_name, patient_father_name, patient_gender, patient_age,
            patient_village, patient_taluka, service_facility_type, opd_category,
            other_facility_name, patient_phone, phc, opd_departments, referred_doctor,
            referred_by_who, additional_notes, hospital_registration_number, visit_date, 
            facility_visited, tribal_classification, census_match, census_member_id,
            matched_member_name, matched_member_age, match_confidence, match_status,
            mmu_patient_record, creation
        FROM `tabPatient Referral`
        WHERE {where_clause}
        ORDER BY referral_date DESC, creation DESC
        LIMIT {limit_start}, {page_size}
    """
    referrals = frappe.db.sql(query, values, as_dict=True)

    for ref in referrals:
        if ref.get("referral_date"):
            try:
                ref["referral_date"] = getdate(ref["referral_date"]).strftime("%d-%m-%Y")
            except Exception:
                pass
        if ref.get("referral_recorded_date"):
            try:
                ref["referral_recorded_date"] = getdate(ref["referral_recorded_date"]).strftime("%d-%m-%Y")
            except Exception:
                pass
        if ref.get("visit_date"):
            try:
                ref["visit_date"] = getdate(ref["visit_date"]).strftime("%d-%m-%Y")
            except Exception:
                pass

        if ref.get("mmu_patient_record") and frappe.db.exists("DocType", "MMU Patient Record"):
            try:
                mmu_data = frappe.db.get_value(
                    "MMU Patient Record",
                    ref["mmu_patient_record"],
                    ["name", "date_of_visit", "diagnosis_1", "diagnosis_2", "diagnosis_3", "diagnosis_4", "diagnosis_5", "diagnosis_6", "dental_diagnosis", "dental_diagnosis_2", "patient_referred", "patient_referred_by_doctor"],
                    as_dict=True
                )
                if mmu_data and mmu_data.get("date_of_visit"):
                    mmu_data["date_of_visit"] = str(mmu_data["date_of_visit"])
                ref["mmu_details"] = mmu_data
            except Exception:
                ref["mmu_details"] = None

        ref["supervisor_visits"] = frappe.db.get_values(
            "Supervisor Visit",
            {"parent": ref["name"], "parenttype": "Patient Referral"},
            ["visit_number", "visit_date", "patient_visited", "facility_visited", "confirmation_date", "patient_health_status", "non_visit_reason_code", "non_visit_reason_text", "supervisor_name", "supervisor_phone"],
            as_dict=True,
            order_by="visit_number asc"
        ) or []

        ref["mhd_followups"] = frappe.db.get_values(
            "MHD Followup",
            {"parent": ref["name"], "parenttype": "Patient Referral"},
            ["followup_day_offset", "visit_date", "patient_info_source", "days_drank_last_15", "notable_incident", "current_complaints", "drinking_pattern", "alcohol_type", "quantity_ml_per_day", "frequency_per_day", "drank_today", "family_opinion", "counselor_observation", "mhd_counselor_name", "mhd_counselor_phone"],
            as_dict=True,
            order_by="visit_date asc"
        ) or []

    return {
        "records": referrals,
        "total_records": total_records,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size
    }


@frappe.whitelist()
def get_portal_village_sessions(search: str = None, session_conducted: str = None, village: str = None, area: str = None, start_date: str = None, end_date: str = None, page: int = 1, page_size: int = 25) -> dict:
    """Fetch paginated village health education sessions for the portal."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required"), frappe.PermissionError)

    page = cint(page or 1)
    page_size = cint(page_size or 25)
    limit_start = (page - 1) * page_size

    conditions = []
    values = {}

    if search:
        conditions.append("(name LIKE %(search)s OR village LIKE %(search)s OR health_educator_name LIKE %(search)s OR area LIKE %(search)s OR search_driver_name LIKE %(search)s)")
        values["search"] = f"%{search.strip()}%"
    if session_conducted:
        conditions.append("session_conducted = %(session_conducted)s")
        values["session_conducted"] = session_conducted.strip()
    if village:
        conditions.append("village = %(village)s")
        values["village"] = village.strip()
    if area:
        conditions.append("area = %(area)s")
        values["area"] = area.strip()
    if start_date:
        conditions.append("date >= %(start_date)s")
        values["start_date"] = start_date.strip()
    if end_date:
        conditions.append("date <= %(end_date)s")
        values["end_date"] = end_date.strip()

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    total_count_query = f"SELECT COUNT(*) FROM `tabVillage Health Education` WHERE {where_clause}"
    total_records = frappe.db.sql(total_count_query, values)[0][0]
    total_pages = (total_records + page_size - 1) // page_size

    query = f"""
        SELECT 
            name, date, village, area, session_conducted,
            total_number_of_participants, number_of_places,
            health_educator_name, search_driver_name,
            village_patil_met, village_patil_name, village_patil_feedback,
            reason_for_not_conducting, reason_for_not_meeting_patil, creation
        FROM `tabVillage Health Education`
        WHERE {where_clause}
        ORDER BY date DESC, creation DESC
        LIMIT {limit_start}, {page_size}
    """
    sessions = frappe.db.sql(query, values, as_dict=True)

    for s in sessions:
        if s.get("date"):
            try:
                s["formatted_date"] = getdate(s["date"]).strftime("%d-%m-%Y")
            except Exception:
                s["formatted_date"] = str(s["date"])

        s["topics"] = frappe.db.get_values(
            "Village Health Education Topic",
            {"parent": s["name"], "parenttype": "Village Health Education"},
            ["topic"],
            as_dict=True,
            order_by="idx asc"
        ) or []

        s["locations"] = frappe.db.get_values(
            "Village Health Education Location",
            {"parent": s["name"], "parenttype": "Village Health Education"},
            ["location_name", "number_of_participants", "photo"],
            as_dict=True,
            order_by="idx asc"
        ) or []

    return {
        "records": sessions,
        "total_records": total_records,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size
    }


# ==============================================================================
# CENSUS ANALYTICS & HOUSEHOLD EXPLORER APIs (System Manager Only)
# ==============================================================================

def check_census_access():
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("Authentication required to access Census data.", frappe.AuthenticationError)
    roles = frappe.get_roles(user)
    if "System Manager" not in roles and user != "Administrator":
        frappe.throw("Access denied. Only users with the System Manager role can view census data.", frappe.PermissionError)


@frappe.whitelist()
def get_current_user_profile() -> dict:
    """
    Returns current logged in user details including System Manager role verification flag.
    """
    user = frappe.session.user
    if user == "Guest":
        return {
            "user": "Guest",
            "full_name": "Guest",
            "roles": ["Guest"],
            "is_system_manager": False
        }
    roles = frappe.get_roles(user)
    is_system_manager = "System Manager" in roles or user == "Administrator"
    full_name = frappe.utils.get_fullname(user) or user
    return {
        "user": user,
        "full_name": full_name,
        "roles": roles,
        "is_system_manager": is_system_manager
    }


@frappe.whitelist()
def get_census_villages() -> dict:
    """
    Returns all 232 Dhanora taluka tribal villages from Village Profile with census household counts and population.
    Only accessible by users with the System Manager role.
    """
    try:
        check_census_access()
        query = """
            SELECT 
                vp.village_name,
                vp.village_name_marathi,
                vp.village_number,
                COUNT(ch.name) as total_households,
                COALESCE(SUM(ch.total_family_members), 0) as estimated_population
            FROM `tabVillage Profile` vp
            LEFT JOIN `tabCensus Household` ch ON (ch.village = vp.name OR ch.village = vp.village_name OR ch.village_number = vp.village_number)
            WHERE (vp.taluka = 'Dhanora' OR vp.taluka LIKE '%Dhanora%' OR vp.taluka IS NULL)
              AND vp.village_number >= 1 AND vp.village_number <= 232
            GROUP BY vp.village_name, vp.village_name_marathi, vp.village_number
            ORDER BY total_households DESC, vp.village_number ASC
        """
        villages = frappe.db.sql(query, as_dict=True)
        
        # Total counts strictly across the 232 tribal villages
        total_hh = sum(int(v.get("total_households", 0) or 0) for v in villages)
        total_pop = int(sum(float(v.get("estimated_population", 0) or 0) for v in villages))

        return {
            "success": True,
            "villages": villages,
            "total_villages": len(villages),
            "total_households": total_hh,
            "total_population": total_pop
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_census_villages API Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_village_census_analytics(village: str = None) -> dict:
    """
    High-performance aggregation for a village (or all 232 tribal villages if village='ALL' or empty)
    delivering metrics for:
    1. Demographics & Population (Age cohorts, gender, sex ratio, education brackets)
    2. Housing & Sanitation (Electricity, house ownership, toilets, bathrooms, bednets, farm wells)
    3. Health & Social Welfare (Ayushman Bharat, MJPJAY, Ration Cards)
    4. Land & Livestock (Farm land acres, cattle, bullocks, goats, buffalo, poultry)
    5. Caste & Social composition (Tribal and community profiles)
    Only accessible by users with the System Manager role.
    """
    try:
        check_census_access()
        cache_key = f"census_analytics_v5:{village or 'ALL'}"
        cached = frappe.cache().get_value(cache_key)
        if cached:
            return cached

        condition = ""
        values = {}
        if village and village != "ALL" and str(village).strip():
            v_clean = str(village).strip()
            v_num = frappe.db.get_value("Village Profile", {"village_name": v_clean}, "village_number") or frappe.db.get_value("Village Profile", {"name": v_clean}, "village_number")
            if v_num:
                condition = "WHERE (ch.village = %(village)s OR ch.village_number = %(v_num)s)"
                values["village"] = v_clean
                values["v_num"] = v_num
            else:
                condition = "WHERE (ch.village = %(village)s)"
                values["village"] = v_clean
        else:
            # Default to all 232 tribal villages
            condition = "WHERE ch.village_number >= 1 AND ch.village_number <= 232"

        # 1. Total Households & Amenities summary
        hh_summary_query = f"""
            SELECT 
                COUNT(ch.name) as total_households,
                COALESCE(SUM(ch.total_family_members), 0) as total_family_members,
                COALESCE(AVG(ch.total_family_members), 0) as avg_family_size,
                COALESCE(SUM(ch.wet_land_acre + (ch.wet_land_guntha/40.0)), 0) as total_wet_land_acres,
                COALESCE(SUM(ch.dry_land_acre + (ch.dry_land_guntha/40.0)), 0) as total_dry_land_acres,
                COALESCE(SUM(CASE WHEN ch.electricity_connection LIKE '%%Yes%%' OR ch.electricity_connection = '1' THEN 1 ELSE 0 END), 0) as electricity_count,
                COALESCE(SUM(CASE WHEN ch.house_ownership = '1' OR ch.house_ownership LIKE '%%Own%%' OR ch.house_ownership LIKE '%%own%%' THEN 1 ELSE 0 END), 0) as own_house_count,
                COALESCE(SUM(CASE WHEN ch.toilet_present LIKE '%%Yes%%' OR ch.toilet_present = '1' THEN 1 ELSE 0 END), 0) as toilet_present_count,
                COALESCE(SUM(CASE WHEN ch.toilet_usage LIKE '%%Yes%%' OR ch.toilet_usage = '1' THEN 1 ELSE 0 END), 0) as toilet_usage_count,
                COALESCE(SUM(CASE WHEN ch.separate_bathroom LIKE '%%Yes%%' OR ch.separate_bathroom = '1' THEN 1 ELSE 0 END), 0) as separate_bathroom_count,
                COALESCE(SUM(CASE WHEN ch.bednet_available LIKE '%%Yes%%' OR ch.bednet_available = '1' THEN 1 ELSE 0 END), 0) as bednet_available_count,
                COALESCE(SUM(CASE WHEN ch.bednet_usage LIKE '%%Yes%%' OR ch.bednet_usage = '1' THEN 1 ELSE 0 END), 0) as bednet_usage_count,
                COALESCE(SUM(CASE WHEN ch.well_in_farm LIKE '%%Yes%%' OR ch.well_in_farm = '1' THEN 1 ELSE 0 END), 0) as well_in_farm_count,
                COALESCE(SUM(CASE WHEN ch.cowshed_present LIKE '%%Yes%%' OR ch.cowshed_present = '1' THEN 1 ELSE 0 END), 0) as cowshed_count
            FROM `tabCensus Household` ch
            {condition}
        """
        hh_stats = frappe.db.sql(hh_summary_query, values, as_dict=True)[0]
        total_hh = hh_stats.get("total_households", 0)

        # 2. Family Members Demographics (Age cohorts, Gender, Education, Marital Status)
        cfm_where = "WHERE cfm.parenttype = 'Census Household'"
        if condition:
            cfm_where += f" AND cfm.parent IN (SELECT name FROM `tabCensus Household` ch {condition})"

        cfm_query = f"""
            SELECT 
                cfm.gender,
                cfm.age,
                cfm.education,
                cfm.marital_status,
                cfm.currently_studying
            FROM `tabCensus Family Member` cfm
            {cfm_where}
        """
        members = frappe.db.sql(cfm_query, values, as_dict=True)
        total_population = len(members)

        def is_male(g):
            g_str = str(g or "").strip().lower()
            return g_str in ["1", "male", "m", "पुरुष"]

        def is_female(g):
            g_str = str(g or "").strip().lower()
            return g_str in ["2", "female", "f", "स्त्री", "महिला"]

        male_count = sum(1 for m in members if is_male(m.get("gender")))
        female_count = sum(1 for m in members if is_female(m.get("gender")))
        other_gender_count = total_population - (male_count + female_count)

        sex_ratio = round((female_count / male_count * 1000), 1) if male_count > 0 else 0

        # Master lookup caches
        edu_masters = {str(d.name): d.education_name for d in frappe.db.get_all("Education Master", fields=["name", "education_name"])} if frappe.db.exists("DocType", "Education Master") else {}
        marital_masters = {str(d.name): d.status_name for d in frappe.db.get_all("Marital Status Master", fields=["name", "status_name"])} if frappe.db.exists("DocType", "Marital Status Master") else {}
        caste_masters = {str(d.caste_code): d.caste_name for d in frappe.db.get_all("Caste Master", fields=["caste_code", "caste_name"])} if frappe.db.exists("DocType", "Caste Master") else {}
        health_masters = {str(d.scheme_code): d.scheme_name for d in frappe.db.get_all("Health Scheme Master", fields=["scheme_code", "scheme_name"])} if frappe.db.exists("DocType", "Health Scheme Master") else {"0": "None", "1": "Ayushman Bharat", "2": "Mahatma Jyotirao Phule (MJPJAY)"}
        ration_masters = {str(d.card_code): d.card_name for d in frappe.db.get_all("Ration Card Master", fields=["card_code", "card_name"])} if frappe.db.exists("DocType", "Ration Card Master") else {"1": "Yellow (BPL)", "2": "Keshari (APL)", "3": "White", "4": "Not Available"}
        livestock_masters = {str(d.animal_code): d.animal_name for d in frappe.db.get_all("Livestock Master", fields=["animal_code", "animal_name"])} if frappe.db.exists("DocType", "Livestock Master") else {
            "1": "Cow (गाय)", "2": "Bullock (बैल)", "3": "Buffalo (म्हैस)", "4": "Bull (सांड)",
            "5": "Goat (शेळी)", "6": "Poultry / Chicken (कोंबडी)", "7": "Dog (कुत्रा)", "8": "Pig (डुक्कर)"
        }

        # Age Cohorts
        age_cohorts = {
            "u5": 0,       # 0 - 5 years (Early childhood)
            "school": 0,   # 6 - 18 years (School age)
            "youth": 0,    # 19 - 35 years (Youth / Working)
            "middle": 0,   # 36 - 60 years (Middle age)
            "senior": 0    # 60+ years (Elderly)
        }
        for m in members:
            try:
                a = int(m.get("age") or 0)
                if a <= 5:
                    age_cohorts["u5"] += 1
                elif a <= 18:
                    age_cohorts["school"] += 1
                elif a <= 35:
                    age_cohorts["youth"] += 1
                elif a <= 60:
                    age_cohorts["middle"] += 1
                else:
                    age_cohorts["senior"] += 1
            except (ValueError, TypeError):
                pass

        # Structured Education Tiers & Refined Currently Studying Count
        edu_counts = defaultdict(int)
        marital_counts = defaultdict(int)
        studying_count = 0
        
        education_brackets = {
            "primary": {"label": "Primary (Class 1–4)", "count": 0, "codes": ["1", "2", "3", "4"]},
            "middle": {"label": "Upper Primary (Class 5–8)", "count": 0, "codes": ["5", "6", "7", "8"]},
            "secondary": {"label": "Secondary (Class 9–10)", "count": 0, "codes": ["9", "10"]},
            "higher_secondary": {"label": "Higher Secondary (Class 11–12)", "count": 0, "codes": ["11", "12"]},
            "graduate_plus": {"label": "Graduation & Above", "count": 0, "codes": ["13", "14"]},
            "literate_only": {"label": "Literate (No Formal School)", "count": 0, "codes": ["98"]},
            "illiterate": {"label": "Illiterate / No Schooling", "count": 0, "codes": ["99", "0", None, ""]}
        }
        
        formal_school_codes = set(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"])

        for m in members:
            raw_edu = str(m.get("education") or "").strip()
            
            # Map into structured brackets
            if raw_edu in education_brackets["primary"]["codes"]:
                education_brackets["primary"]["count"] += 1
            elif raw_edu in education_brackets["middle"]["codes"]:
                education_brackets["middle"]["count"] += 1
            elif raw_edu in education_brackets["secondary"]["codes"]:
                education_brackets["secondary"]["count"] += 1
            elif raw_edu in education_brackets["higher_secondary"]["codes"]:
                education_brackets["higher_secondary"]["count"] += 1
            elif raw_edu in education_brackets["graduate_plus"]["codes"]:
                education_brackets["graduate_plus"]["count"] += 1
            elif raw_edu == "98":
                education_brackets["literate_only"]["count"] += 1
            else:
                education_brackets["illiterate"]["count"] += 1

            edu_label = edu_masters.get(raw_edu, raw_edu) or "Illiterate / No Schooling"
            if edu_label == "None" or not edu_label.strip() or raw_edu in ["0", "99"]:
                edu_label = "Illiterate / No Schooling"
            edu_counts[edu_label] += 1

            raw_mar = str(m.get("marital_status") or "")
            mar_label = marital_masters.get(raw_mar, raw_mar) or "Unspecified"
            marital_counts[mar_label] += 1

            # Count studying strictly if enrolled in formal class brackets (1-14) and studying status is active
            if raw_edu in formal_school_codes and str(m.get("currently_studying") or "").lower() in ["1", "yes", "1=yes"]:
                studying_count += 1

        # 3. Categorical Distributions for Households
        def get_field_distribution(field_name):
            where_sub = f"WHERE {field_name} IS NOT NULL AND {field_name} != ''"
            if condition:
                where_sub = f"{condition} AND {field_name} IS NOT NULL AND {field_name} != ''"
            q = f"""
                SELECT {field_name} as label, COUNT(*) as count 
                FROM `tabCensus Household` ch
                {where_sub}
                GROUP BY {field_name}
                ORDER BY count DESC
            """
            return frappe.db.sql(q, values, as_dict=True)

        # 4. Livestock Distribution
        ls_parent_where = ""
        if condition:
            ls_parent_where = f"WHERE parent IN (SELECT name FROM `tabCensus Household` ch {condition}) AND animal_type IS NOT NULL AND animal_type != '' AND animal_type != '10'"
        else:
            ls_parent_where = "WHERE animal_type IS NOT NULL AND animal_type != '' AND animal_type != '10'"

        ls_query = f"""
            SELECT animal_type as code, SUM(quantity) as count
            FROM `tabCensus Livestock`
            {ls_parent_where}
            GROUP BY animal_type
            ORDER BY count DESC
        """
        raw_livestock = frappe.db.sql(ls_query, values, as_dict=True)
        livestock_dist = []
        for ls in raw_livestock:
            code_str = str(ls.get("code") or "")
            name = livestock_masters.get(code_str, f"Animal #{code_str}")
            livestock_dist.append({
                "code": code_str,
                "label": name,
                "count": int(ls.get("count") or 0)
            })

        # 5. Caste & Social Distribution
        caste_raw = get_field_distribution("caste_of_head")
        caste_dist = []
        for c in caste_raw:
            lbl = str(c.get("label") or "")
            caste_name = caste_masters.get(lbl, lbl)
            caste_dist.append({"label": caste_name, "count": c.get("count")})

        religion_dist = get_field_distribution("religion_of_head")

        # 6. Health Schemes Distribution
        health_raw = get_field_distribution("health_scheme_card")
        health_scheme_dist = []
        for h in health_raw:
            lbl = str(h.get("label") or "")
            scheme_name = health_masters.get(lbl, lbl)
            health_scheme_dist.append({
                "code": lbl,
                "label": scheme_name,
                "count": h.get("count"),
                "pct": round((h.get("count") / total_hh * 100), 1) if total_hh else 0
            })

        # 7. Ration Cards Distribution
        ration_raw = get_field_distribution("ration_card")
        ration_dist = []
        for r in ration_raw:
            lbl = str(r.get("label") or "")
            ration_name = ration_masters.get(lbl, lbl)
            ration_dist.append({
                "code": lbl,
                "label": ration_name,
                "count": r.get("count"),
                "pct": round((r.get("count") / total_hh * 100), 1) if total_hh else 0
            })

        result = {
            "success": True,
            "village": village or "ALL",
            "kpis": {
                "total_households": total_hh,
                "total_population": total_population if total_population > 0 else int(hh_stats.get("total_family_members", 0)),
                "male_population": male_count,
                "female_population": female_count,
                "other_population": other_gender_count,
                "sex_ratio": sex_ratio,
                "avg_family_size": round(float(hh_stats.get("avg_family_size", 0)), 1),
                "children_u5": age_cohorts["u5"],
                "senior_citizens": age_cohorts["senior"],
                "total_wet_land_acres": round(float(hh_stats.get("total_wet_land_acres", 0)), 2),
                "total_dry_land_acres": round(float(hh_stats.get("total_dry_land_acres", 0)), 2),
                "electricity_pct": round((hh_stats.get("electricity_count", 0) / total_hh * 100), 1) if total_hh else 0,
                "own_house_pct": round((hh_stats.get("own_house_count", 0) / total_hh * 100), 1) if total_hh else 0,
                "toilet_present_pct": round((hh_stats.get("toilet_present_count", 0) / total_hh * 100), 1) if total_hh else 0,
                "toilet_usage_pct": round((hh_stats.get("toilet_usage_count", 0) / total_hh * 100), 1) if total_hh else 0,
                "separate_bathroom_pct": round((hh_stats.get("separate_bathroom_count", 0) / total_hh * 100), 1) if total_hh else 0,
                "bednet_available_pct": round((hh_stats.get("bednet_available_count", 0) / total_hh * 100), 1) if total_hh else 0,
                "bednet_usage_pct": round((hh_stats.get("bednet_usage_count", 0) / total_hh * 100), 1) if total_hh else 0,
                "well_in_farm_pct": round((hh_stats.get("well_in_farm_count", 0) / total_hh * 100), 1) if total_hh else 0,
                "cowshed_pct": round((hh_stats.get("cowshed_count", 0) / total_hh * 100), 1) if total_hh else 0
            },
            "demographics": {
                "age_cohorts": age_cohorts,
                "gender": {
                    "male": male_count,
                    "female": female_count,
                    "other": other_gender_count
                },
                "education_brackets": list(education_brackets.values()),
                "education": sorted([{"label": k, "count": v} for k, v in edu_counts.items()], key=lambda x: x["count"], reverse=True),
                "marital_status": sorted([{"label": k, "count": v} for k, v in marital_counts.items()], key=lambda x: x["count"], reverse=True),
                "studying_count": studying_count
            },
            "housing_and_sanitation": {
                "electricity_pct": round((hh_stats.get("electricity_count", 0) / total_hh * 100), 1) if total_hh else 0,
                "own_house_pct": round((hh_stats.get("own_house_count", 0) / total_hh * 100), 1) if total_hh else 0,
                "toilet_present_pct": round((hh_stats.get("toilet_present_count", 0) / total_hh * 100), 1) if total_hh else 0,
                "toilet_usage_pct": round((hh_stats.get("toilet_usage_count", 0) / total_hh * 100), 1) if total_hh else 0,
                "separate_bathroom_pct": round((hh_stats.get("separate_bathroom_count", 0) / total_hh * 100), 1) if total_hh else 0,
                "bednet_available_pct": round((hh_stats.get("bednet_available_count", 0) / total_hh * 100), 1) if total_hh else 0,
                "well_in_farm_pct": round((hh_stats.get("well_in_farm_count", 0) / total_hh * 100), 1) if total_hh else 0,
                "cowshed_pct": round((hh_stats.get("cowshed_count", 0) / total_hh * 100), 1) if total_hh else 0
            },
            "welfare_and_social": {
                "caste": caste_dist,
                "religion": religion_dist,
                "ration_cards": ration_dist,
                "health_schemes": health_scheme_dist,
                "livestock": livestock_dist
            }
        }

        # Cache for 1 hour
        frappe.cache().set_value(cache_key, result, expires_in_sec=3600)
        return result

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_village_census_analytics API Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def search_census_households(village: str = None, house_number: str = None, query: str = None, page: int = 1, page_size: int = 24) -> dict:
    """
    Search and paginated listing of Census Households with filters for village, house number, or general search string.
    Only accessible by users with the System Manager role.
    """
    try:
        check_census_access()
        page = max(int(page or 1), 1)
        page_size = min(max(int(page_size or 24), 1), 100)
        offset = (page - 1) * page_size

        conditions = []
        values = {}

        if village and village != "ALL" and str(village).strip():
            v_clean = str(village).strip()
            v_num = frappe.db.get_value("Village Profile", {"village_name": v_clean}, "village_number") or frappe.db.get_value("Village Profile", {"name": v_clean}, "village_number")
            if v_num:
                conditions.append("(ch.village = %(village)s OR ch.village_number = %(v_num)s)")
                values["village"] = v_clean
                values["v_num"] = v_num
            else:
                conditions.append("ch.village = %(village)s")
                values["village"] = v_clean

        if house_number and str(house_number).strip():
            conditions.append("ch.house_number = %(house_number)s")
            values["house_number"] = str(house_number).strip()

        if query and str(query).strip():
            q_clean = f"%{str(query).strip()}%"
            conditions.append("""(
                ch.name LIKE %(q)s 
                OR ch.mobile_number LIKE %(q)s
                OR ch.name IN (SELECT parent FROM `tabCensus Family Member` WHERE member_name LIKE %(q)s)
            )""")
            values["q"] = q_clean

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        count_query = f"SELECT COUNT(*) FROM `tabCensus Household` ch {where_clause}"
        total_count = frappe.db.sql(count_query, values)[0][0]
        total_pages = (total_count + page_size - 1) // page_size

        sql = f"""
            SELECT 
                ch.name as household_id,
                COALESCE(ch.village, vp.village_name, CONCAT('Village #', ch.village_number)) as village,
                ch.village_number,
                ch.house_number,
                ch.family_number,
                (SELECT member_name FROM `tabCensus Family Member` cfm WHERE cfm.parent = ch.name AND (cfm.identification_number = 1 OR cfm.idx = 1) LIMIT 1) as head_of_household,
                ch.mobile_number,
                ch.total_family_members,
                ch.caste_of_head,
                ch.religion_of_head,
                ch.electricity_connection,
                ch.toilet_present,
                ch.ration_card,
                ch.health_scheme_card,
                (ch.wet_land_acre + (ch.wet_land_guntha/40.0) + ch.dry_land_acre + (ch.dry_land_guntha/40.0)) as total_land_acres
            FROM `tabCensus Household` ch
            LEFT JOIN `tabVillage Profile` vp ON (ch.village_number = vp.village_number OR ch.village = vp.name)
            {where_clause}
            ORDER BY ch.village_number ASC, ch.house_number ASC, ch.family_number ASC
            LIMIT {offset}, {page_size}
        """
        records = frappe.db.sql(sql, values, as_dict=True)

        return {
            "success": True,
            "households": records,
            "total_records": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": page_size
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "search_census_households API Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_household_dossier(household_id: str) -> dict:
    """
    Fetches the full dossier of a Census Household including all members and asset tables.
    Only accessible by users with the System Manager role.
    """
    try:
        check_census_access()
        if not household_id or not frappe.db.exists("Census Household", household_id):
            return {"success": False, "error": "Household not found"}

        doc = frappe.get_doc("Census Household", household_id)
        data = doc.as_dict()

        # Set head_of_household if not explicitly stored
        if not data.get("head_of_household"):
            members = data.get("family_members") or []
            if members:
                head = next((m for m in members if m.get("identification_number") == 1), members[0])
                data["head_of_household"] = head.get("member_name")

        return {
            "success": True,
            "household": data
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_household_dossier API Error")
        return {"success": False, "error": str(e)}



