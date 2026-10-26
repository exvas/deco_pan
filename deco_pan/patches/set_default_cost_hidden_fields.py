import frappe

DEFAULT_HIDDEN_FIELDS = [
	("Stock Entry Detail", "basic_rate"),
	("Stock Entry Detail", "basic_amount"),
	("Stock Entry Detail", "additional_cost"),
	("Stock Entry Detail", "amount"),
	("Stock Entry Detail", "valuation_rate"),
	("Stock Entry", "total_outgoing_value"),
	("Stock Entry", "total_incoming_value"),
	("Stock Entry", "value_difference"),
	("Stock Entry", "additional_costs_section"),
	("Stock Entry", "total_additional_costs"),
	("Item", "purchasing_tab"),
	("Item", "last_purchase_rate"),
	("Item", "valuation_rate"),
]


def execute():
	settings = frappe.get_single("Deco Pan Settings")
	if settings.get("hidden_fields"):
		return

	for document_type, field_name in DEFAULT_HIDDEN_FIELDS:
		settings.append("hidden_fields", {"document_type": document_type, "field_name": field_name})
	settings.flags.ignore_mandatory = True
	settings.save(ignore_permissions=True)
