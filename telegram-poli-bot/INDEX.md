# 📋 PROJECT STRUCTURE & FILES OVERVIEW

## 🎯 Start Here!

New to this project? Read these in order:
1. **QUICKSTART.md** ← Start with this! (5 min setup)
2. **SETUP.md** ← Detailed guide if you need help
3. **README.md** ← Full documentation

---

## 📦 Project Files

### Core Bot Files
- **bot.py** - Main bot with all handlers and logic
  - /start command
  - Poli selection with pagination
  - Photo upload handling
  - PDF creation & Google Drive upload
  - Auto-delete scheduler
  
- **config.py** - Configuration & settings
  - BOT_TOKEN
  - PARENT_FOLDER_ID
  - POLI_FOLDERS mapping (50+ polis)
  - MAX_PHOTO_MB, AUTO_DELETE_DAYS

- **drive_service.py** - Google Drive API wrapper
  - Upload PDF to Drive
  - Delete file from Drive
  - Get file info
  - Check folder exists

- **auto_delete.py** - File auto-delete logic
  - Load/save file database (JSON)
  - Check expired files (> 5 days)
  - Delete files manually
  - Add file records

### Setup & Utility Files
- **setup_folders.py** - Auto-create 50+ Poli folders on Google Drive
  - Initialize Google Drive service
  - Create folders for each Poli
  - Update config.py with folder IDs
  - Shows progress & results

- **quick_setup.py** - Interactive setup wizard
  - Ask for BOT_TOKEN
  - Ask for PARENT_FOLDER_ID
  - Verify credentials.json
  - Update config.py automatically

- **test_setup.py** - Verify configuration & Google Drive access
  - Check all required files exist
  - Check config.py settings
  - Check credentials.json valid
  - Check dependencies installed
  - Test Google Drive connection

### Configuration Files
- **requirements.txt** - Python dependencies
  - python-telegram-bot==20.7
  - Pillow==10.1.0
  - google-api-python-client==1.12.1
  - APScheduler==3.10.4
  - pdf2image==1.16.3

- **credentials.json** - Google Service Account key
  - ⚠️ SECRET FILE - Don't share!
  - Download from Google Cloud Console
  - Add to .gitignore automatically

- **.env.example** - Environment variables template
  - Example for using .env file (optional)
  - Copy to .env and configure

- **docker-compose.yml** - Docker Compose configuration
  - Deploy bot in Docker container
  - Volume mapping for persistence
  - Auto-restart on failure

- **Dockerfile** - Docker image definition
  - Python 3.10 slim base image
  - Install system & Python dependencies
  - Set up working directory

- **.gitignore** - Git ignore patterns
  - Ignore credentials.json
  - Ignore temporary files
  - Ignore Python cache

### Documentation Files
- **QUICKSTART.md** ⭐ START HERE
  - 5-minute setup guide
  - TL;DR quick reference
  - Troubleshooting quick links
  - Common commands

- **SETUP.md** - Detailed setup guide
  - Step-by-step Google Cloud setup
  - Service Account creation
  - Bot token configuration
  - Folder sharing & auto-creation
  - Deployment instructions
  - Production setup with systemd
  - Troubleshooting guide

- **README.md** - Full documentation
  - Features overview
  - Prerequisites
  - Quick start
  - File structure
  - Usage instructions
  - Deployment options
  - Tech stack
  - Security notes

### Data Files
- **files_db.json** - File records database
  - JSON format (no external DB)
  - Store: file_id, file_name, upload_date, delete_date
  - Auto-managed by auto_delete.py
  - Auto-backed up in .gitignore

