import os
from datetime import timedelta

class Config: 
    """基础配置"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 文件上传限制
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/uploads')

    # ✅ 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 文件上传限制
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    UPLOAD_URL_PREFIX = '/uploads'  # 前端访问 URL 前缀

class DevConfig(Config):
    """开发配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Wu20050612!@localhost: 3306/library_system'

class ProdConfig(Config):
    """生产配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:Wu20050612!@localhost:3306/library_system')