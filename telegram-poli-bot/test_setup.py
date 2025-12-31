"""
Testing Script - Verify bot configuration and Google Drive access
Run: python test_setup.py
"""

import os
import json
import sys
from pathlib import Path


def print_test(name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {name}")
    if details and not passed:
        print(f"        {details}")


def test_files_exist():
    """Test if required files exist"""
    print("\n📁 Checking Files...")
    print("-" * 70)
    
    files = {
        "config.py": "Configuration file",
        "bot.py": "Main bot script",
        "drive_service.py": "Google Drive service",
        "auto_delete.py": "Auto-delete module",
        "setup_folders.py": "Folder setup script",
        "requirements.txt": "Dependencies",
        "credentials.json": "Google Service Account"
    }
    
    results = []
    for file_name, description in files.items():
        exists = os.path.isfile(file_name)
        print_test(f"{file_name}: {description}", exists)
        results.append(exists)
    
    return all(results)


def test_config():
    """Test config.py"""
    print("\n⚙️  Checking Configuration...")
    print("-" * 70)
    
    try:
        import config
        
        # Check BOT_TOKEN
        has_token = (
            hasattr(config, 'BOT_TOKEN') and 
            config.BOT_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN_HERE"
        )
        print_test(
            "BOT_TOKEN configured",
            has_token,
            "Update BOT_TOKEN in config.py"
        )
        
        # Check PARENT_FOLDER_ID
        has_folder = (
            hasattr(config, 'PARENT_FOLDER_ID') and 
            config.PARENT_FOLDER_ID != ""
        )
        print_test(
            "PARENT_FOLDER_ID configured",
            has_folder,
            "Update PARENT_FOLDER_ID in config.py"
        )
        
        # Check POLI_FOLDERS
        has_polis = (
            hasattr(config, 'POLI_FOLDERS') and 
            len(config.POLI_FOLDERS) > 0
        )
        poli_count = len(config.POLI_FOLDERS) if has_polis else 0
        print_test(
            f"POLI_FOLDERS configured ({poli_count} polis)",
            has_polis and poli_count >= 50
        )
        
        # Check other settings
        has_temp_dir = hasattr(config, 'TEMP_DIR')
        print_test("TEMP_DIR setting exists", has_temp_dir)
        
        has_db_file = hasattr(config, 'DB_FILE')
        print_test("DB_FILE setting exists", has_db_file)
        
        return has_token and has_folder and has_polis
    
    except Exception as e:
        print_test("Config import", False, str(e))
        return False


def test_credentials():
    """Test credentials.json"""
    print("\n🔑 Checking Credentials...")
    print("-" * 70)
    
    if not os.path.isfile("credentials.json"):
        print_test("credentials.json exists", False)
        return False
    
    try:
        with open("credentials.json", "r") as f:
            creds = json.load(f)
        
        # Check required fields
        has_type = creds.get("type") == "service_account"
        print_test("Type is service_account", has_type)
        
        has_project = "project_id" in creds and creds["project_id"] != "your-project-id"
        print_test("Project ID configured", has_project)
        
        has_email = "client_email" in creds and "@" in creds["client_email"]
        print_test(f"Service Account email: {creds.get('client_email', 'N/A')}", has_email)
        
        has_key = "private_key" in creds and len(creds["private_key"]) > 100
        print_test("Private key present", has_key)
        
        return has_type and has_email and has_key
    
    except json.JSONDecodeError:
        print_test("credentials.json is valid JSON", False, "Invalid JSON format")
        return False
    except Exception as e:
        print_test("credentials.json validation", False, str(e))
        return False


def test_dependencies():
    """Test if dependencies can be imported"""
    print("\n📦 Checking Dependencies...")
    print("-" * 70)
    
    packages = {
        "telegram": "python-telegram-bot",
        "PIL": "Pillow",
        "google.auth": "google-auth",
        "googleapiclient": "google-api-python-client",
        "apscheduler": "APScheduler"
    }
    
    results = []
    for import_name, package_name in packages.items():
        try:
            __import__(import_name)
            print_test(f"{package_name} installed", True)
            results.append(True)
        except ImportError:
            print_test(
                f"{package_name} installed",
                False,
                f"Run: pip install {package_name}"
            )
            results.append(False)
    
    return all(results)


def test_directories():
    """Test if required directories exist"""
    print("\n📂 Checking Directories...")
    print("-" * 70)
    
    dirs = {
        "temp": "Temporary files"
    }
    
    results = []
    for dir_name, description in dirs.items():
        exists = os.path.isdir(dir_name)
        print_test(f"{dir_name}/: {description}", exists)
        if not exists:
            os.makedirs(dir_name, exist_ok=True)
            print(f"   📝 Created {dir_name}/ directory")
        results.append(True)
    
    return all(results)


def test_google_drive_connection():
    """Test Google Drive connection"""
    print("\n🌐 Testing Google Drive Connection...")
    print("-" * 70)
    
    try:
        from drive_service import GoogleDriveService
        import config
        
        print("Initializing Google Drive service...")
        drive = GoogleDriveService()
        
        # Test folder access
        parent_folder_id = config.PARENT_FOLDER_ID
        exists = drive.check_folder_exists(parent_folder_id)
        
        print_test(
            f"Parent folder accessible ({parent_folder_id})",
            exists,
            "Check if Service Account is shared to folder"
        )
        
        return exists
    
    except Exception as e:
        print_test("Google Drive connection", False, str(e))
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("  🧪 TELEGRAM POLI BOT - SETUP TEST")
    print("=" * 70)
    
    results = {
        "Files": test_files_exist(),
        "Config": test_config(),
        "Credentials": test_credentials(),
        "Dependencies": test_dependencies(),
        "Directories": test_directories(),
        "Google Drive": test_google_drive_connection()
    }
    
    # Summary
    print("\n" + "=" * 70)
    print("  📊 TEST SUMMARY")
    print("=" * 70)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print("-" * 70)
    print(f"Total: {passed}/{total} tests passed\n")
    
    if passed == total:
        print("""
✅ ALL TESTS PASSED!

Your bot is ready to run:

1. Run setup_folders.py (if not done yet):
   python setup_folders.py

2. Start bot:
   python bot.py

3. Test in Telegram:
   Open bot and click /start
""")
        return True
    else:
        print(f"""
❌ {total - passed} TEST(S) FAILED

Please fix the issues above before running the bot.

Common issues:
- BOT_TOKEN not configured in config.py
- credentials.json not downloaded or invalid
- Dependencies not installed (pip install -r requirements.txt)
- Service Account not shared to Google Drive folder

For detailed setup, read: SETUP.md
""")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)
