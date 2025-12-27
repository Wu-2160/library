from flask import Blueprint, request, jsonify
from models import db, BookComment, Book, User
from utils.jwt_handler import token_required, admin_required

comment_bp = Blueprint('comment', __name__, url_prefix='/api/comments')

@comment_bp.route('/<int:book_id>', methods=['POST'])
@token_required
def add_comment(payload, book_id):
    """添加评论"""
    user_id = payload['user_id']
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({'code': 404, 'msg': '图书不存在'}), 404
    
    data = request.json
    rating = data.get('rating', 0)
    comment = data.get('comment', '')
    
    if not rating or rating < 1 or rating > 5:
        return jsonify({'code': 400, 'msg': '评分必须在1-5之间'}), 400
    
    # 检查是否已评论
    existing = BookComment.query.filter_by(
        user_id=user_id,
        book_id=book_id
    ).first()
    
    if existing:
        existing.rating = rating
        existing.comment = comment
    else: 
        existing = BookComment(
            user_id=user_id,
            book_id=book_id,
            rating=rating,
            comment=comment
        )
        db.session.add(existing)
    
    db.session.commit()
    
    # 更新图书评分
    avg_rating = db.session.query(db.func.avg(BookComment.rating)).filter_by(book_id=book_id).scalar() or 0
    book.avg_rating = round(avg_rating, 2)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'msg': '评论成功',
        'data': existing.to_dict()
    }), 200

@comment_bp.route('/<int:comment_id>', methods=['DELETE'])
@token_required
def delete_comment(payload, comment_id):
    """删除评论"""
    user_id = payload['user_id']
    comment = BookComment.query.get(comment_id)
    
    if not comment:
        return jsonify({'code': 404, 'msg': '评论不存在'}), 404
    
    # 仅本人和管理员可删除
    if comment.user_id != user_id and payload.get('role') != 'admin':
        return jsonify({'code': 403, 'msg': '无权操作'}), 403
    
    book_id = comment.book_id
    db.session.delete(comment)
    db.session.commit()
    
    # 更新图书评分
    avg_rating = db.session.query(db.func.avg(BookComment.rating)).filter_by(book_id=book_id).scalar() or 0
    book = Book.query.get(book_id)
    book.avg_rating = round(avg_rating, 2) if avg_rating else 0
    db.session.commit()
    
    return jsonify({'code': 200, 'msg':  '删除成功'}), 200

@comment_bp.route('/book/<int:book_id>', methods=['GET'])
def get_book_comments(book_id):
    """获取图书评论"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    paginate = BookComment.query.filter(
        BookComment.book_id == book_id,
        BookComment.is_approved == True
    ).order_by(BookComment.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'code':  200,
        'data':  [comment.to_dict() for comment in paginate.items],
        'pagination': {
            'page': page,
            'per_page':  per_page,
            'total': paginate.total
        }
    }), 200