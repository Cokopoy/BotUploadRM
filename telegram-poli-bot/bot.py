import logging
import os
import json
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageEnhance
import sqlite3
import config
from io import BytesIO

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from telegram.request import HTTPXRequest

# Logging setup - kurangi verbosity
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING  # Ubah dari INFO ke WARNING
)
logger = logging.getLogger(__name__)

# Disable verbose logging dari telegram library
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('apscheduler').setLevel(logging.WARNING)

# States for conversation
SELECTING_POLI, SENDING_PHOTOS, CONFIRM_PDF, VIEWING_FILES, SELECTING_FILE, ENTERING_PASSWORD, ENTERING_LOGIN_PASSWORD = range(7)

# User data storage
user_sessions = {}


class FileManager:
    def __init__(self, db_path="file_storage.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Cek apakah tabel sudah ada
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Cek apakah kolom username ada
            cursor.execute("PRAGMA table_info(files)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'username' not in columns:
                # Migrasi: tambah kolom username
                try:
                    cursor.execute('ALTER TABLE files ADD COLUMN username TEXT')
                    cursor.execute('ALTER TABLE files ADD COLUMN file_path TEXT')
                    conn.commit()
                    logger.info("Database migrated: Added username and file_path columns")
                except Exception as e:
                    logger.warning(f"Migration error: {str(e)}")
        else:
            # Buat tabel baru
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    poli_name TEXT,
                    file_name TEXT,
                    file_path TEXT,
                    upload_date TIMESTAMP,
                    file_type TEXT
                )
            ''')
            conn.commit()
            logger.info("Database created: New files table")
        
        conn.close()
    
    def add_file_record(self, user_id, username, poli_name, file_name, file_path, file_type='pdf'):
        """Add file record to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO files (user_id, username, poli_name, file_name, file_path, upload_date, file_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, poli_name, file_name, file_path, datetime.now(), file_type))
        conn.commit()
        conn.close()
    
    def get_files_by_poli(self, poli_name):
        """Get all files for a specific poli"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, file_name, file_path, upload_date FROM files
            WHERE poli_name = ?
            ORDER BY upload_date DESC
        ''', (poli_name,))
        files = cursor.fetchall()
        conn.close()
        return files
    
    def get_file_by_id(self, file_id):
        """Get file info by database id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT file_name, file_path FROM files WHERE id = ?', (file_id,))
        result = cursor.fetchone()
        conn.close()
        return result


class PDFGenerator:
    """Generate PDF from images"""
    
    @staticmethod
    def apply_scan_effect(image):
        """Apply scan effect to image (color or grayscale)"""
        try:
            # Convert to RGB jika perlu
            if image.mode == 'RGBA':
                rgb_img = Image.new('RGB', image.size, (255, 255, 255))
                rgb_img.paste(image, mask=image.split()[3])
                image = rgb_img
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Cek apakah scan effect enabled
            if not config.SCAN_EFFECT['enabled']:
                return image
            
            # Increase contrast (membuat warna/garis lebih tegas)
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(config.SCAN_EFFECT['contrast'])
            
            # Increase brightness sedikit (menghilangkan shadow)
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(config.SCAN_EFFECT['brightness'])
            
            # Sharpness (untuk ketajaman scan)
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(config.SCAN_EFFECT['sharpness'])
            
            # Convert ke grayscale hanya jika enabled
            if config.SCAN_EFFECT['grayscale']:
                image = image.convert('L').convert('RGB')
            
            return image
            
        except Exception as e:
            logger.error(f"Error applying scan effect: {str(e)}")
            return image
    
    @staticmethod
    def images_to_pdf(image_paths, output_path):
        """Convert multiple images to PDF using PIL"""
        try:
            if not image_paths:
                return False
            
            images = []
            
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    logger.error(f"Image file not found: {img_path}")
                    continue
                
                try:
                    img = Image.open(img_path)
                    
                    # Convert RGBA to RGB
                    if img.mode == 'RGBA':
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        rgb_img.paste(img, mask=img.split()[3])
                        img = rgb_img
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Resize untuk konsistensi (A4 size)
                    max_width = 1654
                    max_height = 2339
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    
                    # ⭐ Apply scan effect (warna atau grayscale sesuai config)
                    img = PDFGenerator.apply_scan_effect(img)
                    
                    images.append(img)
                    
                except Exception as e:
                    logger.error(f"Error processing image {img_path}: {str(e)}")
                    continue
            
            if not images:
                logger.error("No valid images to convert")
                return False
            
            # Simpan sebagai PDF
            try:
                # Pastikan semua image dalam RGB mode
                images = [img.convert('RGB') for img in images]
                
                if len(images) == 1:
                    images[0].save(output_path, 'PDF')
                else:
                    images[0].save(
                        output_path,
                        'PDF',
                        save_all=True,
                        append_images=images[1:]
                    )
                
                logger.info(f"PDF created successfully: {output_path}")
                return True
                
            except Exception as e:
                logger.error(f"Error saving PDF: {str(e)}")
                return False
        
        except Exception as e:
            logger.error(f"Error in images_to_pdf: {str(e)}")
            return False


class BotManager:
    def __init__(self):
        self.file_manager = FileManager()
        self.pdf_generator = PDFGenerator()
        self.poli_list = sorted(list(config.POLI_FOLDERS.keys()))

    def initialize_user_session(self, user_id):
        """Initialize user session"""
        if user_id not in user_sessions:
            user_sessions[user_id] = {
                'poli': None,
                'pdf_files': [],
                'temp_photo_paths': [],
                'poli_page': 0,
                'view_poli': None,
                'file_caption': None
            }

    def get_user_folder_path(self, poli_name, user_id, username):
        """Get folder path: dokumen/Poli/YYYY-MM-DD/"""
        date_folder = datetime.now().strftime('%Y-%m-%d')
        user_folder = f"{config.DOKUMEN_PATH}/{poli_name}/{date_folder}"
        return user_folder

    def get_poli_keyboard(self, page=0):
        """Create inline keyboard for Poli selection with pagination"""
        items_per_page = 8
        total_pages = (len(self.poli_list) + items_per_page - 1) // items_per_page
        
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(self.poli_list))
        
        keyboard = []
        
        # Add poli buttons (2 per row)
        for i in range(start_idx, end_idx, 2):
            row = []
            poli_1 = self.poli_list[i]
            row.append(InlineKeyboardButton(
                poli_1,
                callback_data=f"poli_{i}"
            ))
            
            if i + 1 < end_idx:
                poli_2 = self.poli_list[i + 1]
                row.append(InlineKeyboardButton(
                    poli_2,
                    callback_data=f"poli_{i + 1}"
                ))
            
            keyboard.append(row)
        
        # Add pagination buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Sebelumnya", callback_data=f"page_{page - 1}"))
        
        nav_buttons.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="page_info"))
        
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Selanjutnya ➡️", callback_data=f"page_{page + 1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        return InlineKeyboardMarkup(keyboard)

    def get_view_poli_keyboard(self, poli_name):
        """Create keyboard for viewing files in a poli"""
        files = self.file_manager.get_files_by_poli(poli_name)
        
        keyboard = []
        for file_id, file_name, file_path, upload_date in files:
            keyboard.append([InlineKeyboardButton(
                f"📄 {file_name[:30]}",
                callback_data=f"download_{file_id}"
            )])
        
        keyboard.append([InlineKeyboardButton("⬅️ Kembali", callback_data="back_menu")])
        return InlineKeyboardMarkup(keyboard)

    def get_confirmation_keyboard(self):
        """Create inline keyboard for PDF confirmation"""
        keyboard = [
            [InlineKeyboardButton("✅ Selesai & Buat PDF", callback_data="create_pdf")],
            [InlineKeyboardButton("❌ Batal", callback_data="cancel")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def get_main_menu_keyboard(self):
        """Create main menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("📤 Upload Dokumen", callback_data="upload_doc")],
            [InlineKeyboardButton("📥 Lihat File", callback_data="view_files")]
        ]
        return InlineKeyboardMarkup(keyboard)

