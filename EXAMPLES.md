# Examples

Real-world usage examples for Guru2Notion.

## Example 1: Simple Export (Recommended)

**Scenario:** Export "Sales Playbook" collection with 170 cards

```bash
# Step 1: Export from Guru website
# Go to Guru → Sales Playbook → Settings → Export
# Download: guru_sales_playbook.zip

# Step 2: Enrich and convert
python3 guru_enricher.py ~/Downloads/guru_sales_playbook.zip
```

**Output:**
```
💎 GURU ENRICHER

📦 ANALYZING WEBSITE EXPORT
✓ Extracted 170 card IDs from export

💎 ENRICHING WITH API DATA
  Enriching: ████████████████████ 170/170 (100%)
✓ Enriched 170/170 cards

📦 Creating enriched export...
  ✓ Created guru_sales_playbook_enriched_notion_ready.zip

Convert to Notion format now? (y/n): y
✓ Converted to Notion format

📦 Ready to import: guru_sales_playbook_enriched_notion_ready.zip
```

**Step 3: Import to Notion**
- Settings & Members → Import → Markdown & CSV
- Upload `guru_sales_playbook_enriched_notion_ready.zip`
- Done! ✨

---

## Example 2: Export with Filtering

**Scenario:** Export only TRUSTED cards from "Product Docs"

```bash
python3 guru_exporter_smart.py
```

**Interactive Session:**
```
📋 SELECT COLLECTION TO EXPORT
  10. Product Docs

Enter number: 10

🔍 FILTER OPTIONS
  1. ALL cards
  2. TRUSTED cards only ← Select this
  3. NEEDS_VERIFICATION cards only

Select filter (1-3): 2

📊 Counting cards with filter: TRUSTED...
✓ Found 256 TRUSTED cards

📊 EXPORT LIMIT
  1. Export ALL cards ← Select this
  2. Export first 200 cards
  3. Export first 500 cards
  4. Custom limit

Select option (1-4): 1

💾 Downloading 256 card details...
  Progress: ████████████████████ 256/256 (100%)

✅ SUCCESS!
📦 File: guru_export_Product_Docs_trusted.zip
```

---

## Example 3: Test with Limited Cards

**Scenario:** Test export with first 20 cards

```bash
python3 guru_exporter_smart.py
```

**Session:**
```
Select collection: 12. Sales

Filter: 1. ALL cards

Limit cards? (press Enter for all, or enter number): 20

📊 Fetching cards...
  ✓ Fetched 20 cards total

Will export 20 cards
Continue? (y/n): y

💾 Downloading 20 card details...
  Progress: ████████████████████ 20/20 (100%)

✅ SUCCESS!
```

---

## Example 4: Compare Website vs API

**Scenario:** Understand why API returns 1000 cards when UI shows 170

```bash
python3 guru_unified.py
```

**Session:**
```
📥 GURU UNIFIED TOOL
  1. Analyze local Guru export
  2. Export using API
  3. Compare local export vs API
  4. Export using API (filtered to match local)

Select: 1
Enter path: ~/Downloads/guru_sales_export.zip

📊 LOCAL EXPORT SUMMARY
  Total cards: 170
  Cards by verification:
    • TRUSTED: 98
    • NEEDS_VERIFICATION: 72

Select: 2
Collection: 12. Sales
Limit: 500

Select: 3

🔬 COMPARISON: LOCAL vs API
  • Local export: 170 cards
  • API results:  500 cards
  • In both:      170 cards
  • Only in API:  330 cards

💡 DIAGNOSIS
Cards only in API have these characteristics:
  • 80% have 0 boards assigned
  • Mix of TRUSTED and NEEDS_VERIFICATION

Recommendation: Cards must be assigned to boards to appear in UI

Select: 4
Will export 170 cards (matching local export)

✅ SUCCESS!
📦 guru_export_Sales_filtered.zip
```

---

## Example 5: Multiple Collections

**Scenario:** Export 3 collections for migration

```bash
# Collection 1: Sales
python3 guru_enricher.py ~/Downloads/guru_sales.zip

# Collection 2: Product
python3 guru_enricher.py ~/Downloads/guru_product.zip

# Collection 3: Support
python3 guru_enricher.py ~/Downloads/guru_support.zip
```

**Result:** Three `*_notion_ready.zip` files

**Import to Notion:**
1. Import `guru_sales_notion_ready.zip`
2. Import `guru_product_notion_ready.zip`
3. Import `guru_support_notion_ready.zip`

All organize under one "Guru/" teamspace in Notion:
```
Guru/
├── Sales/
│   ├── Folder 1/
│   └── Cards...
├── Product/
│   ├── Folder 1/
│   └── Cards...
└── Support/
    ├── Folder 1/
    └── Cards...
```

---

## Example 6: Debugging Failed Cards

**Scenario:** 5 cards failed to fetch

```bash
python3 guru_enricher.py guru_export.zip
```

**Output:**
```
⚠️  5 cards failed to fetch
   - abc-123-def
   - xyz-789-ghi
   ...

📝 Check log: guru_export_logs/guru_export_20241105_143022.log
```

**Check the log:**
```bash
tail -50 guru_export_logs/guru_export_20241105_143022.log
```

**Log shows:**
```
ERROR - Failed: cards/abc-123-def - HTTP 404
ERROR - Failed: cards/xyz-789-ghi - Timeout
```

**Resolution:**
- 404 = Card deleted in Guru (expected)
- Timeout = Retry the export
- Other errors = Check API token

---

## Example 7: Large Collection Strategy

**Scenario:** Export collection with 2000 cards

**Strategy 1: Test first**
```bash
# Test with first 50 cards
python3 guru_exporter_smart.py
# Select collection, limit to 50
# Verify import to Notion works

# Then export all
python3 guru_exporter_smart.py
# Select collection, export ALL
```

**Strategy 2: Use website export**
```bash
# Export from Guru website (may take time)
# Then enrich with API
python3 guru_enricher.py guru_large_collection.zip

# Monitor progress
tail -f guru_export_logs/guru_export_*.log
```

**Time estimate:** ~15-20 minutes for 2000 cards

---

## Example 8: Custom Metadata

**Scenario:** Want to preserve custom fields

**Edit guru_enricher.py:**
```python
def create_card_metadata(self, card: Dict) -> Dict:
    # Add your custom fields
    metadata = {
        'Title': card.get('preferredPhrase', 'Untitled'),
        # ... existing fields ...
        
        # Add custom fields
        'CustomField1': card.get('customField1', ''),
        'CustomField2': card.get('customField2', ''),
    }
    return metadata
```

**Then export normally:**
```bash
python3 guru_enricher.py guru_export.zip
```

---

## Example 9: Schedule Regular Exports

**Scenario:** Weekly exports for backup

**Create a script `weekly_export.sh`:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)

# Export from Guru website first
# (manual step or use Guru's scheduled export feature)

# Then enrich
python3 guru_enricher.py ~/Downloads/guru_export.zip

# Move to archive
mv *_notion_ready.zip ~/guru_backups/backup_$DATE.zip

echo "Backup complete: backup_$DATE.zip"
```

**Schedule with cron:**
```bash
# Run every Sunday at 2 AM
0 2 * * 0 /path/to/weekly_export.sh
```

---

## Tips from Examples

1. **Always test small first** - Use 10-20 cards to verify process
2. **Check logs** - They show what's happening and why
3. **Use website export** - Most reliable for getting correct cards
4. **Monitor progress** - Progress bars show it's working
5. **Keep exports** - Save `*_enriched.zip` as backup before converting

---

Need more examples? Create an issue on GitHub!
