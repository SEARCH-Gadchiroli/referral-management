"""
Install Referral Department Master records and Custom Fields on User DocType.

Usage (from bench directory on production):
    bench --site <sitename> execute referral.install_department_field.install

This script:
1. Seeds all 9 departments into 'Referral Department Master' DocType.
2. Creates the 'referral_departments' Table MultiSelect Custom Field on User.
3. Ensures the legacy 'referral_department' Select Custom Field exists for fallback.
4. Clears site cache.
"""
import frappe

DEPARTMENTS = [
    "MMU Doctor",
    "MHD counsellor",
    "Muktipath Karyakarta",
    "ASHA",
    "Arogyadoot",
    "CHW",
    "Supervisor",
    "Optometrist",
    "MPU Physiotherapist",
]


def install():
    """Seed master departments and install referral department custom fields on User."""
    print("--- 1. Seeding Referral Department Master records ---")
    if not frappe.db.exists("DocType", "Referral Department Master"):
        print("❌ Error: DocType 'Referral Department Master' does not exist.")
        print("   Please run 'bench --site <site> migrate' first to create the table!")
        return

    for dept in DEPARTMENTS:
        if not frappe.db.exists("Referral Department Master", dept):
            try:
                doc = frappe.get_doc({
                    "doctype": "Referral Department Master",
                    "department_name": dept,
                })
                doc.insert(ignore_permissions=True)
                print(f"  + Added department: {dept}")
            except Exception as e:
                print(f"  ! Could not insert {dept}: {e}")
        else:
            print(f"  ✓ Department exists: {dept}")

    print("\n--- 2. Setting up User Custom Fields ---")
    dt = "User"

    # Multi-Select Department Field (Table MultiSelect)
    multi_fieldname = "referral_departments"
    if not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": multi_fieldname}):
        doc = frappe.get_doc({
            "doctype": "Custom Field",
            "dt": dt,
            "module": "Referral Management",
            "fieldname": multi_fieldname,
            "fieldtype": "Table MultiSelect",
            "options": "User Referral Department",
            "label": "Referral Departments",
            "insert_after": "last_name",
            "description": "Select multiple departments assigned to this user. Patient referrals will be filtered accordingly.",
        })
        doc.insert(ignore_permissions=True)
        print(f"  + Created Custom Field '{dt}.{multi_fieldname}' (Table MultiSelect)")
    else:
        print(f"  ✓ Custom Field '{dt}.{multi_fieldname}' already exists.")

    # Legacy Single-Select Department Field (Select)
    single_fieldname = "referral_department"
    if not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": single_fieldname}):
        doc = frappe.get_doc({
            "doctype": "Custom Field",
            "dt": dt,
            "module": "Referral Management",
            "fieldname": single_fieldname,
            "fieldtype": "Select",
            "label": "Referral Department",
            "insert_after": multi_fieldname,
            "options": "\n" + "\n".join(DEPARTMENTS),
            "description": "Legacy single department assignment (used as fallback if Referral Departments is empty).",
        })
        doc.insert(ignore_permissions=True)
        print(f"  + Created Custom Field '{dt}.{single_fieldname}' (Select)")
    else:
        print(f"  ✓ Custom Field '{dt}.{single_fieldname}' already exists.")

    frappe.db.commit()
    frappe.clear_cache()
    print("\n✅ Successfully installed! Site cache cleared.")
    print("👉 Next: Open Frappe Desk -> Users -> Select user -> assign their Referral Departments.")

