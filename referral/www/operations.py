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


def get_context(context):
    """Context wrapper for operations overview."""
    if not frappe.has_permission('Patient Referral', 'read'):
        frappe.throw(_('You do not have permission to view this page'),
                     frappe.PermissionError)
    
    context.update({
        'title': 'Operations View',
        'tab': frappe.form_dict.get('tab', 'referral')
    })
    
    if context.tab == 'referral':
        try:
            from referral.www.dashboard import get_context as get_referral_context
            context = get_referral_context(context)
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Operations Referral Import Error")
            context.update({'error_message': str(e)})

    elif context.tab == 'tribal_health':
        try:
            # Load Tribal Health KPIs
            total_sessions = frappe.db.count('Village Health Education')
            
            # Use raw SQL for aggregations since Village Health Education is a simple doctype
            total_participants = frappe.db.sql("""
                SELECT SUM(total_number_of_participants) 
                FROM `tabVillage Health Education`
            """)[0][0] or 0
            
            recent_sessions = frappe.db.get_all(
                'Village Health Education', 
                fields=['date', 'area', 'total_number_of_participants', 'name', 'select_the_village_village_health_education_topics_you_can_choose_more_than_one'],
                order_by='date desc',
                limit_page_length=10
            )

            for session in recent_sessions:
                if session.get('date'):
                    session['date'] = format_to_dd_mm_yyyy(session['date'])


            area_breakdown = frappe.db.sql("""
                SELECT area, COUNT(*) as sessions, SUM(total_number_of_participants) as participants
                FROM `tabVillage Health Education`
                GROUP BY area
                ORDER BY sessions DESC
            """, as_dict=True)
            
            context.update({
                'th_total_sessions': total_sessions,
                'th_total_participants': total_participants,
                'th_recent_sessions': recent_sessions,
                'th_area_breakdown': area_breakdown
            })
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Operations Tribal Health Data Error")
            context.update({'error_message': str(e)})

    return context
