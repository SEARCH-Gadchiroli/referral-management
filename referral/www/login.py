import frappe
from frappe import _

no_cache = True

def get_context(context):
	# Redirect already authenticated users to portal
	if frappe.session.user != "Guest":
		redirect_to = frappe.local.request.args.get("redirect-to") or "/portal"
		
		# Prevent infinite redirect loops if redirect_to is /login
		if redirect_to == "/login" or redirect_to == "login":
			redirect_to = "/portal"
			
		frappe.local.flags.redirect_location = redirect_to
		raise frappe.Redirect

	context.no_header = True
	context.title = _("Sign In")
	
	# Pass system/website name
	context.app_name = (
		frappe.get_website_settings("app_name") or frappe.get_system_settings("app_name") or _("SEARCH Gadchiroli")
	)
	
	return context
