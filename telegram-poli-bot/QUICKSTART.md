# 🚀 GETTING STARTED - Quickstart Guide

## TL;DR - Setup dalam 5 Menit

### 1. Persiapan (1 menit)
```bash
# Buka folder project
cd telegram-poli-bot

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Bot Token (1 menit)
1. Buka Telegram, cari `@BotFather`
2. Ketik `/newbot`
3. Ikuti instruksi dan copy token
4. Edit `config.py`:
   ```python
   BOT_TOKEN = "YOUR_TOKEN_HERE"  # Ganti dengan token dari BotFather
   ```

### 3. Setup Google Drive (3 menit)

**A. Download credentials.json:**
1. Go to: https://console.cloud.google.com/
2. Create project: `TelegramPoliBot`
3. Enable: `Google Drive API`
4. Create: `Service Account`
5. Generate: `JSON Key`
6. Download → Save as `credentials.json` di folder project

**B. Share folder ke Service Account:**
1. Buka Google Drive folder: https://drive.google.com/drive/folders/1LFh3zSj3rOLTIJwIMqT3wBLDB-OJm7HF
2. Klik "Share"
3. Copy email dari `credentials.json` (field: `client_email`)
4. Paste email di "Share with"
5. Click "Share"

**C. Create Poli folders (Auto!):**
```bash
python setup_folders.py
```

### 4. Test Bot (saat itu juga)
```bash
python test_setup.py
```

Jika semua ✅, lanjut ke step 5.

### 5. Jalankan Bot 🎉
```bash
python bot.py
```

Buka Telegram → Cari bot Anda → Klik `/start`

---

## Struktur File

```
telegram-poli-bot/
├── config.py               ← Edit BOT_TOKEN di sini
├── credentials.json        ← Upload dari Google Cloud
├── bot.py                  ← Main bot
├── setup_folders.py        ← Jalankan untuk create folders
├── test_setup.py           ← Test konfigurasi
├── quick_setup.py          ← Interactive wizard (optional)
├── requirements.txt        ← Dependencies
├── SETUP.md               ← Detailed setup guide
├── README.md              ← Full documentation
└── temp/                  ← Auto-created untuk temp files
```

---

## Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| Bot tidak merespons | 1. Cek BOT_TOKEN di config.py<br>2. Run: `python test_setup.py`<br>3. Restart bot |
| credentials.json not found | Download dari Google Cloud Console & simpan di folder root |
| Folder not found error | Share parent folder ke Service Account email |
| Upload fails | Pastikan internet connection stabil |
| Auto-delete tidak jalan | Bot harus tetap running 24/7 |

---

## Interactive Setup (Optional)

Prefer wizard? Jalankan:
```bash
python quick_setup.py
```

Akan guide Anda step-by-step.

---

## Testing Everything

Sebelum jalankan bot, test konfigurasi:
```bash
python test_setup.py
```

Output:
- ✅ PASS = OK
- ❌ FAIL = Fix issue sebelum jalan bot

---

## Next Steps

✅ Bot berhasil jalan?

1. **Share bot ke orang lain:**
   Copy username bot Anda di Telegram

2. **Deploy ke VPS (24/7):**
   Lihat section "Production Deployment" di SETUP.md

3. **Custom Poli atau Folders:**
   Edit `config.py` - no restart needed untuk custom folders

4. **Check Google Drive:**
   Lihat di parent folder → setiap upload PDF masuk ke folder Poli

---

## Quick Commands

```bash
# Run bot
python bot.py

# Test setup
python test_setup.py

# Create folders auto
python setup_folders.py

# Interactive setup
python quick_setup.py

# Install deps
pip install -r requirements.txt

# Uninstall all
pip uninstall -y -r requirements.txt
```

---

## File Sizes & Space

- Bot script: ~20KB
- Temporary files: ~variable (auto-deleted)
- Database (files_db.json): ~1KB per 1000 files
- Credentials: ~2KB
- **Total**: ~1MB disk space needed

---

## Security Checklist

- ✅ DON'T push credentials.json to GitHub
- ✅ DON'T share BOT_TOKEN
- ✅ DO use .gitignore (included)
- ✅ DO rotate credentials periodically
- ✅ DO keep bot running on secure server

---

## Need Help?

1. **Quick issues?** → Check Troubleshooting table above
2. **Detailed setup?** → Read `SETUP.md`
3. **Full docs?** → Read `README.md`
4. **Code issues?** → Check `test_setup.py` output

---

**Ready? Run: `python bot.py` 🚀**
