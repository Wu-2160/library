from flask import Blueprint, request, jsonify
from models import db, User, Book, BorrowRecord, Reservation, BookComment, OperationLog
from utils.jwt_handler import admin_required
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, and_

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users(payload):
    """获取所有用户"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '', type=str).strip()
    
    query = User.query
    if keyword:
        query = query.filter(
            User.username.like(f'%{keyword}%') | User.real_name.like(f'%{keyword}%')
        )
    
    paginate = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'code':  200,
        'data':  [user.to_dict() for user in paginate.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': paginate.total,
            'pages': paginate.pages
        }
    }), 200

@admin_bp.route('/users/<int:user_id>/freeze', methods=['POST'])
@admin_required
def freeze_user(payload, user_id):
    """冻结用户"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    
    user.status = 'frozen'
    db.session.commit()
    
    return jsonify({'code': 200, 'msg': '冻结成功'}), 200

@admin_bp.route('/users/<int:user_id>/unfreeze', methods=['POST'])
@admin_required
def unfreeze_user(payload, user_id):
    """解冻用户"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code':  404, 'msg': '用户不存在'}), 404
    
    user.status = 'active'
    db.session.commit()
    
    return jsonify({'code': 200, 'msg': '解冻成功'}), 200

@admin_bp.route('/statistics/overview', methods=['GET'])
@admin_required
def get_overview_statistics(payload):
    """获取统计概览"""
    total_users = User.query.count()
    total_books = Book.query.count()
    total_borrowed = BorrowRecord.query.filter_by(status='borrowed').count()
    total_reservations = Reservation.query.filter_by(status='waiting').count()
    overdue_count = BorrowRecord.query.filter(
        and_(
            BorrowRecord.status.in_(['borrowed', 'overdue']),
            BorrowRecord.due_time < datetime.now(timezone.utc)
        )
    ).count()
    
    return jsonify({
        'code': 200,
        'data': {
            'total_users': total_users,
            'total_books':  total_books,
            'currently_borrowed': total_borrowed,
            'waiting_reservations': total_reservations,
            'overdue_books': overdue_count
        }
    }), 200

@admin_bp.route('/statistics/top-books', methods=['GET'])
@admin_required
def get_top_books_statistics(payload):
    """获取热门图书排行"""
    limit = request.args.get('limit', 10, type=int)
    
    top_books = db.session.query(
        Book.id,
        Book.title,
        Book.author,
        func.count(BorrowRecord.id).label('borrow_count')
    ).outerjoin(BorrowRecord).group_by(Book.id).order_by(
        func.count(BorrowRecord.id).desc()
    ).limit(limit).all()
    
    data = [
        {
            'id': book[0],
            'title': book[1],
            'author':  book[2],
            'borrow_count': book[3] or 0
        }
        for book in top_books
    ]
    
    return jsonify({
        'code': 200,
        'data': data
    }), 200

@admin_bp.route('/statistics/user-activity', methods=['GET'])
@admin_required
def get_user_activity_statistics(payload):
    """获取用户活跃度统计"""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    daily_stats = db.session.query(
        func.date(BorrowRecord.borrow_time).label('date'),
        func.count(BorrowRecord.id).label('borrow_count'),
        func.count(func.distinct(BorrowRecord.user_id)).label('active_users')
    ).filter(BorrowRecord.borrow_time >= start_date).group_by(
        func.date(BorrowRecord.borrow_time)
    ).all()
    
    data = [
        {
            'date': str(stat[0]),
            'borrow_count': stat[1],
            'active_users': stat[2]
        }
        for stat in daily_stats
    ]
    
    return jsonify({
        'code': 200,
        'data': data
    }), 200

@admin_bp.route('/statistics/category-distribution', methods=['GET'])
@admin_required
def get_category_distribution(payload):
    """获取图书分类分布"""
    from models import BookCategory
    
    stats = db.session.query(
        BookCategory.id,
        BookCategory.name,
        func.count(Book.id).label('book_count')
    ).outerjoin(Book).group_by(BookCategory.id).all()
    
    data = [
        {
            'id':  stat[0],
            'category': stat[1],
            'count': stat[2] or 0
        }
        for stat in stats
    ]
    
    return jsonify({
        'code': 200,
        'data': data
    }), 200

@admin_bp.route('/statistics/borrow-return-rate', methods=['GET'])
@admin_required
def get_borrow_return_rate(payload):
    """获取借还率"""
    total_borrows = BorrowRecord.query.count()
    total_returns = BorrowRecord.query.filter_by(status='returned').count()
    
    return jsonify({
        'code':  200,
        'data':  {
            'total_borrows': total_borrows,
            'total_returns': total_returns,
            'return_rate': round(total_returns / total_borrows * 100, 2) if total_borrows > 0 else 0
        }
    }), 200

@admin_bp.route('/statistics/overdue-report', methods=['GET'])
@admin_required
def get_overdue_report(payload):
    """获取逾期报告"""
    overdue_records = db.session.query(
        BorrowRecord,
        User.username,
        Book.title
    ).join(User).join(Book).filter(
        and_(
            BorrowRecord.status.in_(['borrowed', 'overdue']),
            BorrowRecord.due_time < datetime.now(timezone.utc)
        )
    ).order_by(BorrowRecord.due_time).all()
    
    data = []
    for record, username, title in overdue_records: 
        overdue_days = (datetime.now(timezone.utc) - record.due_time).days
        data.append({
            'record_id': record.id,
            'username': username,
            'book_title': title,
            'due_time': record.due_time.isoformat(),
            'overdue_days': overdue_days
        })
    
    return jsonify({
        'code': 200,
        'data': data
    }), 200

@admin_bp.route('/logs', methods=['GET'])
@admin_required
def get_operation_logs(payload):
    """获取操作日志"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    action = request.args.get('action', '', type=str).strip()
    
    query = OperationLog.query
    if action:
        query = query.filter_by(action=action)
    
    paginate = query.order_by(OperationLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'code':  200,
        'data':  [log.to_dict() for log in paginate.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': paginate.total,
            'pages': paginate.pages
        }
    }), 200

@admin_bp.route('/export/users', methods=['GET'])
@admin_required
def export_users(payload):
    """导出用户数据（模拟）"""
    users = User.query.all()
    data = [user.to_dict() for user in users]
    
    return jsonify({
        'code': 200,
        'msg': '导出成功',
        'data': data,
        'total':  len(data)
    }), 200

@admin_bp.route('/export/borrow-records', methods=['GET'])
@admin_required
def export_borrow_records(payload):
    """导出借阅记录"""
    records = BorrowRecord.query.all()
    data = [record.to_dict() for record in records]
    
    return jsonify({
        'code': 200,
        'msg': '导出成功',
        'data': data,
        'total':  len(data)
    }), 200