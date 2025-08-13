# Smart Item Search for Purchase Orders

This feature provides an intelligent search functionality integrated directly into the Purchase Order Item table's item code field. It allows users to find items using partial matches without any additional buttons or dialogs.

## Features

### 1. Integrated Smart Search
- **Seamless Integration**: Works directly in the item code dropdown field
- **Partial Matching**: Search for "Sika Fix" to find "Sika Anchor Fix1 300ml"
- **Multiple Search Fields**: Searches across item code, item name, and barcode
- **Intelligent Ranking**: Results are ranked by relevance with exact matches appearing first

### 2. Real-time Search
- **Instant Results**: Search results appear as you type in the item code field
- **Fuzzy Matching**: Finds items even with partial or abbreviated terms

## How to Use

### Simple Search Process
1. Open a Purchase Order
2. In the Items table, click on the **Item Code** field
3. Start typing your search query (e.g., "Sika Fix")
4. Select from the dropdown results
5. The item will be automatically populated

### Search Examples

#### Basic Search
- Type: `Sika Fix`
- Finds: "Sika Anchor Fix1 300ml", "Sika Fix Pro", "Sika Quick Fix"

#### Barcode Search
- Type: `12345`
- Finds: Items with barcode containing "12345"

#### Multi-word Search
- Type: `Steel Rod 12mm`
- Finds: Items containing all these terms

#### Brand Search
- Type: `Sika Anchor`
- Finds: All Sika items containing "Anchor"

## Technical Implementation

### Backend (Python)
- `get_items_for_dropdown()`: Enhanced query function for item code field
- Optimized SQL queries with relevance-based ranking
- Fallback to simple search in case of errors

### Frontend (JavaScript)
- Integrated with standard Frappe Link field functionality
- No additional UI components or dialogs
- Maintains all existing Purchase Order functionality

### Database Optimization
- Uses optimized SQL queries with proper indexing
- Limits results to 20 items for performance
- Relevance-based sorting for better user experience

## Benefits

1. **Seamless Experience**: No additional buttons or complex interfaces
2. **Faster Item Selection**: Find items quickly with partial names
3. **Reduced Errors**: Standard dropdown behavior with enhanced search
4. **Zero Learning Curve**: Works exactly like existing item selection
5. **Performance Optimized**: Fast search with minimal overhead

## Installation

The smart search feature is automatically enabled when the `deco_pan` app is installed. The JavaScript files are loaded automatically for Purchase Order forms.

## Customization

You can customize the search behavior by modifying:
- Search ranking algorithm in `item_search.py`
- Number of results returned (currently 20)
- Search fields included in the query

## Troubleshooting

**Search not working**: Ensure the app is properly installed and bench is restarted.
**No results**: Check if items are enabled and contain the search terms.
**Slow performance**: The system limits results to 20 items; try more specific search terms.
