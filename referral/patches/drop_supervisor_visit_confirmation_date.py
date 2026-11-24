import frappe


def execute():
	"""Drop the Supervisor Visit `confirmation_date` column.

	The Glific supervisor flow mapped a single answer onto both `visit_date` and
	`confirmation_date`, so the column never held anything `visit_date` did not
	already say. The field is gone from the DocType; this removes the residue.

	Guarded: production is not inspected from here, so if any row turns out to
	carry a genuinely different date the column is kept and the discrepancy
	logged for a human to look at.
	"""
	if not frappe.db.table_exists("Supervisor Visit"):
		return

	columns = frappe.db.get_table_columns("Supervisor Visit")
	if "confirmation_date" not in columns:
		return

	divergent = frappe.db.sql("""
		SELECT COUNT(*) FROM `tabSupervisor Visit`
		WHERE confirmation_date IS NOT NULL AND confirmation_date <> visit_date
	""")[0][0]

	if divergent:
		frappe.log_error(
			f"{divergent} Supervisor Visit row(s) have a confirmation_date that differs "
			"from visit_date. Column left in place — review before dropping.",
			"drop_supervisor_visit_confirmation_date skipped",
		)
		return

	frappe.db.sql_ddl("ALTER TABLE `tabSupervisor Visit` DROP COLUMN `confirmation_date`")
