from flask import Blueprint, request, jsonify
from models import db, Notification
from utils.jwt_handler import token_required

notification_bp = Blueprint('notification', __name__, url_prefix='/api/notifications')

@notification_bp.route('', methods=['GET'])
@token_required
def get_notifications(payload):
    """获取通知"""
    user_id = payload['user_id']
    is_read = request.args.get('is_read', None, type=int)
    
    query = Notification.query.filter_by(user_id=user_id)
    if is_read is not None:
        query = query.filter_by(is_read=bool(is_read))
    
    notifications = query.order_by(Notification.created_at.desc()).all()
    
    return jsonify({
        'code': 200,
        'data': [notif.to_dict() for notif in notifications]
    }), 200

@notification_bp.route('/<int:notif_id>/read', methods=['PUT'])
@token_required
def mark_as_read(payload, notif_id):
    """标记已读"""
    notification = Notification.query.get(notif_id)
    
    if not notification:
        return jsonify({'code': 404, 'msg': '通知不存在'}), 404
    
    if notification.user_id != payload['user_id']: 
        return jsonify({'code': 403, 'msg': '无权操作'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'code': 200, 'msg': '已标记'}), 200

@notification_bp.route('/read-all', methods=['PUT'])
@token_required
def read_all_notifications(payload):
    """全部标记已读"""
    user_id = payload['user_id']
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    return jsonify({'code':  200, 'msg': '全部标记成功'}), 200