import frappe
from frappe import _

no_cache = True

def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/dashboards"
		raise frappe.Redirect

	try:
		from frappe_metabase.api.embed import get_dashboard_list, get_embed_url
		has_metabase = True
	except ImportError:
		has_metabase = False

	if not has_metabase:
		frappe.throw(_("Metabase integration app is not installed or configured correctly."), frappe.ValidationError)

	# Fetch accessible dashboards
	dashboards = get_dashboard_list()
	
	# If no dashboards and not System Manager, throw Permission Error
	if not dashboards and "System Manager" not in frappe.get_roles():
		frappe.throw(_("You do not have permission to view any dashboards. Please contact your administrator."), frappe.PermissionError)

	dashboard_name = frappe.form_dict.get("name")
	embed_url = None
	current_dashboard = None

	if dashboard_name:
		# If user is a System Manager, they can view any active dashboard.
		# Otherwise, check if it's in their accessible list.
		is_system_manager = "System Manager" in frappe.get_roles()
		
		if is_system_manager:
			# Verify dashboard exists
			current_dashboard = frappe.db.get_value("Metabase Dashboard", dashboard_name, ["name", "title", "description", "iframe_height"], as_dict=True)
		else:
			current_dashboard = next((d for d in dashboards if d.name == dashboard_name), None)
			
		if not current_dashboard:
			frappe.throw(_("You do not have permission to view this dashboard, or it does not exist."), frappe.PermissionError)
		
		# Generate the embed URL
		embed_data = get_embed_url("Metabase Dashboard", dashboard_name)
		embed_url = embed_data.get("url")

	user_fullname = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user

	context.update({
		"title": "Dashboards — SEARCH",
		"dashboards": dashboards,
		"current_dashboard": current_dashboard,
		"embed_url": embed_url,
		"user_fullname": user_fullname
	})

	return context
