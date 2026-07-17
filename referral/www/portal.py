import frappe
from frappe import _


# ── Role → App mappings ────────────────────────────────────────────────────────
# Each app defines which roles grant access and what the card shows.
# A user sees a card if they have ANY of the listed roles (or are System Manager).

APPS = [
    {
        "id": "mental_health",
        "title": "Mental Health",
        "icon": "🧠",
        "color": "#7c3aed",
        "bg": "#ede9fe",
        "roles": [
            "MH_Doctor_View",
            "MH_Chatbot_Reviewer",
            "Data Entry Operator",
            "MH_External_Reviewer",
        ],
        "links": [
            {"label": "View Consultations", "url": "/app/mh_chatbot_consultation_glific", "icon": "📋"},
            {"label": "New Consultation",   "url": "/app/mh_chatbot_consultation_glific/new", "icon": "➕"},
            {"label": "External Reviews",   "url": "/app/mh-external-review", "icon": "🔍"},
            {"label": "MH Settings",        "url": "/app/mh-settings", "icon": "⚙️", "admin_only": True},
        ],
    },
    {
        "id": "referral",
        "title": "Referral",
        "icon": "📋",
        "color": "#059669",
        "bg": "#d1fae5",
        "roles": ["System Manager"], # System Manager (others get access via Patient Referral permission)
        "url": "/referrals",
        "links": [],
    },
    {
        "id": "mmu",
        "title": "MMU",
        "icon": "🏥",
        "color": "#dc2626",
        "bg": "#fee2e2",
        "roles": ["MMU Operator", "MMU Supervisor"],
        "links": [
            {"label": "View Visits",   "url": "/app/mmu-visit", "icon": "🗓️"},
            {"label": "New Visit",     "url": "/app/mmu-visit/new", "icon": "➕"},
        ],
    },
    {
        "id": "tribal_health",
        "title": "Tribal Health",
        "icon": "🌿",
        "color": "#d97706",
        "bg": "#fef3c7",
        "roles": ["Tribal Health Worker", "Tribal Health Supervisor"],
        "links": [
            {"label": "View Sessions",  "url": "/app/health-education", "icon": "📚"},
            {"label": "New Session",    "url": "/app/health-education/new", "icon": "➕"},
        ],
    },
]


def get_context(context):
    """
    Build the unified portal landing page context.
    Filters app cards based on the current user's roles.
    System Manager sees all apps.
    """

    # Redirect guests to login
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/portal"
        raise frappe.Redirect

    user_roles = frappe.get_roles(frappe.session.user)
    is_admin = "System Manager" in user_roles

    # Get full name for greeting
    user_fullname = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user

    visible_apps = []

    for app in APPS:
        has_access = is_admin or any(role in user_roles for role in app["roles"])
        if not has_access and app["id"] == "referral":
            if frappe.has_permission("Patient Referral", "read"):
                has_access = True

        if not has_access:
            continue

        # Filter admin-only links
        links = [
            l for l in app.get("links", [])
            if not l.get("admin_only") or is_admin
        ]

        visible_apps.append({
            **app,
            "links": links,
        })

    # Check dynamic Metabase dashboards access
    try:
        from frappe_metabase.api.embed import get_dashboard_list
        user_dashboards = get_dashboard_list()
        has_dashboards = len(user_dashboards) > 0
    except ImportError:
        has_dashboards = False

    if has_dashboards or is_admin:
        visible_apps.append({
            "id": "dashboards",
            "title": "Dashboards",
            "icon": "📊",
            "color": "#3b82f6",
            "bg": "#dbeafe",
            "url": "/dashboards",
            "links": []
        })

    context.update({
        "title": "SEARCH Gadchiroli — Portal",
        "user_fullname": user_fullname,
        "apps": visible_apps,
        "no_apps": len(visible_apps) == 0,
    })

    return context
