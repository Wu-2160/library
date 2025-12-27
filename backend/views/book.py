from flask import Blueprint, request, jsonify, current_app
from models import db, Book, BookCategory, BorrowRecord, Reservation
from utils.jwt_handler import token_required, admin_required
from utils.file_handler import save_upload_file, delete_file
from sqlalchemy import or_
from datetime import datetime

book_bp = Blueprint('book', __name__, url_prefix='/api/books')


@book_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有图书分类"""
    try:
        categories = BookCategory.query.all()
        return jsonify({
            'code':200,
            'msg':'成功',
            'data':[cat.to_dict() for cat in categories]
        }), 200
    except Exception as e:
        print(f"获取分类错误:{e}")
        return jsonify({'code':500, 'msg':f'获取失败:{str(e)}'}), 500


@book_bp.route('', methods=['GET'])
def get_books():
    """获取图书列表（分页）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        keyword = request.args.get('keyword', '', type=str)
        category_id = request.args.get('category_id', None, type=int)
        sort_by = request.args.get('sort_by', 'created_at', type=str)
        
        # 构建查询
        query = Book.query
        
        # 关键字搜索
        if keyword:
            query = query.filter(or_(
                Book.title.ilike(f'%{keyword}%'),
                Book.author.ilike(f'%{keyword}%'),
                Book.isbn.like(f'%{keyword}%')
            ))
        
        # 分类过滤
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # 排序
        if sort_by == 'borrowed_count':
            query = query.order_by(Book.borrowed_count.desc())
        elif sort_by == 'avg_rating':
            query = query.order_by(Book.avg_rating.desc())
        else:
            query = query.order_by(Book.created_at.desc())
        
        # 分页
        total = query.count()
        books = query.paginate(page=page, per_page=per_page, error_out=False).items
        
        return jsonify({
            'code':200,
            'msg':'成功',
            'data':[book.to_dict() for book in books],
            'pagination':{
                'page':page,
                'per_page': per_page,
                'total':total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
    
    except Exception as e:
        print(f"获取图书列表错误:{e}")
        return jsonify({'code':500, 'msg': f'获取失败:{str(e)}'}), 500


@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """获取单本图书详情"""
    try:
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'code':404, 'msg':'图书不存在'}), 404
        
        return jsonify({
            'code':200,
            'msg':'成功',
            'data':book.to_dict(include_comments=True)
        }), 200
    
    except Exception as e:
        print(f"获取图书详情错误:{e}")
        return jsonify({'code':500, 'msg':f'获取失败:{str(e)}'}), 500


@book_bp.route('', methods=['POST'])
@admin_required
def add_book(payload):
    """添加图书（仅管理员）"""
    try:
        # 处理表单数据（包含文件）
        data = request.form.to_dict()
        
        # 验证必填字段
        if not data.get('isbn') or not data.get('title'):
            return jsonify({'code': 400, 'msg':'书号和书名必填'}), 400
        
        if Book.query.filter_by(isbn=data['isbn']).first():
            return jsonify({'code': 400, 'msg':'该ISBN已存在'}), 400
        
        # 处理文件上传
        cover_url = None
        if 'cover' in request.files:
            file = request.files['cover']
            if file and file.filename != '':
                cover_url, error = save_upload_file(file, folder='covers')
                if error:
                    return jsonify({'code':400, 'msg': error}), 400
        
        # 创建图书
        book = Book(
            isbn=data['isbn'],
            title=data['title'],
            author=data.get('author'),
            publisher=data.get('publisher'),
            price=float(data.get('price', 0)),
            description=data.get('description'),
            category_id=int(data.get('category_id')) if data.get('category_id') else None,
            location=data.get('location'),
            cover_url=cover_url,
            stock=int(data.get('stock', 1)),
            total=int(data.get('total', 1))
        )
        
        db.session.add(book)
        db.session.commit()
        
        print(f"✓ 图书添加成功:{data['title']}")
        
        return jsonify({
            'code': 201,
            'msg': '添加成功',
            'data':book.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'code':400, 'msg':f'数据格式错误:{str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        print(f"✗ 添加图书错误:{e}")
        return jsonify({'code':500, 'msg':f'添加失败:{str(e)}'}), 500


@book_bp.route('/<int:book_id>', methods=['PUT'])
@admin_required
def update_book(payload, book_id):
    """更新图书（仅管理员）"""
    try:
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'code':404, 'msg': '图书不存在'}), 404
        
        data = request.form.to_dict()
        
        # 处理文件上传
        if 'cover' in request.files:
            file = request.files['cover']
            if file and file.filename != '':
                # 删除旧图片
                if book.cover_url:
                    delete_file(book.cover_url)
                
                # 保存新图片
                cover_url, error = save_upload_file(file, folder='covers')
                if error:
                    return jsonify({'code':400, 'msg':error}), 400
                
                book.cover_url = cover_url
        
        # 更新其他字段
        if 'title' in data:
            book.title = data['title']
        if 'author' in data:
            book.author = data['author']
        if 'publisher' in data:
            book.publisher = data['publisher']
        if 'price' in data:
            book.price = float(data['price'])
        if 'description' in data:
            book.description = data['description']
        if 'category_id' in data:
            book.category_id = int(data['category_id']) if data['category_id'] else None
        if 'location' in data:
            book.location = data['location']
        if 'stock' in data:
            book.stock = int(data['stock'])
        if 'total' in data:
            book.total = int(data['total'])
        
        db.session.commit()
        
        print(f"✓ 图书更新成功:{book.title}")
        
        return jsonify({
            'code': 200,
            'msg': '更新成功',
            'data':book.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"✗ 更新图书错误:{e}")
        return jsonify({'code':500, 'msg':f'更新失败:{str(e)}'}), 500


@book_bp.route('/<int:book_id>', methods=['DELETE'])
@admin_required
def delete_book(payload, book_id):
    """删除图书（仅管理员）"""
    try:
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'code':404, 'msg':'图书不存在'}), 404
        
        # 检查是否有未归还的借阅记录
        active_borrows = BorrowRecord.query.filter(
            BorrowRecord.book_id == book_id,
            BorrowRecord.status == 'borrowed'
        ).count()
        
        if active_borrows > 0:
            return jsonify({'code':400, 'msg':'还有未归还的借阅记录，无法删除'}), 400
        
        # 删除图片文件
        if book.cover_url:
            delete_file(book.cover_url)
        
        db.session.delete(book)
        db.session.commit()
        
        print(f"✓ 图书删除成功:{book.title}")
        
        return jsonify({'code':200, 'msg':'删除成功'}), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"✗ 删除图书错误:{e}")
        return jsonify({'code': 500, 'msg':f'删除失败:{str(e)}'}), 500


@book_bp.route('/popular', methods=['GET'])
def get_popular_books():
    """获取热门图书"""
    try:
        limit = request.args.get('limit', 10, type=int)
        books = Book.query.order_by(
            Book.borrowed_count.desc()
        ).limit(limit).all()
        
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data':[book.to_dict() for book in books]
        }), 200
    
    except Exception as e:
        print(f"获取热门图书错误:{e}")
        return jsonify({'code':500, 'msg':f'获取失败:{str(e)}'}), 500


@book_bp.route('/top-rated', methods=['GET'])
def get_top_rated_books():
    """获取评分最高的图书"""
    try:
        limit = request.args.get('limit', 10, type=int)
        books = Book.query.order_by(
            Book.avg_rating.desc()
        ).limit(limit).all()
        
        return jsonify({
            'code':200,
            'msg':'成功',
            'data':[book.to_dict() for book in books]
        }), 200
    
    except Exception as e:
        print(f"获取评分高的图书错误:{e}")
        return jsonify({'code':500, 'msg': f'获取失败:{str(e)}'}), 500