# Password untuk view files
VIEW_PASSWORD = "RMSsitanala1951"
LOGIN_PASSWORD = "RMSitanala1951"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start command - Show main menu"""
    user_id = update.effective_user.id
    
    # ⭐ Minta password login terlebih dahulu
    await update.message.reply_text(
        "🔐 Bot Penyimpanan Dokumen Rekam Medis\n\n"
        "Silakan masukkan password untuk melanjutkan:\n\n"
        "Ketik password Anda:"
    )
    
    return ENTERING_LOGIN_PASSWORD


async def login_password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle password input for login"""
    user_id = update.effective_user.id
    password_input = update.message.text.strip()
    
    # ⭐ Verifikasi password login
    if password_input == LOGIN_PASSWORD:
        # Password benar - initialize session dan tampilkan menu
        bot_manager.initialize_user_session(user_id)
        
        await update.message.reply_text(
            "🏥 Selamat datang di Bot Penyimpanan Dokumen Rekam Medis Rawat Jalan RSUP Dr Sitanala Tangerang!\n\n"
            "Pilih menu yang Anda inginkan:",
            reply_markup=bot_manager.get_main_menu_keyboard()
        )
        return SELECTING_POLI
    else:
        # Password salah
        await update.message.reply_text(
            "❌ Password salah!\n\n"
            "Silakan coba lagi atau gunakan /start untuk memulai ulang"
        )
        return ENTERING_LOGIN_PASSWORD


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle main menu selection"""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    if query.data == "upload_doc":
        await query.edit_message_text(
            "🏥 RSUP Dr Sitanala Tangerang\n\n"
            "Silakan pilih Poli untuk upload dokumen rekam medis:",
            reply_markup=bot_manager.get_poli_keyboard()
        )
        return SELECTING_POLI
    
    elif query.data == "view_files":
        # ⭐ Minta password sebelum view files
        await query.edit_message_text(
            "🔐 Akses Terbatas\n\n"
            "Silakan masukkan password untuk mengakses file:\n\n"
            "Ketik password Anda:"
        )
        return ENTERING_PASSWORD
    
    return SELECTING_POLI


async def password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle password input for view files"""
    user_id = update.effective_user.id
    password_input = update.message.text.strip()
    
    # ⭐ Verifikasi password
    if password_input == VIEW_PASSWORD:
        # Password benar - tampilkan daftar poli
        await update.message.reply_text(
            "🏥 RSUP Dr Sitanala Tangerang\n\n"
            "✅ Password benar! Silakan pilih Poli untuk melihat file:",
            reply_markup=bot_manager.get_poli_keyboard()
        )
        return VIEWING_FILES
    else:
        # Password salah
        await update.message.reply_text(
            "❌ Password salah!\n\n"
            "Silakan coba lagi atau gunakan /start untuk kembali ke menu"
        )
        return ENTERING_PASSWORD


