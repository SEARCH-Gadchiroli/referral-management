import frappe
from frappe import _
from datetime import datetime, timedelta

def get_context(context):
    """Fetch complete Phase 1 referral data from Patient Referral doctype"""
    
    # Check permission
    if not frappe.has_permission('Patient Referral', 'read'):
        frappe.throw(_('You do not have permission to view this page'), 
                     frappe.PermissionError)
    
    try:
        # === TODAY'S STATISTICS ===
        today = datetime.today().date()
        referrals_today = frappe.db.count('Patient Referral', 
            filters={'referral_date': today})
        
        # === OVERALL METRICS ===
        total_referrals = frappe.db.count('Patient Referral')
        
        pending_count = frappe.db.count('Patient Referral', 
            filters={'status': 'Pending'})
        
        visited_count = frappe.db.count('Patient Referral', 
            filters={'status': 'Visited'})
        
        no_show_count = frappe.db.count('Patient Referral', 
            filters={'status': 'No-Show'})
        
        cancelled_count = frappe.db.count('Patient Referral', 
            filters={'status': 'Cancelled'})
        
        # Calculate completion rate
        completion_rate = 0
        if total_referrals > 0:
            completion_rate = round((visited_count / total_referrals) * 100, 1)
        
        # === TODAY'S BREAKDOWN (using raw SQL to avoid aggregate field restrictions) ===
        today_status_breakdown = frappe.db.sql("""
            SELECT status, COUNT(*) as count
            FROM `tabPatient Referral`
            WHERE referral_date = %s
            GROUP BY status
            ORDER BY count DESC
        """, (today,), as_dict=True)
        
        today_opd_breakdown = frappe.db.sql("""
            SELECT opd_departments, COUNT(*) as count
            FROM `tabPatient Referral`
            WHERE referral_date = %s AND opd_departments IS NOT NULL AND opd_departments != ''
            GROUP BY opd_departments
            ORDER BY count DESC
            LIMIT 10
        """, (today,), as_dict=True)
        
        today_referrer_breakdown = frappe.db.sql("""
            SELECT referrer, COUNT(*) as count
            FROM `tabPatient Referral`
            WHERE referral_date = %s AND referrer IS NOT NULL AND referrer != ''
            GROUP BY referrer
            ORDER BY count DESC
            LIMIT 10
        """, (today,), as_dict=True)
        
        # === OVERALL STATUS BREAKDOWN ===
        status_breakdown = frappe.db.sql("""
            SELECT status, COUNT(*) as count
            FROM `tabPatient Referral`
            GROUP BY status
            ORDER BY count DESC
        """, as_dict=True)
        
        # === ALL DATA: OPD DEPARTMENTS ===
        opd_breakdown = frappe.db.sql("""
            SELECT opd_departments, COUNT(*) as count
            FROM `tabPatient Referral`
            WHERE opd_departments IS NOT NULL AND opd_departments != ''
            GROUP BY opd_departments
            ORDER BY count DESC
            LIMIT 25
        """, as_dict=True)
        
        # === ALL DATA: VILLAGES ===
        village_breakdown = frappe.db.sql("""
            SELECT patient_village, COUNT(*) as count
            FROM `tabPatient Referral`
            WHERE patient_village IS NOT NULL AND patient_village != ''
            GROUP BY patient_village
            ORDER BY count DESC
            LIMIT 20
        """, as_dict=True)
        
        # === ALL DATA: REFERRERS ===
        referrer_breakdown = frappe.db.sql("""
            SELECT referrer, COUNT(*) as count
            FROM `tabPatient Referral`
            WHERE referrer IS NOT NULL AND referrer != ''
            GROUP BY referrer
            ORDER BY count DESC
            LIMIT 20
        """, as_dict=True)
        
        # === ALL DATA: PHC BREAKDOWN ===
        phc_breakdown = frappe.db.sql("""
            SELECT phc, COUNT(*) as count
            FROM `tabPatient Referral`
            WHERE phc IS NOT NULL AND phc != ''
            GROUP BY phc
            ORDER BY count DESC
            LIMIT 15
        """, as_dict=True)
        
        # === ALL DATA: GENDER DISTRIBUTION ===
        gender_breakdown = frappe.db.sql("""
            SELECT patient_gender, COUNT(*) as count
            FROM `tabPatient Referral`
            WHERE patient_gender IS NOT NULL AND patient_gender != ''
            GROUP BY patient_gender
            ORDER BY count DESC
        """, as_dict=True)
        
        # === ALL DATA: AGE GROUP DISTRIBUTION ===
        age_data = frappe.db.get_list('Patient Referral',
            fields=['patient_age'],
            filters={'patient_age': ['!=', None]})
        
        age_groups = {
            '0-5': 0,
            '6-15': 0,
            '16-30': 0,
            '31-45': 0,
            '46-60': 0,
            '60+': 0
        }
        
        for row in age_data:
            age = row.get('patient_age')
            if isinstance(age, (int, float)):
                if age <= 5:
                    age_groups['0-5'] += 1
                elif age <= 15:
                    age_groups['6-15'] += 1
                elif age <= 30:
                    age_groups['16-30'] += 1
                elif age <= 45:
                    age_groups['31-45'] += 1
                elif age <= 60:
                    age_groups['46-60'] += 1
                else:
                    age_groups['60+'] += 1
        
        age_breakdown = [
            {'age_group': k, 'count': v} 
            for k, v in age_groups.items() if v > 0
        ]
        
        # === RECENT REFERRALS (with all fields) ===
        recent_referrals = frappe.db.get_list('Patient Referral',
            fields=['reference_number', 'patient_name', 'patient_age', 
                    'patient_gender', 'patient_village', 'patient_phone',
                    'referral_date', 'opd_departments', 'status', 
                    'referrer', 'phc', 'name'],
            order_by='referral_date desc',
            limit_page_length=15)
        
        # === REFERRER DEPARTMENT MAPPING ===
        referrer_details = frappe.db.get_list('Referrer',
            fields=['name', 'full_name', 'department', 'phc'],
            limit_page_length=100)
        
        referrer_map = {}
        for ref in referrer_details:
            referrer_map[ref.name] = {
                'full_name': ref.get('full_name'),
                'department': ref.get('department'),
                'phc': ref.get('phc')
            }
        
        # === REFERRALS BY REFERRER DEPARTMENT ===
        referrer_department_stats = []
        if referrer_map:
            dept_breakdown = frappe.db.sql("""
                SELECT referrer, COUNT(*) as count
                FROM `tabPatient Referral`
                WHERE referrer IS NOT NULL AND referrer != ''
                GROUP BY referrer
                ORDER BY count DESC
            """, as_dict=True)
            
            for item in dept_breakdown:
                referrer_id = item.get('referrer')
                if referrer_id in referrer_map:
                    referrer_department_stats.append({
                        'referrer_name': referrer_map[referrer_id].get('full_name'),
                        'department': referrer_map[referrer_id].get('department'),
                        'count': item.get('count')
                    })
        
        # === TODAY'S REFERRERS BY DEPT ===
        today_referrers_by_dept = frappe.db.sql("""
            SELECT referrer, COUNT(*) as count
            FROM `tabPatient Referral`
            WHERE referral_date = %s AND referrer IS NOT NULL AND referrer != ''
            GROUP BY referrer
            ORDER BY count DESC
        """, (today,), as_dict=True)
        
        today_referrers_dept_stats = []
        for item in today_referrers_by_dept:
            referrer_id = item.get('referrer')
            if referrer_id in referrer_map:
                today_referrers_dept_stats.append({
                    'referrer_name': referrer_map[referrer_id].get('full_name'),
                    'department': referrer_map[referrer_id].get('department'),
                    'count': item.get('count')
                })
        
        # === REFERRALS BY GENDER AND STATUS ===
        gender_status = frappe.db.sql("""
            SELECT patient_gender, status, COUNT(*) as count
            FROM `tabPatient Referral`
            GROUP BY patient_gender, status
            ORDER BY patient_gender, status
        """, as_dict=True)
        
        # === UPCOMING FEATURES ===
        upcoming_features = [
            {
                'icon': '🔔',
                'title': 'Follow-Up Tracking',
                'description': 'Automated follow-up scheduling and tracking for referred patients to ensure care continuity.',
                'eta': 'Phase 2'
            },
            {
                'icon': '🏥',
                'title': 'Service & Facility Mapping',
                'description': 'Map referrals to specific service facilities, track capacity, and monitor facility-level outcomes.',
                'eta': 'Phase 2'
            },
            {
                'icon': '📈',
                'title': 'Trend Analytics',
                'description': 'Weekly and monthly trend graphs to visualise referral patterns over time.',
                'eta': 'Phase 3'
            },
        ]
        
        context.update({
            'title': 'Referral Management Dashboard - Phase 1',
            'today': today.strftime('%d-%m-%Y'),
            'referrals_today': referrals_today,
            
            # Overall metrics
            'total': total_referrals,
            'pending': pending_count,
            'visited': visited_count,
            'no_show': no_show_count,
            'cancelled': cancelled_count,
            'completion_rate': completion_rate,
            
            # Today's breakdown
            'today_status_data': today_status_breakdown,
            'today_opd_data': today_opd_breakdown,
            'today_referrer_data': today_referrer_breakdown,
            'today_referrers_dept_stats': today_referrers_dept_stats,
            
            # Overall breakdown
            'status_data': status_breakdown,
            'opd_data': opd_breakdown,
            'village_data': village_breakdown,
            'referrer_data': referrer_breakdown,
            'phc_data': phc_breakdown,
            'gender_data': gender_breakdown,
            'age_data': age_breakdown,
            'referrer_dept_stats': referrer_department_stats,
            'gender_status_data': gender_status,
            
            # Recent referrals
            'recent': recent_referrals,
            'referrer_map': referrer_map,

            # Upcoming features for banner
            'upcoming_features': upcoming_features,
        })
        
        return context
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Dashboard Error')
        context.update({
            'title': 'Referral Management Dashboard - Phase 1',
            'error': True,
            'error_message': str(e),
            'today': '',
            'referrals_today': 0,
            'total': 0,
            'pending': 0,
            'visited': 0,
            'no_show': 0,
            'cancelled': 0,
            'completion_rate': 0,
            'today_status_data': [],
            'today_opd_data': [],
            'today_referrer_data': [],
            'today_referrers_dept_stats': [],
            'status_data': [],
            'opd_data': [],
            'village_data': [],
            'referrer_data': [],
            'phc_data': [],
            'gender_data': [],
            'age_data': [],
            'referrer_dept_stats': [],
            'gender_status_data': [],
            'recent': [],
            'referrer_map': {},
            'upcoming_features': [],
        })
        return context