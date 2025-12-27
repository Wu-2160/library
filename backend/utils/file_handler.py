import os
from werkzeug.utils import secure_filename
from flask import current_app
import uuid
from datetime import datetime

def allowed_file(filename):
    """检查文件是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def generate_filename(original_filename):
    """生成唯一的文件名"""
    ext = original_filename.rsplit('.', 1)[1].lower()
    # 格式:  book_20251227_093745_uuid.jpg
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    return f"book_{timestamp}_{unique_id}.{ext}"

def save_upload_file(file, folder=''):
    """保存上传的文件"""
    try:
        if not file or file.filename == '':
            return None, '没有选择文件'
        
        if not allowed_file(file.filename):
            return None, f'不支持的文件格式。允许的格式：{", ".join(current_app.config["ALLOWED_EXTENSIONS"])}'
        
        # 创建上传目录
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if folder:
            upload_folder = os.path.join(upload_folder, folder)
        
        os.makedirs(upload_folder, exist_ok=True)
        
        # 生成文件名并保存
        filename = generate_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)
        
        file.save(filepath)
        
        # 返回相对 URL
        if folder:
            url = f"{current_app.config['UPLOAD_URL_PREFIX']}/{folder}/{filename}"
        else:
            url = f"{current_app.config['UPLOAD_URL_PREFIX']}/{filename}"
        
        return url, None
    
    except Exception as e:
        return None, f'文件上传失败: {str(e)}'

def delete_file(file_url):
    """删除文件"""
    try:
        if not file_url:
            return True
        
        # 从 URL 获取文件路径
        relative_path = file_url.replace(current_app.config['UPLOAD_URL_PREFIX'], '').lstrip('/')
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], relative_path)
        
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return True
    
    except Exception as e:
        print(f"删除文件失败: {e}")
        return False