import frappe
from frappe import _
from frappe.utils import getdate

def format_to_dd_mm_yyyy(date_val):
	if not date_val:
		return ""
	try:
		return getdate(date_val).strftime("%d-%m-%Y")
	except Exception:
		return str(date_val)


no_cache = True

def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/referrals"
		raise frappe.Redirect

	# Only allow System Managers or users with Patient Referral read permission
	if "System Manager" not in frappe.get_roles() and not frappe.has_permission("Patient Referral", "read"):
		frappe.throw(_("You do not have permission to view this page. Access is restricted to authorized users."), frappe.PermissionError)

	# Fetch query args
	form_dict = frappe.form_dict
	search = form_dict.get("search", "").strip()
	status = form_dict.get("status", "").strip()
	village = form_dict.get("village", "").strip()
	phc = form_dict.get("phc", "").strip()
	opd_department = form_dict.get("opd_department", "").strip()
	start_date = form_dict.get("start_date", "").strip()
	end_date = form_dict.get("end_date", "").strip()
	referred_by_who = form_dict.get("referred_by_who", "").strip()
	taluka = form_dict.get("taluka", "").strip()
	referring_doctor = form_dict.get("referring_doctor", "").strip()
	referrer_name = form_dict.get("referrer_name", "").strip()
	gender = form_dict.get("gender", "").strip()
	min_age = form_dict.get("min_age", "").strip()
	max_age = form_dict.get("max_age", "").strip()
	
	page = frappe.utils.cint(form_dict.get("page", 1))
	if page < 1:
		page = 1
	page_size = 20
	limit_start = (page - 1) * page_size

	# Build filters list
	conditions = []
	values = {}

	if search:
		conditions.append("(reference_number LIKE %(search)s OR patient_name LIKE %(search)s OR patient_phone LIKE %(search)s OR referrer_name LIKE %(search)s)")
		values["search"] = f"%{search}%"
	if status:
		conditions.append("status = %(status)s")
		values["status"] = status
	if village:
		conditions.append("patient_village = %(village)s")
		values["village"] = village
	if phc:
		conditions.append("phc = %(phc)s")
		values["phc"] = phc
	if opd_department:
		conditions.append("opd_departments = %(opd_department)s")
		values["opd_department"] = opd_department
	if start_date:
		conditions.append("referral_date >= %(start_date)s")
		values["start_date"] = start_date
	if end_date:
		conditions.append("referral_date <= %(end_date)s")
		values["end_date"] = end_date
	if referred_by_who:
		conditions.append("referred_by_who = %(referred_by_who)s")
		values["referred_by_who"] = referred_by_who
	if taluka:
		conditions.append("patient_taluka = %(taluka)s")
		values["taluka"] = taluka
	if referring_doctor:
		conditions.append("referred_doctor = %(referring_doctor)s")
		values["referring_doctor"] = referring_doctor
	if referrer_name:
		conditions.append("referrer_name = %(referrer_name)s")
		values["referrer_name"] = referrer_name
	if gender:
		conditions.append("patient_gender = %(gender)s")
		values["gender"] = gender
	if min_age:
		conditions.append("patient_age >= %(min_age)s")
		values["min_age"] = frappe.utils.cint(min_age)
	if max_age:
		conditions.append("patient_age <= %(max_age)s")
		values["max_age"] = frappe.utils.cint(max_age)

	where_clause = " AND ".join(conditions) if conditions else "1=1"

	# Get total count for pagination
	total_count_query = f"SELECT COUNT(*) FROM `tabPatient Referral` WHERE {where_clause}"
	total_records = frappe.db.sql(total_count_query, values)[0][0]
	total_pages = (total_records + page_size - 1) // page_size

	# Get paginated records
	query = f"""
		SELECT 
			name, reference_number, referral_date, referral_recorded_date, status,
			referrer, referrer_name, referrer_phone, referrer_department,
			patient_name, patient_father_name, patient_gender, patient_age,
			patient_village, patient_taluka, service_facility_type, opd_category,
			other_facility_name, patient_phone, phc, opd_departments, referred_doctor,
			referred_by_who, additional_notes, hospital_registration_number, visit_date, 
			facility_visited, creation
		FROM `tabPatient Referral`
		WHERE {where_clause}
		ORDER BY referral_date DESC, creation DESC
		LIMIT {limit_start}, {page_size}
	"""
	referrals = frappe.db.sql(query, values, as_dict=True)

	for ref in referrals:
		if ref.get("referral_date"):
			ref["referral_date"] = format_to_dd_mm_yyyy(ref["referral_date"])
		if ref.get("visit_date"):
			ref["visit_date"] = format_to_dd_mm_yyyy(ref["visit_date"])

		ref["supervisor_visits"] = frappe.db.get_values(
			"Supervisor Visit",
			{"parent": ref["name"], "parenttype": "Patient Referral"},
			["visit_number", "visit_date", "patient_visited", "facility_visited", "confirmation_date", "patient_health_status", "non_visit_reason_code", "supervisor_name", "supervisor_phone"],
			as_dict=True,
			order_by="visit_number asc"
		) or []
		for visit in ref["supervisor_visits"]:
			if visit.get("visit_date"):
				visit["visit_date"] = format_to_dd_mm_yyyy(visit["visit_date"])
			if visit.get("confirmation_date"):
				visit["confirmation_date"] = format_to_dd_mm_yyyy(visit["confirmation_date"])

		ref["mhd_followups"] = frappe.db.get_values(
			"MHD Followup",
			{"parent": ref["name"], "parenttype": "Patient Referral"},
			["followup_day_offset", "visit_date", "patient_info_source", "days_drank_last_15", "notable_incident", "current_complaints", "drinking_pattern", "alcohol_type", "quantity_ml_per_day", "frequency_per_day", "drank_today", "family_opinion", "counselor_observation", "mhd_counselor_name", "mhd_counselor_phone"],
			as_dict=True,
			order_by="visit_date asc"
		) or []
		for mhd in ref["mhd_followups"]:
			if mhd.get("visit_date"):
				mhd["visit_date"] = format_to_dd_mm_yyyy(mhd["visit_date"])

	# Fetch unique values for filters (for dynamic and responsive UI dropdowns)
	filter_statuses = [r[0] for r in frappe.db.sql("SELECT DISTINCT status FROM `tabPatient Referral` WHERE status IS NOT NULL AND status != ''")]
	filter_villages = [r[0] for r in frappe.db.sql("SELECT DISTINCT patient_village FROM `tabPatient Referral` WHERE patient_village IS NOT NULL AND patient_village != ''")]
	filter_phcs = [r[0] for r in frappe.db.sql("SELECT DISTINCT phc FROM `tabPatient Referral` WHERE phc IS NOT NULL AND phc != ''")]
	filter_opd_departments = [r[0] for r in frappe.db.sql("SELECT DISTINCT opd_departments FROM `tabPatient Referral` WHERE opd_departments IS NOT NULL AND opd_departments != ''")]
	filter_referred_by_whos = [r[0] for r in frappe.db.sql("SELECT DISTINCT referred_by_who FROM `tabPatient Referral` WHERE referred_by_who IS NOT NULL AND referred_by_who != ''")]
	filter_talukas = [r[0] for r in frappe.db.sql("SELECT DISTINCT patient_taluka FROM `tabPatient Referral` WHERE patient_taluka IS NOT NULL AND patient_taluka != ''")]
	filter_referring_doctors = [r[0] for r in frappe.db.sql("SELECT DISTINCT referred_doctor FROM `tabPatient Referral` WHERE referred_doctor IS NOT NULL AND referred_doctor != ''")]
	filter_referrer_names = [r[0] for r in frappe.db.sql("SELECT DISTINCT referrer_name FROM `tabPatient Referral` WHERE referrer_name IS NOT NULL AND referrer_name != ''")]
	filter_genders = [r[0] for r in frappe.db.sql("SELECT DISTINCT patient_gender FROM `tabPatient Referral` WHERE patient_gender IS NOT NULL AND patient_gender != ''")]

	filter_statuses.sort()
	filter_villages.sort()
	filter_phcs.sort()
	filter_opd_departments.sort()
	filter_referred_by_whos.sort()
	filter_talukas.sort()
	filter_referring_doctors.sort()
	filter_referrer_names.sort()
	filter_genders.sort()

	# Calculate active advanced filters count
	active_filters_count = sum(1 for val in [status, village, phc, opd_department, referred_by_who, taluka, referring_doctor, referrer_name, gender, min_age, max_age, start_date, end_date] if val)

	# User greeting
	user_fullname = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user

	context.update({
		"title": "Patient Referrals — SEARCH",
		"referrals": referrals,
		"referrals_json": frappe.as_json(referrals),
		"page": page,
		"total_pages": total_pages,
		"total_records": total_records,
		"page_size": page_size,
		"start_idx": limit_start + 1 if total_records > 0 else 0,
		"end_idx": min(limit_start + page_size, total_records),
		
		# Selected filters
		"search": search,
		"status": status,
		"village": village,
		"phc": phc,
		"opd_department": opd_department,
		"referred_by_who": referred_by_who,
		"taluka": taluka,
		"referring_doctor": referring_doctor,
		"referrer_name": referrer_name,
		"gender": gender,
		"min_age": min_age,
		"max_age": max_age,
		"start_date": start_date,
		"end_date": end_date,
		"active_filters_count": active_filters_count,

		# Dropdown options
		"filter_statuses": filter_statuses,
		"filter_villages": filter_villages,
		"filter_phcs": filter_phcs,
		"filter_opd_departments": filter_opd_departments,
		"filter_referred_by_whos": filter_referred_by_whos,
		"filter_talukas": filter_talukas,
		"filter_referring_doctors": filter_referring_doctors,
		"filter_referrer_names": filter_referrer_names,
		"filter_genders": filter_genders,
		"user_fullname": user_fullname
	})

	return context
