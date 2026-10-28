import frappe

# applied to every query report (rows without a report)
GLOBAL_COST_COLUMNS = [
	"valuation_rate", "val_rate", "incoming_rate", "outgoing_rate", "in_out_rate",
	"stock_value", "stock_value_difference", "stock_value_from_diff", "expected_stock_value",
	"fifo_stock_value", "fifo_valuation_rate", "fifo_valuation_diff", "valuation_diff",
	"opening_val", "in_val", "out_val", "bal_val", "consumption_rate",
	"last_purchase_rate", "buying_rate", "buying_price_list", "buying_amount",
	"avg_buying_price_list_rate", "purchase_rate", "purchase_amount", "gross_purchase_amount",
	"gross_profit", "gross_profit_percent", "gross_profit_loss", "landed_cost_voucher_amount",
	"bom_rate", "operating_cost", "custom_lp_rate",
]


def execute():
	settings = frappe.get_single("Deco Pan Settings")
	existing = {(d.report or None, d.column_name) for d in settings.get("hidden_report_columns", [])}
	for column_name in GLOBAL_COST_COLUMNS:
		if (None, column_name) not in existing:
			settings.append("hidden_report_columns", {"column_name": column_name})

	# site-specific purchase report not based on a standard (blocked) report
	blocked = {d.report for d in settings.get("blocked_reports", [])}
	if "PURCHASE ORDER TRACKING" not in blocked and frappe.db.exists("Report", "PURCHASE ORDER TRACKING"):
		settings.append("blocked_reports", {"report": "PURCHASE ORDER TRACKING"})

	settings.flags.ignore_mandatory = True
	settings.save(ignore_permissions=True)
