import frappe

PURCHASE_HIDDEN_FIELDS = {
	"Purchase Order": [
		"total", "net_total", "base_total", "base_net_total", "taxes_section", "sec_tax_breakup",
		"discount_section", "totals_section", "grand_total", "rounded_total", "base_grand_total",
		"base_rounded_total", "advance_paid", "payment_schedule_section",
	],
	"Purchase Order Item": [
		"price_list_rate", "base_price_list_rate", "discount_amount", "last_purchase_rate", "rate", "amount",
		"base_rate", "base_amount", "net_rate", "net_amount", "base_net_rate", "base_net_amount",
		"blanket_order_rate", "billed_amt", "stock_uom_rate", "rate_with_margin", "base_rate_with_margin",
		"custom_lp_rate",
	],
	"Purchase Invoice": [
		"total", "net_total", "base_total", "base_net_total", "taxes_section", "sec_tax_breakup",
		"section_break_44", "section_break_49", "grand_total", "rounded_total", "base_grand_total",
		"base_rounded_total", "outstanding_amount", "paid_amount", "payments_tab", "payments_section",
		"write_off", "advances_section", "payment_schedule_section",
	],
	"Purchase Invoice Item": [
		"price_list_rate", "base_price_list_rate", "discount_amount", "rate", "amount", "base_rate",
		"base_amount", "net_rate", "net_amount", "base_net_rate", "base_net_amount", "item_tax_amount",
		"valuation_rate", "landed_cost_voucher_amount", "stock_uom_rate", "rate_with_margin",
		"base_rate_with_margin", "custom_lp_rate",
	],
	"Stock Ledger Entry": ["incoming_rate", "outgoing_rate", "valuation_rate", "stock_value", "stock_value_difference"],
	"Bin": ["valuation_rate", "stock_value"],
}

HIDDEN_REPORT_COLUMNS = {
	"Stock Ledger": ["incoming_rate", "valuation_rate", "in_out_rate", "stock_value", "stock_value_difference"],
	"Stock Balance": ["opening_val", "in_val", "out_val", "bal_val", "val_rate"],
	"Warehouse wise Item Balance Age and Value": ["value"],
	"Item Prices": ["last_purchase_rate", "valuation_rate", "purchase_price_list", "bom_rate"],
	"Item Price Stock": ["buying_price_list", "buying_rate"],
}

BLOCKED_REPORTS = [
	"Purchase Register",
	"Item-wise Purchase Register",
	"Item-wise Purchase History",
	"Purchase Analytics",
	"Purchase Order Analysis",
	"Purchase Invoice Trends",
	"Purchase Order Trends",
	"Purchase Receipt Trends",
	"Received Items To Be Billed",
	"Gross Profit",
	"Stock and Account Value Comparison",
	"Incorrect Stock Value Report",
]


def execute():
	settings = frappe.get_single("Deco Pan Settings")

	existing = {(d.document_type, d.field_name) for d in settings.get("hidden_fields", [])}
	for document_type, fieldnames in PURCHASE_HIDDEN_FIELDS.items():
		for field_name in fieldnames:
			if (document_type, field_name) not in existing:
				settings.append("hidden_fields", {"document_type": document_type, "field_name": field_name})

	existing = {(d.report, d.column_name) for d in settings.get("hidden_report_columns", [])}
	for report, columns in HIDDEN_REPORT_COLUMNS.items():
		if not frappe.db.exists("Report", report):
			continue
		for column_name in columns:
			if (report, column_name) not in existing:
				settings.append("hidden_report_columns", {"report": report, "column_name": column_name})

	existing = {d.report for d in settings.get("blocked_reports", [])}
	for report in BLOCKED_REPORTS:
		if report not in existing and frappe.db.exists("Report", report):
			settings.append("blocked_reports", {"report": report})

	settings.flags.ignore_mandatory = True
	settings.save(ignore_permissions=True)