async def poli_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle Poli selection for upload"""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    # Handle pagination
    if query.data.startswith("page_"):
        page_num = int(query.data.split("_")[1])
        user_sessions[user_id]['poli_page'] = page_num
        await query.edit_message_text(
            "🏥 Silakan pilih Poli untuk upload dokumen:",
            reply_markup=bot_manager.get_poli_keyboard(page_num)
        )
        return SELECTING_POLI
    
    # Handle poli selection
    if query.data.startswith("poli_"):
        poli_index = int(query.data.split("_")[1])
        poli_name = bot_manager.poli_list[poli_index]
        
        user_sessions[user_id]['poli'] = poli_name
        
        await query.edit_message_text(
            f"✅ Anda memilih: {poli_name}\n\n"
            "Sekarang silakan kirim foto dokumen. Anda bisa mengirim 1 atau lebih foto.\n"
            "💡 Tips: Tambahkan caption pada foto pertama untuk memberi nama file\n"
            "Foto akan digabungkan menjadi 1 file PDF."
        )
        
        return SENDING_PHOTOS
    
    await query.edit_message_text("❌ Pilihan tidak valid")
    return SELECTING_POLI


async def poli_selected_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle Poli selection for viewing files"""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    # Handle pagination
    if query.data.startswith("page_"):
        page_num = int(query.data.split("_")[1])
        user_sessions[user_id]['poli_page'] = page_num
        await query.edit_message_text(
            "📁 Silakan pilih Poli untuk melihat file:",
            reply_markup=bot_manager.get_poli_keyboard(page_num)
        )
        return VIEWING_FILES
    
    # Handle poli selection
    if query.data.startswith("poli_"):
        poli_index = int(query.data.split("_")[1])
        poli_name = bot_manager.poli_list[poli_index]
        
        user_sessions[user_id]['view_poli'] = poli_name
        
        files = bot_manager.file_manager.get_files_by_poli(poli_name)
        if not files:
            await query.edit_message_text(
                f"📁 Folder {poli_name}\n\n"
                "❌ Belum ada file di folder ini",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="back_menu")]])
            )
        else:
            await query.edit_message_text(
                f"📁 File di folder {poli_name}:\n",
                reply_markup=bot_manager.get_view_poli_keyboard(poli_name)
            )
        
        return SELECTING_FILE
    
    return VIEWING_FILES


