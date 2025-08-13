import frappe
import re

@frappe.whitelist()
def get_items_for_dropdown(doctype, txt, searchfield, start, page_len, filters):
    """
    Enhanced item search for dropdown - used by Link field queries
    This replaces the standard item search with smart search functionality
    """
    # Debug logging
    print(f"DECO_PAN DEBUG: Search called with txt='{txt}'")
    frappe.logger().info(f"DECO_PAN: Smart search called with txt: '{txt}'")
    
    if not txt:
        return frappe.db.sql("""
            SELECT item_code, item_name
            FROM `tabItem`
            WHERE disabled = 0
            ORDER BY modified DESC
            LIMIT 20
        """)
    
    # Split search terms
    search_terms = [term.strip() for term in txt.split() if term.strip()]
    print(f"DECO_PAN DEBUG: Search terms: {search_terms}")
    
    if len(search_terms) == 0:
        return []
    
    # Simple approach: find items where ALL search terms appear somewhere
    try:
        if len(search_terms) == 1:
            # Single term search
            term = search_terms[0].lower()
            results = frappe.db.sql("""
                SELECT item_code, item_name
                FROM `tabItem`
                WHERE disabled = 0 
                AND (LOWER(item_code) LIKE %s OR LOWER(item_name) LIKE %s)
                ORDER BY 
                    CASE 
                        WHEN LOWER(item_code) LIKE %s THEN 1
                        WHEN LOWER(item_name) LIKE %s THEN 2
                        ELSE 3
                    END,
                    item_name
                LIMIT 20
            """, (f"%{term}%", f"%{term}%", f"{term}%", f"{term}%"))
            
        else:
            # Multiple terms - all must be present
            like_conditions = []
            values = []
            
            for term in search_terms:
                like_conditions.append("""
                    (LOWER(item_code) LIKE %s OR LOWER(item_name) LIKE %s)
                """)
                term_lower = term.lower()
                values.extend([f"%{term_lower}%", f"%{term_lower}%"])
            
            where_clause = " AND ".join(like_conditions)
            
            sql = f"""
                SELECT item_code, item_name
                FROM `tabItem`
                WHERE disabled = 0 
                AND {where_clause}
                ORDER BY item_name
                LIMIT 20
            """
            
            results = frappe.db.sql(sql, values)
        
        print(f"DECO_PAN DEBUG: Found {len(results)} results")
        for r in results[:3]:  # Show first 3 results
            print(f"DECO_PAN DEBUG: Result: {r[0]} - {r[1]}")
            
        return results
        
    except Exception as e:
        print(f"DECO_PAN DEBUG: Error: {str(e)}")
        frappe.log_error(f"Error in smart search: {str(e)}")
        # Simple fallback
        return frappe.db.sql("""
            SELECT item_code, item_name
            FROM `tabItem`
            WHERE disabled = 0 
            AND (LOWER(item_code) LIKE %s OR LOWER(item_name) LIKE %s)
            ORDER BY item_name
            LIMIT 20
        """, (f"%{txt.lower()}%", f"%{txt.lower()}%"))

