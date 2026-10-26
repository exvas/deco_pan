// Copyright (c) 2024, sammish and contributors
// For license information, please see license.txt

frappe.ui.form.on("Deco Pan Hidden Field", {
	document_type(frm, cdt, cdn) {
		set_field_name_options(frm, locals[cdt][cdn]);
	},
	form_render(frm, cdt, cdn) {
		set_field_name_options(frm, locals[cdt][cdn]);
	},
});

function set_field_name_options(frm, row) {
	if (!row.document_type) return;
	frappe.model.with_doctype(row.document_type, () => {
		const options = frappe.meta
			.get_docfields(row.document_type)
			.filter((df) => !frappe.model.no_value_type.includes(df.fieldtype) || df.fieldtype === "Tab Break" || df.fieldtype === "Section Break")
			.map((df) => ({ value: df.fieldname, label: `${__(df.label || df.fieldname)} (${df.fieldname})` }));
		frm.fields_dict.hidden_fields.grid.update_docfield_property("field_name", "options", options);
	});
}
