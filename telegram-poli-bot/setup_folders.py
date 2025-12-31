"""
Script untuk membuat subfolder Poli otomatis di Google Drive
Jalankan: python setup_folders.py
"""

import json
import os
import re
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import config


def setup_google_drive():
    """Initialize Google Drive service"""
    try:
        credentials = Credentials.from_service_account_file(
            config.CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        service = build('drive', 'v3', credentials=credentials)
        return service
    except FileNotFoundError:
        print(f"❌ ERROR: File {config.CREDENTIALS_FILE} tidak ditemukan!")
        print("Silakan download credentials.json dari Google Cloud Console")
        return None
    except Exception as e:
        print(f"❌ ERROR: Gagal inisialisasi Google Drive: {str(e)}")
        return None


def create_folder(service, folder_name, parent_folder_id):
    """Create folder in Google Drive"""
    try:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        
        folder = service.files().create(
            body=file_metadata,
            fields='id, name, webViewLink'
        ).execute()
        
        return folder
    except Exception as e:
        print(f"❌ Gagal membuat folder '{folder_name}': {str(e)}")
        return None


def update_config_file(folder_mapping):
    """Update config.py dengan folder ID yang baru dibuat"""
    try:
        config_path = 'config.py'
        
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate poli folders dict
        poli_dict_lines = ["POLI_FOLDERS = {"]
        for poli_name, folder_id in folder_mapping.items():
            poli_dict_lines.append(f'    "{poli_name}": "{folder_id}",')
        poli_dict_lines[-1] = poli_dict_lines[-1].rstrip(',')  # Remove trailing comma
        poli_dict_lines.append("}")
        poli_dict_str = "\n".join(poli_dict_lines)
        
        # Replace old POLI_FOLDERS definition
        pattern = r'POLI_FOLDERS = \{[^}]*\}'
        content = re.sub(pattern, poli_dict_str, content, flags=re.DOTALL)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ config.py berhasil diupdate!")
        return True
    except Exception as e:
        print(f"❌ Gagal update config.py: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("🚀 Auto-Create Folder Poli di Google Drive")
    print("=" * 60)
    
    # Initialize Google Drive
    print("\n📡 Menghubungkan ke Google Drive...")
    service = setup_google_drive()
    if not service:
        return False
    
    print("✅ Terkoneksi ke Google Drive")
    
    # Verify parent folder exists
    parent_folder_id = config.PARENT_FOLDER_ID
    print(f"\n📁 Parent Folder ID: {parent_folder_id}")
    
    try:
        parent_folder = service.files().get(
            fileId=parent_folder_id,
            fields='id, name'
        ).execute()
        print(f"✅ Parent Folder: {parent_folder['name']}")
    except Exception as e:
        print(f"❌ ERROR: Parent folder tidak ditemukan atau tidak bisa diakses!")
        print(f"   Pastikan Service Account sudah share folder: {parent_folder_id}")
        return False
    
    # Get list of poli
    poli_list = sorted(list(config.POLI_FOLDERS.keys()))
    print(f"\n📋 Total Poli: {len(poli_list)}")
    
    # Create folders
    print("\n⏳ Membuat subfolder...")
    print("-" * 60)
    
    folder_mapping = {}
    success_count = 0
    failed_count = 0
    
    for idx, poli_name in enumerate(poli_list, 1):
        print(f"[{idx}/{len(poli_list)}] Membuat folder: {poli_name}...", end=" ")
        
        folder = create_folder(service, poli_name, parent_folder_id)
        
        if folder:
            folder_id = folder['id']
            folder_mapping[poli_name] = folder_id
            folder_link = folder['webViewLink']
            print(f"✅")
            print(f"    ID: {folder_id}")
            print(f"    Link: {folder_link}")
            success_count += 1
        else:
            folder_mapping[poli_name] = f"YOUR_FOLDER_ID_{poli_name.replace(' ', '_').upper()}"
            failed_count += 1
    
    print("-" * 60)
    print(f"\n📊 Hasil:")
    print(f"   ✅ Berhasil: {success_count}")
    print(f"   ❌ Gagal: {failed_count}")
    
    # Update config
    if success_count > 0:
        print("\n💾 Mengupdate config.py...")
        if update_config_file(folder_mapping):
            print("\n" + "=" * 60)
            print("✅ SELESAI!")
            print("=" * 60)
            print(f"\n✓ {success_count} folder berhasil dibuat")
            print("✓ config.py berhasil diupdate")
            print("\nSilakan jalankan bot dengan: python bot.py")
            return True
    else:
        print("\n❌ Tidak ada folder yang berhasil dibuat.")
        return False


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Dibatalkan oleh user")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        exit(1)
