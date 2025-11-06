# Setup Guide

Complete step-by-step setup instructions for Guru2Notion.

## Prerequisites

### 1. Python Installation

**Check if Python is installed:**
```bash
python3 --version
```

You need Python 3.6 or higher.

**Install Python (if needed):**

- **macOS:** 
  ```bash
  brew install python3
  ```

- **Ubuntu/Debian:**
  ```bash
  sudo apt update
  sudo apt install python3 python3-pip
  ```

- **Windows:** 
  Download from [python.org](https://www.python.org/downloads/)

### 2. Guru API Access

**Get your API credentials:**

1. Log into Guru
2. Go to **Settings** → **API**
3. Click **"Generate New Token"**
4. Copy your token (you'll need this!)
5. Note your Guru email address

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/Guru2Notion.git
cd Guru2Notion
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install with system packages flag (if needed):
```bash
pip install -r requirements.txt --break-system-packages
```

**Verify installation:**
```bash
python3 -c "import requests, yaml, bs4, markdownify, tqdm; print('✅ All dependencies installed')"
```

### Step 3: Configure Credentials

**Option A: Edit the script directly (easiest)**

Edit `guru_enricher.py`:
```python
# Find these lines near the top:
USER_EMAIL = "you@example.com"  # ← Replace with YOUR email
USER_TOKEN = "your-token-here"            # ← Replace with YOUR token
```

**Option B: Use environment variables (more secure)**

Create a `.env` file:
```bash
echo "GURU_EMAIL=your.email@company.com" > .env
echo "GURU_TOKEN=your-api-token" >> .env
```

Then modify the script to read from environment:
```python
import os
USER_EMAIL = os.getenv('GURU_EMAIL', 'default@example.com')
USER_TOKEN = os.getenv('GURU_TOKEN', 'your-token-here')
```

## Testing

### Quick Test

Test with a small collection first:

1. **Export a small collection from Guru:**
   - Choose a collection with ~10-20 cards
   - Settings → Export → Download

2. **Run the enricher:**
   ```bash
   python3 guru_enricher.py ~/Downloads/guru_test_export.zip
   ```

3. **Verify output:**
   - Check for `*_enriched.zip` and `*_notion_ready.zip`
   - Verify card count matches
   - Check log file for any errors

### Test Import to Notion

1. Open Notion
2. Settings & Members → Import
3. Select "Markdown & CSV"
4. Upload your `*_notion_ready.zip`
5. Verify:
   - Folder structure is preserved
   - Card content displays correctly
   - Metadata tables show up
   - Links work

## Troubleshooting

### "pip: command not found"
```bash
# Try pip3 instead:
pip3 install -r requirements.txt

# Or use python -m pip:
python3 -m pip install -r requirements.txt
```

### "Permission denied"
```bash
# Use --user flag:
pip install -r requirements.txt --user
```

### "Module not found" errors
```bash
# Reinstall dependencies:
pip install -r requirements.txt --force-reinstall
```

### "Invalid API token"
- Verify token hasn't expired
- Check for extra spaces when copying
- Generate a new token if needed

### Test Your Setup

Run this diagnostic:
```bash
python3 -c "
import requests
import yaml
import bs4
import markdownify
try:
    import tqdm
    print('✅ All required packages installed')
except:
    print('⚠️  tqdm missing (optional - for progress bars)')
    print('   Install with: pip install tqdm')
"
```

## Next Steps

Once setup is complete:
1. Read the [README.md](README.md) for usage instructions
2. Try the [Quick Start](README.md#quick-start) guide
3. Export your first collection!

## Getting Help

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section above
2. Look at existing [GitHub Issues](https://github.com/yourusername/Guru2Notion/issues)
3. Create a new issue with:
   - Error messages
   - Steps to reproduce
   - Your Python version
   - Operating system

Happy exporting! 🚀
