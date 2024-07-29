
import frappe

@frappe.whitelist()
def get_old_purchase_rate(item_code, customer):
    rate = 0
    # Fetch the last rate for the item from the given supplier
    result = frappe.db.sql("""
        SELECT rate
        FROM `tabSales Order Item`
        WHERE item_code = %s
        AND parenttype = 'Sales Order'
        AND docstatus = 1
        AND parent IN (
            SELECT name FROM `tabSales Order`
            WHERE customer = %s
        )
        ORDER BY creation DESC
        LIMIT 1
    """, (item_code, customer), as_dict=True)
    
    if result:
        rate = result[0].get('rate', 0)
    
    return rate
