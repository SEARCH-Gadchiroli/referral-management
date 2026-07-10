from frappe.model.document import Document

class Referrer(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        department: DF.Data | None
        designation: DF.Data | None
        full_name: DF.Data
        is_active: DF.Check
        phc: DF.Link | None
        phone: DF.Data
        referrer_id: DF.Data
        village: DF.Link | None
    # end: auto-generated types

    pass
