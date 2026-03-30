// Copyright (c) 2026, SEARCH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Patient Referral", {
	refresh(frm) {
		// Show "Find Census Matches" button when admin needs to review
		if (
			frm.doc.match_status === "Unmatched" ||
			frm.doc.match_status === "Multiple Matches" ||
			frm.doc.match_status === "Auto-Matched"
		) {
			frm.add_custom_button(
				__("Find Census Matches"),
				function () {
					frm.trigger("open_census_match_dialog");
				},
				__("Census")
			);
		}
	},

	open_census_match_dialog(frm) {
		frappe.call({
			method:
				"referral.referral_management.doctype.patient_referral.patient_referral.search_census_matches",
			args: { referral_name: frm.doc.name },
			freeze: true,
			freeze_message: __("Searching census records..."),
			callback: function (r) {
				if (!r.message || !r.message.success) {
					frappe.msgprint(
						__(
							"Error searching census: " +
								(r.message ? r.message.error : "Unknown error")
						)
					);
					return;
				}

				let matches = r.message.matches || [];
				let patient = r.message.patient_info || {};

				if (matches.length === 0) {
					frappe.msgprint(
						__("No census matches found for this patient."),
						__("Census Match")
					);
					return;
				}

				// Build the match dialog
				let html = `
					<div style="margin-bottom: 15px; padding: 10px; background: var(--bg-light-gray); border-radius: 6px;">
						<strong>Patient:</strong> ${patient.name || ""}
						| <strong>Father:</strong> ${patient.father_name || ""}
						| <strong>Age:</strong> ${patient.age || ""}
						| <strong>Gender:</strong> ${patient.gender || ""}
						| <strong>Village:</strong> ${patient.village || ""}
					</div>
					<table class="table table-bordered table-hover" style="font-size: 13px;">
						<thead>
							<tr style="background: var(--bg-light-gray);">
								<th></th>
								<th>${__("Name")}</th>
								<th>${__("Father Name")}</th>
								<th>${__("Age")}</th>
								<th>${__("Gender")}</th>
								<th>${__("Household")}</th>
								<th>${__("Confidence")}</th>

							</tr>
						</thead>
						<tbody>
				`;

				matches.forEach(function (m, idx) {
					let confidence_color =
						m.confidence >= 100
							? "green"
							: m.confidence >= 90
								? "blue"
								: m.confidence >= 70
									? "orange"
									: "red";


					html += `
						<tr>
							<td><input type="radio" name="census_match" value="${idx}" ${idx === 0 ? "checked" : ""} /></td>
							<td><strong>${m.member_first_name || ""}</strong></td>
							<td>${m.member_father_name || ""}</td>
							<td>${m.age || 0}</td>
							<td>${m.gender || ""}</td>
							<td><small>${m.household || ""}</small></td>
							<td><span style="color: ${confidence_color}; font-weight: bold;">${m.confidence}%</span></td>
						</tr>
					`;
				});

				html += "</tbody></table>";

				let dialog = new frappe.ui.Dialog({
					title: __("Census Matches ({0} found)", [matches.length]),
					size: "extra-large",
					fields: [
						{
							fieldtype: "HTML",
							fieldname: "matches_html",
							options: html,
						},
					],
					primary_action_label: __("Confirm Selected Match"),
					primary_action: function () {
						let selected_idx = dialog.$wrapper
							.find('input[name="census_match"]:checked')
							.val();
						if (selected_idx === undefined) {
							frappe.msgprint(__("Please select a match."));
							return;
						}

						let selected = matches[parseInt(selected_idx)];

						frappe.call({
							method:
								"referral.referral_management.doctype.patient_referral.patient_referral.confirm_census_match",
							args: {
								referral_name: frm.doc.name,
								household: selected.household,
								member_name: selected.member_name,
								member_age: selected.age,
								confidence: selected.confidence,
							},
							freeze: true,
							freeze_message: __("Confirming match..."),
							callback: function (cr) {
								if (cr.message && cr.message.success) {
									frappe.show_alert(
										{
											message: __(
												"Census match confirmed!"
											),
											indicator: "green",
										},
										5
									);
									dialog.hide();
									frm.reload_doc();
								} else {
									frappe.msgprint(
										__(
											"Error confirming match: " +
												(cr.message
													? cr.message.error
													: "Unknown error")
										)
									);
								}
							},
						});
					},
					secondary_action_label: __("Cancel"),
				});

				dialog.show();
			},
		});
	},
});
