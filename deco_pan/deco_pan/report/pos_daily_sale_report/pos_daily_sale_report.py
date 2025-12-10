import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    report_summary = get_report_summary(filters, data)

    return columns, data, None, None, report_summary


def get_columns(filters):
    columns = [
        {
            "label": _("S.No"),
            "fieldname": "s_no",
            "fieldtype": "Int",
            "width": 60
        },
        {
            "label": _("Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("Invoice Number"),
            "fieldname": "invoice_no",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 210
        },
        {
            "label": _("Customer Name"),
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "width": 350
        },
    ]

    if filters.get("detailed_report"):
        columns.extend([
            {
                "label": _("Item"),
                "fieldname": "item_code",
                "fieldtype": "Link",
                "options": "Item",
                "width": 500
            },
            {
                "label": _("Qty"),
                "fieldname": "qty",
                "fieldtype": "Float",
                "width": 80
            },
            {
                "label": _("Rate"),
                "fieldname": "rate",
                "fieldtype": "Currency",
                "width": 100
            },
        ])

    columns.extend([
        {
            "label": _("Amount"),
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Cash"),
            "fieldname": "cash_amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Card"),
            "fieldname": "card_amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("General"),
            "fieldname": "general_amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Mode"),
            "fieldname": "mode_of_payment",
            "fieldtype": "Data",
            "width": 300
        },
        {
            "label": _("User"),
            "fieldname": "owner_name",
            "fieldtype": "Data",
            "width": 250
        },
    ])

    return columns


def get_data(filters):
    conditions = get_conditions(filters)

    if filters.get("detailed_report"):
        return get_detailed_data(conditions, filters)
    else:
        return get_summary_data(conditions, filters)


def get_conditions(filters):
    conditions = ["si.docstatus = 1", "si.is_pos = 1"]

    if filters.get("from_date"):
        conditions.append(f"si.posting_date >= '{filters.get('from_date')}'")

    if filters.get("to_date"):
        conditions.append(f"si.posting_date <= '{filters.get('to_date')}'")

    if filters.get("pos_profile"):
        conditions.append(f"si.pos_profile = '{filters.get('pos_profile')}'")

    if filters.get("customer"):
        conditions.append(f"si.customer = '{filters.get('customer')}'")

    if filters.get("owner"):
        conditions.append(f"si.owner = '{filters.get('owner')}'")

    return " AND ".join(conditions)


def get_summary_data(conditions, filters):
    data = frappe.db.sql(f"""
        SELECT
            si.posting_date,
            si.name as invoice_no,
            si.customer_name,
            si.grand_total as amount,
            si.owner,
            (SELECT full_name FROM `tabUser` WHERE name = si.owner) as owner_name
        FROM
            `tabSales Invoice` si
        WHERE
            {conditions}
        ORDER BY
            si.posting_date, si.name
    """, as_dict=True)

    result = []
    for idx, row in enumerate(data, 1):
        row["s_no"] = idx

        payment_details = get_payment_details(row.invoice_no)
        row["cash_amount"] = payment_details.get("cash", 0)
        row["card_amount"] = payment_details.get("card", 0)
        row["general_amount"] = payment_details.get("general", 0)
        row["mode_of_payment"] = payment_details.get("mode", "")

        result.append(row)

    return result


def get_detailed_data(conditions, filters):
    data = frappe.db.sql(f"""
        SELECT
            si.posting_date,
            si.name as invoice_no,
            si.customer_name,
            sii.item_code,
            sii.item_name,
            sii.qty,
            sii.rate,
            sii.amount,
            si.owner,
            (SELECT full_name FROM `tabUser` WHERE name = si.owner) as owner_name
        FROM
            `tabSales Invoice` si
        INNER JOIN
            `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE
            {conditions}
        ORDER BY
            si.posting_date, si.name, sii.idx
    """, as_dict=True)

    result = []
    current_invoice = None
    s_no = 0

    for row in data:
        if current_invoice != row.invoice_no:
            current_invoice = row.invoice_no
            s_no += 1
            row["s_no"] = s_no

            payment_details = get_payment_details(row.invoice_no)
            row["cash_amount"] = payment_details.get("cash", 0)
            row["card_amount"] = payment_details.get("card", 0)
            row["general_amount"] = payment_details.get("general", 0)
            row["mode_of_payment"] = payment_details.get("mode", "")
        else:
            row["s_no"] = ""
            row["posting_date"] = ""
            row["customer_name"] = ""
            row["cash_amount"] = ""
            row["card_amount"] = ""
            row["general_amount"] = ""
            row["mode_of_payment"] = ""
            row["owner_name"] = ""

        result.append(row)

    return result


def get_payment_details(invoice_no):
    payments = frappe.db.sql("""
        SELECT sip.mode_of_payment, sip.amount, mop.type as mode_type
        FROM `tabSales Invoice Payment` sip
        LEFT JOIN `tabMode of Payment` mop ON mop.name = sip.mode_of_payment
        WHERE sip.parent = %s
    """, invoice_no, as_dict=True)

    cash_amount = 0
    card_amount = 0
    general_amount = 0
    modes = []

    for payment in payments:
        mode = payment.get("mode_of_payment", "")
        mode_type = payment.get("mode_type", "")
        amount = flt(payment.get("amount", 0))

        if mode_type == "Cash":
            cash_amount += amount
        elif mode_type == "Bank":
            card_amount += amount
        elif mode_type == "General":
            general_amount += amount
        else:
            general_amount += amount

        if mode and mode not in modes:
            modes.append(mode)

    mode_display = ", ".join(modes) if modes else ""

    return {
        "cash": cash_amount,
        "card": card_amount,
        "general": general_amount,
        "mode": mode_display
    }


def get_report_summary(filters, data):
    total_amount = 0
    total_cash = 0
    total_card = 0
    total_general = 0

    processed_invoices = set()

    for row in data:
        invoice_no = row.get("invoice_no")
        if invoice_no and invoice_no not in processed_invoices:
            processed_invoices.add(invoice_no)
            total_amount += flt(row.get("amount", 0))
            total_cash += flt(row.get("cash_amount", 0)) if row.get("cash_amount") != "" else 0
            total_card += flt(row.get("card_amount", 0)) if row.get("card_amount") != "" else 0
            total_general += flt(row.get("general_amount", 0)) if row.get("general_amount") != "" else 0

    opening_cash = flt(filters.get("opening_cash_balance", 0))
    closing_cash = opening_cash + total_cash

    return [
        {
            "value": total_amount,
            "indicator": "Blue",
            "label": _("Total Amount"),
            "datatype": "Currency",
            "currency": frappe.db.get_default("currency")
        },
        {
            "value": total_cash,
            "indicator": "Green",
            "label": _("Total Cash"),
            "datatype": "Currency",
            "currency": frappe.db.get_default("currency")
        },
        {
            "value": total_card,
            "indicator": "Orange",
            "label": _("Total Card"),
            "datatype": "Currency",
            "currency": frappe.db.get_default("currency")
        },
        {
            "value": total_general,
            "indicator": "Purple",
            "label": _("Total General"),
            "datatype": "Currency",
            "currency": frappe.db.get_default("currency")
        },
        {
            "value": opening_cash,
            "indicator": "Blue",
            "label": _("Opening Cash Balance"),
            "datatype": "Currency",
            "currency": frappe.db.get_default("currency")
        },
        {
            "value": closing_cash,
            "indicator": "Green",
            "label": _("Closing Cash Balance"),
            "datatype": "Currency",
            "currency": frappe.db.get_default("currency")
        },
    ]
