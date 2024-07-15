frappe.listview_settings['Cash Invoice'] = {
    get_indicator(doc) {
            // customize indicator color
            if (doc.status == "Paid" && doc.docstatus == 1) {
                return [__("Paid"), "green", "status,=,Paid"];
            }
        },
    }