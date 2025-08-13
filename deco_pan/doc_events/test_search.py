import frappe

@frappe.whitelist()
def test_simple_search(txt):
    """
    Simple test search to verify functionality
    """
    if not txt:
        return []
    
    # Very simple search
    results = frappe.db.sql("""
        SELECT item_code, item_name
        FROM `tabItem`
        WHERE disabled = 0 
        AND (LOWER(item_name) LIKE %s OR LOWER(item_code) LIKE %s)
        ORDER BY item_name
        LIMIT 10
    """, (f"%{txt.lower()}%", f"%{txt.lower()}%"))
    
    return [{"item_code": r[0], "item_name": r[1]} for r in results]
