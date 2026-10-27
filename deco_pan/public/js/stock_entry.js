// Limit Stock Entry Type for users restricted in Deco Pan Settings

frappe.ui.form.on("Stock Entry", {
	setup(frm) {
		const allowed = frappe.boot.deco_pan_allowed_stock_entry_types || [];
		if (!allowed.length) return;

		frm.set_query("stock_entry_type", () => ({
			filters: { name: ["in", allowed] },
		}));
	},

	onload(frm) {
		const allowed = frappe.boot.deco_pan_allowed_stock_entry_types || [];
		if (frm.is_new() && allowed.length && !allowed.includes(frm.doc.stock_entry_type)) {
			frm.set_value("stock_entry_type", allowed[0]);
		}
	},
});
