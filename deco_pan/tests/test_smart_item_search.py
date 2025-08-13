import frappe
import unittest
from deco_pan.doc_events.item_search import smart_item_search, get_item_suggestions, get_item_filters

class TestSmartItemSearch(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test items if they don't exist
        test_items = [
            {
                "item_code": "SIKA-FIX-001",
                "item_name": "Sika Anchor Fix1 300ml",
                "item_group": "Adhesives",
                "brand": "Sika",
                "stock_uom": "Nos"
            },
            {
                "item_code": "SIKA-FIX-002", 
                "item_name": "Sika Quick Fix Pro",
                "item_group": "Adhesives",
                "brand": "Sika",
                "stock_uom": "Nos"
            },
            {
                "item_code": "STEEL-ROD-001",
                "item_name": "Steel Rod 12mm TMT",
                "item_group": "Steel",
                "brand": "Tata",
                "stock_uom": "Kg"
            }
        ]
        
        for item_data in test_items:
            if not frappe.db.exists("Item", item_data["item_code"]):
                item_doc = frappe.get_doc({
                    "doctype": "Item",
                    "item_code": item_data["item_code"],
                    "item_name": item_data["item_name"],
                    "item_group": item_data["item_group"],
                    "brand": item_data["brand"],
                    "stock_uom": item_data["stock_uom"],
                    "is_stock_item": 1
                })
                item_doc.insert(ignore_permissions=True)
                frappe.db.commit()

    def test_smart_search_partial_match(self):
        """Test partial matching functionality"""
        results = smart_item_search("Sika Fix")
        
        # Should find items containing both "Sika" and "Fix"
        self.assertGreater(len(results), 0)
        
        # Check if our test items are found
        item_codes = [item["value"] for item in results]
        self.assertIn("SIKA-FIX-001", item_codes)
        self.assertIn("SIKA-FIX-002", item_codes)

    def test_smart_search_with_brand_filter(self):
        """Test search with brand filter"""
        results = smart_item_search("Fix", brand="Sika")
        
        # Should only find Sika brand items containing "Fix"
        for item in results:
            if item["brand"]:
                self.assertEqual(item["brand"], "Sika")

    def test_smart_search_with_item_group_filter(self):
        """Test search with item group filter"""
        results = smart_item_search("Steel", item_group="Steel")
        
        # Should only find items in Steel group
        for item in results:
            self.assertEqual(item["item_group"], "Steel")

    def test_get_item_filters(self):
        """Test getting available filters"""
        filters = get_item_filters()
        
        self.assertIn("item_groups", filters)
        self.assertIn("brands", filters)
        self.assertIsInstance(filters["item_groups"], list)
        self.assertIsInstance(filters["brands"], list)

    def test_get_item_suggestions(self):
        """Test getting item suggestions"""
        suggestions = get_item_suggestions("SIKA-FIX-001")
        
        # Should return list of related items
        self.assertIsInstance(suggestions, list)
        
        # Suggestions should not include the original item
        suggestion_codes = [item["value"] for item in suggestions]
        self.assertNotIn("SIKA-FIX-001", suggestion_codes)

    def test_empty_search_query(self):
        """Test behavior with empty search query"""
        results = smart_item_search("")
        self.assertEqual(len(results), 0)

    def test_no_results_found(self):
        """Test behavior when no results are found"""
        results = smart_item_search("NonExistentItemXYZ123")
        self.assertEqual(len(results), 0)

    def tearDown(self):
        """Clean up test data"""
        test_item_codes = ["SIKA-FIX-001", "SIKA-FIX-002", "STEEL-ROD-001"]
        for item_code in test_item_codes:
            if frappe.db.exists("Item", item_code):
                frappe.delete_doc("Item", item_code, ignore_permissions=True)
        frappe.db.commit()


if __name__ == "__main__":
    unittest.main()
