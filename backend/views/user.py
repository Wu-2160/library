from flask import Blueprint, request, jsonify
from models import db, User
from utils.jwt_handler import create_token, token_required
from werkzeug.security import generate_password_hash, check_password_hash
import re

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    real_name = data.get('real_name', '').strip()
    email = data.get('email', '').strip()
    
    # 验证
    if not username or len(username) < 3:
        return jsonify({'code': 400, 'msg': '用户名至少3个字符'}), 400
    if not password or len(password) < 6:
        return jsonify({'code': 400, 'msg':  '密码至少6个字符'}), 400
    if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({'code':  400, 'msg': '邮箱格式不正确'}), 400
    
    # 检查用户是否存在
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'msg': '用户名已存在'}), 400
    
    # 创建用户
    user = User(
        username=username,
        password=generate_password_hash(password),
        real_name=real_name,
        email=email
    )
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'msg': '注册成功',
        'data':  user.to_dict()
    }), 201

@user_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'code': 400, 'msg': '用户名和密码必填'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password, password):
        return jsonify({'code': 401, 'msg': '用户名或密码错误'}), 401
    
    if user.status == 'frozen':
        return jsonify({'code': 403, 'msg':  '账户已被冻结'}), 403
    
    token = create_token(user.id, user.role)
    
    return jsonify({
        'code': 200,
        'msg': '登录成功',
        'data': {
            'token': token,
            'user': user.to_dict()
        }
    }), 200

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(payload):
    """获取用户信息"""
    user = User.query.get(payload['user_id'])
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    
    return jsonify({
        'code':  200,
        'data': user.to_dict()
    }), 200

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(payload):
    """更新用户信息"""
    user = User.query.get(payload['user_id'])
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    
    data = request.json
    if 'real_name' in data:
        user.real_name = data['real_name'].strip()
    if 'email' in data:
        email = data['email'].strip()
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'code':  400, 'msg': '邮箱格式不正确'}), 400
        user.email = email
    if 'phone' in data:
        user.phone = data['phone'].strip()
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'msg': '更新成功',
        'data': user.to_dict()
    }), 200

@user_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(payload):
    """修改密码"""
    user = User.query.get(payload['user_id'])
    data = request.json
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    
    if not check_password_hash(user.password, old_password):
        return jsonify({'code': 400, 'msg': '旧密码错误'}), 400
    
    if len(new_password) < 6:
        return jsonify({'code': 400, 'msg':  '新密码至少6个字符'}), 400
    
    user.password = generate_password_hash(new_password)
    db.session.commit()
    
    return jsonify({'code': 200, 'msg': '密码修改成功'}), 200