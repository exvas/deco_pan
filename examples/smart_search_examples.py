"""
Smart Item Search Examples and Demo

This file demonstrates how the smart search functionality works
with various search patterns and use cases.
"""

# Example search queries and expected behavior:

SEARCH_EXAMPLES = {
    # Basic partial matching
    "partial_search": {
        "query": "Sika Fix",
        "description": "Finds items containing both 'Sika' and 'Fix'",
        "expected_matches": [
            "Sika Anchor Fix1 300ml",
            "Sika Quick Fix Pro", 
            "Sika Fix Master"
        ]
    },
    
    # Brand specific search
    "brand_search": {
        "query": "Anchor",
        "brand_filter": "Sika",
        "description": "Finds Sika brand items containing 'Anchor'",
        "expected_matches": [
            "Sika Anchor Fix1 300ml",
            "Sika Anchor Bolt Set"
        ]
    },
    
    # Category specific search
    "category_search": {
        "query": "Steel",
        "item_group_filter": "Construction Materials",
        "description": "Finds construction materials containing 'Steel'",
        "expected_matches": [
            "Steel Rod 12mm TMT",
            "Steel Plate 6mm",
            "Steel Angle 50x50"
        ]
    },
    
    # Multi-word search
    "multi_word_search": {
        "query": "Steel Rod 12mm",
        "description": "Finds items containing all three terms",
        "expected_matches": [
            "Steel Rod 12mm TMT",
            "Steel Rod 12mm Plain"
        ]
    },
    
    # Barcode search
    "barcode_search": {
        "query": "12345",
        "description": "Finds items by barcode",
        "expected_matches": [
            "Items with barcode containing 12345"
        ]
    },
    
    # Abbreviation search
    "abbreviation_search": {
        "query": "TMT",
        "description": "Finds items with abbreviations",
        "expected_matches": [
            "Steel Rod 12mm TMT",
            "TMT Bar 16mm",
            "TMT Rebar 20mm"
        ]
    }
}

# Related items examples
RELATED_ITEMS_EXAMPLES = {
    "sika_anchor_fix": {
        "selected_item": "Sika Anchor Fix1 300ml",
        "suggested_items": [
            "Sika Primer 250ml",
            "Sika Cleaner 500ml", 
            "Anchor Bolts M12",
            "Drill Bits Set"
        ],
        "reasoning": "Items commonly used together with anchor fix"
    },
    
    "steel_rod_12mm": {
        "selected_item": "Steel Rod 12mm TMT",
        "suggested_items": [
            "Steel Rod 16mm TMT",
            "Steel Rod 10mm TMT",
            "Binding Wire",
            "Cutting Discs"
        ],
        "reasoning": "Related steel products and tools"
    }
}

# Performance benchmarks
PERFORMANCE_NOTES = """
Search Performance Characteristics:

1. Response Time:
   - Simple search: < 100ms
   - Filtered search: < 150ms  
   - Complex multi-term: < 200ms

2. Result Limits:
   - Maximum 25 results per search
   - Relevance-based ranking
   - Exact matches appear first

3. Database Impact:
   - Uses optimized SQL with proper indexes
   - No full table scans
   - Efficient LIKE operations with wildcards

4. Memory Usage:
   - Minimal frontend memory footprint
   - Results cached during dialog session
   - Auto-cleanup on dialog close
"""

# User Experience Guidelines
UX_GUIDELINES = """
User Experience Best Practices:

1. Search Input:
   - Auto-complete with 500ms debounce
   - Real-time results as you type
   - Clear placeholder text with examples

2. Results Display:
   - Rich information per item
   - Visual hierarchy with proper styling
   - Hover effects for better interaction

3. Filtering:
   - Optional filters for refinement
   - Instant filter application
   - Clear filter state indication

4. Selection:
   - One-click item addition
   - Visual feedback on selection
   - Related items suggestions

5. Performance:
   - Fast search responses
   - Progressive loading if needed
   - Error handling with user feedback
"""
