

frappe.ui.form.on('Purchase Receipt Item', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code && frm.doc.supplier) {
            frappe.call({
                // method: 'custom_app.custom_methods.get_old_purchase_rate',
                method: "deco_pan.doc_events.purchase_receipt.get_old_purchase_rate",
                args: {
                    item_code: row.item_code,
                    supplier: frm.doc.supplier
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'custom_lp_rate', r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, 'custom_lp_rate', 0);
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, 'custom_lp_rate', 0);
        }
    }
});

frappe.ui.form.on('Purchase Receipt', {
    supplier: function(frm) {
        frm.doc.items.forEach(function(item) {
            if (item.item_code) {
                frappe.call({
                    method: "deco_pan.doc_events.purchase_receipt.get_old_purchase_rate",

                    args: {
                        item_code: item.item_code,
                        supplier: frm.doc.supplier
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.model.set_value(item.doctype, item.name, 'custom_lp_rate', r.message);
                        } else {
                            frappe.model.set_value(item.doctype, item.name, 'custom_lp_rate', 0);
                        }
                    }
                });
            }
        });
    }
});