@frappe.whitelist()
def smart_item_search(query="", doctype="Purchase Order", item_group="", brand=""):
    """
    Smart item search that allows partial matching of item names
    Example: Searching "Sika Fix" will find "Sika Anchor Fix1 300ml"
    """
    if not query:
        return []
    
    # Clean and prepare the search query
    search_terms = [term.strip() for term in query.split() if term.strip()]
    
    if not search_terms:
        return []
    
    # Build SQL conditions for smart search
    conditions = []
    values = []
    
    # Search in item_code, item_name, and barcode
    for term in search_terms:
        # Use LIKE with wildcards for partial matching
        term_condition = """
            (item_code LIKE %s OR 
             item_name LIKE %s OR
             item_code LIKE %s OR
             item_name LIKE %s OR
             barcode LIKE %s)
        """
        # Add different variations of the search term
        wildcard_term = f"%{term}%"
        start_term = f"{term}%"
        
        conditions.append(term_condition)
        values.extend([wildcard_term, wildcard_term, start_term, start_term, wildcard_term])
    
    # Join conditions with AND to match all terms
    where_clause = " AND ".join([f"({condition})" for condition in conditions])
    
    # Add filters for item_group and brand if provided
    additional_filters = []
    if item_group:
        additional_filters.append("item_group = %s")
        values.append(item_group)
    
    if brand:
        additional_filters.append("brand = %s")
        values.append(brand)
    
    if additional_filters:
        where_clause += " AND " + " AND ".join(additional_filters)
    
    # Base SQL query
    sql_query = f"""
        SELECT 
            item_code,
            item_name,
            stock_uom,
            item_group,
            brand,
            description,
            barcode,
            CASE 
                WHEN item_code LIKE %s THEN 1
                WHEN item_name LIKE %s THEN 2
                WHEN barcode LIKE %s THEN 3
                ELSE 4
            END as relevance_score
        FROM `tabItem`
        WHERE disabled = 0 
        AND ({where_clause})
        ORDER BY relevance_score, item_name
        LIMIT 25
    """
    
    # Add values for relevance scoring (exact match gets higher score)
    exact_match_term = f"{query}%"
    final_values = [exact_match_term, exact_match_term, exact_match_term] + values
    
    try:
        results = frappe.db.sql(sql_query, final_values, as_dict=True)
        
        # Format results for frontend consumption
        formatted_results = []
        for item in results:
            formatted_results.append({
                "value": item.item_code,
                "label": f"{item.item_code} - {item.item_name}",
                "description": item.description or "",
                "item_name": item.item_name,
                "stock_uom": item.stock_uom,
                "item_group": item.item_group,
                "brand": item.brand or "",
                "barcode": item.barcode or ""
            })
        
        return formatted_results
        
    except Exception as e:
        frappe.log_error(f"Error in smart_item_search: {str(e)}")
        return []

@frappe.whitelist()
def get_item_filters():
    """
    Get item groups and brands for filtering
    """
    try:
        # Get item groups
        item_groups = frappe.db.sql("""
            SELECT DISTINCT item_group 
            FROM `tabItem` 
            WHERE disabled = 0 AND item_group IS NOT NULL AND item_group != ''
            ORDER BY item_group
        """, as_dict=True)
        
        # Get brands
        brands = frappe.db.sql("""
            SELECT DISTINCT brand 
            FROM `tabItem` 
            WHERE disabled = 0 AND brand IS NOT NULL AND brand != ''
            ORDER BY brand
        """, as_dict=True)
        
        return {
            "item_groups": [group.item_group for group in item_groups],
            "brands": [brand.brand for brand in brands]
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_item_filters: {str(e)}")
        return {"item_groups": [], "brands": []}

@frappe.whitelist()
def get_item_suggestions(item_code):
    """
    Get similar items based on the selected item
    This can be used to suggest related products
    """
    if not item_code:
        return []
    
    try:
        # Get the current item details
        current_item = frappe.get_doc("Item", item_code)
        
        if not current_item:
            return []
        
        # Extract keywords from the current item name for finding similar items
        item_name = current_item.item_name or ""
        item_words = re.findall(r'\w+', item_name.lower())
        
        # Remove common words that don't help in matching
        common_words = {'ml', 'kg', 'pcs', 'piece', 'pieces', 'pack', 'box', 'the', 'and', 'or', 'of', 'in', 'on', 'at', 'to', 'for', 'with'}
        significant_words = [word for word in item_words if word not in common_words and len(word) > 2]
        
        if not significant_words:
            return []
        
        # Build search for similar items
        conditions = []
        values = []
        
        for word in significant_words[:3]:  # Use only first 3 significant words
            conditions.append("(item_name LIKE %s OR item_code LIKE %s)")
            wildcard_word = f"%{word}%"
            values.extend([wildcard_word, wildcard_word])
        
        where_clause = " OR ".join(conditions)
        
        sql_query = f"""
            SELECT 
                item_code,
                item_name,
                stock_uom,
                item_group
            FROM `tabItem`
            WHERE disabled = 0 
            AND item_code != %s
            AND ({where_clause})
            ORDER BY item_name
            LIMIT 10
        """
        
        final_values = [item_code] + values
        results = frappe.db.sql(sql_query, final_values, as_dict=True)
        
        formatted_results = []
        for item in results:
            formatted_results.append({
                "value": item.item_code,
                "label": f"{item.item_code} - {item.item_name}",
                "item_name": item.item_name,
                "stock_uom": item.stock_uom,
                "item_group": item.item_group
            })
        
        return formatted_results
        
    except Exception as e:
        frappe.log_error(f"Error in get_item_suggestions: {str(e)}")
        return []
