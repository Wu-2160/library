from flask import Blueprint, request, jsonify
from models import db, BorrowRecord, Book, User, Notification
from utils.jwt_handler import token_required
from datetime import datetime, timedelta, timezone
from sqlalchemy import and_

borrow_bp = Blueprint('borrow', __name__, url_prefix='/api/borrows')

@borrow_bp.route('/<int:book_id>', methods=['POST'])
@token_required
def borrow_book(payload, book_id):
    """借阅图书"""
    user_id = payload['user_id']
    user = User.query.get(user_id)
    book = Book.query.get(book_id)
    
    if not book: 
        return jsonify({'code':  404, 'msg': '图书不存在'}), 404
    
    if book.stock <= 0:
        return jsonify({'code': 400, 'msg': '图书库存不足'}), 400
    
    # 检查用户是否已借阅此书
    existing = BorrowRecord.query.filter(
        and_(
            BorrowRecord.user_id == user_id,
            BorrowRecord.book_id == book_id,
            BorrowRecord.status == 'borrowed'
        )
    ).first()
    
    if existing: 
        return jsonify({'code':  400, 'msg': '您已借阅此书，请先归还'}), 400
    
    # 创建借阅记录（30天借期）
    due_time = datetime.now(timezone.utc) + timedelta(days=30)
    borrow_record = BorrowRecord(
        user_id=user_id,
        book_id=book_id,
        due_time=due_time
    )
    
    db.session.add(borrow_record)
    
    # 添加通知
    notification = Notification(
        user_id=user_id,
        title='借阅成功',
        content=f'您已成功借阅《{book.title}》，请于{due_time.strftime("%Y-%m-%d")}前归还',
        type='borrow'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'msg': '借阅成功',
        'data': borrow_record.to_dict()
    }), 200

@borrow_bp.route('/<int:record_id>/return', methods=['POST'])
@token_required
def return_book(payload, record_id):
    """归还图书"""
    user_id = payload['user_id']
    borrow_record = BorrowRecord.query.get(record_id)
    
    if not borrow_record:
        return jsonify({'code': 404, 'msg': '借阅记录不存在'}), 404
    
    if borrow_record.user_id != user_id:
        return jsonify({'code': 403, 'msg': '无权操作'}), 403
    
    if borrow_record.status != 'borrowed':
        return jsonify({'code': 400, 'msg': '该图书已归还'}), 400
    
    borrow_record.return_time = datetime.now(timezone.utc)
    borrow_record.status = 'returned'
    
    book = borrow_record.book

    
    # 添加通知
    notification = Notification(
        user_id=user_id,
        title='归还成功',
        content=f'您已成功归还《{book.title}》',
        type='return'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({
        'code':  200,
        'msg':  '归还成功'
    }), 200

@borrow_bp.route('/my-records', methods=['GET'])
@token_required
def get_my_borrow_records(payload):
    """获取我的借阅记录"""
    user_id = payload['user_id']
    status = request.args.get('status', '', type=str)
    
    query = BorrowRecord.query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)
    
    records = query.order_by(BorrowRecord.borrow_time.desc()).all()
    
    return jsonify({
        'code': 200,
        'data': [record.to_dict() for record in records]
    }), 200

@borrow_bp.route('/<int:record_id>/renew', methods=['POST'])
@token_required
def renew_book(payload, record_id):
    """续借图书"""
    user_id = payload['user_id']
    borrow_record = BorrowRecord.query.get(record_id)
    
    if not borrow_record: 
        return jsonify({'code': 404, 'msg': '借阅记录不存在'}), 404
    
    if borrow_record.user_id != user_id:
        return jsonify({'code': 403, 'msg': '无权操作'}), 403
    
    if borrow_record.status != 'borrowed':
        return jsonify({'code': 400, 'msg': '仅能续借中的图书'}), 400
    
    if borrow_record.renewal_count >= 3:
        return jsonify({'code': 400, 'msg': '最多只能续借3次'}), 400
    
    # 延期14天
    borrow_record.due_time = borrow_record.due_time + timedelta(days=14)
    borrow_record.renewal_count += 1
    db.session.commit()
    
    return jsonify({
        'code':  200,
        'msg':  '续借成功',
        'data': borrow_record.to_dict()
    }), 200

@borrow_bp.route('/overdue', methods=['GET'])
@token_required
def get_overdue_records(payload):
    """获取逾期图书"""
    user_id = payload['user_id']
    overdue_records = BorrowRecord.query.filter(
        and_(
            BorrowRecord.user_id == user_id,
            BorrowRecord.status.in_(['borrowed', 'overdue']),
            BorrowRecord.due_time < datetime.now(timezone.utc)
        )
    ).all()
    
    return jsonify({
        'code': 200,
        'data': [record.to_dict() for record in overdue_records]
    }), 200