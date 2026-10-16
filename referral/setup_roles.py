import frappe

def setup():
    # 1. Clean up duplicate roles and migrate assigned users
    role_migration_map = {
        "Village Tribal Health Admin": "Tribal Health Admin",
        "Village Tribal Health User": "Tribal Health User",
        "Referral Admin": "Referral Admin User"
    }

    for old_role, new_role in role_migration_map.items():
        # Ensure new role exists first
        if not frappe.db.exists("Role", new_role):
            doc = frappe.get_doc({
                "doctype": "Role",
                "role_name": new_role,
                "desk_access": 1
            })
            doc.insert(ignore_permissions=True)
            print(f"Created Role: {new_role}")

        # Migrate users assigned old_role to new_role
        user_roles = frappe.get_all("Has Role", filters={"role": old_role}, fields=["name", "parent"])
        for ur in user_roles:
            user = ur.parent
            if not frappe.db.exists("Has Role", {"parent": user, "role": new_role}):
                user_doc = frappe.get_doc("User", user)
                user_doc.append("roles", {"role": new_role})
                user_doc.save(ignore_permissions=True)
                print(f"Migrated user {user} from {old_role} to {new_role}")
            # Remove old role assignment
            frappe.db.delete("Has Role", {"name": ur.name})

        # Remove obsolete DocPerms referencing old_role
        frappe.db.delete("DocPerm", {"role": old_role})
        frappe.db.delete("Custom DocPerm", {"role": old_role})

        # Remove old Role record if present
        if frappe.db.exists("Role", old_role):
            frappe.db.delete("Role", {"name": old_role})
            print(f"Deleted deprecated duplicate role: {old_role}")

    # 2. Canonical Roles
    roles = [
        {"role_name": "Referral Admin User", "desk_access": 1},
        {"role_name": "Referral User", "desk_access": 1},
        {"role_name": "Census Admin", "desk_access": 1},
        {"role_name": "MMU Admin", "desk_access": 1},
        {"role_name": "MMU User", "desk_access": 1},
        {"role_name": "Tribal Health Admin", "desk_access": 1},
        {"role_name": "Tribal Health User", "desk_access": 1},
    ]

    for r in roles:
        if not frappe.db.exists("Role", r["role_name"]):
            doc = frappe.get_doc({
                "doctype": "Role",
                "role_name": r["role_name"],
                "desk_access": r.get("desk_access", 1)
            })
            doc.insert(ignore_permissions=True)
            print(f"Created Role: {r['role_name']}")
        else:
            frappe.db.set_value("Role", r["role_name"], "desk_access", r.get("desk_access", 1))
            print(f"Role exists: {r['role_name']}")

    # 3. Permissions to set up
    perm_definitions = [
        # Referral Admin User
        {
            "parent": "Patient Referral",
            "role": "Referral Admin User",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },
        {
            "parent": "Raw Patient Referral Data",
            "role": "Referral Admin User",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 0, "delete": 1,
            "report": 1, "export": 1, "print": 1, "share": 0, "email": 1
        },
        {
            "parent": "Referrer",
            "role": "Referral Admin User",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 1,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },
        {
            "parent": "Referral Department Master",
            "role": "Referral Admin User",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 0,
            "report": 1, "export": 1, "print": 1, "share": 0, "email": 1
        },
        {
            "parent": "Referral Settings",
            "role": "Referral Admin User",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 0, "delete": 0,
            "report": 1, "export": 0, "print": 0, "share": 0, "email": 0
        },
        {
            "parent": "Village Profile",
            "role": "Referral Admin User",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "report": 1, "export": 1, "print": 1, "share": 0, "email": 1
        },
        {
            "parent": "PHC",
            "role": "Referral Admin User",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 0
        },
        {
            "parent": "Taluka",
            "role": "Referral Admin User",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 0,
            "report": 1, "export": 1, "print": 1, "share": 0, "email": 0
        },
        {
            "parent": "State",
            "role": "Referral Admin User",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 0,
            "report": 1, "export": 1, "print": 1, "share": 0, "email": 0
        },

        # Referral User
        {
            "parent": "Patient Referral",
            "role": "Referral User",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0, "amend": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 1
        },
        {
            "parent": "Referrer",
            "role": "Referral User",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 0
        },
        {
            "parent": "Referral Department Master",
            "role": "Referral User",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 0
        },
        {
            "parent": "Village Profile",
            "role": "Referral User",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 0
        },
        {
            "parent": "PHC",
            "role": "Referral User",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 0
        },

        # MMU Admin
        {
            "parent": "MMU Patient Record",
            "role": "MMU Admin",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },
        {
            "parent": "MMU Patient Record Medicine",
            "role": "MMU Admin",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 1,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },
        {
            "parent": "Census Household",
            "role": "MMU Admin",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 0,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },
        {
            "parent": "Census Family Member",
            "role": "MMU Admin",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 0,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },
        {
            "parent": "Village Profile",
            "role": "MMU Admin",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },
        {
            "parent": "Patient Referral",
            "role": "MMU Admin",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 0,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },

        # MMU User
        {
            "parent": "MMU Patient Record",
            "role": "MMU User",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0, "amend": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 1
        },
        {
            "parent": "MMU Patient Record Medicine",
            "role": "MMU User",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 1
        },
        {
            "parent": "Census Household",
            "role": "MMU User",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 1
        },
        {
            "parent": "Census Family Member",
            "role": "MMU User",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 1
        },
        {
            "parent": "Village Profile",
            "role": "MMU User",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 1
        },
        {
            "parent": "Patient Referral",
            "role": "MMU User",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 1
        },

        # Tribal Health Admin
        {
            "parent": "Village Health Education",
            "role": "Tribal Health Admin",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },
        {
            "parent": "Raw Village Health Education",
            "role": "Tribal Health Admin",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 1,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },
        {
            "parent": "Village Health Education Location",
            "role": "Tribal Health Admin",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 1,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },
        {
            "parent": "Village Health Education Topic",
            "role": "Tribal Health Admin",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 1,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },
        {
            "parent": "Village Profile",
            "role": "Tribal Health Admin",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },

        # Tribal Health User
        {
            "parent": "Village Health Education",
            "role": "Tribal Health User",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0, "amend": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 1
        },
        {
            "parent": "Raw Village Health Education",
            "role": "Tribal Health User",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 1, "delete": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 1
        },
        {
            "parent": "Village Health Education Location",
            "role": "Tribal Health User",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 1
        },
        {
            "parent": "Village Health Education Topic",
            "role": "Tribal Health User",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 1
        },
        {
            "parent": "Village Profile",
            "role": "Tribal Health User",
            "permlevel": 0,
            "read": 1, "write": 0, "create": 0, "delete": 0,
            "report": 1, "export": 0, "print": 1, "share": 0, "email": 1
        },

        # Census Admin (Full Central Registry & Microdata Access)
        {
            "parent": "Census Household",
            "role": "Census Admin",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },
        {
            "parent": "Census Family Member",
            "role": "Census Admin",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 1,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },
        {
            "parent": "Village Profile",
            "role": "Census Admin",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 0,
            "report": 1, "export": 1, "print": 1, "share": 1, "email": 1
        },
    ]

    # Insert/update DocPerm in database
    for p in perm_definitions:
        parent_dt = p["parent"]
        if not frappe.db.exists("DocType", parent_dt):
            continue

        existing = frappe.db.get_value(
            "DocPerm",
            {"parent": parent_dt, "role": p["role"], "permlevel": p.get("permlevel", 0)},
            "name"
        )
        if existing:
            doc = frappe.get_doc("DocPerm", existing)
            doc.update(p)
            doc.save(ignore_permissions=True)
            print(f"Updated DocPerm for {parent_dt} -> {p['role']}")
        else:
            doc = frappe.new_doc("DocPerm")
            doc.update(p)
            doc.parenttype = "DocType"
            doc.parentfield = "permissions"
            doc.insert(ignore_permissions=True)
            print(f"Created DocPerm for {parent_dt} -> {p['role']}")

    frappe.db.commit()
    frappe.clear_cache()
    print("Roles and permissions successfully initialized and cache cleared.")

if __name__ == "__main__":
    setup()
