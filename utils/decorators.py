from functools import wraps
from models import User, OperationLog
from app import db
from flask import request

def log_operation(action, table_name):
    """操作日志装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            result = f(*args, **kwargs)
            
            # 记录操作日志
            user_id = None
            if 'payload' in kwargs:
                user_id = kwargs['payload'].get('user_id')
            
            log = OperationLog(
                user_id=user_id,
                action=action,
                table_name=table_name,
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
            
            return result
        return decorated
    return decorator