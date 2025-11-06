# Frequently Asked Questions

## General Questions

### Q: Why use Guru2Notion instead of manual export?

**A:** Guru2Notion provides:
- Complete metadata preservation (verifiers, timestamps, tags)
- Automated conversion to Notion format
- Folder structure maintenance
- Batch processing capabilities
- Error handling and retry logic

Manual export/import loses metadata and requires manual reorganization.

---

### Q: Which script should I use?

**A:** Use `guru_enricher.py` for most cases:
- Reliable and fast
- Uses Guru's own filtering
- No API card count issues
- Recommended for first-time users

Use `guru_exporter_smart.py` if you:
- Don't have access to Guru website export
- Want to filter by verification state
- Need to test with limited cards

---

### Q: How long does export take?

**A:** Typical speeds:
- Small collections (10-50 cards): 1-2 minutes
- Medium collections (100-200 cards): 3-5 minutes
- Large collections (500-1000 cards): 10-20 minutes

Speed: ~2-4 cards per second (API rate limited)

---

## Technical Questions

### Q: Why does API return more cards than the Guru UI shows?

**A:** The Guru API returns ALL cards including:
- Cards not assigned to boards/folders
- Archived or draft cards
- Cards from different views
- Historical versions

The Guru website export applies its own filtering. That's why we recommend using `guru_enricher.py` with a website export.

---

### Q: What if some cards fail to fetch?

**A:** The script:
- Continues processing other cards
- Logs failed card IDs
- Shows count of failed cards
- You get all successfully fetched cards

Check the log file to see why specific cards failed (usually 404 = deleted, timeout = network issue).

---

### Q: Can I export multiple collections at once?

**A:** Not currently in one command, but you can:
1. Export each collection from Guru website
2. Run `guru_enricher.py` on each export
3. Import each `*_notion_ready.zip` to Notion

All will organize under "Guru/" teamspace in Notion.

---

### Q: What metadata is preserved?

**A:** Full metadata including:
- Title and content
- Verification state and history
- Tags and boards
- Owner and verifiers
- Creation/modification dates
- View counts
- Version numbers
- Folder assignments

---

## Troubleshooting

### Q: "No card IDs found in export"

**A:** Ensure you're using a Guru **website export** (not an API export). The export should contain a `cards/` directory with `.yaml` files.

---

### Q: "API token invalid"

**A:** 
1. Check token hasn't expired
2. Verify no extra spaces when copying
3. Generate a new token in Guru Settings → API
4. Update the script with new token

---

### Q: Export seems stuck

**A:** 
1. Check the log file: `guru_export_logs/guru_export_*.log`
2. Large collections take time (~2-4 cards/sec)
3. Progress bar shows activity
4. Look for ERROR messages in logs

The script shows progress - if numbers are changing, it's working!

---

### Q: Wrong number of cards exported

**A:** Two scenarios:

**Too many cards (API returning extras):**
- Solution: Use `guru_enricher.py` with website export
- This uses Guru's filtering, not ours

**Too few cards:**
- Check for API errors in log file
- Verify API token permissions
- Some cards may be deleted or inaccessible

---

## Notion Import Questions

### Q: How do I import to Notion?

**A:**
1. Open Notion
2. Go to **Settings & Members** → **Import**
3. Select **"Markdown & CSV"**
4. Upload your `*_notion_ready.zip` file
5. Wait for Notion to process
6. Find imported content under "Guru/" page

---

### Q: Folder structure not preserved?

**A:** Check that:
- You imported the `*_notion_ready.zip` (not `*_enriched.zip`)
- You selected "Markdown & CSV" import (not plain text)
- Notion finished processing (can take a few minutes)

---

### Q: Links don't work in Notion?

**A:** 
- External links should work as clickable links
- Internal Guru card links won't work (those are Guru-specific)
- Google Docs links show with preview hint
- Check that URLs in original cards were valid

---

### Q: Can I customize the Notion output?

**A:** Yes! Edit `guru_to_notion_enhanced.py`:
- Modify metadata tables (line ~138)
- Change status banners (line ~256)
- Adjust link preview format (line ~91)
- Customize headers and formatting

---

## Best Practices

### Q: Should I test with a small collection first?

**A:** **Yes, absolutely!**
1. Choose a test collection with ~10-20 cards
2. Run the full export process
3. Import to Notion and verify
4. Then export your larger collections

This helps you:
- Verify credentials work
- Check output format
- Understand the process
- Catch any issues early

---

### Q: How often can I export?

**A:** As often as needed! But note:
- Guru API has rate limits
- Scripts include delays to respect limits
- For frequent syncs, consider spacing exports

---

### Q: Can I export to other platforms besides Notion?

**A:** The enriched export (before Notion conversion) is a standard format:
- YAML metadata files
- HTML content files
- Folder structure

You could write converters for:
- Confluence
- Google Docs
- Other markdown systems
- Custom wikis

The `guru_to_notion_enhanced.py` is a reference implementation.

---

## Need More Help?

- Check the [README.md](../README.md) for basic usage
- See [SETUP.md](../SETUP.md) for installation help
- Review [API.md](API.md) for technical details
- Create a GitHub issue for bugs or questions

---

**Didn't find your question?** Create an issue on GitHub!
