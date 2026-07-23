import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey-change-this-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///portfolio.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ADMIN_PASSWORD = '123456'  # كلمة مرور بسيطة لتسجيل الدخول (يمكنك تغييرها)