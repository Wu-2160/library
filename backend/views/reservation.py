from flask import Blueprint, request, jsonify
from models import db, Reservation, Book, BorrowRecord, Notification, User
from utils.jwt_handler import token_required
from datetime import datetime
from sqlalchemy import and_

reservation_bp = Blueprint('reservation', __name__, url_prefix='/api/reservations')

@reservation_bp.route('/<int:book_id>', methods=['POST'])
@token_required
def reserve_book(payload, book_id):
    """预约图书"""
    user_id = payload['user_id']
    user = User.query.get(user_id)
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({'code': 404, 'msg': '图书不存在'}), 404
    
    # 检查是否已预约
    existing = Reservation.query.filter(
        and_(
            Reservation.user_id == user_id,
            Reservation.book_id == book_id,
            Reservation.status.in_(['waiting', 'notified'])
        )
    ).first()
    
    if existing: 
        return jsonify({'code':  400, 'msg': '您已预约此书'}), 400
    
    # 获取队列位置
    queue_position = db.session.query(db.func.max(Reservation.queue_position)).filter(
        Reservation.book_id == book_id
    ).scalar() or 0
    queue_position += 1
    
    reservation = Reservation(
        user_id=user_id,
        book_id=book_id,
        queue_position=queue_position
    )
    
    db.session.add(reservation)
    
    # 添加通知
    notification = Notification(
        user_id=user_id,
        title='预约成功',
        content=f'您已预约《{book.title}》，队列位置：{queue_position}',
        type='reservation'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'msg': '预约成功',
        'data': reservation.to_dict()
    }), 200

@reservation_bp.route('/my-reservations', methods=['GET'])
@token_required
def get_my_reservations(payload):
    """获取我的预约"""
    user_id = payload['user_id']
    status = request.args.get('status', '', type=str)
    
    query = Reservation.query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)
    
    reservations = query.order_by(Reservation.queue_position).all()
    
    return jsonify({
        'code': 200,
        'data': [res.to_dict() for res in reservations]
    }), 200

@reservation_bp.route('/<int:reservation_id>/cancel', methods=['POST'])
@token_required
def cancel_reservation(payload, reservation_id):
    """取消预约"""
    user_id = payload['user_id']
    reservation = Reservation.query.get(reservation_id)
    
    if not reservation:
        return jsonify({'code': 404, 'msg': '预约不存在'}), 404
    
    if reservation.user_id != user_id:
        return jsonify({'code': 403, 'msg': '无权操作'}), 403
    
    if reservation.status == 'cancelled':
        return jsonify({'code': 400, 'msg':  '已取消'}), 400
    
    reservation.status = 'cancelled'
    db.session.commit()
    
    return jsonify({'code': 200, 'msg': '取消成功'}), 200

@reservation_bp.route('/queue/<int:book_id>', methods=['GET'])
def get_reservation_queue(book_id):
    """获取预约队列"""
    reservations = Reservation.query.filter(
        and_(
            Reservation.book_id == book_id,
            Reservation.status.in_(['waiting', 'notified'])
        )
    ).order_by(Reservation.queue_position).all()
    
    return jsonify({
        'code': 200,
        'data': [res.to_dict() for res in reservations]
    }), 200