import frappe
from frappe import _

from deco_pan.deco_pan.doctype.deco_pan_settings.deco_pan_settings import get_allowed_stock_entry_types


def validate(doc, method=None):
	allowed = get_allowed_stock_entry_types()
	if allowed and doc.stock_entry_type not in allowed:
		frappe.throw(
			_("You are only allowed to create Stock Entries of type: {0}").format(", ".join(allowed)),
			frappe.PermissionError,
		)
