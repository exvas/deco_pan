

// Smart search functionality for Purchase Order items
frappe.ui.form.on('Purchase Order', {
    onload: function(frm) {
        // Debug log to confirm this code is running
        console.log("Deco Pan: Setting up smart search for Purchase Order");
        
        // Set up smart search for item_code field in items table
        frm.fields_dict["items"].grid.get_field("item_code").get_query = function(doc, cdt, cdn) {
            console.log("Deco Pan: Custom query called for item_code");
            return {
                query: "deco_pan.doc_events.item_search.get_items_for_dropdown",
                filters: {
                    doctype: "Purchase Order"
                }
            };
        };
        
        // Also try to override after form is fully loaded
        setTimeout(() => {
            if (frm.fields_dict["items"] && frm.fields_dict["items"].grid) {
                let item_field = frm.fields_dict["items"].grid.get_field("item_code");
                if (item_field) {
                    item_field.get_query = function(doc, cdt, cdn) {
                        console.log("Deco Pan: Delayed custom query setup");
                        return {
                            query: "deco_pan.doc_events.item_search.get_items_for_dropdown"
                        };
                    };
                }
            }
        }, 1000);
    }
});

frappe.ui.form.on('Purchase Order Item', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code && frm.doc.supplier) {
            frappe.call({
                method: "deco_pan.doc_events.purchase_order.get_old_purchase_rate",
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

frappe.ui.form.on('Purchase Order', {
    supplier: function(frm) {
        frm.doc.items.forEach(function(item) {
            if (item.item_code) {
                frappe.call({
                    method: "deco_pan.doc_events.purchase_order.get_old_purchase_rate",
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
