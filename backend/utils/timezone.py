# utils/timezone.py
from datetime import datetime, timezone, timedelta
import pytz

class TimezoneHelper:
    """时区处理工具类"""
    
    @staticmethod
    def get_utc_now():
        """获取当前UTC时间（aware datetime）"""
        return datetime.now(timezone.utc)
    
    @staticmethod
    def get_utc_naive_now():
        """获取当前UTC时间（naive datetime）"""
        return datetime.utcnow()
    
    @staticmethod
    def make_aware(dt):
        """将naive datetime转换为aware datetime（假设是UTC时区）"""
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    
    @staticmethod
    def make_naive(dt):
        """将aware datetime转换为naive datetime（转换为UTC）"""
        if dt is None:
            return None
        if dt.tzinfo is not None:
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    
    @staticmethod
    def format_datetime(dt, format_str="%Y-%m-%d %H:%M:%S"):
        """格式化datetime"""
        if dt is None:
            return None
        return dt.strftime(format_str)
    
    @staticmethod
    def calculate_days_left(due_time, current_time=None):
        """计算剩余天数"""
        if due_time is None:
            return 0
        
        if current_time is None:
            current_time = datetime.utcnow()
        
        # 确保两个都是naive datetime
        if due_time.tzinfo is not None:
            due_time = TimezoneHelper.make_naive(due_time)
        if current_time.tzinfo is not None:
            current_time = TimezoneHelper.make_naive(current_time)
        
        delta = due_time - current_time
        return delta.days if delta.days > 0 else 0