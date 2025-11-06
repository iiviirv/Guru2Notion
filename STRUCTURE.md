# Project Structure

```
Guru2Notion/
│
├── README.md                          # Main documentation
├── LICENSE                            # MIT License
├── SETUP.md                           # Installation guide
├── CONTRIBUTING.md                    # Contribution guidelines
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
│
├── guru_enricher.py                   # ⭐ Main tool (recommended)
├── guru_exporter_smart.py             # Direct API export with filters
├── guru_to_notion_enhanced.py         # Guru → Notion converter
├── guru_unified.py                    # Analysis & comparison tool
│
├── docs/                              # Documentation
│   ├── API.md                         # API reference
│   ├── FAQ.md                         # Frequently asked questions
│   └── EXAMPLES.md                    # Usage examples
│
└── tools/                             # Diagnostic tools
    ├── guru_diagnostic_quick.py       # Quick API analysis
    └── guru_diagnostic_deep.py        # Deep metadata analysis
```

## File Descriptions

### Root Files

**README.md**
- Main project documentation
- Quick start guide
- Feature overview
- Basic usage instructions

**LICENSE**
- MIT License
- Open source, free to use and modify

**SETUP.md**
- Detailed installation instructions
- Python setup
- Dependency installation
- Credentials configuration
- Troubleshooting

**CONTRIBUTING.md**
- How to contribute
- Code style guidelines
- Commit message format
- Pull request process

**requirements.txt**
- Python package dependencies
- requests, pyyaml, beautifulsoup4, markdownify, tqdm

**.gitignore**
- Prevents committing sensitive data
- Ignores logs, credentials, exports

### Main Scripts

**guru_enricher.py** ⭐
- Primary export tool
- Takes Guru website export
- Enriches with API data
- Converts to Notion format
- **Use this one first!**

**guru_exporter_smart.py**
- Direct API export
- Filtering options (TRUSTED/ALL/etc.)
- Limiting options (200/500/custom)
- Real-time progress tracking
- Interactive menus

**guru_to_notion_enhanced.py**
- Conversion engine
- HTML → Notion markdown
- Metadata table generation
- Link preview enhancement
- Folder structure preservation
- Called automatically by guru_enricher.py

**guru_unified.py**
- Advanced analysis tool
- Compare website vs API exports
- Identify filtering logic
- Export with precise filters
- For debugging and understanding

### Documentation

**docs/API.md**
- Detailed API reference
- Function documentation
- Class descriptions
- Usage patterns

**docs/FAQ.md**
- Common questions
- Troubleshooting guide
- Best practices
- Tips and tricks

**docs/EXAMPLES.md**
- Real-world usage examples
- Step-by-step scenarios
- Common workflows
- Advanced techniques

### Tools

**tools/guru_diagnostic_quick.py**
- Quick card analysis
- Samples first 200 cards
- Shows distributions
- ~30 second runtime

**tools/guru_diagnostic_deep.py**
- Comprehensive analysis
- All card fields
- Detailed breakdowns
- Sample cards
- ~1-2 minute runtime

## Generated Files

When you run the tools, they create:

```
guru_export_logs/                      # Log files
├── guru_export_20241105_143022.log    # Timestamped logs
└── guru_export_20241105_150433.log

guru_export_Sales.zip                  # API export (if using smart exporter)
guru_export_Sales_enriched.zip         # Enriched export
guru_export_Sales_notion_ready.zip     # Ready for Notion import ⭐
```

## Workflow Diagrams

### Recommended Workflow (guru_enricher.py)

```
Guru Website          Python Script              Notion
    │                      │                        │
    │  1. Export          │                        │
    │─────────────────────>│                        │
    │  (170 cards)         │                        │
    │                      │ 2. Extract IDs         │
    │                      │                        │
    │                      │ 3. Fetch from API      │
Guru API<─────────────────│                        │
    │                      │ (170 calls)            │
    │─────────────────────>│                        │
    │  (full metadata)     │                        │
    │                      │ 4. Convert to Notion   │
    │                      │                        │
    │                      │ 5. Create zip          │
    │                      │─────────────────────────>
    │                      │  (*_notion_ready.zip)  │
    │                      │                        │
```

### Direct API Workflow (guru_exporter_smart.py)

```
Guru API             Python Script              Notion
    │                      │                        │
    │  1. Fetch cards      │                        │
    │<─────────────────────│                        │
    │  (with filters)      │                        │
    │─────────────────────>│                        │
    │                      │ 2. Get details         │
    │<─────────────────────│                        │
    │─────────────────────>│                        │
    │                      │ 3. Convert to Notion   │
    │                      │                        │
    │                      │ 4. Create zip          │
    │                      │─────────────────────────>
    │                      │  (*_notion_ready.zip)  │
```

## Data Flow

### Card Enrichment Process

```
1. Input: guru_website_export.zip
   │
   ├── cards/
   │   ├── card-id-1.yaml      (basic metadata)
   │   ├── card-id-1.html      (content)
   │   └── ...
   │
   ├── folders/
   │   └── folder-id-1.yaml
   │
   └── collection.yaml

2. Extract Card IDs
   │
   └── Set of card IDs: {id-1, id-2, ...}

3. API Enrichment (for each ID)
   │
   ├── GET /api/v1/cards/{id}
   │
   └── Full metadata:
       ├── Verification details
       ├── Verifier info
       ├── Timestamps
       ├── Tags
       ├── View counts
       └── Complete content

4. Output: guru_export_enriched.zip
   │
   ├── cards/
   │   ├── card-id-1.yaml      (FULL metadata)
   │   ├── card-id-1.html      (content)
   │   └── ...
   │
   ├── folders/
   │   └── folder-id-1.yaml
   │
   └── collection.yaml

5. Notion Conversion
   │
   ├── HTML → Markdown
   ├── Metadata tables
   ├── Status banners
   └── Link enhancement

6. Output: guru_export_notion_ready.zip
   │
   └── Guru/
       └── Collection Name/
           ├── Collection.md
           ├── Folder 1/
           │   ├── Folder 1.md
           │   ├── Card 1.md
           │   └── Card 2.md
           └── Folder 2/
               └── ...
```

## Dependencies

```
requests (≥2.31.0)
├── HTTP client for Guru API
└── Handles authentication and retries

pyyaml (≥6.0)
├── YAML parsing and generation
└── Card/folder metadata

beautifulsoup4 (≥4.12.0)
├── HTML parsing
└── Content extraction

markdownify (≥0.11.6)
├── HTML to Markdown conversion
└── Notion formatting

tqdm (≥4.66.0)
├── Progress bars
└── Optional (graceful fallback)
```

## Size Estimates

- **Scripts:** ~150 KB total
- **Dependencies:** ~5 MB
- **Logs:** ~10 KB per export
- **Exports:** Varies by collection
  - Small (10 cards): ~100 KB
  - Medium (100 cards): ~1 MB
  - Large (1000 cards): ~10 MB

## Performance

- **API Rate:** ~2-4 cards/second
- **Small export (50 cards):** 1-2 minutes
- **Medium export (200 cards):** 3-5 minutes
- **Large export (1000 cards):** 10-20 minutes

## Support

See individual documentation files for detailed help:
- Installation issues → SETUP.md
- Usage questions → README.md  
- Troubleshooting → docs/FAQ.md
- Examples → docs/EXAMPLES.md
- Technical details → docs/API.md
