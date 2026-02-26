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

		anganwadi_center: DF.Literal["1", "2"]
		bank_branch: DF.Literal["1", "2"]
		bank_distance_if_no: DF.Float
		distance_from_district_hospital: DF.Float
		distance_from_search: DF.Float
		distance_to_gram_panchayat: DF.Float
		distance_to_police_station: DF.Float
		district: DF.Link | None
		drains_constructed: DF.Literal["1", "2"]
		gram_panchayat: DF.Data | None
		key_personnel: DF.Table[VillageKeyPersonnel]
		kirana_shops_count: DF.Int
		mobile_networks: DF.Table[VillageMobileNetworks]
		paan_shops_count: DF.Int
		phc_available: DF.Literal["1", "2"]
		private_clinic: DF.Literal["1", "2"]
		ration_shop_pds: DF.Literal["1", "2"]
		roads_asphalt_cement: DF.Literal["1", "2"]
		school_available: DF.Literal["1", "2"]
		school_class_level: DF.Int
		serial_number: DF.Int
		sewage_accumulation: DF.Literal["1", "2"]
		st_bus_available: DF.Literal["1", "2"]
		st_bus_distance_if_no: DF.Float
		state: DF.Link | None
		subcenter: DF.Literal["1", "2"]
		taluka: DF.Link | None
		village_name: DF.Data
		village_number: DF.Int
		water_tank: DF.Literal["1", "2"]
		weekly_market_day: DF.Link | None
		weekly_market_village: DF.Data | None
		women_self_help_groups: DF.Literal["1", "2"]
	# end: auto-generated types

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from village_key_personnel import VillageKeyPersonnel
		from village_mobile_networks import VillageMobileNetworks
		from frappe.types import DF

		anganwadi_center: DF.Literal["1=Yes", "2=No"]
		bank_branch: DF.Literal["1=Yes", "2=No"]
		bank_distance_if_no: DF.Float
		distance_from_district_hospital: DF.Float
		distance_from_search: DF.Float
		distance_to_gram_panchayat: DF.Float
		distance_to_police_station: DF.Float
		district: DF.Link | None
		drains_constructed: DF.Literal["1=Yes", "2=No"]
		gram_panchayat: DF.Data | None
		key_personnel: DF.Table[VillageKeyPersonnel]
		kirana_shops_count: DF.Int
		mobile_networks: DF.Table[VillageMobileNetworks]
		paan_shops_count: DF.Int
		phc_available: DF.Literal["1=Yes", "2=No"]
		private_clinic: DF.Literal["1=Yes", "2=No"]
		ration_shop_pds: DF.Literal["1=Yes", "2=No"]
		roads_asphalt_cement: DF.Literal["1=Yes", "2=No"]
		school_available: DF.Literal["1=Yes", "2=No"]
		school_class_level: DF.Int
		serial_number: DF.Int
		sewage_accumulation: DF.Literal["1=Yes", "2=No"]
		st_bus_available: DF.Literal["1=Yes", "2=No"]
		st_bus_distance_if_no: DF.Float
		state: DF.Link | None
		subcenter: DF.Literal["1=Yes", "2=No"]
		taluka: DF.Link | None
		village_name: DF.Data
		village_number: DF.Int
		water_tank: DF.Literal["1=Yes", "2=No"]
		weekly_market_day: DF.Link | None
		weekly_market_village: DF.Data | None
		women_self_help_groups: DF.Literal["1=Yes", "2=No"]

	def validate(self):
		"""Validate data and auto-fetch state from district if needed"""
		if self.district and not self.state:
			district_doc = frappe.get_doc("District", self.district)
			self.state = district_doc.state
