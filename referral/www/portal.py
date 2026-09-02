import frappe
import os

no_cache = True

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/portal"
        raise frappe.Redirect

    csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()
    context.csrf_token = csrf_token
    
    # Read the compiled Vite index.html
    html_path = os.path.join(frappe.get_app_path('referral'), 'public', 'portal', 'index.html')
    if os.path.exists(html_path):
        with open(html_path, 'r') as f:
            template_content = f.read()
            context.vite_html = template_content.replace('{{ csrf_token }}', csrf_token)
    else:
        context.vite_html = '<h2>Frontend build not found. Please run yarn build in the frontend directory.</h2>'
