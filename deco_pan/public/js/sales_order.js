

frappe.ui.form.on('Sales Order Item', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code && frm.doc.customer) {
            frappe.call({
                // method: 'custom_app.custom_methods.get_old_purchase_rate',
                method: "deco_pan.doc_events.sales_order.get_old_purchase_rate",
                args: {
                    item_code: row.item_code,
                    customer: frm.doc.customer
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

frappe.ui.form.on('Sales Order', {
    customer: function(frm) {
        frm.doc.items.forEach(function(item) {
            if (item.item_code) {
                frappe.call({
                    method: "deco_pan.doc_events.sales_order.get_old_purchase_rate",

                    args: {
                        item_code: item.item_code,
                        customer: frm.doc.customer
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
