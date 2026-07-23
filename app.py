import os
from dotenv import load_dotenv

load_dotenv()  # تحميل متغيرات البيئة من ملف .env

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey-change-this-in-production'
    
    # استخدام PostgreSQL عبر Supabase
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        # في حالة التشغيل المحلي، استخدم SQLite
        SQLALCHEMY_DATABASE_URI = 'sqlite:///portfolio.db'
    else:
        # تحويل الرابط إلى صيغة SQLAlchemy
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql://')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # مجلد رفع الملفات (سيستخدم خدمة تخزين خارجية في الإنتاج)
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    
    # كلمة مرور لوحة الإدارة (ضعها في متغيرات البيئة)
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or '123456'
    
    # إعدادات Supabase Storage (للصور)
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY')