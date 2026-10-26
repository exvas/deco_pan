# Copyright (c) 2024, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DecoPanSettings(Document):
	def on_update(self):
		# hidden fields are shipped in bootinfo, which is cached per user
		frappe.clear_cache()


def get_hidden_fields(user=None):
	"""Return {doctype: [fieldnames]} to hide for the user, as configured in Deco Pan Settings."""
	user = user or frappe.session.user
	settings = frappe.get_cached_doc("Deco Pan Settings")
	if not settings.get("hide_cost"):
		return {}
	if user not in [d.user for d in settings.get("restricted_users", [])]:
		return {}

	hidden = {}
	for row in settings.get("hidden_fields", []):
		hidden.setdefault(row.document_type, []).append(row.field_name)
	return hidden


def boot_session(bootinfo):
	bootinfo.deco_pan_hidden_fields = get_hidden_fields()
