# generate_test_data.py
import pymysql
import random
from datetime import datetime, timedelta
import hashlib
import string
from tqdm import tqdm
import json

class LibraryDataGenerator:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        self.cursor = None
        
        # 按数据库分类定义图书数据
        self.category_books = {
            '文学': [
                "三体", "红楼梦", "西游记", "水浒传", "三国演义", "百年孤独",
                "追风筝的人", "解忧杂货店", "白夜行", "嫌疑人X的献身", "挪威的森林",
                "活着", "许三观卖血记", "平凡的世界", "围城", "边城",
                "霍乱时期的爱情", "杀死一只知更鸟", "1984", "动物农场", "麦田里的守望者",
                "傲慢与偏见", "简爱", "呼啸山庄", "飘", "基督山伯爵",
                "老人与海", "了不起的盖茨比", "少年维特的烦恼", "罪与罚", "战争与和平"
            ],
            '技术': [
                "Python编程从入门到实践", "深入理解计算机系统", "算法导论", "计算机网络", "操作系统概念",
                "JavaScript高级程序设计", "深入理解MySQL", "Redis设计与实现", "Spring Boot实战",
                "Docker技术入门与实战", "Kubernetes权威指南", "微服务架构设计模式", "Clean Code",
                "设计模式", "重构:改善既有代码的设计", "代码整洁之道", "人月神话", "编程珠玑",
                "C++ Primer", "Java核心技术", "Effective Java", "Thinking in Java",
                "Head First设计模式", "敏捷软件开发", "测试驱动开发", "持续交付", "DevOps实践指南",
                "人工智能:一种现代方法", "机器学习", "深度学习", "统计学习方法", "Python机器学习",
                "自然语言处理", "计算机视觉", "推荐系统实践", "数据挖掘概念与技术", "大数据处理技术",
                "Flask Web开发实战", "Django企业开发实战", "Vue.js实战", "React全家桶", "TypeScript编程",
                "Web性能权威指南", "HTTP权威指南", "TCP/IP详解", "网络安全基础", "加密与解密"
            ],
            '历史': [
                "人类简史", "未来简史", "今日简史", "时间简史", "宇宙简史",
                "明朝那些事儿", "万历十五年", "中国通史", "世界通史", "枪炮、病菌与钢铁",
                "罗马帝国衰亡史", "资治通鉴", "史记", "全球通史", "大国的兴衰",
                "世界文明史", "中国历代政治得失", "第二次世界大战回忆录", "丝绸之路", "大航海时代"
            ],
            '哲学': [
                "中国哲学简史", "西方哲学史", "道德经", "论语", "庄子",
                "苏菲的世界", "理想国", "存在与虚无", "纯粹理性批判", "查拉图斯特拉如是说",
                "沉思录", "作为意志和表象的世界", "悲剧的诞生", "精神现象学", "小逻辑",
                "哲学的故事", "中国哲学史", "西方哲学史讲演录", "哲学原理", "形而上学的沉思"
            ],
            '艺术': [
                "大艺术家", "艺术的故事", "美的历程", "中国艺术史", "西方美术史",
                "艺术哲学", "艺术与视知觉", "设计的法则", "色彩的艺术", "构图的艺术",
                "音乐的故事", "电影艺术", "摄影的艺术", "舞蹈艺术", "戏剧艺术",
                "建筑的艺术", "雕塑的艺术", "绘画的艺术", "书法艺术", "陶瓷艺术"
            ]
        }
        
        # 按数据库分类定义作者
        self.category_authors = {
            '文学': ["刘慈欣", "余华", "莫言", "路遥", "陈忠实", "贾平凹", "王小波", "钱钟书", "沈从文", "鲁迅",
                   "史蒂芬·金", "村上春树", "东野圭吾", "J.K.罗琳", "乔治·马丁", "托尔金", "阿西莫夫", "海明威", "马克·吐温",
                   "简·奥斯汀", "夏洛蒂·勃朗特", "艾米莉·勃朗特", "玛格丽特·米切尔", "大仲马", "小仲马"],
            '技术': ["作者A", "作者B", "作者C", "作者D", "Stephen Prata", "Robert C. Martin", "Eric Freeman",
                   "Bruce Eckel", "David Flanagan", "Marijn Haverbeke", "Ian Goodfellow", "Yoshua Bengio", 
                   "Aaron Courville", "王明", "李华", "张强", "赵磊"],
            '历史': ["尤瓦尔·赫拉利", "史蒂芬·霍金", "当年明月", "黄仁宇", "司马迁", "司马光",
                   "贾雷德·戴蒙德", "爱德华·吉本", "房龙", "吕思勉", "吴于廑", "齐世荣",
                   "威尔·杜兰特", "威廉·麦克尼尔", "汤因比"],
            '哲学': ["冯友兰", "柏拉图", "尼采", "康德", "叔本华", "老子", "孔子", "庄子",
                   "乔斯坦·贾德", "萨特", "黑格尔", "马克思", "罗素", "笛卡尔", "休谟",
                   "维特根斯坦", "海德格尔", "卢梭", "伏尔泰", "培根"],
            '艺术': ["某某", "贡布里希", "李泽厚", "高居翰", "朱光潜", "宗白华", "鲁道夫·阿恩海姆",
                   "威廉·荷加斯", "约翰内斯·伊顿", "安塞尔·亚当斯", "苏珊·朗格", "贝多芬", 
                   "斯坦利·库布里克", "玛莎·葛兰姆", "莎士比亚", "勒·柯布西耶", "米开朗基罗",
                   "张大千", "齐白石", "王羲之", "唐三彩"]
        }
        
        self.publishers = [
            "人民邮电出版社", "清华大学出版社", "机械工业出版社", "电子工业出版社", "中信出版社",
            "北京大学出版社", "浙江大学出版社", "上海交通大学出版社", "高等教育出版社", "科学出版社",
            "中国电力出版社", "中国水利水电出版社", "中国铁道出版社", "人民文学出版社", "商务印书馆",
            "重庆出版社", "人民出版社", "浙江人民出版社", "上海人民出版社", "江苏人民出版社"
        ]
        
        self.comments = [
            "这本书写得非常好，让我受益匪浅！",
            "内容详实，适合初学者入门学习。",
            "经典著作，值得反复阅读思考。",
            "印刷质量很好，内容也很精彩。",
            "有点难懂，需要有一定的基础。",
            "作者的观点很独特，启发性很强。",
            "翻译质量一般，建议阅读原版。",
            "案例分析很实用，对工作有帮助。",
            "理论结合实践，非常有指导意义。",
            "适合作为参考书，不太适合入门。",
            "内容比较基础，适合新手。",
            "深度不够，但广度还可以。",
            "性价比很高，推荐购买。",
            "纸张质量一般，但内容不错。",
            "买来送人的，对方很喜欢。"
        ]
        
        # 通知类型映射
        self.notification_types = {
            'overdue': 'overdue',
            'reservation': 'reservation',
            'system': 'system',
            'borrow': 'borrow',
            'return': 'return'
        }
    
    def connect(self):
        """连接数据库"""
        try:
            self.connection = pymysql.connect(
                host=self.db_config['host'],
                port=self.db_config.get('port', 3306),
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                charset='utf8mb4'
            )
            self.cursor = self.connection.cursor()
            print("✅ 数据库连接成功！")
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("✅ 数据库连接已关闭")
    
    def disable_triggers(self):
        """临时禁用触发器（通过删除并重建）"""
        try:
            print("🔧 临时删除触发器...")
            
            # 删除触发器
            self.cursor.execute("DROP TRIGGER IF EXISTS update_stock_on_borrow")
            self.cursor.execute("DROP TRIGGER IF EXISTS update_stock_on_return")
            self.cursor.execute("DROP TRIGGER IF EXISTS update_book_rating")
            
            self.connection.commit()
            print("✅ 触发器已临时删除")
            return True
        except Exception as e:
            print(f"⚠️ 删除触发器时出错: {e}")
            return False
    
    def restore_triggers(self):
        """恢复触发器"""
        try:
            print("🔧 恢复触发器...")
            
            # 恢复自动更新库存的触发器
            self.cursor.execute("""
                CREATE TRIGGER update_stock_on_borrow AFTER INSERT ON borrow_record
                FOR EACH ROW
                BEGIN
                    IF NEW.status = 'borrowed' OR NEW.status = 'overdue' THEN
                        UPDATE book SET stock = stock - 1 WHERE id = NEW.book_id;
                    END IF;
                    UPDATE book SET borrowed_count = borrowed_count + 1 WHERE id = NEW.book_id;
                END
            """)
            
            self.cursor.execute("""
                CREATE TRIGGER update_stock_on_return AFTER UPDATE ON borrow_record
                FOR EACH ROW
                BEGIN
                    IF NEW.status = 'returned' AND OLD.status != 'returned' THEN
                        UPDATE book SET stock = stock + 1 WHERE id = NEW.book_id;
                    END IF;
                END
            """)
            
            self.cursor.execute("""
                CREATE TRIGGER update_book_rating AFTER INSERT ON book_comment
                FOR EACH ROW
                BEGIN
                    UPDATE book SET avg_rating = (
                        SELECT ROUND(AVG(rating), 2) FROM book_comment WHERE book_id = NEW.book_id
                    ) WHERE id = NEW.book_id;
                END
            """)
            
            self.connection.commit()
            print("✅ 触发器已恢复")
            return True
        except Exception as e:
            print(f"⚠️ 恢复触发器时出错: {e}")
            return False
    
    def optimize_database(self):
        """优化数据库设置以提高插入性能"""
        try:
            print("⚡ 优化数据库设置...")
            self.cursor.execute("SET autocommit = 0")
            self.cursor.execute("SET unique_checks = 0")
            self.cursor.execute("SET foreign_key_checks = 0")
            print("✅ 数据库优化完成")
        except Exception as e:
            print(f"⚠️ 数据库优化失败: {e}")
    
    def restore_database_settings(self):
        """恢复数据库设置"""
        try:
            self.cursor.execute("SET autocommit = 1")
            self.cursor.execute("SET unique_checks = 1")
            self.cursor.execute("SET foreign_key_checks = 1")
            print("✅ 数据库设置已恢复")
        except Exception as e:
            print(f"⚠️ 恢复数据库设置失败: {e}")
    
    def clear_existing_data(self):
        """清理现有的测试数据"""
        try:
            print("🧹 清理现有测试数据...")
            
            # 获取当前用户数量（保留admin）
            self.cursor.execute("SELECT COUNT(*) FROM user WHERE username != 'admin'")
            user_count = self.cursor.fetchone()[0]
            
            if user_count > 0:
                confirm = input(f"⚠️ 发现 {user_count} 条现有用户数据，是否清除？(y/n): ")
                if confirm.lower() != 'y':
                    print("❌ 用户取消操作")
                    return False
            
            # 临时禁用触发器
            self.disable_triggers()
            
            try:
                # 注意：由于有外键约束，需要按特定顺序删除
                # 先删除有外键约束的子表数据
                tables = [
                    'operation_log', 'notification', 'book_comment', 
                    'reservation', 'borrow_record', 'book', 'user'
                ]
                
                for table in tables:
                    try:
                        if table == 'user':
                            self.cursor.execute("DELETE FROM user WHERE username != 'admin'")
                            self.cursor.execute("ALTER TABLE user AUTO_INCREMENT = 2")
                        elif table == 'book':
                            # 删除图书数据，保留初始数据
                            self.cursor.execute("DELETE FROM book WHERE id > 5")
                            self.cursor.execute("ALTER TABLE book AUTO_INCREMENT = 6")
                        else:
                            self.cursor.execute(f"DELETE FROM {table}")
                            self.cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
                    except Exception as e:
                        print(f"⚠️ 清理表 {table} 时出错: {e}")
                
                self.connection.commit()
                print("✅ 数据清理完成")
                return True
                
            finally:
                # 恢复触发器
                self.restore_triggers()
            
        except Exception as e:
            self.connection.rollback()
            print(f"❌ 清理数据失败: {e}")
            return False
    
    def generate_users(self, count):
        """生成用户数据"""
        print(f"👤 正在生成 {count} 条用户数据...")
        
        sql = """
        INSERT INTO user (username, password, real_name, email, phone, role, status)
        VALUES (%s, %s, %s, %s, %s, 'reader', 'active')
        """
        
        batch_size = 500
        data = []
        
        for i in tqdm(range(1, count + 1), desc="生成用户"):
            username = f"reader{i:04d}"
            real_name = f"读者{self.get_random_chinese_name()}"
            email = f"reader{i:04d}@test.com"
            phone = f"1{random.randint(30, 89)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}"
            
            data.append((
                username,
                'pbkdf2:sha256:600000$XOHHUaFjfiPNjmFx$5f3433c80addca1f454e27be724672ebd211b3b7016b7f7cf7da9d85b37bee45',  # 123456
                real_name,
                email,
                phone
            ))
            
            # 批量插入
            if len(data) >= batch_size:
                self.cursor.executemany(sql, data)
                self.connection.commit()
                data = []
        
        # 插入剩余数据
        if data:
            self.cursor.executemany(sql, data)
            self.connection.commit()
        
        print(f"✅ 用户数据生成完成，共 {count} 条")
    
    def generate_books(self, count):
        """生成图书数据"""
        print(f"📚 正在生成 {count} 条图书数据...")
        
        # 获取分类ID和名称
        self.cursor.execute("SELECT id, name FROM book_category")
        category_data = self.cursor.fetchall()
        
        if not category_data:
            print("❌ 没有找到图书分类，请先运行数据库初始化脚本")
            return
        
        sql = """
        INSERT INTO book (isbn, title, author, publisher, price, 
                         category_id, stock, total, location, description, borrowed_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        batch_size = 500
        data = []
        
        for i in tqdm(range(1, count + 1), desc="生成图书"):
            # 随机选择一个分类
            category_id, category_name = random.choice(category_data)
            
            # 根据分类名称选择对应的书名和作者
            if category_name in self.category_books:
                title = random.choice(self.category_books[category_name])
            else:
                # 如果分类不在预定义列表中，从所有书中随机选择
                all_titles = []
                for books in self.category_books.values():
                    all_titles.extend(books)
                title = random.choice(all_titles)
            
            if category_name in self.category_authors:
                author = random.choice(self.category_authors[category_name])
            else:
                # 如果分类不在预定义列表中，从所有作者中随机选择
                all_authors = []
                for authors in self.category_authors.values():
                    all_authors.extend(authors)
                author = random.choice(all_authors)
            
            # 生成ISBN
            isbn = f"978-7-{random.randint(100, 999):03d}-{random.randint(10000, 99999):05d}-{random.randint(1, 9):1d}"
            
            # 30%的几率加上副标题
            if random.random() < 0.3:
                subtitle_options = ['实战篇', '进阶篇', '精解', '深度剖析', '经典版', '最新版', '修订版']
                title += f"：{random.choice(subtitle_options)}"
            
            publisher = random.choice(self.publishers)
            price = round(random.uniform(25, 150), 2)
            total = random.randint(3, 20)  # 总库存3-20本
            stock = total  # 初始库存等于总库存
            location = f"书架{random.randint(1, 20)}区-{random.randint(1, 50)}号"
            borrowed_count = 0  # 初始借阅次数为0
            
            # 根据分类生成描述
            descriptions = {
                '文学': f"《{title}》是一部文学经典，作者{author}以其独特的文笔和深刻的社会洞察力，描绘了丰富的人物形象和动人的故事情节。",
                '技术': f"《{title}》是一本关于编程、算法和软件开发的优秀著作。作者{author}以其深厚的专业知识和丰富的实践经验，系统性地阐述了相关概念和技术。",
                '历史': f"《{title}》以详实的史料和独特的视角，展现了历史发展的脉络，是了解{random.choice(['中国', '世界', '特定时期'])}历史的重要读物。",
                '哲学': f"《{title}》探讨了人类思想、心灵和存在的根本问题，引导读者进行深入的哲学思考。作者{author}的论述严谨而富有启发性。",
                '艺术': f"《{title}》展示了{random.choice(['绘画', '音乐', '舞蹈', '建筑', '设计'])}艺术的魅力，作者{author}对艺术的独到见解令人耳目一新。"
            }
            
            description = descriptions.get(category_name, 
                f"《{title}》是一本优秀的{category_name}类著作，内容详实，值得一读。")
            
            data.append((
                isbn, title, author, publisher, price,
                category_id, stock, total, location, description, borrowed_count
            ))
            
            if len(data) >= batch_size:
                self.cursor.executemany(sql, data)
                self.connection.commit()
                data = []
        
        if data:
            self.cursor.executemany(sql, data)
            self.connection.commit()
        
        print(f"✅ 图书数据生成完成，共 {count} 条")
    
    def generate_borrow_records(self, count):
        """生成借阅记录 - 完全在代码中管理库存"""
        print(f"📖 正在生成 {count} 条借阅记录...")
        
        # 临时禁用触发器，我们自己管理库存
        self.disable_triggers()
        
        try:
            # 获取读者ID
            self.cursor.execute("SELECT id FROM user WHERE role = 'reader'")
            user_ids = [row[0] for row in self.cursor.fetchall()]
            
            # 获取图书ID、库存和总库存
            self.cursor.execute("SELECT id, stock, total FROM book")
            book_info = {}
            for row in self.cursor.fetchall():
                book_info[row[0]] = {
                    'stock': row[1],
                    'total': row[2],
                    'borrowed_count': 0
                }
            
            if not user_ids or not book_info:
                print("❌ 需要先生成用户和图书数据！")
                return
            
            # 获取图书ID列表
            book_ids = list(book_info.keys())
            
            sql = """
            INSERT INTO borrow_record (user_id, book_id, borrow_time, due_time, 
                                      return_time, status, renewal_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            batch_size = 500
            data = []
            
            for i in tqdm(range(count), desc="生成借阅记录"):
                user_id = random.choice(user_ids)
                
                # 选择一本图书
                # 优先选择有库存的图书用于借阅中/逾期状态
                available_books = [bid for bid in book_ids if book_info[bid]['stock'] > 0]
                
                # 如果没有可用库存，就从所有图书中随机选择（只能生成已归还的记录）
                if not available_books:
                    book_id = random.choice(book_ids)
                else:
                    book_id = random.choice(available_books)
                
                book = book_info[book_id]
                
                # 随机借阅时间（过去一年内）
                borrow_time = datetime.now() - timedelta(days=random.randint(0, 365))
                due_time = borrow_time + timedelta(days=30)
                
                # 决定记录状态
                if book['stock'] > 0:
                    # 有库存，可以生成任何状态的记录
                    rand_val = random.random()
                    if rand_val < 0.3:  # 30%的几率是正在借阅
                        status = "borrowed"
                        return_time = None
                        book['stock'] -= 1
                    elif rand_val < 0.6:  # 30%的几率是逾期
                        status = "overdue"
                        return_time = None
                        book['stock'] -= 1
                    else:  # 40%的几率是已归还
                        status = "returned"
                        return_time = borrow_time + timedelta(days=random.randint(1, 25))
                else:
                    # 没有库存，只能生成已归还的记录
                    status = "returned"
                    return_time = borrow_time + timedelta(days=random.randint(1, 35))
                
                # 如果已归还但超期，标记为逾期
                if status == "returned" and return_time > due_time:
                    status = "overdue"
                
                renewal_count = random.randint(0, 2) if status == "returned" else 0
                
                data.append((
                    user_id, book_id, borrow_time, due_time,
                    return_time, status, renewal_count
                ))
                
                # 更新借阅次数
                book['borrowed_count'] += 1
                
                if len(data) >= batch_size:
                    self.cursor.executemany(sql, data)
                    self.connection.commit()
                    data = []
            
            # 插入剩余数据
            if data:
                self.cursor.executemany(sql, data)
                self.connection.commit()
            
            # 更新图书库存和借阅次数
            print("🔄 更新图书库存和借阅次数...")
            update_sql = "UPDATE book SET stock = %s, borrowed_count = %s WHERE id = %s"
            update_data = [(info['stock'], info['borrowed_count'], book_id) for book_id, info in book_info.items()]
            
            # 分批更新
            batch_size = 500
            for i in range(0, len(update_data), batch_size):
                batch = update_data[i:i+batch_size]
                self.cursor.executemany(update_sql, batch)
                self.connection.commit()
            
            print(f"✅ 借阅记录生成完成，共 {count} 条")
            
        finally:
            # 恢复触发器
            self.restore_triggers()
    
    def generate_comments(self, count):
        """生成评论数据"""
        print(f"💬 正在生成 {count} 条评论数据...")
        
        # 临时禁用评分触发器，我们自己更新评分
        self.disable_triggers()
        
        try:
            # 获取用户ID
            self.cursor.execute("SELECT id FROM user WHERE role = 'reader'")
            user_ids = [row[0] for row in self.cursor.fetchall()]
            
            # 获取图书ID
            self.cursor.execute("SELECT id FROM book")
            book_ids = [row[0] for row in self.cursor.fetchall()]
            
            if not user_ids or not book_ids:
                print("❌ 需要先生成用户和图书数据！")
                return
            
            sql = """
            INSERT INTO book_comment (user_id, book_id, rating, comment, is_approved)
            VALUES (%s, %s, %s, %s, 1)
            """
            
            batch_size = 500
            data = []
            
            for i in tqdm(range(count), desc="生成评论"):
                user_id = random.choice(user_ids)
                book_id = random.choice(book_ids)
                rating = random.randint(1, 5)
                comment = random.choice(self.comments)
                
                data.append((user_id, book_id, rating, comment))
                
                if len(data) >= batch_size:
                    self.cursor.executemany(sql, data)
                    self.connection.commit()
                    data = []
            
            if data:
                self.cursor.executemany(sql, data)
                self.connection.commit()
            
            print(f"✅ 评论数据生成完成，共 {count} 条")
            
            # 手动更新图书平均评分
            print("📊 更新图书平均评分...")
            self.cursor.execute("""
                UPDATE book b
                SET avg_rating = (
                    SELECT ROUND(AVG(rating), 2) 
                    FROM book_comment bc 
                    WHERE bc.book_id = b.id
                    GROUP BY bc.book_id
                )
                WHERE EXISTS (
                    SELECT 1 FROM book_comment bc WHERE bc.book_id = b.id
                )
            """)
            self.connection.commit()
            print("✅ 图书评分更新完成")
            
        finally:
            # 恢复触发器
            self.restore_triggers()
    
    def generate_reservations(self, count):
        """生成预约记录"""
        print(f"⏳ 正在生成 {count} 条预约记录...")
        
        # 获取用户ID
        self.cursor.execute("SELECT id FROM user WHERE role = 'reader'")
        user_ids = [row[0] for row in self.cursor.fetchall()]
        
        # 获取库存为0的图书
        self.cursor.execute("SELECT id FROM book WHERE stock = 0")
        zero_stock_books = [row[0] for row in self.cursor.fetchall()]
        
        # 如果库存为0的图书不够，再选择一些库存较少的
        if len(zero_stock_books) < count:
            self.cursor.execute("SELECT id FROM book WHERE stock <= 2")
            low_stock_books = [row[0] for row in self.cursor.fetchall()]
            book_ids = list(set(zero_stock_books + low_stock_books))
        else:
            book_ids = zero_stock_books
        
        if not user_ids or not book_ids:
            print("⚠️ 没有找到合适的图书生成预约记录")
            return
        
        sql = """
        INSERT INTO reservation (user_id, book_id, queue_position, reserve_time, status)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        batch_size = 200
        data = []
        
        # 为每本图书维护队列位置
        book_queues = {}
        
        for i in tqdm(range(count), desc="生成预约"):
            user_id = random.choice(user_ids)
            book_id = random.choice(book_ids)
            
            # 获取当前队列位置
            if book_id not in book_queues:
                self.cursor.execute("""
                    SELECT MAX(queue_position) FROM reservation 
                    WHERE book_id = %s AND status IN ('waiting', 'notified')
                """, (book_id,))
                result = self.cursor.fetchone()
                book_queues[book_id] = result[0] or 0
            
            book_queues[book_id] += 1
            queue_position = book_queues[book_id]
            
            # 随机预约时间
            reserve_time = datetime.now() - timedelta(days=random.randint(0, 30))
            
            # 状态分布：60%等待中，20%已通知，15%已取消，5%已完成
            rand_val = random.random()
            if rand_val < 0.6:
                status = "waiting"
            elif rand_val < 0.8:
                status = "notified"
            elif rand_val < 0.95:
                status = "cancelled"
            else:
                status = "finished"
            
            data.append((user_id, book_id, queue_position, reserve_time, status))
            
            if len(data) >= batch_size:
                self.cursor.executemany(sql, data)
                self.connection.commit()
                data = []
        
        if data:
            self.cursor.executemany(sql, data)
            self.connection.commit()
        
        print(f"✅ 预约记录生成完成，共 {count} 条")
    
    def generate_notifications(self, count_per_user=2):
        """生成系统通知"""
        print(f"🔔 正在生成系统通知...")
        
        # 获取所有用户
        self.cursor.execute("SELECT id FROM user")
        user_ids = [row[0] for row in self.cursor.fetchall()]
        
        sql = """
        INSERT INTO notification (user_id, title, content, type, is_read)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        data = []
        notification_templates = [
            ("借阅提醒", "您借阅的图书即将到期，请及时归还。", "overdue"),
            ("新书推荐", "根据您的借阅历史，我们为您推荐了一些新书。", "system"),
            ("活动通知", "图书馆将举办读书分享会，欢迎参加。", "system"),
            ("预约成功", "您预约的图书已经到货，请及时借阅。", "reservation"),
            ("系统维护", "图书馆系统将于本周末进行维护升级。", "system"),
            ("借阅超期", "您有图书已超期，请尽快归还。", "overdue"),
            ("欢迎使用", "欢迎使用图书馆管理系统，祝您使用愉快！", "system"),
            ("图书归还", "您借阅的图书已成功归还，感谢使用！", "return"),
            ("借阅成功", "您已成功借阅图书，请按时归还。", "borrow")
        ]
        
        for user_id in tqdm(user_ids, desc="生成通知"):
            # 每个用户生成1-3条通知
            for _ in range(random.randint(1, count_per_user)):
                title, content, notif_type = random.choice(notification_templates)
                is_read = random.choice([0, 1])  # 0表示未读，1表示已读
                
                # 个性化内容
                if "借阅的图书" in content:
                    # 获取用户的借阅图书
                    self.cursor.execute("""
                        SELECT b.title FROM borrow_record br
                        JOIN book b ON br.book_id = b.id
                        WHERE br.user_id = %s AND br.status = 'borrowed'
                        LIMIT 1
                    """, (user_id,))
                    result = self.cursor.fetchone()
                    if result:
                        content = f"您借阅的《{result[0]}》即将到期，请及时归还。"
                
                data.append((user_id, title, content, notif_type, is_read))
                
                if len(data) >= 100:
                    self.cursor.executemany(sql, data)
                    self.connection.commit()
                    data = []
        
        if data:
            self.cursor.executemany(sql, data)
            self.connection.commit()
        
        print(f"✅ 系统通知生成完成")
    
    def generate_operation_logs(self, count):
        """生成操作日志"""
        print(f"📝 正在生成 {count} 条操作日志...")
        
        # 获取用户ID
        self.cursor.execute("SELECT id FROM user")
        user_ids = [row[0] for row in self.cursor.fetchall()]
        
        actions = ['登录', '登出', '借阅图书', '归还图书', '预约图书', '取消预约', '添加评论', '修改个人信息']
        table_names = ['user', 'book', 'borrow_record', 'reservation', 'book_comment']
        
        sql = """
        INSERT INTO operation_log (user_id, action, table_name, record_id, ip_address)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        batch_size = 200
        data = []
        
        for i in tqdm(range(count), desc="生成操作日志"):
            user_id = random.choice(user_ids) if random.random() > 0.1 else None  # 10%的记录没有用户ID
            action = random.choice(actions)
            table_name = random.choice(table_names)
            record_id = random.randint(1, 1000)
            ip_address = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
            
            data.append((user_id, action, table_name, record_id, ip_address))
            
            if len(data) >= batch_size:
                self.cursor.executemany(sql, data)
                self.connection.commit()
                data = []
        
        if data:
            self.cursor.executemany(sql, data)
            self.connection.commit()
        
        print(f"✅ 操作日志生成完成，共 {count} 条")
    
    def get_random_chinese_name(self):
        """生成随机中文姓名"""
        surnames = ["张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴",
                   "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗"]
        names = ["伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "洋",
                "勇", "艳", "杰", "娟", "涛", "明", "超", "秀兰", "霞", "平",
                "刚", "军", "波", "峰", "建", "华", "国", "民", "志", "文"]
        return random.choice(surnames) + random.choice(names)
    
    def verify_data(self):
        """验证生成的数据"""
        print("\n" + "="*50)
        print("📊 数据生成验证报告")
        print("="*50)
        
        try:
            tables = [
                ('user', '用户'),
                ('book', '图书'),
                ('borrow_record', '借阅记录'),
                ('book_comment', '评论'),
                ('reservation', '预约'),
                ('notification', '通知'),
                ('operation_log', '操作日志')
            ]
            
            for table, name in tables:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                print(f"{name}数量: {count:>8} 条")
            
            # 检查借阅统计
            self.cursor.execute("""
                SELECT 
                    SUM(CASE WHEN status = 'borrowed' THEN 1 ELSE 0 END) as borrowed,
                    SUM(CASE WHEN status = 'returned' THEN 1 ELSE 0 END) as returned,
                    SUM(CASE WHEN status = 'overdue' THEN 1 ELSE 0 END) as overdue
                FROM borrow_record
            """)
            borrowed, returned, overdue = self.cursor.fetchone()
            print(f"借阅中: {borrowed or 0:>8} 本")
            print(f"已归还: {returned or 0:>8} 本")
            print(f"已逾期: {overdue or 0:>8} 本")
            
            # 检查库存是否正确（不应该有负数）
            self.cursor.execute("SELECT COUNT(*) FROM book WHERE stock < 0")
            negative_stock = self.cursor.fetchone()[0]
            print(f"库存负数: {negative_stock:>8} 本")
            
            if negative_stock > 0:
                print("❌ 错误：发现库存为负数的图书！")
                self.cursor.execute("SELECT id, title, stock, total FROM book WHERE stock < 0 LIMIT 5")
                for row in self.cursor.fetchall():
                    print(f"  图书ID {row[0]}: 《{row[1]}》 库存: {row[2]} / 总库存: {row[3]}")
            else:
                print("✅ 所有图书库存正常")
            
            # 检查图书评分分布
            self.cursor.execute("SELECT AVG(avg_rating) FROM book WHERE avg_rating > 0")
            avg_rating = self.cursor.fetchone()[0]
            print(f"平均评分: {avg_rating or 0:.2f}")
            
            # 显示分类统计
            print("\n📊 图书分类统计:")
            self.cursor.execute("""
                SELECT c.name, COUNT(b.id) as count, 
                       SUM(b.stock) as total_stock, 
                       SUM(b.total) as total_copies
                FROM book_category c
                LEFT JOIN book b ON c.id = b.category_id
                GROUP BY c.id, c.name
                ORDER BY count DESC
            """)
            for row in self.cursor.fetchall():
                print(f"  {row[0]}: {row[1]:>5} 本 (库存: {row[2] or 0}/{row[3] or 0})")
            
            print("="*50)
            print("✅ 数据验证完成")
            
        except Exception as e:
            print(f"❌ 数据验证失败: {e}")
    
    def generate_all_data(self, config):
        """生成所有测试数据"""
        try:
            print("="*60)
            print("🚀 开始生成图书馆系统测试数据")
            print("="*60)
            start_time = datetime.now()
            
            # 1. 优化数据库设置
            self.optimize_database()
            
            # 2. 清理现有数据
            if not self.clear_existing_data():
                return
            
            # 3. 生成用户数据
            self.generate_users(config.get('users', 1000))
            
            # 4. 生成图书数据
            self.generate_books(config.get('books', 5000))
            
            # 5. 生成借阅记录（修复库存问题）
            self.generate_borrow_records(config.get('borrows', 10000))
            
            # 6. 生成评论数据
            self.generate_comments(config.get('comments', 20000))
            
            # 7. 生成预约记录
            self.generate_reservations(config.get('reservations', 2000))
            
            # 8. 生成系统通知
            self.generate_notifications(config.get('notifications_per_user', 2))
            
            # 9. 生成操作日志
            self.generate_operation_logs(config.get('operation_logs', 5000))
            
            # 10. 恢复数据库设置
            self.restore_database_settings()
            
            # 11. 验证数据
            self.verify_data()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("\n" + "="*60)
            print("🎉 所有测试数据生成完成！")
            print(f"⏱️  总耗时: {duration:.2f} 秒")
            print("="*60)
            
        except Exception as e:
            self.connection.rollback()
            print(f"\n❌ 生成数据时出错: {e}")
            raise
    
    def export_sample_data(self, filename="sample_data.json"):
        """导出少量样本数据供测试使用"""
        try:
            print(f"\n📄 导出样本数据到 {filename}...")
            
            sample_data = {
                'users': [],
                'books': [],
                'admin': {},
                'categories': []
            }
            
            # 获取管理员信息
            self.cursor.execute("SELECT username, password, real_name FROM user WHERE role = 'admin' LIMIT 1")
            admin_data = self.cursor.fetchone()
            if admin_data:
                sample_data['admin'] = {
                    'username': admin_data[0],
                    'password': '123456',  # 默认密码
                    'real_name': admin_data[2]
                }
            
            # 获取分类信息
            self.cursor.execute("SELECT name, description FROM book_category")
            for row in self.cursor.fetchall():
                sample_data['categories'].append({
                    'name': row[0],
                    'description': row[1]
                })
            
            # 获取一些用户
            self.cursor.execute("SELECT username, real_name, email FROM user WHERE role = 'reader' LIMIT 5")
            for row in self.cursor.fetchall():
                sample_data['users'].append({
                    'username': row[0],
                    'password': '123456',  # 默认密码
                    'real_name': row[1],
                    'email': row[2]
                })
            
            # 获取一些图书
            self.cursor.execute("SELECT title, author, publisher, isbn, stock, total FROM book LIMIT 10")
            for row in self.cursor.fetchall():
                sample_data['books'].append({
                    'title': row[0],
                    'author': row[1],
                    'publisher': row[2],
                    'isbn': row[3],
                    'stock': row[4],
                    'total': row[5]
                })
            
            # 保存到文件
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 样本数据已导出到 {filename}")
            
        except Exception as e:
            print(f"❌ 导出样本数据失败: {e}")


def main():
    """主函数"""
    # 数据库配置
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'Wu20050612!',
        'database': 'library_system'
    }
    
    # 数据量配置（可以根据需要调整）
    data_config = {
        'users': 1000,           # 1000个用户
        'books': 5000,           # 5000本书
        'borrows': 10000,        # 10000条借阅记录
        'comments': 20000,       # 20000条评论
        'reservations': 2000,    # 2000条预约记录
        'notifications_per_user': 2,  # 每个用户2条通知
        'operation_logs': 5000   # 5000条操作日志
    }
    
    print("📚 图书馆系统测试数据生成工具")
    print("-" * 40)
    
    # 显示配置
    print("当前配置：")
    for key, value in data_config.items():
        print(f"  {key}: {value}")
    
    print("\n注意：")
    print("  1. 将删除所有现有测试数据（保留管理员和初始5本图书）")
    print("  2. 生成过程可能需要几分钟时间")
    print("  3. 请确保数据库服务正在运行")
    print("  4. 此版本会临时删除和恢复触发器，确保库存正确")
    
    confirm = input("\n是否继续？(y/n): ")
    if confirm.lower() != 'y':
        print("❌ 用户取消操作")
        return
    
    # 生成数据
    generator = LibraryDataGenerator(db_config)
    
    try:
        if generator.connect():
            generator.generate_all_data(data_config)
            generator.export_sample_data()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
    finally:
        generator.close()


if __name__ == "__main__":
    main()