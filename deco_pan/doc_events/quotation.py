
import frappe

@frappe.whitelist()
def get_old_purchase_rate(item_code, party_name):
    rate = 0
    # Fetch the last rate for the item from the given supplier
    result = frappe.db.sql("""
        SELECT rate
        FROM `tabQuotation Item`
        WHERE item_code = %s
        AND parenttype = 'Quotation'
        AND docstatus = 1
        AND parent IN (
            SELECT name FROM `tabQuotation`
            WHERE party_name = %s
        )
        ORDER BY creation DESC
        LIMIT 1
    """, (item_code, party_name), as_dict=True)
    
    if result:
        rate = result[0].get('rate', 0)
    
    return rate
