import os

# Bot Token dari BotFather
BOT_TOKEN = "8506883128:AAFAyyn08CcetczDWgcU4oEvAuLL6vlDH9s"

# Daftar folder Poli - LENGKAP
POLI_FOLDERS = {
    "Anak": "anak",
    "Anestesi": "anestesi",
    "Bedah Anak": "bedah_anak",
    "Bedah Digestiv": "bedah_digestiv",
    "Bedah Mulut": "bedah_mulut",
    "Bedah Plastik": "bedah_plastik",
    "Bedah Saraf": "bedah_saraf",
    "Bedah Thorax & Kardiovaskular": "bedah_thorax",
    "Bedah Umum": "bedah_umum",
    "Bedah Vaskuler": "bedah_vaskuler",
    "Eksekutif Anak": "eks_anak",
    "Eksekutif Bedah Mulut": "eks_bedah_mulut",
    "Eksekutif Bedah Plastik": "eks_bedah_plastik",
    "Eksekutif Bedah Umum": "eks_bedah_umum",
    "Eksekutif Jantung & Pembuluh Darah": "eks_jantung",
    "Eksekutif Jiwa": "eks_jiwa",
    "Eksekutif Kecantikan": "eks_kecantikan",
    "Eksekutif Kulit dan Kelamin": "eks_kulit",
    "Eksekutif Orthopaedi": "eks_ortho",
    "Eksekutif Paru": "eks_paru",
    "Eksekutif Penyakit Dalam": "eks_dalam",
    "Eksekutif Saraf": "eks_saraf",
    "Eksekutif THT": "eks_tht",
    "Fetomaternal": "fetomaternal",
    "Fisioterapi": "fisioterapi",
    "Forensik": "forensik",
    "Gigi": "gigi",
    "Gigi Endodonsi / Konservasi Gigi": "gigi_endo",
    "Hemodialisa": "hemodialisa",
    "IGD": "igd",
    "Jantung & Pembuluh Darah": "jantung",
    "Kebidanan & Kandungan": "kebidanan",
    "Kebidanan & Kandungan Eksekutif": "kebidanan_eks",
    "Kesehatan Jiwa": "jiwa",
    "Kulit & Kelamin": "kulit",
    "Kusta": "kusta",
    "Mata": "mata",
    "Medical Checkup": "medical_checkup",
    "Okupasi": "okupasi",
    "Okupasi Terapi": "okupasi_terapi",
    "Onkologi": "onkologi",
    "Orthopedi": "orthopedi",
    "Paru": "paru",
    "Penyakit Dalam": "dalam",
    "Prothesa": "prothesa",
    "Psikologi": "psikologi",
    "Rehab Medik": "rehab",
    "Saraf": "saraf",
    "Terapi Wicara": "terapi_wicara",
    "Teratai": "teratai",
    "THT": "tht",
    "Umum": "umum",
    "Urologi": "urologi",
}

# Konfigurasi upload
MAX_PHOTO_MB = 20
TEMP_DIR = "./temp"

# ⭐ LOKASI PENYIMPANAN DOKUMEN
DOKUMEN_PATH = r"G:\My Drive\SCAN RAJAL"

# PDF Configuration
PDF_QUALITY = 90
PDF_PAGE_SIZE = (210, 297)

# Auto delete configuration
AUTO_DELETE_DAYS = 30

# Scan Effect Configuration
SCAN_EFFECT = {
    'enabled': True,  # Enable/disable scan effect
    'contrast': 1.8,  # 1.0-2.5 (lebih tinggi = lebih tegas)
    'brightness': 1.1,  # 1.0-1.5 (lebih tinggi = lebih cerah)
    'sharpness': 1.5,  # 1.0-2.0 (lebih tinggi = lebih tajam)
    'grayscale': False  # False = Tetap Warna, True = B&W
}
