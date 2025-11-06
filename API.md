# API & Script Reference

Detailed documentation for all Guru2Notion scripts and functions.

## Main Scripts

### guru_enricher.py ⭐ **Recommended**

The primary tool for most users. Takes a Guru website export and enriches it with API data.

**Usage:**
```bash
python3 guru_enricher.py <guru_website_export.zip>
```

**What it does:**
1. Extracts card IDs from Guru website export
2. Fetches complete details for each card from API
3. Preserves folder structure and collection metadata
4. Creates enriched export with full metadata
5. Optionally converts to Notion format

**Output:**
- `{filename}_enriched.zip` - Enriched Guru export
- `{filename}_enriched_notion_ready.zip` - Ready for Notion import

**Best for:**
- Getting exact cards from Guru UI
- Avoiding API card count discrepancies
- Fast, reliable exports

---

### guru_exporter_smart.py

Direct export from Guru API with filtering and limiting options.

**Interactive Options:**
1. Filter by verification state (ALL/TRUSTED/NEEDS_VERIFICATION)
2. Limit export size (200/500/custom/all)
3. Real-time progress tracking

**Best for:**
- Direct API access
- Testing with limited card counts
- Filtering by verification state

---

### guru_to_notion_enhanced.py

Converts Guru exports to Notion-optimized format.

**Features:**
- HTML to Notion markdown conversion
- Metadata tables
- Link preview enhancement
- Folder hierarchy preservation

---

## Workflow Recommendations

### Scenario 1: Standard Export (Recommended)
```bash
# 1. Export from Guru website
# 2. Enrich with API
python3 guru_enricher.py guru_export.zip
# 3. Import *_notion_ready.zip to Notion
```

### Scenario 2: API Direct Export
```bash
python3 guru_exporter_smart.py
# Select collection, filter, and limit
# Import resulting *_notion_ready.zip to Notion
```

### Scenario 3: Analysis & Comparison
```bash
python3 guru_unified.py
# Compare website export vs API
# Export with precise filtering
```

---

For complete API details, see the docstrings in each script.
