import frappe

PURCHASE_RECEIPT_HIDDEN_FIELDS = [
	("Purchase Receipt", "total"),
	("Purchase Receipt", "net_total"),
	("Purchase Receipt", "base_total"),
	("Purchase Receipt", "base_net_total"),
	("Purchase Receipt", "taxes_charges_section"),
	("Purchase Receipt", "taxes_section"),
	("Purchase Receipt", "sec_tax_breakup"),
	("Purchase Receipt", "totals"),
	("Purchase Receipt", "section_break_46"),
	("Purchase Receipt", "grand_total"),
	("Purchase Receipt", "rounded_total"),
	("Purchase Receipt", "base_grand_total"),
	("Purchase Receipt", "base_rounded_total"),
	("Purchase Receipt Item", "price_list_rate"),
	("Purchase Receipt Item", "base_price_list_rate"),
	("Purchase Receipt Item", "discount_amount"),
	("Purchase Receipt Item", "rate"),
	("Purchase Receipt Item", "amount"),
	("Purchase Receipt Item", "base_rate"),
	("Purchase Receipt Item", "base_amount"),
	("Purchase Receipt Item", "net_rate"),
	("Purchase Receipt Item", "net_amount"),
	("Purchase Receipt Item", "base_net_rate"),
	("Purchase Receipt Item", "base_net_amount"),
	("Purchase Receipt Item", "valuation_rate"),
	("Purchase Receipt Item", "stock_uom_rate"),
	("Purchase Receipt Item", "rate_with_margin"),
	("Purchase Receipt Item", "base_rate_with_margin"),
	("Purchase Receipt Item", "landed_cost_voucher_amount"),
	("Purchase Receipt Item", "item_tax_amount"),
	("Purchase Receipt Item", "custom_lp_rate"),
]


def execute():
	settings = frappe.get_single("Deco Pan Settings")
	existing = {(d.document_type, d.field_name) for d in settings.get("hidden_fields", [])}

	for document_type, field_name in PURCHASE_RECEIPT_HIDDEN_FIELDS:
		if (document_type, field_name) not in existing:
			settings.append("hidden_fields", {"document_type": document_type, "field_name": field_name})
	settings.flags.ignore_mandatory = True
	settings.save(ignore_permissions=True)
