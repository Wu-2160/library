from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()


class User(db.Model):
    """用户模型"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    real_name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    role = db.Column(db.Enum('reader', 'admin'), default='reader')
    status = db.Column(db.Enum('active', 'frozen'), default='active')
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow())
    
    borrow_records = db.relationship('BorrowRecord', backref='user', lazy=True)
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    comments = db.relationship('BookComment', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'email': self.email,
            'phone': self.phone,
            'role':  self.role,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class BookCategory(db.Model):
    """图书分类"""
    __tablename__ = 'book_category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    
    books = db.relationship('Book', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Book(db.Model):
    """图书模型"""
    __tablename__ = 'book'
    
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(128), nullable=False)
    author = db.Column(db.String(64))
    publisher = db.Column(db.String(64))
    price = db.Column(db.Numeric(8, 2))
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('book_category.id'))
    location = db.Column(db.String(64))
    cover_url = db.Column(db.String(256))
    stock = db.Column(db.Integer, default=1)
    total = db.Column(db.Integer, default=1)
    borrowed_count = db.Column(db.Integer, default=0)
    avg_rating = db.Column(db.Numeric(3, 2), default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow())
    
    borrow_records = db.relationship('BorrowRecord', backref='book', lazy=True)
    reservations = db.relationship('Reservation', backref='book', lazy=True)
    comments = db.relationship('BookComment', backref='book', lazy=True)
    
    def to_dict(self, include_comments=False):
        data = {
            'id': self.id,
            'isbn':  self.isbn,
            'title': self.title,
            'author': self.author,
            'publisher': self.publisher,
            'price': float(self.price) if self.price else 0,
            'description': self.description,
            'category_id': self.category_id,
            'category': self.category.name if self.category else None,
            'location': self.location,
            'cover_url': self.cover_url,
            'stock':  self.stock,
            'total': self.total,
            'borrowed_count': self.borrowed_count,
            'avg_rating': float(self.avg_rating) if self.avg_rating else 0,
            'created_at':  self.created_at.isoformat() if self.created_at else None
        }
        if include_comments:
            data['comments'] = [c.to_dict() for c in self.comments]
        return data


class BorrowRecord(db.Model):
    """借阅记录"""
    __tablename__ = 'borrow_record'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_time = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    due_time = db.Column(db.DateTime)
    return_time = db.Column(db.DateTime)
    status = db.Column(db.Enum('borrowed', 'returned', 'overdue'), default='borrowed')
    renewal_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    
    def to_dict(self):
        """转换为字典"""
        days_left = 0
        if self.due_time:
            delta = self.due_time - datetime.utcnow()
            days_left = delta.days
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.username if self.user else None,
            'book_id': self.book_id,
            'book':  self.book.title if self.book else None,
            'borrow_time': self.borrow_time.isoformat() if self.borrow_time else None,
            'due_time':  self.due_time.isoformat() if self.due_time else None,
            'return_time': self.return_time.isoformat() if self.return_time else None,
            'status': self.status,
            'renewal_count': self.renewal_count,
            'days_left': days_left
        }
    
    def is_overdue(self):
        """判断是否逾期"""
        if self.status == 'borrowed' and self.due_time:
            return datetime.utcnow() > self.due_time
        return False


class Reservation(db.Model):
    """预约记录"""
    __tablename__ = 'reservation'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    queue_position = db.Column(db.Integer)
    reserve_time = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    status = db.Column(db.Enum('waiting', 'notified', 'cancelled', 'finished'), default='waiting')
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'book_title': self.book.title,
            'queue_position': self.queue_position,
            'reserve_time': self.reserve_time.isoformat() if self.reserve_time else None,
            'status': self.status
        }


class BookComment(db.Model):
    """评论"""
    __tablename__ = 'book_comment'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow())
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'book_id': self.book_id,
            'rating': self.rating,
            'comment': self.comment,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Notification(db.Model):
    """通知"""
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(128))
    content = db.Column(db.String(512))
    type = db.Column(db.Enum('borrow', 'return', 'reservation', 'overdue', 'system'), default='system')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    
    def to_dict(self):
        return {
            'id':  self.id,
            'title': self.title,
            'content': self.content,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class OperationLog(db.Model):
    """操作日志"""
    __tablename__ = 'operation_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(64))
    table_name = db.Column(db.String(32))
    record_id = db.Column(db.Integer)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action':  self.action,
            'table_name': self.table_name,
            'record_id':  self.record_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }