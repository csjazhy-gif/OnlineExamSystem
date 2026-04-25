-- 通知公告表
CREATE TABLE IF NOT EXISTS announcement (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL COMMENT '公告标题',
  content TEXT NOT NULL COMMENT '公告内容',
  publisher_id INT COMMENT '发布者ID',
  publisher_name VARCHAR(50) COMMENT '发布者姓名',
  publisher_role VARCHAR(20) COMMENT '发布者角色: admin/teacher',
  target_role VARCHAR(20) DEFAULT 'all' COMMENT '目标角色: all/student/teacher',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  status INT DEFAULT 1 COMMENT '状态: 1-已发布, 0-草稿'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统公告表';

-- 系统操作日志表
CREATE TABLE IF NOT EXISTS system_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  operator_id INT COMMENT '操作者ID',
  operator_name VARCHAR(50) COMMENT '操作者姓名',
  operator_role VARCHAR(20) COMMENT '操作者角色',
  action VARCHAR(100) NOT NULL COMMENT '操作类型',
  detail TEXT COMMENT '操作详情',
  ip VARCHAR(50) COMMENT 'IP地址',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统操作日志表';

-- 插入一些示例公告
INSERT INTO announcement (title, content, publisher_id, publisher_name, publisher_role, target_role) VALUES
('欢迎使用在线考试系统', '亲爱的同学们，欢迎使用在线考试系统！请熟悉系统功能，如有问题请联系管理员。', 1, '管理员', 'admin', 'all'),
('期中考试安排通知', '期中考试将于下周一开始，请同学们做好复习准备。考试期间请遵守考场纪律。', 1, '管理员', 'admin', 'student'),
('系统维护通知', '系统将于本周六晚22:00-次日6:00进行维护升级，届时系统将暂停服务。', 1, '管理员', 'admin', 'all');

-- 插入一些示例日志
INSERT INTO system_log (operator_id, operator_name, operator_role, action, detail, ip) VALUES
(1, '管理员', 'admin', '系统登录', '管理员登录系统', '127.0.0.1'),
(1, '管理员', 'admin', '发布公告', '发布公告：欢迎使用在线考试系统', '127.0.0.1'),
(1, '管理员', 'admin', '创建考试', '创建考试：2024年期中考试', '127.0.0.1');
