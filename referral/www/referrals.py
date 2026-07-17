import frappe
from frappe import _

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
	
	page = frappe.utils.cint(form_dict.get("page", 1))
	if page < 1:
		page = 1
	page_size = 20
	limit_start = (page - 1) * page_size

	# Build filters list
	conditions = []
	values = {}

	if search:
		conditions.append("(reference_number LIKE %(search)s OR patient_name LIKE %(search)s OR patient_phone LIKE %(search)s)")
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
			additional_notes, hospital_registration_number, visit_date, facility_visited,
			creation
		FROM `tabPatient Referral`
		WHERE {where_clause}
		ORDER BY referral_date DESC, creation DESC
		LIMIT {limit_start}, {page_size}
	"""
	referrals = frappe.db.sql(query, values, as_dict=True)

	for ref in referrals:
		ref["supervisor_visits"] = frappe.db.get_values(
			"Supervisor Visit",
			{"parent": ref["name"], "parenttype": "Patient Referral"},
			["visit_number", "visit_date", "patient_visited", "facility_visited", "confirmation_date", "patient_health_status", "non_visit_reason_code", "supervisor_name", "supervisor_phone"],
			as_dict=True,
			order_by="visit_number asc"
		) or []

	# Fetch unique values for filters (for dynamic and responsive UI dropdowns)
	filter_statuses = [r[0] for r in frappe.db.sql("SELECT DISTINCT status FROM `tabPatient Referral` WHERE status IS NOT NULL AND status != ''")]
	filter_villages = [r[0] for r in frappe.db.sql("SELECT DISTINCT patient_village FROM `tabPatient Referral` WHERE patient_village IS NOT NULL AND patient_village != ''")]
	filter_phcs = [r[0] for r in frappe.db.sql("SELECT DISTINCT phc FROM `tabPatient Referral` WHERE phc IS NOT NULL AND phc != ''")]
	filter_opd_departments = [r[0] for r in frappe.db.sql("SELECT DISTINCT opd_departments FROM `tabPatient Referral` WHERE opd_departments IS NOT NULL AND opd_departments != ''")]

	filter_statuses.sort()
	filter_villages.sort()
	filter_phcs.sort()
	filter_opd_departments.sort()

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
		"start_date": start_date,
		"end_date": end_date,

		# Dropdown options
		"filter_statuses": filter_statuses,
		"filter_villages": filter_villages,
		"filter_phcs": filter_phcs,
		"filter_opd_departments": filter_opd_departments,
		"user_fullname": user_fullname
	})

	return context
