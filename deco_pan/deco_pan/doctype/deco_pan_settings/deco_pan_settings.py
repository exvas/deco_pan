# Copyright (c) 2024, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DecoPanSettings(Document):
	def on_update(self):
		# restrictions are shipped in bootinfo, which is cached per user
		frappe.clear_cache()


def is_restricted_user(user=None):
	user = user or frappe.session.user
	settings = frappe.get_cached_doc("Deco Pan Settings")
	return user in [d.user for d in settings.get("restricted_users", [])]


def get_hidden_fields(user=None):
	"""Return {doctype: [fieldnames]} to hide for the user, as configured in Deco Pan Settings."""
	settings = frappe.get_cached_doc("Deco Pan Settings")
	if not settings.get("hide_cost") or not is_restricted_user(user):
		return {}

	hidden = {}
	for row in settings.get("hidden_fields", []):
		hidden.setdefault(row.document_type, []).append(row.field_name)
	return hidden


def get_allowed_stock_entry_types(user=None):
	"""Return the Stock Entry Types the user may use, or an empty list if unrestricted."""
	if not is_restricted_user(user):
		return []
	settings = frappe.get_cached_doc("Deco Pan Settings")
	return [d.stock_entry_type for d in settings.get("allowed_stock_entry_types", [])]


def boot_session(bootinfo):
	bootinfo.deco_pan_hidden_fields = get_hidden_fields()
	bootinfo.deco_pan_allowed_stock_entry_types = get_allowed_stock_entry_types()
