#!/usr/bin/env python3
"""
GURU ENRICHER: Take website export + enrich with API data for Notion

Simple workflow:
1. Export from Guru website (gets correct cards)
2. Run this script on that export
3. Script uses API to get full details for ONLY those cards
4. Output ready for Notion

Usage: python3 guru_enricher.py <guru_website_export.zip>
"""

import os
import sys
import time
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Set
import requests
from requests.auth import HTTPBasicAuth
import yaml

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("💡 Tip: Install tqdm for progress bars: pip install tqdm --break-system-packages\n")

# ============================================================================
# CONFIGURATION
# ============================================================================
USER_EMAIL = "you@example.com"
USER_TOKEN = "403c0bd0-7649-4a4a-a970-71e6f33f5259"
# ============================================================================


class GuruEnricher:
    def __init__(self, email: str, token: str):
        self.email = email
        self.token = token
        self.auth = HTTPBasicAuth(email, token)
        self.base_url = "https://api.getguru.com/api/v1"
        self.session = requests.Session()
        self.session.auth = self.auth
        self.failed_cards = []
    
    def request(self, endpoint: str, method: str = "GET", max_retries: int = 3, **kwargs):
        """Make API request with retry"""
        url = f"{self.base_url}/{endpoint}"
        
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
                    return None
        return None
    
    def extract_card_ids_from_export(self, zip_path: Path) -> Set[str]:
        """Extract card IDs from Guru website export"""
        print(f"\n{'='*70}")
        print(f"📦 ANALYZING WEBSITE EXPORT")
        print(f"{'='*70}\n")
        
        print(f"File: {zip_path}")
        
        # Extract to temp
        temp_dir = Path("/tmp/guru_website_export")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        print("📂 Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(temp_dir)
        
        # Find card IDs
        card_ids = set()
        
        # Look for cards directory with YAML files
        cards_dir = temp_dir / 'cards'
        if cards_dir.exists():
            yaml_files = list(cards_dir.glob("*.yaml"))
            print(f"✓ Found {len(yaml_files)} card metadata files")
            
            for yaml_file in yaml_files:
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                    
                    card_id = data.get('ExternalId') or data.get('id')
                    if card_id:
                        card_ids.add(card_id)
                except:
                    pass
        
        # Alternative: look for card IDs in filenames
        if not card_ids:
            print("  Trying alternative: extracting IDs from filenames...")
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    # Card IDs are typically UUIDs in filenames
                    if '.yaml' in file or '.html' in file:
                        # Extract UUID-like patterns
                        import re
                        uuid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
                        matches = re.findall(uuid_pattern, file)
                        card_ids.update(matches)
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        print(f"\n✓ Extracted {len(card_ids)} card IDs from export\n")
        
        return card_ids
    
    def enrich_cards(self, card_ids: Set[str], output_dir: Path):
        """Get full card details from API for each card ID"""
        print(f"{'='*70}")
        print(f"💎 ENRICHING WITH API DATA")
        print(f"{'='*70}\n")
        
        print(f"Will fetch full details for {len(card_ids)} cards from API...")
        
        cards_dir = output_dir / 'cards'
        cards_dir.mkdir(parents=True, exist_ok=True)
        
        # Create progress bar
        if HAS_TQDM:
            pbar = tqdm(list(card_ids), desc="  Enriching", unit="card")
        else:
            pbar = list(card_ids)
            print(f"  Progress: 0/{len(card_ids)} cards", end="")
        
        enriched = 0
        
        for idx, card_id in enumerate(pbar, 1):
            # Get full card details from API
            full_card = self.request(f"cards/{card_id}")
            
            if not full_card:
                self.failed_cards.append(card_id)
                if not HAS_TQDM:
                    print(f"\r  Progress: {idx}/{len(card_ids)} cards (⚠️ {len(self.failed_cards)} failed)", end="")
                continue
            
            # Save enriched metadata as YAML
            card_yaml = self.create_card_metadata(full_card)
            
            yaml_file = cards_dir / f"{card_id}.yaml"
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(card_yaml, f, default_flow_style=False, allow_unicode=True)
            
            # Save HTML content
            html_file = cards_dir / f"{card_id}.html"
            with open(html_file, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(full_card.get('content', ''))
            
            enriched += 1
            
            if not HAS_TQDM:
                print(f"\r  Progress: {idx}/{len(card_ids)} cards", end="")
            
            time.sleep(0.15)  # Rate limiting
        
        if not HAS_TQDM:
            print()  # New line
        
        print(f"\n✓ Enriched {enriched}/{len(card_ids)} cards")
        
        if self.failed_cards:
            print(f"⚠️  {len(self.failed_cards)} cards failed to fetch")
            if len(self.failed_cards) <= 10:
                for card_id in self.failed_cards:
                    print(f"   - {card_id}")
        
        return enriched
    
    def create_card_metadata(self, card: Dict) -> Dict:
        """Create comprehensive card metadata"""
        title = card.get('preferredPhrase', 'Untitled')
        
        # Extract verifier info
        verifiers = card.get('verifiers', [])
        verifier_emails = [v.get('user', {}).get('email', '') 
                          for v in verifiers if v.get('type') == 'user']
        verifier_groups = [v.get('userGroup', {}).get('name', '') 
                          for v in verifiers if v.get('type') == 'user-group']
        
        # Extract owner info
        owner = card.get('owner', {})
        owner_email = owner.get('email', '')
        owner_name = f"{owner.get('firstName', '')} {owner.get('lastName', '')}".strip()
        
        # Last modified by
        last_mod = card.get('lastModifiedBy', {})
        last_mod_email = last_mod.get('email', '')
        last_mod_name = f"{last_mod.get('firstName', '')} {last_mod.get('lastName', '')}".strip()
        
        # Last verified by
        last_ver = card.get('lastVerifiedBy', {})
        last_ver_email = last_ver.get('email', '')
        last_ver_name = f"{last_ver.get('firstName', '')} {last_ver.get('lastName', '')}".strip()
        
        return {
            'Title': title,
            'OriginalTitle': title,
            'ExternalId': card.get('id', ''),
            'ShareStatus': card.get('shareStatus', ''),
            
            # Verification
            'VerificationState': card.get('verificationState', 'UNKNOWN'),
            'VerificationInterval': card.get('verificationInterval', ''),
            'VerificationType': card.get('verificationType', ''),
            'NextVerificationDate': card.get('nextVerificationDate', ''),
            'LastVerified': card.get('lastVerified', ''),
            'LastVerifiedBy': {
                'Email': last_ver_email,
                'Name': last_ver_name
            },
            'Verifiers': {
                'Users': verifier_emails,
                'Groups': verifier_groups
            },
            'VerificationReasons': card.get('verificationReasons', []),
            
            # Timestamps
            'DateCreated': card.get('dateCreated', ''),
            'LastModified': card.get('lastModified', ''),
            
            # People
            'Owner': {
                'Email': owner_email,
                'Name': owner_name
            },
            'LastModifiedBy': {
                'Email': last_mod_email,
                'Name': last_mod_name
            },
            
            # Content
            'Tags': [tag.get('value', '') for tag in card.get('tags', [])],
            'Boards': [
                {
                    'Id': board.get('id', ''),
                    'Title': board.get('title', '')
                }
                for board in card.get('boards', [])
            ],
            
            # Stats
            'Version': card.get('version', ''),
            'ViewCount': card.get('cardInfo', {}).get('analytics', {}).get('views', 0),
            
            # Collection info
            'CollectionId': card.get('collection', {}).get('id', '') if isinstance(card.get('collection'), dict) else '',
            'CollectionName': card.get('collection', {}).get('name', '') if isinstance(card.get('collection'), dict) else '',
        }
    
    def enrich_export(self, zip_path: Path) -> Path:
        """Main enrichment process"""
        print("\n" + "="*70)
        print("💎 GURU ENRICHER")
        print("="*70 + "\n")
        
        print(f"Input:  {zip_path}")
        print(f"User:   {self.email}\n")
        
        start_time = time.time()
        
        # Step 1: Extract card IDs from website export
        card_ids = self.extract_card_ids_from_export(zip_path)
        
        if not card_ids:
            print("❌ No card IDs found in export")
            return None
        
        # Step 2: Create output directory
        output_dir = Path(f"/tmp/guru_enriched_{int(time.time())}")
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True)
        
        # Step 3: Enrich cards with API data
        enriched_count = self.enrich_cards(card_ids, output_dir)
        
        if enriched_count == 0:
            print("❌ Failed to enrich any cards")
            return None
        
        # Step 4: Copy folders and collection metadata from original export
        print(f"\n📁 Copying folder structure from original export...")
        
        temp_extract = Path("/tmp/guru_original_extract")
        if temp_extract.exists():
            shutil.rmtree(temp_extract)
        temp_extract.mkdir()
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(temp_extract)
        
        # Copy folders if they exist
        src_folders = temp_extract / 'folders'
        if src_folders.exists():
            dst_folders = output_dir / 'folders'
            shutil.copytree(src_folders, dst_folders)
            folder_count = len(list(dst_folders.glob("*.yaml")))
            print(f"  ✓ Copied {folder_count} folders")
        
        # Copy collection metadata if exists
        src_collection = temp_extract / 'collection.yaml'
        if src_collection.exists():
            dst_collection = output_dir / 'collection.yaml'
            shutil.copy(src_collection, dst_collection)
            print(f"  ✓ Copied collection metadata")
        
        # Copy resources if they exist
        src_resources = temp_extract / 'resources'
        if src_resources.exists() and any(src_resources.iterdir()):
            dst_resources = output_dir / 'resources'
            shutil.copytree(src_resources, dst_resources)
            print(f"  ✓ Copied resources")
        
        shutil.rmtree(temp_extract)
        
        # Step 5: Create enriched zip
        print(f"\n📦 Creating enriched export...")
        
        output_zip = zip_path.parent / f"{zip_path.stem}_enriched.zip"
        
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(output_dir)
                    zipf.write(file_path, arcname)
        
        # Cleanup
        shutil.rmtree(output_dir)
        
        elapsed = time.time() - start_time
        
        print(f"  ✓ Created {output_zip}")
        
        print(f"\n{'='*70}")
        print("✅ SUCCESS!")
        print(f"{'='*70}\n")
        
        print(f"📊 Summary:")
        print(f"  • Input cards:     {len(card_ids)}")
        print(f"  • Enriched:        {enriched_count}")
        print(f"  • Failed:          {len(self.failed_cards)}")
        print(f"  • Time:            {elapsed:.1f}s")
        print(f"\n📦 Enriched export: {output_zip}")
        print(f"\n💡 Next step: Convert to Notion format")
        print(f"   python3 guru_to_notion_enhanced.py {output_zip}")
        
        return output_zip


def main():
    if len(sys.argv) < 2:
        print("\n" + "="*70)
        print("💎 Guru Enricher")
        print("="*70 + "\n")
        print("Usage: python3 guru_enricher.py <guru_website_export.zip>")
        print("\nThis tool:")
        print("  1. Takes your Guru website export (170 cards)")
        print("  2. Uses API to get full details for ONLY those cards")
        print("  3. Creates enriched export ready for Notion")
        print("\nExample:")
        print("  python3 guru_enricher.py ~/Downloads/guru_sales_export.zip")
        print()
        sys.exit(1)
    
    export_path = Path(sys.argv[1])
    
    if not export_path.exists():
        print(f"❌ File not found: {export_path}")
        sys.exit(1)
    
    if not export_path.suffix.lower() == '.zip':
        print("❌ Please provide a .zip file")
        sys.exit(1)
    
    try:
        enricher = GuruEnricher(USER_EMAIL, USER_TOKEN)
        enriched_zip = enricher.enrich_export(export_path)
        
        if enriched_zip and enriched_zip.exists():
            # Ask if user wants to convert to Notion
            print("\n" + "="*70)
            convert = input("Convert to Notion format now? (y/n): ").strip().lower()
            
            if convert == 'y':
                converter_script = Path("guru_to_notion_enhanced.py")
                if converter_script.exists():
                    print("\n🔄 Converting to Notion format...")
                    import subprocess
                    try:
                        subprocess.run(["python3", str(converter_script), str(enriched_zip)], check=True)
                    except:
                        print("⚠️  Conversion had issues, but enriched file is ready")
                else:
                    print(f"⚠️  Converter not found: {converter_script}")
                    print("   Run manually: python3 guru_to_notion_enhanced.py " + str(enriched_zip))
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
