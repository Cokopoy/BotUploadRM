"""
Quick Setup Script - Interactive configuration wizard
Run: python quick_setup.py
"""

import json
import os
import sys
from pathlib import Path


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(text):
    """Print colored header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_step(step_num, text):
    """Print step"""
    print(f"\n[STEP {step_num}] {text}")
    print("-" * 70)


def validate_folder_exists(path):
    """Check if folder exists"""
    return os.path.isdir(path)


def check_file_exists(path):
    """Check if file exists"""
    return os.path.isfile(path)


def get_input_safe(prompt, default=None):
    """Get user input with default"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    user_input = input(prompt).strip()
    return user_input if user_input else default


def setup_config():
    """Interactive setup for config.py"""
    clear_screen()
    print_header("⚙️  QUICK SETUP - Telegram Poli Bot")
    
    print("Wizard ini akan membantu Anda setup bot dalam 3 langkah mudah\n")
    
    # Step 1: Bot Token
    print_step(1, "Konfigurasi Bot Token")
    print("""
Anda perlu Bot Token dari Telegram BotFather.

Cara mendapat Bot Token:
1. Buka Telegram dan cari @BotFather
2. Ketik /newbot
3. Ikuti instruksi dan copy token yang diberikan
4. Paste token di bawah

(Contoh token: 1234567890:ABCDefGhIjKlMnOpQrStUvWxYzABCDefG)
""")
    
    bot_token = get_input_safe("Bot Token").strip()
    
    if not bot_token or len(bot_token) < 20:
        print("\n❌ ERROR: Bot Token tidak valid!")
        sys.exit(1)
    
    # Step 2: Google Drive Folder
    print_step(2, "Konfigurasi Google Drive Parent Folder")
    print("""
Anda perlu Folder ID dari Google Drive parent folder.

Parent Folder yang sudah tersedia:
1LFh3zSj3rOLTIJwIMqT3wBLDB-OJm7HF

Cara mendapat Folder ID:
1. Buka folder di Google Drive
2. URL: https://drive.google.com/drive/folders/FOLDER_ID_DISINI
3. Copy ID dari URL

(Jika Anda punya folder lain, bisa gunakan ID-nya)
""")
    
    parent_folder_id = get_input_safe(
        "Parent Folder ID",
        "1LFh3zSj3rOLTIJwIMqT3wBLDB-OJm7HF"
    )
    
    if not parent_folder_id or len(parent_folder_id) < 10:
        print("\n❌ ERROR: Folder ID tidak valid!")
        sys.exit(1)
    
    # Step 3: Verify credentials.json
    print_step(3, "Verifikasi credentials.json")
    
    if check_file_exists("credentials.json"):
        print("✅ credentials.json ditemukan!")
    else:
        print("""
❌ credentials.json TIDAK ditemukan!

Anda harus download credentials.json dari Google Cloud Console:

1. Go to: https://console.cloud.google.com/
2. Create project: "TelegramPoliBot"
3. Enable Google Drive API
4. Create Service Account
5. Generate JSON key
6. Download dan rename menjadi credentials.json
7. Pindahkan ke folder telegram-poli-bot/

Setelah download credentials.json, jalankan ulang script ini.
""")
        sys.exit(1)
    
    # Verify credentials.json is valid JSON
    try:
        with open("credentials.json", "r") as f:
            creds = json.load(f)
        
        if "client_email" in creds:
            print(f"✅ Service Account: {creds['client_email']}")
        else:
            print("❌ credentials.json format tidak valid!")
            sys.exit(1)
    except json.JSONDecodeError:
        print("❌ credentials.json bukan JSON valid!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading credentials.json: {str(e)}")
        sys.exit(1)
    
    # Update config.py
    print_step(4, "Update config.py")
    
    try:
        with open("config.py", "r", encoding="utf-8") as f:
            config_content = f.read()
        
        # Replace BOT_TOKEN
        config_content = config_content.replace(
            'BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"',
            f'BOT_TOKEN = "{bot_token}"'
        )
        
        # Replace PARENT_FOLDER_ID
        config_content = config_content.replace(
            'PARENT_FOLDER_ID = "1LFh3zSj3rOLTIJwIMqT3wBLDB-OJm7HF"',
            f'PARENT_FOLDER_ID = "{parent_folder_id}"'
        )
        
        with open("config.py", "w", encoding="utf-8") as f:
            f.write(config_content)
        
        print("✅ config.py berhasil diupdate!")
    
    except Exception as e:
        print(f"❌ Error update config.py: {str(e)}")
        sys.exit(1)
    
    # Summary
    print_header("✅ SETUP SELESAI!")
    
    print("""
Langkah selanjutnya:

1. Setup Google Drive folders (PENTING!):
   
   python setup_folders.py
   
   Script ini akan:
   - Membuat 50+ folder untuk setiap Poli
   - Auto-update config.py dengan Folder ID
   
   ⏱️  Tunggu sampai SELESAI, jangan cancel!

2. Install dependencies:
   
   pip install -r requirements.txt

3. Jalankan bot:
   
   python bot.py

4. Test di Telegram:
   Cari bot Anda dan klik /start

---

📚 Untuk info lebih detail, baca:
   - README.md (documentasi lengkap)
   - SETUP.md (setup guide detail)

⚠️  PENTING:
   - Jangan push credentials.json ke GitHub!
   - Jangan share BOT_TOKEN
   - credentials.json sudah di-.gitignore

Ready? Jalankan: python setup_folders.py
""")


def main():
    """Main setup function"""
    try:
        # Check if already in correct directory
        if not check_file_exists("config.py"):
            print("""
❌ ERROR: Script harus dijalankan dari folder telegram-poli-bot/

Current directory: {cwd}

Silakan masuk ke folder bot terlebih dahulu:
cd telegram-poli-bot
python quick_setup.py
""".format(cwd=os.getcwd()))
            sys.exit(1)
        
        setup_config()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup dibatalkan oleh user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