async def photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle photo uploads"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions or not user_sessions[user_id]['poli']:
        await update.message.reply_text(
            "❌ Silakan pilih Poli terlebih dahulu dengan /start"
        )
        return SELECTING_POLI
    
    photo_file = update.message.photo[-1]
    file_size_mb = photo_file.file_size / (1024 * 1024)
    
    if file_size_mb > config.MAX_PHOTO_MB:
        await update.message.reply_text(
            f"❌ Foto terlalu besar ({file_size_mb:.2f}MB). "
            f"Maksimal {config.MAX_PHOTO_MB}MB"
        )
        return SENDING_PHOTOS
    
    try:
        # Cek apakah ada caption di foto pertama
        if len(user_sessions[user_id]['pdf_files']) == 0 and update.message.caption:
            user_sessions[user_id]['file_caption'] = update.message.caption.strip()
        
        # Buat temp folder
        os.makedirs(config.TEMP_DIR, exist_ok=True)
        
        # Download foto ke temp
        file = await context.bot.get_file(photo_file.file_id)
        temp_photo_path = f"{config.TEMP_DIR}/photo_{user_id}_{len(user_sessions[user_id]['pdf_files'])}.jpg"
        await file.download_to_drive(temp_photo_path)
        
        user_sessions[user_id]['pdf_files'].append(photo_file.file_id)
        user_sessions[user_id]['temp_photo_paths'].append(temp_photo_path)
        
        photo_count = len(user_sessions[user_id]['pdf_files'])
        await update.message.reply_text(
            f"✅ Foto {photo_count} diterima\n\n"
            "Kirim foto lagi atau klik 'Selesai & Buat PDF'",
            reply_markup=bot_manager.get_confirmation_keyboard()
        )
        
        return SENDING_PHOTOS
    
    except Exception as e:
        logger.error(f"Error handling photo: {str(e)}")
        await update.message.reply_text("❌ Gagal memproses foto. Coba lagi.")
        return SENDING_PHOTOS


