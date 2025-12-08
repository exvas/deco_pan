frappe.query_reports["POS Daily Sale Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "pos_profile",
            "label": __("POS Profile"),
            "fieldtype": "Link",
            "options": "POS Profile"
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer"
        },
        {
            "fieldname": "mode_of_payment",
            "label": __("Mode of Payment"),
            "fieldtype": "Link",
            "options": "Mode of Payment"
        },
        {
            "fieldname": "owner",
            "label": __("User"),
            "fieldtype": "Link",
            "options": "User"
        },
        {
            "fieldname": "opening_cash_balance",
            "label": __("Opening Cash Balance"),
            "fieldtype": "Currency",
            "default": 0
        },
        {
            "fieldname": "detailed_report",
            "label": __("Detailed Report"),
            "fieldtype": "Check",
            "default": 0
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname == "amount" && data && data.amount) {
            value = "<b>" + value + "</b>";
        }

        return value;
    },

    "onload": function(report) {
        report.page.add_inner_button(__("Print"), function() {
            frappe.query_report.print_report();
        });
    }
};