### Directories
- **temp/** - Temporary files directory
  - Auto-created if not exists
  - Stores downloaded photos temporarily
  - Stores PDF before upload
  - Auto-cleaned up after upload

---

## 🚀 Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Interactive setup (recommended)
python quick_setup.py

# 3. OR manual setup + auto-create folders
# - Edit config.py (BOT_TOKEN, PARENT_FOLDER_ID)
# - Upload credentials.json
# - Run:
python setup_folders.py

# 4. Test configuration
python test_setup.py

# 5. Run bot
python bot.py
```

---

## 📊 File Dependencies

```
bot.py
├── config.py                 (settings)
├── drive_service.py          (Google Drive)
├── auto_delete.py            (auto-delete logic)
└── telegram.ext (library)

drive_service.py
├── config.py                 (CREDENTIALS_FILE)
└── google.api-python-client (library)

auto_delete.py
├── config.py                 (DB_FILE, AUTO_DELETE_DAYS)
└── drive_service.py          (delete files)

setup_folders.py
├── config.py                 (PARENT_FOLDER_ID, POLI_FOLDERS)
└── drive_service.py          (create folders)

test_setup.py
├── config.py                 (verify config)
├── drive_service.py          (test connection)
└── credentials.json          (validate)
```

---

## 📈 How It Works

### Flow Diagram
```
User Opens Bot
    ↓
[/start command]
    ↓
[Show Poli Selection] (pagination: 8 per page)
    ↓
[User Select Poli]
    ↓
[Show "Send Photos" message]
    ↓
[User Send Photos] (1 or more)
    ↓
[Validate & Save Temp] (max 20MB each)
    ↓
[User Click "Selesai & Buat PDF"]
    ↓
[Convert Photos to PDF] (Pillow)
    ↓
[Upload to Google Drive] (Service Account)
    ↓
[Save Record to files_db.json]
    ↓
[Delete Temp Files]
    ↓
[Show Success Message]
    ↓
[Scheduler: Check Expired Files Every 1 Hour]
    ↓
[Auto-Delete Files > 5 Days]
```

---

## 🔐 Security Features

- ✅ Service Account (no user login needed)
- ✅ Isolated folders per Poli (no cross-access)
- ✅ credentials.json in .gitignore
- ✅ Temp files auto-deleted after upload
- ✅ File records stored locally (JSON)
- ✅ No external database required
- ✅ No user data stored permanently

---

## ⚙️ Configuration Summary

### Essential (Must Configure)
| Setting | Where | Default |
|---------|-------|---------|
| BOT_TOKEN | config.py | "YOUR_TOKEN" |
| PARENT_FOLDER_ID | config.py | "1LFh3zSj3rOLTIJwIMqT3wBLDB-OJm7HF" |
| credentials.json | root folder | - |

### Optional (Can Keep Default)
| Setting | Where | Default |
|---------|-------|---------|
| AUTO_DELETE_DAYS | config.py | 5 |
| MAX_PHOTO_MB | config.py | 20 |
| POLI_FOLDERS | config.py | Auto-fill by setup_folders.py |

---

## 📱 Supported Poli (50+)

Anak, Anestesi, Bedah Anak, Bedah Digestif, Bedah Mulut, Bedah Plastik, Bedah Saraf, Bedah Thorax & Kardiovaskular, Bedah Umum, Bedah Vaskuler, Eksekutif Anak, Eksekutif Bedah Mulut, Eksekutif Bedah Plastik, Eksekutif Bedah Umum, Eksekutif Jantung & Pembuluh Darah, Eksekutif Jiwa, Eksekutif Kecantikan, Eksekutif Kulit dan Kelamin, Eksekutif Orthopaedi, Eksekutif Paru, Eksekutif Penyakit Dalam, Eksekutif Saraf, Eksekutif THT, Fetomaternal, Fisioterapi, Forensik, Gigi, Gigi Endodonsi / Konservasi Gigi, Hemodialisa, IGD, Jantung & Pembuluh Darah, Kebidanan & Kandungan, Kebidanan & Kandungan Eksekutif, Kesehatan Jiwa, Kulit & Kelamin, Kusta, Mata, Medical Checkup, Okupasi, Okupasi Terapi, Onkologi, Orthopedi, Paru, Penyakit Dalam, Prothesa, Psikologi, Rehab Medik, Saraf, Terapi Wicara, Teratai, THT, Umum, Urologi

**Total: 50+ Polis with pagination support**

---

## 🎯 Next Steps

1. **NEW?** → Start with [QUICKSTART.md](QUICKSTART.md) (5 min)
2. **SETUP ISSUES?** → Check [SETUP.md](SETUP.md)
3. **FULL INFO?** → Read [README.md](README.md)
4. **RUNNING BOT?** → Execute: `python bot.py`

---

## 📞 Support

- **Quick help?** → QUICKSTART.md troubleshooting
- **Setup stuck?** → SETUP.md has step-by-step guide
- **Config issues?** → Run: `python test_setup.py`
- **Code questions?** → Read inline comments in .py files

---

**All set? Run: `python bot.py` 🚀**
