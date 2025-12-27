from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys

from models import db

def create_app(config_name='dev'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    if config_name == 'prod':
        from config import ProdConfig
        app.config.from_object(ProdConfig)
    else:
        from config import DevConfig
        app.config.from_object(DevConfig)
    
    db.init_app(app)
    
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True
             }
         }
    )
    
    # 创建上传目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # ✅ 注册静态文件路由（提供上传的文件访问）
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        from flask import send_from_directory
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    with app.app_context():
        from views.user import user_bp
        from views.book import book_bp
        from views.borrow import borrow_bp
        from views.reservation import reservation_bp
        from views.comment import comment_bp
        from views.notification import notification_bp
        from views.admin import admin_bp
        
        app.register_blueprint(user_bp)
        app.register_blueprint(book_bp)
        app.register_blueprint(borrow_bp)
        app.register_blueprint(reservation_bp)
        app.register_blueprint(comment_bp)
        app.register_blueprint(notification_bp)
        app.register_blueprint(admin_bp)
        
        db.create_all()
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'code': 404, 'msg': '资源不存在'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        print(f"500 错误: {error}", file=sys.stderr)
        return jsonify({'code': 500, 'msg': '服务器内部错误'}), 500
    
    @app.route('/api/test', methods=['GET'])
    def test():
        return jsonify({'code': 200, 'msg':  '后端连接正常'})
    
    return app

if __name__ == '__main__': 
    app = create_app('dev')
    print("=" * 50)
    print("🚀 Flask 应用启动")
    print("=" * 50)
    print("📡 API 服务:   http://localhost:5000")
    print("🌐 CORS 已启用")
    print("📁 上传文件夹: " + app.config['UPLOAD_FOLDER'])
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)