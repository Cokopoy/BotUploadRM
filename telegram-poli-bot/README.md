# Bot Upload Dokumen Telegram - Poli

Bot Telegram untuk menerima foto dokumen, mengubahnya menjadi PDF, dan mengunggah ke Google Drive dengan fitur auto-delete setelah 5 hari.

## Fitur

✅ 50+ pilihan Poli (dengan pagination)
✅ Upload foto dokumen (single atau multiple)
✅ Konversi foto ke PDF otomatis
✅ Upload ke Google Drive
✅ Auto-delete file setelah 5 hari
✅ Support hingga 30 user bersamaan
✅ Gratis - tidak perlu database eksternal
✅ Production-ready
✅ Auto-create all Poli folders di Google Drive

## Prerequisites

- Python 3.8+
- Telegram Bot Token (dari BotFather)
- Google Service Account JSON
- Google Drive API enabled

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Google Cloud & Service Account
Ikuti **SETUP.md** step 1-2

### 3. Auto-Create All Poli Folders
```bash
python setup_folders.py
```

Script ini akan:
- ✅ Membuat 50+ folder untuk setiap Poli
- ✅ Auto-update config.py dengan Folder ID

### 4. Run Bot
```bash
python bot.py
```

## Struktur Project

```
telegram-poli-bot/
├── bot.py                   # Main bot logic
├── config.py                # Configuration
├── drive_service.py         # Google Drive API wrapper
├── auto_delete.py           # File auto-delete logic
├── setup_folders.py         # Auto-create folders script
├── files_db.json            # File records (auto-created)
├── requirements.txt         # Dependencies
├── credentials.json         # Google Service Account (secret!)
├── README.md                # Dokumentasi singkat
├── SETUP.md                 # Setup guide lengkap
├── .gitignore              # Git config
└── temp/                    # Temporary files (auto-created)
```

## Fitur Bot

### 1. Memilih Poli
- User membuka bot dengan /start
- Tampilkan inline keyboard 50+ Poli (dengan pagination)
- User pilih 1 Poli
- Bot konfirmasi pilihan

### 2. Upload Foto
- User kirim 1 atau lebih foto
- Bot validasi ukuran (max 20MB per foto)
- Bot tampilkan jumlah foto diterima
- User bisa kirim foto lagi atau klik "Selesai & Buat PDF"

### 3. Konversi & Upload
- Bot konversi semua foto ke 1 PDF
- PDF diupload ke Google Drive (folder sesuai Poli)
- File lokal dihapus
- Metadata disimpan (file_id + tanggal upload)

### 4. Auto-Delete
- Job scheduler otomatis cek file > 5 hari
- File Google Drive dihapus otomatis
- Database di-update
- User bisa manual delete juga

## Konfigurasi

Edit **config.py**:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Token dari BotFather
PARENT_FOLDER_ID = "..."      # Parent folder Google Drive ID
AUTO_DELETE_DAYS = 5          # Delete file setelah 5 hari
MAX_PHOTO_MB = 20             # Max size per foto
```

Setelah setup_folders.py, file berikut auto-update:
```python
POLI_FOLDERS = {
    "Anak": "folder_id_xxx",
    "Anestesi": "folder_id_yyy",
    # ... dll (auto-update dari script)
}
```

## Penggunaan di Telegram

1. Cari bot di Telegram: `@username_bot_anda`
2. Klik START
3. Pilih Poli dari list (gunakan Sebelumnya/Selanjutnya untuk navigasi)
4. Kirim foto dokumen (1 atau lebih)
5. Klik "✅ Selesai & Buat PDF"
6. PDF akan diupload ke Google Drive
7. Cek di Google Drive folder Poli Anda

## Deployment Production

### Docker (Recommended)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

### VPS Linux (Ubuntu/Debian)
```bash
sudo apt-get install python3 python3-pip
git clone <repo>
cd telegram-poli-bot
pip install -r requirements.txt
python3 bot.py &  # atau gunakan systemd service
```

Lihat **SETUP.md** untuk detail deployment.

## Troubleshooting

| Error | Solusi |
|-------|--------|
| Bot tidak merespons | Cek BOT_TOKEN di config.py, restart bot |
| Credentials file not found | Pastikan credentials.json ada di folder root |
| Folder not found | Cek PARENT_FOLDER_ID, cek Service Account share folder |
| PDF upload gagal | Cek internet connection, cek Google Drive API quota |
| Auto-delete tidak jalan | Bot harus tetap running, job check setiap 1 jam |

## Limits & Specs

- **Max concurrent users:** 30
- **Max photo size:** 20MB per foto
- **Max total photos:** unlimited
- **Auto-delete:** 5 hari (configurable)
- **Free tier:** Ya, gratis tanpa biaya
- **Uptime requirement:** 24/7 untuk auto-delete

## Tech Stack

- **Bot Framework:** python-telegram-bot v20+
- **Image Processing:** Pillow
- **Google Drive API:** google-api-python-client
- **Scheduler:** APScheduler
- **Database:** JSON file (no external DB needed)

## Security Notes

- 🔒 **JANGAN push credentials.json ke GitHub!**
- 🔒 **JANGAN share BOT_TOKEN**
- 🔒 Gunakan .gitignore (sudah included)
- 🔒 Rotate credentials secara berkala
- 🔒 Use environment variables untuk secrets (optional)

## License

Free to use and modify

## Support

Untuk help/issues, lihat **SETUP.md** section Troubleshooting