async def create_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Create PDF and save to local folder"""
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or f"user_{user_id}"
    
    await query.answer()
    
    if user_id not in user_sessions:
        await query.edit_message_text("❌ Session expired. Gunakan /start untuk memulai ulang")
        return SELECTING_POLI
    
    session = user_sessions[user_id]
    
    if not session['pdf_files']:
        await query.edit_message_text("❌ Tidak ada foto yang dikirim")
        return SENDING_PHOTOS
    
    await query.edit_message_text("⏳ Membuat PDF... Mohon tunggu...")
    
    try:
        poli_name = session['poli']
        
        # Gunakan caption sebagai nama file jika ada, jika tidak gunakan "Dokumen"
        file_prefix = session['file_caption'] if session['file_caption'] else "Dokumen"
        pdf_filename = f"{file_prefix}_{poli_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Buat folder untuk user dengan struktur hierarki
        user_folder = bot_manager.get_user_folder_path(poli_name, user_id, username)
        os.makedirs(user_folder, exist_ok=True)
        
        # Buat PDF
        pdf_path = f"{user_folder}/{pdf_filename}.pdf"
        
        if bot_manager.pdf_generator.images_to_pdf(session['temp_photo_paths'], pdf_path):
            # Simpan referensi ke database
            bot_manager.file_manager.add_file_record(
                user_id, 
                username, 
                poli_name, 
                pdf_filename, 
                pdf_path, 
                'pdf'
            )
            
            # Hapus temp files
            for temp_path in session['temp_photo_paths']:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
            
            # Buat keyboard untuk opsi lanjutan
            keyboard = [
                [InlineKeyboardButton("📤 Upload Lagi (Poli Sama)", callback_data="upload_again")],
                [InlineKeyboardButton("🏠 Kembali ke Menu", callback_data="back_to_menu")]
            ]
            
            # Reset session tapi simpan poli
            user_sessions[user_id] = {
                'poli': poli_name,
                'pdf_files': [],
                'temp_photo_paths': [],
                'poli_page': 0,
                'view_poli': None,
                'file_caption': None
            }
            
            await query.edit_message_text(
                f"✅ PDF berhasil dibuat!\n\n"
                f"📄 Nama file: {pdf_filename}.pdf\n"
                f"📁 Folder: {poli_name}\n"
                f"📸 Halaman: {len(session['pdf_files'])}\n"
                f"💾 Lokasi: {user_folder}\n\n"
                "Apa yang ingin Anda lakukan?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text("❌ Gagal membuat PDF")
            return SENDING_PHOTOS
        
        return SENDING_PHOTOS
    
    except Exception as e:
        logger.error(f"Error in create_pdf: {str(e)}")
        await query.edit_message_text(f"❌ Error: {str(e)}")
        return SENDING_PHOTOS


async def upload_again(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle upload lagi - upload ke poli yang sama"""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    if query.data == "upload_again":
        if user_id in user_sessions and user_sessions[user_id]['poli']:
            poli_name = user_sessions[user_id]['poli']
            
            # Reset file list tapi keep poli
            user_sessions[user_id]['pdf_files'] = []
            user_sessions[user_id]['temp_photo_paths'] = []
            user_sessions[user_id]['file_caption'] = None
            
            await query.edit_message_text(
                f"✅ Siap upload ke: {poli_name}\n\n"
                "Silakan kirim foto dokumen rekam medis. Anda bisa mengirim 1 atau lebih foto.\n"
                "💡 Tips: Tambahkan caption pada foto pertama untuk memberi nama file\n"
                "Foto akan digabungkan menjadi 1 file PDF."
            )
            
            return SENDING_PHOTOS
        else:
            await query.edit_message_text(
                "❌ Poli tidak ditemukan. Gunakan /start untuk memulai dari awal"
            )
            return SELECTING_POLI
    
    elif query.data == "back_to_menu":
        user_sessions[user_id] = {
            'poli': None,
            'pdf_files': [],
            'temp_photo_paths': [],
            'poli_page': 0,
            'view_poli': None,
            'file_caption': None
        }
        
        await query.edit_message_text(
            "🏥 Selamat datang di Bot Penyimpanan Dokumen Rekam Medis Rawat Jalan RSUP Dr Sitanala Tangerang!\n\n"
            "Pilih menu yang Anda inginkan:",
            reply_markup=bot_manager.get_main_menu_keyboard()
        )
        return SELECTING_POLI
    
    return SENDING_PHOTOS


