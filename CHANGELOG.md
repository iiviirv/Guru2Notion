# Changelog

All notable changes to Guru2Notion will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-06

### Added
- Initial release of Guru2Notion
- `guru_enricher.py` - Main tool for enriching Guru website exports
- `guru_exporter_smart.py` - Direct API export with filtering options
- `guru_to_notion_enhanced.py` - Guru to Notion converter
- `guru_unified.py` - Analysis and comparison tool
- Diagnostic tools for troubleshooting
- Comprehensive documentation
- Progress tracking with tqdm
- Automatic retry logic for API calls
- Detailed logging system
- Metadata preservation (verification, tags, ownership, timestamps)
- Folder structure preservation
- Notion-optimized markdown conversion
- Status banners and metadata tables in Notion
- Link preview enhancement
- MIT License

### Features
- ✅ Export from Guru website with API enrichment
- ✅ Direct API export with filtering
- ✅ Verification state filtering (TRUSTED/NEEDS_VERIFICATION/ALL)
- ✅ Export size limiting (test with small samples)
- ✅ Real-time progress tracking
- ✅ Comprehensive error handling
- ✅ Folder hierarchy preservation
- ✅ Full metadata preservation
- ✅ Notion-ready output format
- ✅ Detailed logging
- ✅ Interactive menus
- ✅ Automatic Notion conversion

### Documentation
- README.md with quick start guide
- SETUP.md with detailed installation instructions
- CONTRIBUTING.md with contribution guidelines
- docs/API.md with technical reference
- docs/FAQ.md with common questions
- docs/EXAMPLES.md with real-world usage
- docs/STRUCTURE.md with project organization

## [Unreleased]

### Planned Features
- [ ] Batch processing for multiple collections
- [ ] Direct Notion API integration
- [ ] Image and attachment handling improvements
- [ ] Code block preservation
- [ ] Export scheduling
- [ ] Configuration file support
- [ ] Progress persistence (resume interrupted exports)
- [ ] Incremental exports (only new/modified cards)
- [ ] Export templates
- [ ] Custom field mapping

---

## Version History

### Version Numbering

We use semantic versioning:
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards compatible manner
- **PATCH** version for backwards compatible bug fixes

### How to Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to Guru2Notion.

### Support

For issues, questions, or feature requests, please create an issue on GitHub.

---

*This changelog format is inspired by [Keep a Changelog](https://keepachangelog.com/).*
