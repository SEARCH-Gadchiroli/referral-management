# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VillageProfile(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from referral.referral_management.doctype.village_key_personnel.village_key_personnel import VillageKeyPersonnel
		from referral.referral_management.doctype.village_mobile_networks.village_mobile_networks import VillageMobileNetworks

		anganwadi_center: DF.Link | None
		bank_branch: DF.Link | None
		bank_distance_if_no: DF.Float
		distance_from_district_hospital: DF.Float
		distance_from_search: DF.Float
		distance_to_gram_panchayat: DF.Float
		distance_to_police_station: DF.Float
		district: DF.Link | None
		drains_constructed: DF.Link | None
		gram_panchayat: DF.Data | None
		key_personnel: DF.Table[VillageKeyPersonnel]
		kirana_shops_count: DF.Int
		mobile_networks: DF.Table[VillageMobileNetworks]
		paan_shops_count: DF.Int
		phc_available: DF.Link | None
		private_clinic: DF.Link | None
		ration_shop_pds: DF.Link | None
		roads_asphalt_cement: DF.Link | None
		school_available: DF.Link | None
		school_class_level: DF.Int
		serial_number: DF.Int
		sewage_accumulation: DF.Link | None
		st_bus_available: DF.Link | None
		st_bus_distance_if_no: DF.Float
		state: DF.Link | None
		subcenter: DF.Link | None
		taluka: DF.Link | None
		village_name: DF.Data
		village_number: DF.Int
		water_tank: DF.Link | None
		weekly_market_day: DF.Link | None
		weekly_market_village: DF.Data | None
		women_self_help_groups: DF.Link | None
	# end: auto-generated types

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from village_key_personnel import VillageKeyPersonnel
		from village_mobile_networks import VillageMobileNetworks
		from frappe.types import DF

		anganwadi_center: DF.Link | None
		bank_branch: DF.Link | None
		bank_distance_if_no: DF.Float
		distance_from_district_hospital: DF.Float
		distance_from_search: DF.Float
		distance_to_gram_panchayat: DF.Float
		distance_to_police_station: DF.Float
		district: DF.Link | None
		drains_constructed: DF.Link | None
		gram_panchayat: DF.Data | None
		key_personnel: DF.Table[VillageKeyPersonnel]
		kirana_shops_count: DF.Int
		mobile_networks: DF.Table[VillageMobileNetworks]
		paan_shops_count: DF.Int
		phc_available: DF.Link | None
		private_clinic: DF.Link | None
		ration_shop_pds: DF.Link | None
		roads_asphalt_cement: DF.Link | None
		school_available: DF.Link | None
		school_class_level: DF.Int
		serial_number: DF.Int
		sewage_accumulation: DF.Link | None
		st_bus_available: DF.Link | None
		st_bus_distance_if_no: DF.Float
		state: DF.Link | None
		subcenter: DF.Link | None
		taluka: DF.Link | None
		village_name: DF.Data
		village_number: DF.Int
		water_tank: DF.Link | None
		weekly_market_day: DF.Link | None
		weekly_market_village: DF.Data | None
		women_self_help_groups: DF.Link | None

	def validate(self):
		"""Validate data and auto-fetch state from district if needed"""
		if self.district and not self.state:
			district_doc = frappe.get_doc("District", self.district)
			self.state = district_doc.state


def get_list(doctype, txt, filters, limit_start, limit_page_length, order_by=None):
	"""
	Custom get_list for Village Profile Link field search.
	Enables substring matching on both English (village_name) and Marathi
	(village_name_marathi) names so users can find villages by typing partial
	names in either script.

	Default Frappe Link search only does prefix match on `name` — this is
	insufficient for 1500+ villages, especially when users type in Devanagari.
	"""
	txt = (txt or "").strip()
	if not txt:
		return frappe.get_all(
			"Village Profile",
			filters=filters,
			fields=["name", "village_name", "village_name_marathi", "taluka", "village_number"],
			order_by="village_name asc",
			start=limit_start,
			page_length=limit_page_length,
		)

	# Build condition list for parameterized SQL
	conditions = []
	params = {"txt_like": f"%{txt}%", "txt_prefix": f"{txt}%", "txt_exact": txt}

	# Search across English name, Marathi name, taluka, and village number
	conditions.append("""(
		village_name LIKE %(txt_like)s
		OR village_name_marathi LIKE %(txt_like)s
		OR name LIKE %(txt_like)s
		OR taluka LIKE %(txt_prefix)s
		OR CAST(village_number AS CHAR) LIKE %(txt_prefix)s
	)""")

	# Apply any additional filters passed by Frappe
	filter_conditions = ""
	if filters:
		if isinstance(filters, dict):
			for key, val in filters.items():
				param_key = f"filter_{key}"
				filter_conditions += f" AND `{key}` = %({param_key})s"
				params[param_key] = val

	query = f"""
		SELECT name, village_name, village_name_marathi, taluka, village_number
		FROM `tabVillage Profile`
		WHERE {conditions[0]} {filter_conditions}
		ORDER BY
			CASE
				WHEN village_name = %(txt_exact)s OR village_name_marathi = %(txt_exact)s THEN 0
				WHEN village_name LIKE %(txt_prefix)s OR village_name_marathi LIKE %(txt_prefix)s THEN 1
				WHEN village_name LIKE %(txt_like)s OR village_name_marathi LIKE %(txt_like)s THEN 2
				ELSE 3
			END,
			village_name ASC
		LIMIT %(limit_start)s, %(limit_page_length)s
	"""
	params["limit_start"] = limit_start or 0
	params["limit_page_length"] = limit_page_length or 20

	return frappe.db.sql(query, params, as_dict=True)