async def poli_selected_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle Poli selection for viewing files"""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    # Handle pagination
    if query.data.startswith("page_"):
        page_num = int(query.data.split("_")[1])
        user_sessions[user_id]['poli_page'] = page_num
        await query.edit_message_text(
            "📁 Silakan pilih Poli untuk melihat file:",
            reply_markup=bot_manager.get_poli_keyboard(page_num)
        )
        return VIEWING_FILES
    
    # Handle poli selection
    if query.data.startswith("poli_"):
        poli_index = int(query.data.split("_")[1])
        poli_name = bot_manager.poli_list[poli_index]
        
        user_sessions[user_id]['view_poli'] = poli_name
        
        files = bot_manager.file_manager.get_files_by_poli(poli_name)
        if not files:
            await query.edit_message_text(
                f"📁 Folder {poli_name}\n\n"
                "❌ Belum ada file di folder ini",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="back_menu")]])
            )
        else:
            await query.edit_message_text(
                f"📁 File di folder {poli_name}:\n",
                reply_markup=bot_manager.get_view_poli_keyboard(poli_name)
            )
        
        return SELECTING_FILE
    
    return VIEWING_FILES


async def download_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle file download"""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    if query.data.startswith("download_"):
        file_db_id = int(query.data.split("_")[1])
        file_info = bot_manager.file_manager.get_file_by_id(file_db_id)
        
        if not file_info:
            await query.edit_message_text("❌ File tidak ditemukan")
            return SELECTING_FILE
        
        file_name, file_path = file_info
        
        try:
            if os.path.exists(file_path):
                await context.bot.send_document(
                    chat_id=query.from_user.id,
                    document=open(file_path, 'rb'),
                    filename=f"{file_name}.pdf"
                )
                await query.answer("✅ File dikirim via DM", show_alert=True)
            else:
                await query.answer("❌ File tidak ditemukan di server", show_alert=True)
                
                
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            await query.answer("❌ Gagal mengirim file", show_alert=True)
    
    elif query.data == "back_menu":
        await query.edit_message_text(
            "🏥 Selamat datang di Bot Penyimpanan Dokumen Rekam Medis Rawat Jalan RSUP Dr Sitanala Tangerang!\n\n"
            "Pilih menu yang Anda inginkan:",
            reply_markup=bot_manager.get_main_menu_keyboard()
        )
        return SELECTING_POLI
    
    return SELECTING_FILE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel operation"""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    if user_id in user_sessions:
        # Hapus temp files
        for temp_path in user_sessions[user_id]['temp_photo_paths']:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass
        
        user_sessions[user_id] = {
            'poli': None,
            'pdf_files': [],
            'temp_photo_paths': [],
            'poli_page': 0,
            'view_poli': None
        }
    
    await query.edit_message_text(
        "❌ Dibatalkan\n\n"
        "Pilih menu yang Anda inginkan:",
        reply_markup=bot_manager.get_main_menu_keyboard()
    )
    return SELECTING_POLI


def main():
    """Start the bot"""
    global bot_manager
    bot_manager = BotManager()
    
    # Create request object dengan timeout config
    request = HTTPXRequest(
        connect_timeout=10,
        read_timeout=15,
        write_timeout=15,
        pool_timeout=10
    )
    
    # Create application dengan request config
    app = Application.builder().token(config.BOT_TOKEN).request(request).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ENTERING_LOGIN_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, login_password_handler)
            ],
            SELECTING_POLI: [
                CallbackQueryHandler(menu_handler, pattern="^upload_doc$|^view_files$"),
                CallbackQueryHandler(poli_selected, pattern="^poli_|^page_")
            ],
            SENDING_PHOTOS: [
                MessageHandler(filters.PHOTO, photo_received),
                CallbackQueryHandler(create_pdf, pattern="^create_pdf$"),
                CallbackQueryHandler(upload_again, pattern="^upload_again$|^back_to_menu$"),
                CallbackQueryHandler(cancel, pattern="^cancel$")
            ],
            ENTERING_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, password_handler)
            ],
            VIEWING_FILES: [
                CallbackQueryHandler(poli_selected_view, pattern="^poli_|^page_"),
                CallbackQueryHandler(download_file, pattern="^download_|^back_menu$")
            ],
            SELECTING_FILE: [
                CallbackQueryHandler(download_file, pattern="^download_|^back_menu$")
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False
    )
    
    app.add_handler(conv_handler)
    
    logger.info("Bot started successfully")
    
    # Jalankan dengan error handling
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Error running bot: {str(e)}")
        import time
        logger.info("Retrying in 10 seconds...")
        time.sleep(10)
        main()  # Recursive restart

if __name__ == "__main__":
    main()
