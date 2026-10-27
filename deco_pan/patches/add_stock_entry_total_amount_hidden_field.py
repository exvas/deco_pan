import frappe


def execute():
	settings = frappe.get_single("Deco Pan Settings")
	existing = {(d.document_type, d.field_name) for d in settings.get("hidden_fields", [])}
	if ("Stock Entry", "total_amount") in existing:
		return

	settings.append("hidden_fields", {"document_type": "Stock Entry", "field_name": "total_amount"})
	settings.flags.ignore_mandatory = True
	settings.save(ignore_permissions=True)
