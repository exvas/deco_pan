
import frappe

@frappe.whitelist()
def get_old_purchase_rate(item_code, supplier):
    rate = 0
    # Fetch the last rate for the item from the given supplier
    result = frappe.db.sql("""
        SELECT rate
        FROM `tabPurchase Invoice Item`
        WHERE item_code = %s
        AND parenttype = 'Purchase Invoice'
        AND docstatus = 1
        AND parent IN (
            SELECT name FROM `tabPurchase Invoice`
            WHERE supplier = %s
        )
        ORDER BY creation DESC
        LIMIT 1
    """, (item_code, supplier), as_dict=True)
    
    if result:
        rate = result[0].get('rate', 0)
    
    return rate
