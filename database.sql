SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS library_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE library_system;

-- 用户表
CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(32) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(128) NOT NULL COMMENT '密码hash',
    real_name VARCHAR(64) COMMENT '真实姓名',
    email VARCHAR(64) COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '电话',
    role ENUM('reader', 'admin') DEFAULT 'reader' COMMENT '角色：读者/管理员',
    status ENUM('active', 'frozen') DEFAULT 'active' COMMENT '账户状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 图书分类表
CREATE TABLE book_category (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(32) NOT NULL UNIQUE COMMENT '分类名称',
    description VARCHAR(256) COMMENT '分类描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图书分类表';

-- 图书表
CREATE TABLE book (
    id INT PRIMARY KEY AUTO_INCREMENT,
    isbn VARCHAR(20) NOT NULL UNIQUE COMMENT 'ISBN',
    title VARCHAR(128) NOT NULL COMMENT '书名',
    author VARCHAR(64) COMMENT '作者',
    publisher VARCHAR(64) COMMENT '出版社',
    price DECIMAL(8, 2) COMMENT '价格',
    description TEXT COMMENT '描述',
    category_id INT COMMENT '分类ID',
    location VARCHAR(64) COMMENT '馆藏位置',
    cover_url VARCHAR(256) COMMENT '封面图片URL',
    stock INT DEFAULT 1 COMMENT '可用库存',
    total INT DEFAULT 1 COMMENT '总库存',
    borrowed_count INT DEFAULT 0 COMMENT '借阅次数',
    avg_rating DECIMAL(3, 2) DEFAULT 0 COMMENT '平均评分',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES book_category(id),
    INDEX idx_title (title),
    INDEX idx_author (author),
    INDEX idx_isbn (isbn),
    INDEX idx_category (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图书表';

-- 借阅记录表
CREATE TABLE borrow_record (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    book_id INT NOT NULL COMMENT '图书ID',
    borrow_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '借阅时间',
    due_time DATETIME COMMENT '应还日期',
    return_time DATETIME COMMENT '实际归还时间',
    status ENUM('borrowed', 'returned', 'overdue') DEFAULT 'borrowed' COMMENT '状态',
    renewal_count INT DEFAULT 0 COMMENT '续借次数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (book_id) REFERENCES book(id),
    INDEX idx_user (user_id),
    INDEX idx_book (book_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='借阅记录表';

-- 预约表
CREATE TABLE reservation (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    book_id INT NOT NULL COMMENT '图书ID',
    queue_position INT COMMENT '队列位置',
    reserve_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '预约时间',
    status ENUM('waiting', 'notified', 'cancelled', 'finished') DEFAULT 'waiting' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (book_id) REFERENCES book(id),
    INDEX idx_book_status (book_id, status),
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预约表';

-- 评论表
CREATE TABLE book_comment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    book_id INT NOT NULL COMMENT '图书ID',
    rating TINYINT NOT NULL COMMENT '评分1-5',
    comment TEXT COMMENT '评论内容',
    is_approved TINYINT(1) DEFAULT 1 COMMENT '是否显示',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (book_id) REFERENCES book(id),
    CHECK (rating BETWEEN 1 AND 5),
    INDEX idx_book (book_id),
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评论表';

-- 系统通知表
CREATE TABLE notification (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    title VARCHAR(128) COMMENT '通知标题',
    content VARCHAR(512) COMMENT '通知内容',
    type ENUM('borrow', 'return', 'reservation', 'overdue', 'system') DEFAULT 'system' COMMENT '通知类型',
    is_read TINYINT(1) DEFAULT 0 COMMENT '是否已读',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    INDEX idx_user_read (user_id, is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知表';

-- 操作日志表
CREATE TABLE operation_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT COMMENT '用户ID',
    action VARCHAR(64) COMMENT '操作类型',
    table_name VARCHAR(32) COMMENT '表名',
    record_id INT COMMENT '记录ID',
    old_value TEXT COMMENT '旧值',
    new_value TEXT COMMENT '新值',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';

-- 插入演示数据
INSERT INTO book_category (name, description) VALUES
('文学', '各类文学作品'),
('技术', '计算机与技术类书籍'),
('历史', '历史相关著作'),
('哲学', '哲学思想著作'),
('艺术', '艺术与设计');

INSERT INTO user (username, password, real_name, email, role) VALUES
('admin','pbkdf2:sha256:600000$XOHHUaFjfiPNjmFx$5f3433c80addca1f454e27be724672ebd211b3b7016b7f7cf7da9d85b37bee45', '管理员', 'admin@library.com', 'admin');

INSERT INTO book (isbn, title, author, publisher, price, category_id, stock, total) VALUES
('978-7-115-29099-8', 'Python编程从入门到精通', '王明', '电子工业出版社', 79.00, 2, 5, 5),
('978-7-115-52311-7', '三体', '刘慈欣', '重庆出版社', 39.80, 1, 3, 5),
('978-7-201-04607-2', '人类简史', '尤瓦尔', '中信出版社', 68.00, 3, 2, 4),
('978-7-010-09127-2', '道德经', '老子', '人民出版社', 18.00, 4, 8, 8),
('978-7-218-13563-4', '大艺术家', '某某', '浙江人民出版社', 58.00, 5, 1, 3);

-- 创建视图：用户借阅统计
CREATE VIEW user_borrow_stats AS
SELECT 
    u.id, u.username, u.real_name,
    COUNT(br.id) as total_borrowed,
    SUM(CASE WHEN br.status = 'borrowed' THEN 1 ELSE 0 END) as current_borrowed,
    SUM(CASE WHEN br.status = 'overdue' THEN 1 ELSE 0 END) as overdue_count
FROM user u
LEFT JOIN borrow_record br ON u.id = br.user_id
GROUP BY u.id;

-- 创建视图：图书热度排行
CREATE VIEW book_popularity AS
SELECT 
    b.id, b.title, b.author,
    COUNT(br.id) as borrow_times,
    ROUND(AVG(bc.rating), 2) as avg_rating,
    COUNT(r.id) as reservation_count
FROM book b
LEFT JOIN borrow_record br ON b.id = br.book_id
LEFT JOIN book_comment bc ON b.id = bc.book_id
LEFT JOIN reservation r ON b.id = r.book_id
GROUP BY b.id
ORDER BY borrow_times DESC;

-- 创建触发器：更新图书评分
DELIMITER //
CREATE TRIGGER update_book_rating AFTER INSERT ON book_comment
FOR EACH ROW
BEGIN
    UPDATE book SET avg_rating = (
        SELECT ROUND(AVG(rating), 2) FROM book_comment WHERE book_id = NEW.book_id
    ) WHERE id = NEW.book_id;
END//
DELIMITER ;

-- 创建触发器：自动更新库存
DELIMITER //
CREATE TRIGGER update_stock_on_borrow AFTER INSERT ON borrow_record
FOR EACH ROW
BEGIN
    UPDATE book SET stock = stock - 1 WHERE id = NEW.book_id;
    UPDATE book SET borrowed_count = borrowed_count + 1 WHERE id = NEW.book_id;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER update_stock_on_return AFTER UPDATE ON borrow_record
FOR EACH ROW
BEGIN
    IF NEW.status = 'returned' AND OLD.status != 'returned' THEN
        UPDATE book SET stock = stock + 1 WHERE id = NEW.book_id;
    END IF;
END//
DELIMITER ;