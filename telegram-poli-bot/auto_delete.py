import json
import os
from datetime import datetime, timedelta
import config
from drive_service import GoogleDriveService


class FileAutoDelete:
    def __init__(self):
        self.drive = GoogleDriveService()

    def load_database(self):
        """Load files database from JSON"""
        if not os.path.exists(config.DB_FILE):
            return {}
        
        try:
            with open(config.DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_database(self, data):
        """Save files database to JSON"""
        try:
            with open(config.DB_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving database: {str(e)}")

    def add_file_record(self, user_id, file_id, file_name, poli):
        """Add file record to database"""
        db = self.load_database()
        
        if str(user_id) not in db:
            db[str(user_id)] = []
        
        record = {
            'file_id': file_id,
            'file_name': file_name,
            'poli': poli,
            'upload_date': datetime.now().isoformat(),
            'delete_date': (datetime.now() + timedelta(days=config.AUTO_DELETE_DAYS)).isoformat()
        }
        
        db[str(user_id)].append(record)
        self.save_database(db)

    def check_expired_files(self):
        """Check and delete expired files"""
        db = self.load_database()
        now = datetime.now()
        files_deleted = 0

        for user_id, files in list(db.items()):
            remaining_files = []
            
            for file_record in files:
                delete_date = datetime.fromisoformat(file_record['delete_date'])
                
                if now >= delete_date:
                    if self.drive.delete_file(file_record['file_id']):
                        files_deleted += 1
                        print(f"Auto-deleted: {file_record['file_name']}")
                    else:
                        remaining_files.append(file_record)
                else:
                    remaining_files.append(file_record)
            
            if remaining_files:
                db[user_id] = remaining_files
            else:
                del db[user_id]

        self.save_database(db)
        return files_deleted

    def get_user_files(self, user_id):
        """Get user's uploaded files"""
        db = self.load_database()
        return db.get(str(user_id), [])

    def delete_file_manually(self, user_id, file_id):
        """Delete file manually by user"""
        db = self.load_database()
        
        if str(user_id) in db:
            db[str(user_id)] = [
                f for f in db[str(user_id)] 
                if f['file_id'] != file_id
            ]
            self.save_database(db)
            return self.drive.delete_file(file_id)
        
        return False
