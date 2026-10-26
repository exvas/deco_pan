// Hide cost / buying price fields for users restricted in Deco Pan Settings.
// The rules come from bootinfo (deco_pan.deco_pan.doctype.deco_pan_settings.deco_pan_settings.boot_session).

frappe.provide("deco_pan");

deco_pan.hide_cost_fields = function () {
	const hidden = (frappe.boot && frappe.boot.deco_pan_hidden_fields) || {};
	Object.keys(hidden).forEach((doctype) => {
		const meta = locals.DocType && locals.DocType[doctype];
		if (!meta) return;
		(meta.fields || []).forEach((df) => {
			if (hidden[doctype].includes(df.fieldname)) {
				df.hidden = 1;
				df.in_list_view = 0;
				df.in_preview = 0;
			}
		});
	});
};

$(document).on("app_ready", () => {
	if (!Object.keys(frappe.boot.deco_pan_hidden_fields || {}).length) return;

	// meta (including child doctypes) is loaded lazily; patch it every time a doctype loads
	const init_doctype = frappe.model.init_doctype;
	frappe.model.init_doctype = function (doctype) {
		deco_pan.hide_cost_fields();
		return init_doctype.apply(this, arguments);
	};
	deco_pan.hide_cost_fields();
});

// child table columns follow the patched meta; this keeps parent fields hidden even if
// a form script toggles them back on
$(document).on("form-refresh", (e, frm) => {
	const fieldnames = frm && (frappe.boot.deco_pan_hidden_fields || {})[frm.doctype];
	(fieldnames || []).forEach((fieldname) => frm.toggle_display(fieldname, false));
});
