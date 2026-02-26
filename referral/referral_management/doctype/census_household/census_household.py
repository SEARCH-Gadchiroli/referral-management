# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CensusHousehold(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from referral.referral_management.doctype.census_building_material.census_building_material import CensusBuildingMaterial
		from referral.referral_management.doctype.census_building_material_floor.census_building_material_floor import CensusBuildingMaterialFloor
		from referral.referral_management.doctype.census_building_material_roof.census_building_material_roof import CensusBuildingMaterialRoof
		from referral.referral_management.doctype.census_cooking_fuel.census_cooking_fuel import CensusCookingFuel
		from referral.referral_management.doctype.census_family_member.census_family_member import CensusFamilyMember
		from referral.referral_management.doctype.census_household_item.census_household_item import CensusHouseholdItem
		from referral.referral_management.doctype.census_livestock.census_livestock import CensusLivestock
		from referral.referral_management.doctype.census_occupation.census_occupation import CensusOccupation
		from referral.referral_management.doctype.census_water_source.census_water_source import CensusWaterSource

		bednet_available: DF.Literal["1", "2"]
		bednet_usage: DF.Literal["0=No", "1=Yes", "2=No"]
		caste_of_head: DF.Link | None
		cooking_fuel: DF.Table[CensusCookingFuel]
		cowshed_location: DF.Literal["0", "1", "2"]
		cowshed_present: DF.Literal["0", "1", "2"]
		dev: DF.Int
		dry_land_acre: DF.Float
		dry_land_guntha: DF.Float
		electricity_connection: DF.Literal["1", "2"]
		external_kitchen: DF.Literal["1", "2"]
		family_members: DF.Table[CensusFamilyMember]
		family_number: DF.Int
		health_scheme_card: DF.Link | None
		house_number: DF.Int
		house_ownership: DF.Literal["1", "2"]
		household_items: DF.Table[CensusHouseholdItem]
		livestock: DF.Table[CensusLivestock]
		material_floor: DF.Table[CensusBuildingMaterialFloor]
		material_roof: DF.Table[CensusBuildingMaterialRoof]
		material_wall: DF.Table[CensusBuildingMaterial]
		mobile_number: DF.Data | None
		occupations: DF.Table[CensusOccupation]
		old_family_number: DF.Data | None
		old_household_number: DF.Data | None
		ration_card: DF.Link | None
		register_page_number: DF.Int
		religion_of_head: DF.Link | None
		separate_bathroom: DF.Literal["1", "2"]
		toilet_present: DF.Literal["1", "2"]
		toilet_usage: DF.Literal["0", "1", "2"]
		total_bednets: DF.Int
		total_beds: DF.Int
		total_family_members: DF.Int
		total_rooms: DF.Int
		village: DF.Link | None
		village_number: DF.Int
		water_source: DF.Table[CensusWaterSource]
		well_in_farm: DF.Literal["0", "1", "2"]
		wet_land_acre: DF.Float
		wet_land_guntha: DF.Float
	# end: auto-generated types

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from census_building_material import CensusBuildingMaterial
		from census_cooking_fuel import CensusCookingFuel
		from census_family_member import CensusFamilyMember
		from census_household_item import CensusHouseholdItem
		from census_livestock import CensusLivestock
		from census_occupation import CensusOccupation
		from census_water_source import CensusWaterSource
		from frappe.types import DF

		bednet_available: DF.Literal["0", "1", "2"]
		bednet_usage: DF.Literal["0", "1", "2"]
		building_materials: DF.Table[CensusBuildingMaterial]
		caste_of_head: DF.Link | None
		cooking_fuels: DF.Table[CensusCookingFuel]
		cowshed_location: DF.Literal["0", "1", "2"]
		cowshed_present: DF.Literal["0", "1", "2"]
		dev: DF.Int
		dry_land_acre: DF.Float
		dry_land_guntha: DF.Float
		electricity_connection: DF.Literal["0", "1", "2"]
		external_kitchen: DF.Literal["0", "1", "2"]
		family_members: DF.Table[CensusFamilyMember]
		family_number: DF.Int
		health_scheme_card: DF.Link | None
		house_number: DF.Int
		house_ownership: DF.Literal["0", "1", "2"]
		household_items: DF.Table[CensusHouseholdItem]
		livestock: DF.Table[CensusLivestock]
		mobile_number: DF.Data | None
		occupations: DF.Table[CensusOccupation]
		old_family_number: DF.Data | None
		old_household_number: DF.Data | None
		ration_card: DF.Link | None
		register_page_number: DF.Int
		religion_of_head: DF.Link | None
		separate_bathroom: DF.Literal["0", "1", "2"]
		toilet_present: DF.Literal["0", "1", "2"]
		toilet_usage: DF.Literal["0", "1", "2"]
		total_beds: DF.Int
		total_bednets: DF.Int
		total_family_members: DF.Int
		total_rooms: DF.Int
		village: DF.Link | None
		village_number: DF.Int
		water_sources: DF.Table[CensusWaterSource]
		well_in_farm: DF.Literal["0", "1", "2"]
		wet_land_acre: DF.Float
		wet_land_guntha: DF.Float

	def validate(self):
		"""Validate family member count matches child table"""
		if self.family_members:
			actual_count = len(self.family_members)
			if self.total_family_members != actual_count:
				frappe.msgprint(
					f"Warning: Total family members ({self.total_family_members}) "
					f"doesn't match actual count ({actual_count})"
				)
