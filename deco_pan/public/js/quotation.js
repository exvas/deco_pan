

frappe.ui.form.on('Quotation Item', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code && frm.doc.party_name) {
            frappe.call({
                // method: 'custom_app.custom_methods.get_old_purchase_rate',
                method: "deco_pan.doc_events.quotation.get_old_purchase_rate",
                args: {
                    item_code: row.item_code,
                    party_name: frm.doc.party_name
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'custom_ls_rate', r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, 'custom_ls_rate', 0);
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, 'custom_ls_rate', 0);
        }
    }
});

frappe.ui.form.on('Quotation', {
    party_name: function(frm) {
        frm.doc.items.forEach(function(item) {
            if (item.item_code) {
                frappe.call({
                    method: "deco_pan.doc_events.quotation.get_old_purchase_rate",

                    args: {
                        item_code: item.item_code,
                        party_name: frm.doc.party_name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.model.set_value(item.doctype, item.name, 'custom_ls_rate', r.message);
                        } else {
                            frappe.model.set_value(item.doctype, item.name, 'custom_ls_rate', 0);
                        }
                    }
                });
            }
        });
    }
});
