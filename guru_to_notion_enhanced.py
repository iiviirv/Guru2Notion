#!/usr/bin/env python3
"""
ENHANCED: Guru to Notion Converter
With metadata tables, link previews, and Notion-optimized formatting

Usage: python3 guru_to_notion_enhanced.py <guru_export.zip>
"""

import os
import re
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Dict, Optional
import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from datetime import datetime


class EnhancedNotionConverter:
    def __init__(self, export_path: Path):
        self.export_path = export_path
        self.temp_dir = None
        self.output_dir = None
        self.folders = {}
        self.cards = {}
        self.processed = set()
    
    def sanitize(self, name: str) -> str:
        """Safe filename"""
        safe = re.sub(r'[<>:"/\\|?*]', '_', name)
        safe = re.sub(r'\s+', ' ', safe).strip()
        return safe[:200] if len(safe) > 200 else safe
    
    def load_yaml(self, path: Path) -> Optional[Dict]:
        """Load YAML file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except:
            return None
    
    def load_folders(self, folder_dir: Path) -> Dict:
        """Load folders"""
        folders = {}
        if not folder_dir.exists():
            return folders
        
        for yaml_file in folder_dir.glob("*.yaml"):
            if yaml_file.name.startswith('._'):
                continue
            data = self.load_yaml(yaml_file)
            if data and 'ExternalId' in data:
                folders[data['ExternalId']] = {
                    'title': data.get('Title', 'Untitled'),
                    'items': data.get('Items', []),
                    'id': data['ExternalId']
                }
        return folders
    
    def load_cards(self, card_dir: Path) -> Dict:
        """Load cards"""
        cards = {}
        if not card_dir.exists():
            return cards
        
        for yaml_file in card_dir.glob("*.yaml"):
            if yaml_file.name.startswith('._'):
                continue
            data = self.load_yaml(yaml_file)
            if data and 'ExternalId' in data:
                cards[data['ExternalId']] = {
                    'title': data.get('Title', 'Untitled'),
                    'original': data.get('OriginalTitle', data.get('Title', 'Untitled')),
                    'id': data['ExternalId']
                }
        return cards
    
    def format_date(self, date_str: str) -> str:
        """Format ISO date to readable format"""
        if not date_str:
            return "Never"
        try:
            dt = datetime.fromisoformat(date_str.replace('+0000', '+00:00').replace('Z', '+00:00'))
            return dt.strftime('%b %d, %Y at %I:%M %p UTC')
        except:
            return date_str
    
    def extract_and_enhance_links(self, markdown: str) -> str:
        """Extract links and convert to Notion bookmark format for previews"""
        # Find all markdown links [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        
        def replace_link(match):
            text = match.group(1)
            url = match.group(2)
            
            # Check if it's a URL that should have a preview
            if url.startswith('http://') or url.startswith('https://'):
                # For Google Docs, Sheets, etc., create a bookmark block
                if 'google.com' in url or 'docs.google' in url:
                    return f"\n\n[{text}]({url})\n\n💡 **Link Preview:** {url}\n\n"
                # For other URLs, keep as link but add preview hint
                elif any(domain in url for domain in ['notion.', 'confluence.', 'sharepoint.', 'dropbox.']):
                    return f"[{text}]({url}) 🔗"
                else:
                    return f"[{text}]({url})"
            return match.group(0)
        
        enhanced = re.sub(link_pattern, replace_link, markdown)
        
        # Also find standalone URLs and make them clickable
        url_pattern = r'(?<!\()(?<!\[)(https?://[^\s\)]+)(?!\))'
        enhanced = re.sub(url_pattern, r'<\1>', enhanced)
        
        return enhanced
    
    def html_to_md(self, html: str) -> str:
        """Convert HTML to Markdown with Notion enhancements"""
        if not html:
            return ""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Convert to markdown
        markdown = md(str(soup), heading_style="ATX")
        
        # Clean up excessive newlines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        # Enhance links for previews
        markdown = self.extract_and_enhance_links(markdown)
        
        return markdown.strip()
    
    def create_metadata_table(self, metadata: Dict) -> str:
        """Create a markdown table with metadata"""
        lines = []
        
        # Card Information Table
        lines.append("## 📊 Card Information\n")
        lines.append("| Property | Value |")
        lines.append("|----------|-------|")
        
        # Status
        verification = metadata.get('VerificationState', 'UNKNOWN')
        emoji = {'VERIFIED': '✅', 'NEEDS_VERIFICATION': '⚠️', 'UNVERIFIED': '❓', 'UNKNOWN': '❔'}.get(verification, '❔')
        lines.append(f"| **Status** | {emoji} {verification} |")
        
        # Verifiers
        verifiers = metadata.get('Verifiers', {})
        if verifiers:
            users = verifiers.get('Users', [])
            if users:
                lines.append(f"| **Verifier(s)** | {', '.join(users)} |")
        
        # Last Verified
        last_verified = metadata.get('LastVerified', '')
        if last_verified:
            formatted = self.format_date(last_verified)
            lines.append(f"| **Last Verified** | {formatted} |")
            
            last_ver_by = metadata.get('LastVerifiedBy', {})
            if last_ver_by and last_ver_by.get('Name'):
                lines.append(f"| **Verified By** | {last_ver_by['Name']} |")
        
        # Verification Interval
        interval = metadata.get('VerificationInterval', '')
        if interval:
            lines.append(f"| **Review Every** | {interval} days |")
        
        lines.append("")
        
        # Ownership & History Table
        lines.append("## 👥 Ownership & History\n")
        lines.append("| Property | Value |")
        lines.append("|----------|-------|")
        
        # Owner
        owner = metadata.get('Owner', {})
        if owner and owner.get('Name'):
            lines.append(f"| **Owner** | {owner['Name']} ({owner.get('Email', '')}) |")
        
        # Created
        created = metadata.get('DateCreated', '')
        if created:
            formatted = self.format_date(created)
            lines.append(f"| **Created** | {formatted} |")
        
        # Last Modified
        last_modified = metadata.get('LastModified', '')
        if last_modified:
            formatted = self.format_date(last_modified)
            lines.append(f"| **Last Modified** | {formatted} |")
            
            last_mod_by = metadata.get('LastModifiedBy', {})
            if last_mod_by and last_mod_by.get('Name'):
                lines.append(f"| **Modified By** | {last_mod_by['Name']} ({last_mod_by.get('Email', '')}) |")
        
        # Stats
        views = metadata.get('ViewCount', 0)
        version = metadata.get('Version', '')
        if views:
            lines.append(f"| **👁️ Views** | {views} |")
        if version:
            lines.append(f"| **Version** | {version} |")
        
        lines.append("")
        
        # Tags
        tags = metadata.get('Tags', [])
        if tags:
            lines.append("## 🏷️ Tags\n")
            lines.append(" • ".join(tags))
            lines.append("")
        
        return "\n".join(lines)
    
    def create_card(self, card_id: str, card_dir: Path, output: Path):
        """Create card page with enhanced formatting"""
        if card_id in self.processed:
            return
        
        card_info = self.cards.get(card_id)
        if not card_info:
            return
        
        title_emoji = card_info['title']
        title_plain = card_info['original']
        
        # Load full metadata from YAML
        yaml_file = card_dir / f"{card_id}.yaml"
        metadata = self.load_yaml(yaml_file) if yaml_file.exists() else {}
        
        html_file = card_dir / f"{card_id}.html"
        if not html_file.exists():
            return
        
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()
        
        # Convert with enhancements
        content_markdown = self.html_to_md(html)
        
        safe_title = self.sanitize(title_emoji)
        card_file = output / f"{safe_title}.md"
        
        # Build the page
        with open(card_file, 'w', encoding='utf-8') as f:
            # Title
            f.write(f"# {title_plain}\n\n")
            
            # Status banner
            verification = metadata.get('VerificationState', 'UNKNOWN')
            emoji = {'VERIFIED': '✅', 'NEEDS_VERIFICATION': '⚠️', 'UNVERIFIED': '❓', 'UNKNOWN': '❔'}.get(verification, '❔')
            
            if verification == 'VERIFIED':
                f.write(f"> ✅ **Verified** - This content is up to date and approved\n\n")
            elif verification == 'NEEDS_VERIFICATION':
                f.write(f"> ⚠️ **Needs Verification** - This content requires review\n\n")
            elif verification == 'UNVERIFIED':
                f.write(f"> ❓ **Unverified** - This content has not been verified\n\n")
            else:
                f.write(f"> ❔ **Status Unknown**\n\n")
            
            # Metadata tables
            metadata_section = self.create_metadata_table(metadata)
            f.write(metadata_section)
            
            # Divider
            f.write("\n---\n\n")
            
            # Content
            f.write("## 📄 Content\n\n")
            f.write(content_markdown)
        
        self.processed.add(card_id)
        print(f"  ✓ {safe_title}")
    
    def process_folder(self, folder_id: str, card_dir: Path, output: Path, level: int = 0):
        """Process folder recursively"""
        if folder_id in self.processed:
            return
        
        folder_info = self.folders.get(folder_id)
        if not folder_info:
            return
        
        title = folder_info['title']
        items = folder_info['items']
        
        indent = "  " * level
        print(f"{indent}📁 {title} ({len(items)} items)")
        
        safe_title = self.sanitize(title)
        folder_path = output / safe_title
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # Folder index with description
        index_file = folder_path / f"{safe_title}.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"This folder contains **{len(items)} items**.\n\n")
        
        self.processed.add(folder_id)
        
        for item in items:
            item_id = item.get('ID')
            item_type = item.get('Type')
            
            if not item_id or not item_type:
                continue
            
            if item_type == 'folder':
                self.process_folder(item_id, card_dir, folder_path, level + 1)
            elif item_type == 'card':
                self.create_card(item_id, card_dir, folder_path)
    
    def convert(self):
        """Main conversion"""
        print("\n" + "="*60)
        print("🔄 Enhanced Guru → Notion Converter")
        print("="*60 + "\n")
        
        # Extract
        self.temp_dir = Path("/tmp/guru_export")
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.temp_dir.mkdir()
        
        print("📦 Extracting...")
        with zipfile.ZipFile(self.export_path, 'r') as z:
            z.extractall(self.temp_dir)
        
        card_dir = self.temp_dir / 'cards'
        folder_dir = self.temp_dir / 'folders'
        coll_file = self.temp_dir / 'collection.yaml'
        
        if not card_dir.exists():
            print("❌ No cards found")
            return False
        
        # Load
        print("\n📚 Loading...")
        self.folders = self.load_folders(folder_dir)
        self.cards = self.load_cards(card_dir)
        
        print(f"  ✓ {len(self.folders)} folders")
        print(f"  ✓ {len(self.cards)} cards")
        
        coll_data = self.load_yaml(coll_file)
        if not coll_data:
            print("❌ No collection data")
            return False
        
        coll_name = coll_data.get('Title', 'Guru Export')
        
        # Create output with Guru teamspace structure
        # Output structure: Guru / {Collection Name} / content
        safe_name = self.sanitize(coll_name)
        
        # Create Guru parent folder
        guru_root = Path(f"/tmp/Guru")
        if not guru_root.exists():
            guru_root.mkdir(parents=True)
        
        # Create collection folder under Guru
        collection_folder = guru_root / safe_name
        if collection_folder.exists():
            shutil.rmtree(collection_folder)
        collection_folder.mkdir(parents=True)
        
        self.output_dir = guru_root
        root = collection_folder
        
        # Create Guru teamspace index (if it doesn't exist)
        guru_index = guru_root / "Guru.md"
        if not guru_index.exists():
            with open(guru_index, 'w', encoding='utf-8') as f:
                f.write("# 📚 Guru Knowledge Base\n\n")
                f.write("Welcome to the Guru knowledge base imported to Notion!\n\n")
                f.write("## Collections\n\n")
                f.write("Each collection from Guru is organized as a separate section below.\n\n")
        
        # Collection index
        index = root / f"{safe_name}.md"
        with open(index, 'w', encoding='utf-8') as f:
            f.write(f"# {coll_name}\n\n")
            f.write(f"{coll_data.get('Description', '')}\n\n")
            f.write(f"📊 **{len(self.cards)} cards** • 📁 **{len(self.folders)} folders**\n")
        
        print("\n🔨 Converting...\n")
        
        # Process items
        items = coll_data.get('Items', [])
        for item in items:
            item_id = item.get('ID')
            item_type = item.get('Type')
            
            if not item_id or not item_type:
                continue
            
            if item_type == 'folder':
                self.process_folder(item_id, card_dir, root)
            elif item_type == 'card':
                self.create_card(item_id, card_dir, root)
        
        # Resources
        res_dir = self.temp_dir / 'resources'
        if res_dir.exists() and any(res_dir.iterdir()):
            print("\n📎 Copying resources...")
            shutil.copytree(res_dir, root / 'resources')
        
        # Create zip
        output_zip = self.export_path.parent / f"{self.export_path.stem}_notion_ready.zip"
        print(f"\n📦 Creating {output_zip.name}")
        
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root_dir, dirs, files in os.walk(self.output_dir):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if file.startswith('.'):
                        continue
                    file_path = Path(root_dir) / file
                    # Archive path starts with "Guru/"
                    arcname = file_path.relative_to(self.output_dir.parent)
                    zipf.write(file_path, arcname)
        
        print(f"\n✅ Done!")
        print(f"📁 {output_zip}")
        print(f"\n💡 Structure in Notion:")
        print(f"   Guru/")
        print(f"   └── {coll_name}/")
        print(f"       ├── Folders...")
        print(f"       └── Cards...")
        print(f"\n💡 Import to Notion:")
        print(f"   Settings → Import → Markdown & CSV")
        print(f"\n✨ All collections will be organized under 'Guru' teamspace!")
        
        # Cleanup
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        
        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 guru_to_notion_enhanced.py <export.zip>")
        sys.exit(1)
    
    export_path = Path(sys.argv[1])
    
    if not export_path.exists():
        print(f"❌ Not found: {export_path}")
        sys.exit(1)
    
    if not export_path.suffix.lower() == '.zip':
        print("❌ Need .zip file")
        sys.exit(1)
    
    converter = EnhancedNotionConverter(export_path)
    success = converter.convert()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
