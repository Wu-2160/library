import jwt
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, timedelta,timezone

def create_token(user_id, role):
    """创建JWT token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.now(timezone.utc) + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )

def verify_token(token):
    """验证JWT token"""
    try: 
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """JWT认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'code': 401, 'msg': '无效的token格式'}), 401
        
        if not token:
            return jsonify({'code': 401, 'msg': '缺少token'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'code': 401, 'msg': 'token过期或无效'}), 401
        
        return f(payload, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    @token_required
    def decorated(payload, *args, **kwargs):
        if payload.get('role') != 'admin':
            return jsonify({'code': 403, 'msg':  '需要管理员权限'}), 403
        return f(payload, *args, **kwargs)
    
    return decorated