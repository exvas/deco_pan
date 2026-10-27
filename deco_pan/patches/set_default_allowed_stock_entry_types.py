import frappe


def execute():
	settings = frappe.get_single("Deco Pan Settings")
	if settings.get("allowed_stock_entry_types"):
		return

	settings.append("allowed_stock_entry_types", {"stock_entry_type": "Material Transfer"})
	settings.flags.ignore_mandatory = True
	settings.save(ignore_permissions=True)
