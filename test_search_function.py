import frappe
from deco_pan.doc_events.item_search import get_items_for_dropdown

def test_search():
    """Simple test function to verify search works"""
    
    # Test search for "sika fix"
    print("Testing search for 'sika fix':")
    results = get_items_for_dropdown("Purchase Order", "sika fix", "item_code", 0, 20, {})
    
    for result in results:
        print(f"Found: {result[0]} - {result[1]}")
    
    print(f"\nTotal results: {len(results)}")
    
    # Test search for "anchor"
    print("\nTesting search for 'anchor':")
    results2 = get_items_for_dropdown("Purchase Order", "anchor", "item_code", 0, 20, {})
    
    for result in results2:
        print(f"Found: {result[0]} - {result[1]}")
    
    print(f"\nTotal results: {len(results2)}")

if __name__ == "__main__":
    test_search()
