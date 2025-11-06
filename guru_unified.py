#!/usr/bin/env python3
"""
UNIFIED GURU ANALYZER & EXPORTER
Works with both local Guru exports and API

Features:
1. Analyze a local Guru export (from website)
2. Export using API (with filtering options)
3. Compare local export vs API to find filtering logic

Usage: python3 guru_unified.py
"""

import os
import sys
import time
import zipfile
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import yaml

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    class tqdm:
        def __init__(self, iterable=None, **kwargs):
            self.iterable = iterable
        def __iter__(self):
            return iter(self.iterable) if self.iterable else iter([])
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def update(self, n=1):
            pass

# ============================================================================
# CONFIGURATION
# ============================================================================
USER_EMAIL = "you@example.com"
USER_TOKEN = "403c0bd0-7649-4a4a-a970-71e6f33f5259"
# ============================================================================


class GuruUnified:
    def __init__(self, email: str, token: str):
        self.email = email
        self.token = token
        self.auth = HTTPBasicAuth(email, token)
        self.base_url = "https://api.getguru.com/api/v1"
        self.session = requests.Session()
        self.session.auth = self.auth
    
    def request(self, endpoint: str, method: str = "GET", **kwargs):
        """Make API request"""
        url = f"{self.base_url}/{endpoint}"
        try:
            if method == "GET":
                response = self.session.get(url, timeout=30, **kwargs)
            elif method == "POST":
                response = self.session.post(url, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None
    
    def analyze_local_export(self, zip_path: Path) -> Dict:
        """Analyze a local Guru export"""
        print(f"\n{'='*70}")
        print(f"🔍 ANALYZING LOCAL EXPORT")
        print(f"{'='*70}\n")
        
        print(f"📦 File: {zip_path}")
        
        if not zip_path.exists():
            print(f"❌ File not found: {zip_path}")
            return {}
        
        # Extract to temp directory
        temp_dir = Path("/tmp/guru_local_analysis")
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        print("📂 Extracting...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(temp_dir)
        except Exception as e:
            print(f"❌ Failed to extract: {e}")
            return {}
        
        # Analyze structure
        print("\n📊 Analyzing structure...\n")
        
        analysis = {
            'card_ids': set(),
            'card_count': 0,
            'cards_by_status': {},
            'cards_by_verification': {},
            'folder_count': 0,
            'has_metadata': False,
            'file_structure': []
        }
        
        # Walk through extracted files
        for root, dirs, files in os.walk(temp_dir):
            rel_path = Path(root).relative_to(temp_dir)
            for file in files:
                file_path = Path(root) / file
                rel_file = rel_path / file
                analysis['file_structure'].append(str(rel_file))
        
        print("📁 File structure:")
        for item in sorted(analysis['file_structure'][:20]):
            print(f"  • {item}")
        if len(analysis['file_structure']) > 20:
            print(f"  ... and {len(analysis['file_structure']) - 20} more files")
        
        # Check for common Guru export formats
        cards_dir = temp_dir / 'cards'
        folders_dir = temp_dir / 'folders'
        collection_file = temp_dir / 'collection.yaml'
        
        # Try to find card files
        if cards_dir.exists():
            print(f"\n✓ Found cards directory")
            card_files = list(cards_dir.glob("*.yaml"))
            analysis['card_count'] = len(card_files)
            
            print(f"  Reading {len(card_files)} card metadata files...")
            
            for card_file in card_files:
                try:
                    with open(card_file, 'r', encoding='utf-8') as f:
                        card_data = yaml.safe_load(f)
                    
                    if card_data:
                        card_id = card_data.get('ExternalId') or card_data.get('id')
                        if card_id:
                            analysis['card_ids'].add(card_id)
                        
                        # Track status
                        status = card_data.get('ShareStatus') or card_data.get('shareStatus', 'UNKNOWN')
                        analysis['cards_by_status'][status] = analysis['cards_by_status'].get(status, 0) + 1
                        
                        # Track verification
                        ver = card_data.get('VerificationState') or card_data.get('verificationState', 'UNKNOWN')
                        analysis['cards_by_verification'][ver] = analysis['cards_by_verification'].get(ver, 0) + 1
                        
                        analysis['has_metadata'] = True
                except:
                    pass
        
        # Check for folders
        if folders_dir.exists():
            folder_files = list(folders_dir.glob("*.yaml"))
            analysis['folder_count'] = len(folder_files)
            print(f"✓ Found {len(folder_files)} folders")
        
        # Check for collection metadata
        if collection_file.exists():
            try:
                with open(collection_file, 'r', encoding='utf-8') as f:
                    coll_data = yaml.safe_load(f)
                print(f"✓ Found collection metadata: {coll_data.get('Title', 'Unknown')}")
            except:
                pass
        
        # Summary
        print(f"\n{'='*70}")
        print("📊 LOCAL EXPORT SUMMARY")
        print(f"{'='*70}\n")
        
        print(f"  Total cards: {len(analysis['card_ids'])}")
        
        if analysis['cards_by_status']:
            print(f"\n  Cards by status:")
            for status, count in sorted(analysis['cards_by_status'].items()):
                print(f"    • {status}: {count}")
        
        if analysis['cards_by_verification']:
            print(f"\n  Cards by verification:")
            for ver, count in sorted(analysis['cards_by_verification'].items()):
                print(f"    • {ver}: {count}")
        
        print(f"\n  Folders: {analysis['folder_count']}")
        
        return analysis
    
    def get_api_cards(self, collection_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get cards from API"""
        print(f"\n{'='*70}")
        print(f"🔍 FETCHING FROM API")
        print(f"{'='*70}\n")
        
        all_cards = []
        skip = 0
        batch_size = 50
        
        print("📊 Fetching cards...")
        
        while True:
            if limit and len(all_cards) >= limit:
                all_cards = all_cards[:limit]
                break
            
            search_body = {
                "queryType": "cards",
                "collectionIds": [collection_id],
                "skip": skip,
                "limit": batch_size
            }
            
            cards = self.request("search/cardmgr", method="POST", json=search_body)
            
            if not cards or len(cards) == 0:
                break
            
            all_cards.extend(cards)
            print(f"  → Fetched {len(all_cards)} cards...", end="\r")
            
            if len(cards) < batch_size:
                break
            
            skip += batch_size
            time.sleep(0.2)
        
        print(f"  ✓ Fetched {len(all_cards)} cards total     ")
        
        return all_cards
    
    def compare_exports(self, local_analysis: Dict, api_cards: List[Dict]):
        """Compare local export vs API results"""
        print(f"\n{'='*70}")
        print(f"🔬 COMPARISON: LOCAL vs API")
        print(f"{'='*70}\n")
        
        local_ids = local_analysis.get('card_ids', set())
        api_ids = {card.get('id') for card in api_cards if card.get('id')}
        
        # Basic counts
        print(f"📊 Card counts:")
        print(f"  • Local export: {len(local_ids)} cards")
        print(f"  • API results:  {len(api_ids)} cards")
        print(f"  • Difference:   {abs(len(local_ids) - len(api_ids))} cards\n")
        
        # Set operations
        in_both = local_ids & api_ids
        only_local = local_ids - api_ids
        only_api = api_ids - local_ids
        
        print(f"📊 Set comparison:")
        print(f"  • In both:       {len(in_both)} cards")
        print(f"  • Only in local: {len(only_local)} cards")
        print(f"  • Only in API:   {len(only_api)} cards\n")
        
        if len(only_api) > 0:
            print(f"{'='*70}")
            print(f"🔍 ANALYZING CARDS ONLY IN API")
            print(f"{'='*70}\n")
            
            print(f"These {len(only_api)} cards are returned by API but NOT in local export.")
            print("This tells us what Guru's export filters OUT.\n")
            
            # Analyze the cards only in API
            api_only_cards = [c for c in api_cards if c.get('id') in only_api]
            
            # Group by status and verification
            by_status = {}
            by_verification = {}
            by_boards = {}
            
            for card in api_only_cards[:100]:  # Analyze first 100
                status = card.get('shareStatus', 'UNKNOWN')
                by_status[status] = by_status.get(status, 0) + 1
                
                ver = card.get('verificationState', 'UNKNOWN')
                by_verification[ver] = by_verification.get(ver, 0) + 1
                
                boards = len(card.get('boards', []))
                by_boards[boards] = by_boards.get(boards, 0) + 1
            
            print("  Characteristics of API-only cards (sample of 100):")
            print(f"\n  Status distribution:")
            for status, count in sorted(by_status.items()):
                pct = count / len(api_only_cards[:100]) * 100
                print(f"    • {status}: {count} ({pct:.1f}%)")
            
            print(f"\n  Verification distribution:")
            for ver, count in sorted(by_verification.items()):
                pct = count / len(api_only_cards[:100]) * 100
                print(f"    • {ver}: {count} ({pct:.1f}%)")
            
            print(f"\n  Board count distribution:")
            for boards, count in sorted(by_boards.items()):
                pct = count / len(api_only_cards[:100]) * 100
                print(f"    • {boards} board(s): {count} ({pct:.1f}%)")
            
            # Show sample cards
            print(f"\n  Sample API-only cards:")
            for card in api_only_cards[:5]:
                title = card.get('preferredPhrase', 'Untitled')[:50]
                status = card.get('shareStatus', 'UNKNOWN')
                ver = card.get('verificationState', 'UNKNOWN')
                boards = len(card.get('boards', []))
                print(f"    • '{title}'")
                print(f"      Status: {status} | Verification: {ver} | Boards: {boards}")
        
        if len(only_local) > 0:
            print(f"\n⚠️  Warning: {len(only_local)} cards in local export but not in API")
            print("    This is unusual - the API should return everything.")
        
        # Conclusion
        print(f"\n{'='*70}")
        print(f"💡 FILTERING RECOMMENDATION")
        print(f"{'='*70}\n")
        
        if len(only_api) > 0:
            print("To match Guru's website export, the API export should:")
            
            # Determine likely filter
            if len(local_ids) > 0:
                match_rate = len(in_both) / len(local_ids) * 100
                print(f"  ✓ Match rate: {match_rate:.1f}%")
                
                if match_rate > 95:
                    print("\n  The exports are already very similar!")
                    print("  Minor differences may be due to timing or permissions.")
                else:
                    print("\n  Suggested filters based on API-only cards:")
                    print("  • Check status, verification state, or board assignments")
                    print("  • The characteristics above show what to filter OUT")
        else:
            print("  ✅ Perfect match! Local export and API return the same cards.")
            print("  No additional filtering needed.")
        
        return {
            'local_count': len(local_ids),
            'api_count': len(api_ids),
            'in_both': len(in_both),
            'only_local': len(only_local),
            'only_api': len(only_api)
        }
    
    def export_with_filter(self, collection_id: str, collection_name: str, 
                          filter_ids: Optional[Set[str]] = None):
        """Export cards, optionally filtered to specific IDs"""
        print(f"\n{'='*70}")
        print(f"📦 EXPORTING: {collection_name}")
        print(f"{'='*70}\n")
        
        # Get all cards from API
        all_cards = self.get_api_cards(collection_id)
        
        # Filter if needed
        if filter_ids:
            all_cards = [c for c in all_cards if c.get('id') in filter_ids]
            print(f"\n  ✓ Filtered to {len(all_cards)} cards (matching local export)")
        
        if not all_cards:
            print("  ⚠️  No cards to export")
            return None
        
        # Confirm
        print(f"\n  Will export {len(all_cards)} cards")
        confirm = input("  Continue? (y/n): ").strip().lower()
        if confirm != 'y':
            print("  ❌ Export cancelled")
            return None
        
        # Get folders
        print("\n📁 Fetching folder structure...")
        folders = self.get_and_process_folders(collection_id, collection_name)
        
        # Create temp directory
        temp_dir = Path(f"/tmp/guru_export_{collection_id}")
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True)
        
        cards_dir = temp_dir / 'cards'
        folders_dir = temp_dir / 'folders'
        cards_dir.mkdir()
        folders_dir.mkdir()
        
        # Download cards
        print(f"\n💾 Downloading {len(all_cards)} card details...")
        
        with tqdm(all_cards, desc="  Progress", unit="card") as pbar:
            for card in pbar:
                card_id = card.get('id')
                if not card_id:
                    continue
                
                full_card = self.request(f"cards/{card_id}")
                if not full_card:
                    continue
                
                # Save metadata
                self.save_card(full_card, cards_dir)
                time.sleep(0.15)
        
        # Save folders
        self.save_folders(folders, folders_dir)
        
        # Save collection metadata
        self.save_collection(collection_name, collection_id, all_cards, folders, temp_dir)
        
        # Create zip
        print("\n📦 Creating zip file...")
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' 
                           for c in collection_name)
        safe_name = safe_name.replace(' ', '_')[:50]
        
        suffix = "_filtered" if filter_ids else ""
        zip_path = Path(f"guru_export_{safe_name}{suffix}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
        print(f"  ✓ Created {zip_path}")
        
        return zip_path
    
    def get_and_process_folders(self, collection_id: str, collection_name: str) -> Dict:
        """Get and process folder hierarchy"""
        # Get collection to find home board
        collections = self.request("collections")
        if not collections:
            return {}
        
        collection = next((c for c in collections if c.get('id') == collection_id), None)
        if not collection:
            return {}
        
        home_slug = collection.get('homeBoardSlug')
        if not home_slug:
            return {}
        
        folder_id = home_slug.split('/')[0] if '/' in home_slug else home_slug
        home_folder = self.request(f"folders/{folder_id}/items")
        
        if not home_folder:
            return {}
        
        top_folders = [item for item in home_folder if item.get('type') == 'folder']
        
        folders = {}
        
        def process_folder(folder_data):
            fid = folder_data.get('id') or folder_data.get('itemId')
            if not fid or fid in folders:
                return
            
            items = self.request(f"folders/{fid}/items")
            
            folder_info = {
                'id': fid,
                'title': folder_data.get('title', 'Untitled'),
                'cards': [],
                'subfolders': []
            }
            
            if items:
                for item in items:
                    item_type = item.get('type')
                    item_id = item.get('id') or item.get('itemId')
                    
                    if item_type == 'card' and item_id:
                        folder_info['cards'].append(item_id)
                    elif item_type == 'folder' and item_id:
                        folder_info['subfolders'].append(item_id)
                        process_folder(item)
            
            folders[fid] = folder_info
        
        for folder in top_folders:
            process_folder(folder)
        
        print(f"  ✓ Found {len(folders)} folders")
        return folders
    
    def save_card(self, card: Dict, cards_dir: Path):
        """Save card metadata and content"""
        card_id = card.get('id')
        title = card.get('preferredPhrase', 'Untitled')
        
        # Save YAML metadata
        card_yaml = {
            'Title': title,
            'OriginalTitle': title,
            'ExternalId': card_id,
            'ShareStatus': card.get('shareStatus', ''),
            'VerificationState': card.get('verificationState', 'UNKNOWN'),
            'VerificationInterval': card.get('verificationInterval', ''),
            'LastVerified': card.get('lastVerified', ''),
            'Tags': [tag.get('value', '') for tag in card.get('tags', [])],
            'DateCreated': card.get('dateCreated', ''),
            'LastModified': card.get('lastModified', ''),
        }
        
        yaml_file = cards_dir / f"{card_id}.yaml"
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(card_yaml, f, default_flow_style=False, allow_unicode=True)
        
        # Save HTML content
        html_file = cards_dir / f"{card_id}.html"
        with open(html_file, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(card.get('content', ''))
    
    def save_folders(self, folders: Dict, folders_dir: Path):
        """Save folder metadata"""
        for folder_id, folder_data in folders.items():
            items = []
            for subfolder_id in folder_data.get('subfolders', []):
                items.append({'ID': subfolder_id, 'Type': 'folder'})
            for card_id in folder_data.get('cards', []):
                items.append({'ID': card_id, 'Type': 'card'})
            
            folder_yaml = {
                'Title': folder_data['title'],
                'ExternalId': folder_id,
                'Items': items
            }
            
            yaml_file = folders_dir / f"{folder_id}.yaml"
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(folder_yaml, f, default_flow_style=False, allow_unicode=True)
    
    def save_collection(self, name: str, coll_id: str, cards: List[Dict], 
                       folders: Dict, temp_dir: Path):
        """Save collection metadata"""
        cards_in_folders = set()
        for folder_data in folders.values():
            cards_in_folders.update(folder_data.get('cards', []))
        
        items = []
        
        # Add top-level folders
        for folder_data in folders.values():
            is_subfolder = any(folder_data['id'] in f.get('subfolders', []) 
                             for f in folders.values())
            if not is_subfolder:
                items.append({'ID': folder_data['id'], 'Type': 'folder'})
        
        # Add cards not in folders
        for card in cards:
            card_id = card.get('id')
            if card_id and card_id not in cards_in_folders:
                items.append({'ID': card_id, 'Type': 'card'})
        
        collection_yaml = {
            'Title': name,
            'Description': '',
            'ExternalId': coll_id,
            'Items': items
        }
        
        coll_file = temp_dir / "collection.yaml"
        with open(coll_file, 'w', encoding='utf-8') as f:
            yaml.dump(collection_yaml, f, default_flow_style=False, allow_unicode=True)
    
    def main_menu(self):
        """Main menu"""
        print("\n" + "="*70)
        print("📥 GURU UNIFIED TOOL")
        print("="*70 + "\n")
        print("  1. Analyze local Guru export (from website)")
        print("  2. Export using API")
        print("  3. Compare local export vs API")
        print("  4. Export using API (filtered to match local)")
        print()
        print("  0. Exit")
        print("\n" + "="*70)
        
        while True:
            choice = input("\nSelect option (0-4): ").strip()
            if choice in ['0', '1', '2', '3', '4']:
                return choice
            print("❌ Enter 0, 1, 2, 3, or 4")
    
    def run(self):
        """Main loop"""
        print("\n" + "="*70)
        print("📥 Guru Unified Analyzer & Exporter")
        print("="*70 + "\n")
        
        print(f"User: {self.email}\n")
        
        local_analysis = None
        api_cards = None
        collection_id = None
        collection_name = None
        
        while True:
            choice = self.main_menu()
            
            if choice == '0':
                break
            
            elif choice == '1':
                # Analyze local export
                zip_path = input("\nEnter path to Guru export zip file: ").strip()
                zip_path = Path(zip_path)
                local_analysis = self.analyze_local_export(zip_path)
            
            elif choice == '2':
                # Export using API
                collections = self.request("collections")
                if not collections:
                    print("❌ Could not fetch collections")
                    continue
                
                collections.sort(key=lambda x: x.get('name', '').lower())
                
                print("\n" + "="*70)
                print("📋 SELECT COLLECTION")
                print("="*70 + "\n")
                
                for i, coll in enumerate(collections, 1):
                    print(f"  {i:2d}. {coll.get('name', 'Unknown')}")
                
                try:
                    idx = int(input("\nEnter number: ").strip()) - 1
                    if 0 <= idx < len(collections):
                        selected = collections[idx]
                        collection_id = selected.get('id')
                        collection_name = selected.get('name', 'Unknown')
                        
                        # Ask for limit
                        limit_input = input("\nLimit cards? (press Enter for all, or enter number): ").strip()
                        limit = int(limit_input) if limit_input else None
                        
                        api_cards = self.get_api_cards(collection_id, limit)
                        
                        # Ask to export
                        export = input("\nExport these cards? (y/n): ").strip().lower()
                        if export == 'y':
                            self.export_with_filter(collection_id, collection_name)
                except ValueError:
                    print("❌ Invalid number")
            
            elif choice == '3':
                # Compare
                if not local_analysis:
                    print("\n❌ Please analyze a local export first (option 1)")
                    continue
                
                if not collection_id:
                    print("\n❌ Please fetch API cards first (option 2)")
                    continue
                
                if not api_cards:
                    api_cards = self.get_api_cards(collection_id)
                
                self.compare_exports(local_analysis, api_cards)
            
            elif choice == '4':
                # Export with filter
                if not local_analysis:
                    print("\n❌ Please analyze a local export first (option 1)")
                    continue
                
                if not collection_id:
                    print("\n❌ Please fetch API cards first (option 2)")
                    continue
                
                filter_ids = local_analysis.get('card_ids')
                if filter_ids:
                    self.export_with_filter(collection_id, collection_name, filter_ids)
                else:
                    print("❌ No card IDs found in local export")
        
        print("\n✨ Done!\n")


def main():
    try:
        tool = GuruUnified(USER_EMAIL, USER_TOKEN)
        tool.run()
    except KeyboardInterrupt:
        print("\n\n👋 Bye!\n")


if __name__ == "__main__":
    main()
