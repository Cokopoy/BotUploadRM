# 🚀 Setup Guide - Telegram Poli Bot

## STEP 1: Setup Google Cloud & Service Account

### 1.1 Buat Project di Google Cloud Console
1. Go to: https://console.cloud.google.com/
2. Klik "Select a Project" → "NEW PROJECT"
3. Beri nama: `TelegramPoliBot`
4. Klik "CREATE"

### 1.2 Enable Google Drive API
1. Di search bar, cari: `Google Drive API`
2. Klik hasil pencarian
3. Klik "ENABLE"
4. Tunggu beberapa detik sampai enabled

### 1.3 Buat Service Account
1. Di sidebar, klik "APIs & Services" → "Credentials"
2. Klik "Create Credentials" → "Service Account"
3. Isi:
   - Service account name: `telegram-bot`
   - Klik "CREATE AND CONTINUE"
4. Grant roles: Cari dan pilih "Editor"
5. Klik "CONTINUE" → "DONE"

### 1.4 Generate JSON Key
1. Di halaman Service Account, klik tab "KEYS"
2. Klik "Add Key" → "Create new key"
3. Pilih format "JSON"
4. Klik "CREATE"
5. File JSON akan otomatis download
6. Rename menjadi `credentials.json`
7. Pindahkan ke folder `telegram-poli-bot/`

---

## STEP 2: Setup Telegram Bot Token

### 2.1 Buat Bot di Telegram
1. Go to: https://t.me/BotFather
2. Ketik: `/newbot`
3. Ikuti instruksi:
   - Bot name: `Poli Doc Bot` (atau nama lain)
   - Bot username: `poli_doc_bot_yourname` (harus unik)
4. Simpan token yang diberikan

### 2.2 Update config.py
```python
BOT_TOKEN = "YOUR_TOKEN_HERE"  # Ganti dengan token dari BotFather
```

---

## STEP 3: Setup Google Drive Folders

### 3.1 Share Parent Folder ke Service Account
1. Buka parent folder Google Drive:
   https://drive.google.com/drive/folders/1LFh3zSj3rOLTIJwIMqT3wBLDB-OJm7HF

2. Klik "Share"

3. Copy email Service Account dari credentials.json:
   (Cari field: "client_email")
   Contoh: `telegram-bot@project-id.iam.gserviceaccount.com`

4. Paste email di kolom "Share with"

5. Jangan centang "Notify people"

6. Klik "Share"

### 3.2 Auto-Create All Poli Folders
Jalankan script setup:
```bash
python setup_folders.py
```

Script ini akan:
- ✅ Membuat 50+ subfolder untuk setiap Poli
- ✅ Update config.py dengan Folder ID otomatis
- ✅ Tampilkan link untuk verify folder di Google Drive

**Tunggu sampai selesai**, jangan cancel!

---

## STEP 4: Install Dependencies

```bash
pip install -r requirements.txt
```

Atau install manual:
```bash
pip install python-telegram-bot==20.7
pip install Pillow==10.1.0
pip install google-api-python-client==1.12.1
pip install google-auth-httplib2==0.2.0
pip install google-auth-oauthlib==1.2.0
pip install APScheduler==3.10.4
```

---

## STEP 5: Run Bot

```bash
python bot.py
```

Output akan seperti ini:
```
2025-12-30 10:30:45,123 - telegram.ext._application - INFO - Application started
Bot started successfully
```

---

## STEP 6: Test Bot di Telegram

1. Go to: https://t.me/username_bot_anda

2. Klik "Start"

3. Bot akan menampilkan:
   - List pilihan Poli (dengan pagination)
   - Tombol untuk pilih Poli

4. Pilih satu Poli → Kirim foto test

5. Klik "Selesai & Buat PDF"

6. Cek Google Drive apakah PDF ter-upload

---

## Troubleshooting

### Bot tidak merespons
- Cek BOT_TOKEN benar di config.py
- Restart bot: `Ctrl+C` kemudian `python bot.py`
- Cek internet connection

### Error: "Credentials file not found"
- Cek file `credentials.json` ada di folder `telegram-poli-bot/`
- Pastikan nama file tepat (case-sensitive)

### Error: "Parent folder not found"
- Cek PARENT_FOLDER_ID di config.py benar
- Cek Service Account sudah di-share ke parent folder

### Folder tidak ter-create saat setup_folders.py
- Cek credentials.json valid
- Cek Service Account email ter-share ke parent folder
- Cek API sudah enabled di Google Cloud Console

### PDF tidak ter-upload
- Cek POLI_FOLDERS di config.py tidak kosong
- Cek internet connection stabil
- Cek Google Drive API quota

### File tidak ter-delete otomatis (5 hari)
- Bot harus tetap berjalan untuk auto-delete job
- Job run setiap 1 jam untuk cek expired files

---

## File Structure

```
telegram-poli-bot/
├── bot.py                    # Main bot
├── config.py                 # Configuration
├── drive_service.py          # Google Drive wrapper
├── auto_delete.py            # Auto-delete logic
├── setup_folders.py          # Setup script (jalankan sekali)
├── requirements.txt          # Dependencies
├── credentials.json          # Service Account (secret!)
├── files_db.json             # File records
├── README.md                 # Documentation
├── SETUP.md                  # File ini
├── .gitignore               # Git config
└── temp/                     # Temporary files (auto-created)
```

---

## Production Deployment (VPS)

### Install di VPS Linux (Ubuntu/Debian):

```bash
# 1. SSH ke VPS
ssh user@your-vps-ip

# 2. Update system
sudo apt-get update && sudo apt-get upgrade -y

# 3. Install Python & pip
sudo apt-get install python3 python3-pip -y

# 4. Clone project
git clone <repo-url>
cd telegram-poli-bot

# 5. Install dependencies
pip install -r requirements.txt

# 6. Upload credentials.json via SFTP

# 7. Update BOT_TOKEN di config.py

# 8. Test run
python3 bot.py

# 9. Setup systemd service (optional)
sudo nano /etc/systemd/system/telegram-bot.service
```

### Systemd Service File:
```ini
[Unit]
Description=Telegram Poli Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/telegram-poli-bot
ExecStart=/usr/bin/python3 /home/your-username/telegram-poli-bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable & start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

### View logs:
```bash
sudo journalctl -u telegram-bot -f
```

---

## Backup & Security

### Important Files to Backup:
- ✅ `credentials.json` (JANGAN di-commit ke git!)
- ✅ `files_db.json` (database file records)

### Security:
- 🔒 Jangan share `credentials.json`
- 🔒 Jangan push credentials.json ke GitHub
- 🔒 Use `.gitignore` untuk hide sensitive files
- 🔒 Rotate credentials secara berkala

---

## Support & Help

Jika ada error:
1. Cek log output di terminal
2. Cek troubleshooting section di atas
3. Verify semua step setup sudah done
4. Cek Google Cloud Console permissions

---

**Setup selesai! Bot Anda siap digunakan** 🎉
