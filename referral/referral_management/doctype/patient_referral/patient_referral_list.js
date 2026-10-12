/**
 * Patient Referral List View Customization
 *
 * Department-wise visibility: Non-admin users with a `referral_department`
 * set on their User record will see only referrals matching their department.
 * The filter area is hidden so they get a clean, focused list.
 *
 * System Manager / Administrator users see everything as usual.
 */
frappe.listview_settings["Patient Referral"] = {
	onload(listview) {
		// Administrator sees everything — no restrictions
		if (frappe.session.user === "Administrator") {
			return;
		}

		// Fetch the logged-in user's profile and assigned departments
		frappe.call({
			method: "referral.api.get_current_user_profile",
			callback: (res) => {
				const depts = res.message?.referral_departments || [];
				if (!depts.length) {
					// No departments set — show everything
					return;
				}

				if (listview.filter_area) {
					listview.filter_area.clear();
					if (depts.length === 1) {
						listview.filter_area.add([["Patient Referral", "referred_by_who", "=", depts[0]]]);
					} else {
						listview.filter_area.add([["Patient Referral", "referred_by_who", "in", depts]]);
					}

					// Hide filter area & buttons so user cannot alter or remove the department filter
					if (listview.filter_area.$filter_list_wrapper) {
						listview.filter_area.$filter_list_wrapper.hide();
					}
					if (listview.filter_area.standard_filters_wrapper) {
						listview.filter_area.standard_filters_wrapper.hide();
					}
				}

				// Hide filter buttons in page actions
				listview.page?.wrapper?.find(".filter-button, .filter-selector, .filter-x-button").hide();

				// Show clear indicator of active departments
				listview.page?.set_indicator(__("Showing: {0}", [depts.join(", ")]), "blue");
			},
		});
	},

	refresh(listview) {
		if (frappe.session.user === "Administrator") {
			return;
		}
		frappe.call({
			method: "referral.api.get_current_user_profile",
			callback: (res) => {
				const depts = res.message?.referral_departments || [];
				if (depts.length) {
					listview.filter_area?.$filter_list_wrapper?.hide();
					listview.filter_area?.standard_filters_wrapper?.hide();
					listview.page?.wrapper?.find(".filter-button, .filter-selector, .filter-x-button").hide();
					listview.page?.set_indicator(__("Showing: {0}", [depts.join(", ")]), "blue");
				}
			},
		});
	},
};
