#!/usr/bin/env python3
"""
SMART EXPORTER: Guru Exporter with Filtering and Limits
Gives you control over what to export

Features:
- Preview card count before export
- Filter by verification state (TRUSTED, NEEDS_VERIFICATION, or ALL)
- Limit number of cards to export
- Shows progress in real-time

Usage: python3 guru_exporter_smart.py
"""

import os
import sys
import time
import zipfile
import logging
from pathlib import Path
from typing import Dict, List, Optional
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
            self.n = 0
        def __iter__(self):
            return iter(self.iterable)
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def update(self, n=1):
            self.n += n

# ============================================================================
# CONFIGURATION
# ============================================================================
USER_EMAIL = "you@example.com"
USER_TOKEN = "403c0bd0-7649-4a4a-a970-71e6f33f5259"
# ============================================================================


class SmartGuruExporter:
    def __init__(self, email: str, token: str):
        self.email = email
        self.token = token
        self.auth = HTTPBasicAuth(email, token)
        self.base_url = "https://api.getguru.com/api/v1"
        self.session = requests.Session()
        self.session.auth = self.auth
        
        # Setup logging
        log_dir = Path("guru_export_logs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = log_dir / f"guru_export_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.stats = {
            'api_calls': 0,
            'cards_fetched': 0,
            'cards_exported': 0,
            'cards_skipped': 0,
        }
    
    def request(self, endpoint: str, method: str = "GET", max_retries: int = 3, **kwargs):
        """Make API request with retry logic"""
        url = f"{self.base_url}/{endpoint}"
        self.stats['api_calls'] += 1
        
        for attempt in range(max_retries):
            try:
                if method == "GET":
                    response = self.session.get(url, timeout=30, **kwargs)
                elif method == "POST":
                    response = self.session.post(url, timeout=30, **kwargs)
                
                response.raise_for_status()
                return response.json() if response.content else {}
                
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    self.logger.error(f"Failed: {endpoint} - {e}")
                    return None
        return None
    
    def get_collections(self) -> List[Dict]:
        """Get all collections"""
        print("📚 Loading collections...")
        collections = self.request("collections")
        if not collections or not isinstance(collections, list):
            return []
        collections.sort(key=lambda x: x.get('name', '').lower())
        return collections
    
    def get_all_cards(self, collection_id: str, limit: Optional[int] = None, 
                      verification_filter: Optional[str] = None) -> List[Dict]:
        """Get cards with optional limit and filtering"""
        all_cards = []
        skip = 0
        batch_size = 50
        
        print(f"\n📊 Fetching cards from API...")
        
        while True:
            if limit and len(all_cards) >= limit:
                break
            
            search_body = {
                "queryType": "cards",
                "collectionIds": [collection_id],
                "skip": skip,
                "limit": batch_size
            }
            
            cards = self.request("search/cardmgr", method="POST", json=search_body)
            
            if not cards or not isinstance(cards, list) or len(cards) == 0:
                break
            
            # Apply verification filter if specified
            if verification_filter and verification_filter != "ALL":
                cards = [c for c in cards if c.get('verificationState') == verification_filter]
            
            all_cards.extend(cards)
            self.stats['cards_fetched'] = len(all_cards)
            
            print(f"  → Fetched {len(all_cards)} cards...", end="\r")
            
            if len(cards) < batch_size:
                break
            
            skip += batch_size
            time.sleep(0.2)
        
        print(f"  ✓ Fetched {len(all_cards)} cards total     ")
        return all_cards
    
    def show_filter_menu(self) -> str:
        """Ask user which cards to export"""
        print("\n" + "="*70)
        print("🔍 FILTER OPTIONS")
        print("="*70 + "\n")
        
        print("  1. ALL cards (includes TRUSTED and NEEDS_VERIFICATION)")
        print("  2. TRUSTED cards only (verified and up to date)")
        print("  3. NEEDS_VERIFICATION cards only (requires review)")
        print()
        
        while True:
            choice = input("Select filter (1-3): ").strip()
            if choice == "1":
                return "ALL"
            elif choice == "2":
                return "TRUSTED"
            elif choice == "3":
                return "NEEDS_VERIFICATION"
            print("❌ Enter 1, 2, or 3")
    
    def show_limit_menu(self, total_cards: int) -> Optional[int]:
        """Ask user if they want to limit export"""
        print("\n" + "="*70)
        print("📊 EXPORT LIMIT")
        print("="*70 + "\n")
        
        print(f"  Total cards available: {total_cards}")
        print()
        print("  Options:")
        print("  1. Export ALL cards")
        print("  2. Export first 200 cards (quick test)")
        print("  3. Export first 500 cards")
        print("  4. Custom limit")
        print()
        
        while True:
            choice = input("Select option (1-4): ").strip()
            if choice == "1":
                return None  # No limit
            elif choice == "2":
                return min(200, total_cards)
            elif choice == "3":
                return min(500, total_cards)
            elif choice == "4":
                while True:
                    try:
                        custom = input(f"Enter limit (1-{total_cards}): ").strip()
                        limit = int(custom)
                        if 1 <= limit <= total_cards:
                            return limit
                        print(f"❌ Enter a number between 1 and {total_cards}")
                    except ValueError:
                        print("❌ Enter a valid number")
            print("❌ Enter 1, 2, 3, or 4")
    
    def export_collection(self, collection: Dict, card_limit: Optional[int] = None,
                         verification_filter: str = "ALL"):
        """Export collection with filters"""
        coll_id = collection.get('id')
        coll_name = collection.get('name', 'Unknown')
        
        print(f"\n{'='*70}")
        print(f"📦 EXPORTING: {coll_name}")
        print(f"{'='*70}\n")
        
        start_time = time.time()
        
        # Get filtered cards
        all_cards = self.get_all_cards(coll_id, card_limit, verification_filter)
        
        if not all_cards:
            print("  ⚠️  No cards found matching filter")
            return None
        
        print(f"\n  ✓ Will export {len(all_cards)} cards")
        
        # Confirm
        if len(all_cards) > 100:
            print(f"\n  ⚠️  This will download {len(all_cards)} cards")
            print(f"  Estimated time: ~{len(all_cards) * 0.4 / 60:.1f} minutes")
            confirm = input("\n  Continue? (y/n): ").strip().lower()
            if confirm != 'y':
                print("  ❌ Export cancelled")
                return None
        
        # Get folders
        print("\n📁 Fetching folder structure...")
        top_folders = self.get_folders(collection)
        folders = self.process_folders(top_folders)
        print(f"  ✓ Found {len(folders)} folders")
        
        # Create temp directory
        temp_dir = Path(f"/tmp/guru_export_{coll_id}")
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
        
        failed_cards = []
        
        with tqdm(all_cards, desc="  Progress", unit="card") as pbar:
            for card in pbar:
                card_id = card.get('id')
                if not card_id:
                    continue
                
                full_card = self.request(f"cards/{card_id}")
                
                if not full_card:
                    failed_cards.append(card_id)
                    continue
                
                # Save card metadata
                self.save_card_metadata(full_card, cards_dir)
                
                # Save card HTML
                html_file = cards_dir / f"{card_id}.html"
                with open(html_file, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(full_card.get('content', ''))
                
                self.stats['cards_exported'] += 1
                time.sleep(0.15)
        
        print(f"\n  ✓ Downloaded {self.stats['cards_exported']}/{len(all_cards)} cards")
        
        if failed_cards:
            print(f"  ⚠️  {len(failed_cards)} cards failed")
            self.logger.warning(f"Failed cards: {failed_cards[:10]}")
        
        # Save folders
        self.save_folders(folders, folders_dir)
        
        # Save collection metadata
        self.save_collection_metadata(collection, all_cards, folders, temp_dir)
        
        # Create zip
        print("\n📦 Creating zip file...")
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in coll_name)
        safe_name = safe_name.replace(' ', '_')[:50]
        
        suffix = ""
        if card_limit:
            suffix = f"_first{card_limit}"
        if verification_filter != "ALL":
            suffix += f"_{verification_filter.lower()}"
        
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
        
        elapsed = time.time() - start_time
        
        print(f"  ✓ Created {zip_path}")
        print(f"\n⏱️  Total time: {elapsed:.1f}s")
        
        return zip_path
    
    def save_card_metadata(self, card: Dict, cards_dir: Path):
        """Save card metadata to YAML"""
        card_id = card.get('id')
        title = card.get('preferredPhrase', 'Untitled')
        
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
            'ViewCount': card.get('cardInfo', {}).get('analytics', {}).get('views', 0),
        }
        
        yaml_file = cards_dir / f"{card_id}.yaml"
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(card_yaml, f, default_flow_style=False, allow_unicode=True)
    
    def get_folders(self, collection: Dict) -> List[Dict]:
        """Get top-level folders"""
        home_slug = collection.get('homeBoardSlug')
        if not home_slug:
            return []
        
        folder_id = home_slug.split('/')[0] if '/' in home_slug else home_slug
        home_folder = self.request(f"folders/{folder_id}/items")
        
        if not home_folder or not isinstance(home_folder, list):
            return []
        
        return [item for item in home_folder if item.get('type') == 'folder']
    
    def process_folders(self, top_folders: List[Dict]) -> Dict:
        """Process folder hierarchy"""
        folders = {}
        
        def process_folder(folder_data):
            folder_id = folder_data.get('id') or folder_data.get('itemId')
            if not folder_id or folder_id in folders:
                return
            
            items = self.request(f"folders/{folder_id}/items")
            
            folder_info = {
                'id': folder_id,
                'title': folder_data.get('title', 'Untitled'),
                'cards': [],
                'subfolders': []
            }
            
            if items and isinstance(items, list):
                for item in items:
                    item_type = item.get('type')
                    item_id = item.get('id') or item.get('itemId')
                    
                    if item_type == 'card' and item_id:
                        folder_info['cards'].append(item_id)
                    elif item_type == 'folder' and item_id:
                        folder_info['subfolders'].append(item_id)
                        process_folder(item)
            
            folders[folder_id] = folder_info
        
        for folder in top_folders:
            process_folder(folder)
        
        return folders
    
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
    
    def save_collection_metadata(self, collection: Dict, cards: List[Dict], 
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
            'Title': collection.get('name', 'Export'),
            'Description': collection.get('description', ''),
            'ExternalId': collection.get('id'),
            'Items': items
        }
        
        coll_file = temp_dir / "collection.yaml"
        with open(coll_file, 'w', encoding='utf-8') as f:
            yaml.dump(collection_yaml, f, default_flow_style=False, allow_unicode=True)
    
    def show_menu(self, collections: List[Dict]):
        """Display collection menu"""
        print("\n" + "="*70)
        print("📋 SELECT COLLECTION TO EXPORT")
        print("="*70 + "\n")
        for i, coll in enumerate(collections, 1):
            name = coll.get('name', 'Unknown')
            if len(name) > 50:
                name = name[:47] + "..."
            print(f"  {i:2d}. {name}")
        print(f"\n   0. Exit")
        print("\n" + "="*70)
    
    def get_choice(self, max_num: int) -> int:
        """Get user's choice"""
        while True:
            try:
                choice = input("\nEnter number (0 to exit): ").strip()
                if not choice:
                    continue
                num = int(choice)
                if 0 <= num <= max_num:
                    return num
                print(f"❌ Enter 0-{max_num}")
            except ValueError:
                print("❌ Enter a number")
            except KeyboardInterrupt:
                return 0
    
    def run(self):
        """Main loop"""
        print("\n" + "="*70)
        print("📥 Smart Guru Exporter")
        print("="*70 + "\n")
        
        print(f"User: {self.email}")
        print(f"Log:  {self.log_file}\n")
        
        collections = self.get_collections()
        if not collections:
            print("❌ No collections found")
            return
        
        print(f"✓ Found {len(collections)} collections")
        
        while True:
            self.show_menu(collections)
            choice = self.get_choice(len(collections))
            
            if choice == 0:
                break
            
            selected = collections[choice - 1]
            
            try:
                # Reset stats
                self.stats = {
                    'api_calls': 0,
                    'cards_fetched': 0,
                    'cards_exported': 0,
                    'cards_skipped': 0,
                }
                
                # Ask for filters
                verification_filter = self.show_filter_menu()
                
                # Quick count
                print(f"\n📊 Counting cards with filter: {verification_filter}...")
                test_cards = self.get_all_cards(selected.get('id'), limit=500, 
                                               verification_filter=verification_filter)
                
                card_limit = self.show_limit_menu(len(test_cards))
                
                # Export
                zip_path = self.export_collection(selected, card_limit, verification_filter)
                
                if zip_path:
                    print(f"\n{'='*70}")
                    print("✅ SUCCESS!")
                    print(f"{'='*70}")
                    print(f"\n📦 File: {zip_path}")
                    print(f"\n📊 Stats:")
                    print(f"  • API calls: {self.stats['api_calls']}")
                    print(f"  • Cards exported: {self.stats['cards_exported']}")
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Cancelled by user")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                self.logger.exception(f"Export failed: {e}")
            
            print("\n" + "="*70)
            another = input("\nExport another? (y/n): ").strip().lower()
            if another != 'y':
                break
        
        print("\n✨ Done!\n")


def main():
    try:
        exporter = SmartGuruExporter(USER_EMAIL, USER_TOKEN)
        exporter.run()
    except KeyboardInterrupt:
        print("\n\n👋 Bye!\n")


if __name__ == "__main__":
    main()
