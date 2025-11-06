# Guru2Notion 🧠 → 📝

Export your Guru knowledge base and import it seamlessly into Notion with full metadata, folder structure, and formatting preserved.

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🎯 **Smart Export**: Works with Guru website exports to get exactly the cards you want
- 💎 **API Enrichment**: Automatically enriches cards with complete metadata from Guru API
- 📊 **Full Metadata**: Preserves verification status, tags, ownership, timestamps, and more
- 📁 **Folder Structure**: Maintains your complete folder hierarchy
- 🔄 **Notion-Ready**: Converts to Notion's markdown format with enhanced formatting
- ⚡ **Progress Tracking**: Real-time progress bars and detailed logging
- 🛡️ **Error Handling**: Robust retry logic and graceful failure handling

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- Guru account with API access
- Guru collection exported from website

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/Guru2Notion.git
cd Guru2Notion
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your credentials:
```bash
# Edit guru_enricher.py and add your Guru API credentials:
USER_EMAIL = "your.email@company.com"
USER_TOKEN = "your-guru-api-token"
```

### Usage

**Step 1: Export from Guru Website**
1. Go to your Guru dashboard
2. Navigate to the collection you want to export
3. Click Settings → Export
4. Download the `.zip` file

**Step 2: Enrich and Convert**
```bash
python3 guru_enricher.py ~/Downloads/guru_export.zip
```

The script will:
- Extract card IDs from your export
- Fetch complete details from API
- Convert to Notion format
- Create `*_notion_ready.zip`

**Step 3: Import to Notion**
1. Open Notion
2. Go to Settings & Members → Import
3. Select "Markdown & CSV"
4. Upload your `*_notion_ready.zip` file
5. Done! ✨

## 📖 Documentation

### Main Scripts

#### 1. `guru_enricher.py` - **Recommended**
The simplest and most reliable approach. Takes a Guru website export and enriches it with API data.

```bash
python3 guru_enricher.py <guru_website_export.zip>
```

**Why use this?**
- Uses Guru's own filtering logic
- Only fetches cards you actually want
- Fast (only processes exported cards)
- No API card count issues

#### 2. `guru_exporter_smart.py` - API Direct Export
Export directly from API with filtering options.

```bash
python3 guru_exporter_smart.py
```

**Features:**
- Filter by verification state (TRUSTED, NEEDS_VERIFICATION, ALL)
- Limit export size (first 200, 500, or custom)
- Real-time progress tracking
- Interactive menu

#### 3. `guru_to_notion_enhanced.py` - Converter
Converts Guru exports to Notion format (automatically called by enricher).

```bash
python3 guru_to_notion_enhanced.py <guru_export.zip>
```

**What it does:**
- Converts HTML to Notion markdown
- Creates metadata tables
- Enhances link previews
- Organizes in folder structure

### Advanced Tools

#### `guru_unified.py` - Analysis & Comparison
Compare Guru website exports with API results to understand filtering.

```bash
python3 guru_unified.py
```

**Use cases:**
- Analyze what's in a website export
- Compare website vs API results
- Identify Guru's filtering logic
- Export with precise filtering

#### Diagnostic Tools
- `guru_diagnostic_quick.py` - Quick analysis of API results
- `guru_diagnostic_deep.py` - Deep dive into card metadata
- Useful for troubleshooting and understanding data

## 📊 What Gets Exported

### Card Metadata
- ✅ Title and content (HTML → Markdown)
- ✅ Verification state and history
- ✅ Tags and boards
- ✅ Owner and verifiers
- ✅ Creation and modification dates
- ✅ View counts and version numbers
- ✅ Links and attachments

### Structure
- ✅ Folder hierarchy
- ✅ Card organization
- ✅ Collection metadata

### Notion Features
- ✅ Status banners (Verified, Needs Review, etc.)
- ✅ Metadata tables
- ✅ Link previews for Google Docs, etc.
- ✅ Proper heading structure
- ✅ Team space organization

## 🔧 Configuration

### Guru API Setup

1. **Get your API token:**
   - Go to Guru → Settings → API
   - Click "Generate New Token"
   - Copy the token

2. **Find your email:**
   - The email address you use to log into Guru

3. **Update the scripts:**
   ```python
   USER_EMAIL = "your.email@company.com"
   USER_TOKEN = "your-api-token-here"
   ```

### Advanced Options

#### guru_enricher.py
- Automatically uses card IDs from website export
- No configuration needed beyond API credentials

#### guru_exporter_smart.py
- `WARN_THRESHOLD`: Warning for large exports (default: 500)
- Configurable through interactive prompts

## 🐛 Troubleshooting

### "No card IDs found in export"
- Ensure you're using a Guru website export (not API export)
- Check that the zip file isn't corrupted
- Verify the export contains `cards/` directory

### "API errors" or timeouts
- Check your API token is valid
- Verify your internet connection
- The script will retry automatically (up to 3 times)

### "Wrong number of cards"
If API returns more cards than expected:
1. Use `guru_enricher.py` with website export (recommended)
2. Or use `guru_exporter_smart.py` with filtering options

### Progress seems stuck
- Check the log file: `guru_export_logs/guru_export_TIMESTAMP.log`
- Large collections take time (~2-4 cards per second)
- The script will show progress updates

## 📝 Examples

### Example 1: Simple Export
```bash
# Export Sales collection from Guru website
# Then enrich and convert:
python3 guru_enricher.py ~/Downloads/guru_sales_export.zip

# Output: guru_sales_export_enriched_notion_ready.zip
# Import to Notion!
```

### Example 2: Export with Filtering
```bash
# Use smart exporter with filters
python3 guru_exporter_smart.py

# Select collection: 12. Sales
# Filter: 2. TRUSTED cards only
# Limit: 1. Export ALL cards
# Output: Ready for Notion import
```

### Example 3: Analyze Before Export
```bash
# Compare website export vs API
python3 guru_unified.py

# Option 1: Analyze local export
# Option 2: Fetch from API
# Option 3: Compare both
# Option 4: Export with perfect filtering
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
```bash
git clone https://github.com/yourusername/Guru2Notion.git
cd Guru2Notion
pip install -r requirements.txt
```

### Running Tests
```bash
# Test with a small collection first
python3 guru_enricher.py test_export.zip
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for teams migrating from Guru to Notion
- Inspired by the need for better knowledge base portability
- Thanks to the Guru API for making this possible

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/Guru2Notion/issues)
- **Questions**: Create a discussion in the repository

## 🗺️ Roadmap

- [ ] Batch processing for multiple collections
- [ ] Direct Notion API integration (skip zip import)
- [ ] More metadata preservation options
- [ ] Better handling of attachments and images
- [ ] Support for Guru cards with code blocks
- [ ] Export scheduling and automation

## ⭐ Star History

If you find this useful, please consider giving it a star! ⭐

---

Made with ❤️ for knowledge workers everywhere
