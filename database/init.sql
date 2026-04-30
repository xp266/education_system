
-- =========================================
-- 教育系统智能体数据库初始化脚本
-- 创建日期：2026-04-21
-- =========================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS `education_system` 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `education_system`;

-- =========================================
-- 1. 专业表
-- =========================================
CREATE TABLE IF NOT EXISTS `majors` (
    `major_id` INT NOT NULL AUTO_INCREMENT COMMENT '专业ID',
    `major_code` VARCHAR(20) NOT NULL COMMENT '专业代码',
    `major_name` VARCHAR(100) NOT NULL COMMENT '专业名称',
    `department` VARCHAR(100) DEFAULT NULL COMMENT '所属院系',
    `degree_type` ENUM('本科', '硕士', '博士') DEFAULT '本科' COMMENT '学位类型',
    `duration` INT DEFAULT 4 COMMENT '学制(年)',
    `description` TEXT DEFAULT NULL COMMENT '专业描述',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`major_id`),
    UNIQUE KEY `uk_major_code` (`major_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='专业表';

-- =========================================
-- 2. 教师表
-- =========================================
CREATE TABLE IF NOT EXISTS `teachers` (
    `teacher_id` INT NOT NULL AUTO_INCREMENT COMMENT '教师ID',
    `teacher_no` VARCHAR(20) NOT NULL COMMENT '工号',
    `teacher_name` VARCHAR(50) NOT NULL COMMENT '姓名',
    `gender` ENUM('男', '女') DEFAULT NULL COMMENT '性别',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
    `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    `department` VARCHAR(100) DEFAULT NULL COMMENT '所属院系',
    `title` VARCHAR(50) DEFAULT NULL COMMENT '职称',
    `edu_sys_password` VARCHAR(100) DEFAULT '123456' COMMENT '系统密码',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`teacher_id`),
    UNIQUE KEY `uk_teacher_no` (`teacher_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教师表';

-- =========================================
-- 3. 班级表
-- =========================================
CREATE TABLE IF NOT EXISTS `classes` (
    `class_id` INT NOT NULL AUTO_INCREMENT COMMENT '班级ID',
    `class_name` VARCHAR(50) NOT NULL COMMENT '班级名称',
    `major_id` INT DEFAULT NULL COMMENT '专业ID',
    `grade` VARCHAR(10) DEFAULT NULL COMMENT '年级',
    `head_teacher_id` INT DEFAULT NULL COMMENT '班主任ID',
    `student_count` INT DEFAULT 0 COMMENT '学生人数',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`class_id`),
    KEY `idx_major_id` (`major_id`),
    KEY `idx_head_teacher_id` (`head_teacher_id`),
    CONSTRAINT `fk_class_major` FOREIGN KEY (`major_id`) REFERENCES `majors` (`major_id`) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT `fk_class_teacher` FOREIGN KEY (`head_teacher_id`) REFERENCES `teachers` (`teacher_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='班级表';

-- =========================================
-- 4. 学生表
-- =========================================
CREATE TABLE IF NOT EXISTS `students` (
    `student_id` INT NOT NULL AUTO_INCREMENT COMMENT '学生ID',
    `student_no` VARCHAR(20) NOT NULL COMMENT '学号',
    `student_name` VARCHAR(50) NOT NULL COMMENT '姓名',
    `gender` ENUM('男', '女') DEFAULT NULL COMMENT '性别',
    `birth_date` DATE DEFAULT NULL COMMENT '出生日期',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
    `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    `major_id` INT DEFAULT NULL COMMENT '专业ID',
    `class_id` INT DEFAULT NULL COMMENT '班级ID',
    `enrollment_date` DATE DEFAULT NULL COMMENT '入学日期',
    `status` TINYINT DEFAULT 1 COMMENT '状态(1-在读,2-休学,3-毕业,4-退学)',
    `edu_sys_password` VARCHAR(100) DEFAULT '123456' COMMENT '系统密码',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`student_id`),
    UNIQUE KEY `uk_student_no` (`student_no`),
    KEY `idx_major_id` (`major_id`),
    KEY `idx_class_id` (`class_id`),
    CONSTRAINT `fk_student_major` FOREIGN KEY (`major_id`) REFERENCES `majors` (`major_id`) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT `fk_student_class` FOREIGN KEY (`class_id`) REFERENCES `classes` (`class_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生表';

-- =========================================
-- 5. 课程表
-- =========================================
CREATE TABLE IF NOT EXISTS `courses` (
    `course_id` INT NOT NULL AUTO_INCREMENT COMMENT '课程ID',
    `course_code` VARCHAR(20) NOT NULL COMMENT '课程代码',
    `course_name` VARCHAR(100) NOT NULL COMMENT '课程名称',
    `credits` DECIMAL(3,1) DEFAULT NULL COMMENT '学分',
    `hours` INT DEFAULT NULL COMMENT '学时',
    `course_type` ENUM('必修', '选修', '通识教育') DEFAULT '必修' COMMENT '课程类型',
    `description` TEXT DEFAULT NULL COMMENT '课程描述',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`course_id`),
    UNIQUE KEY `uk_course_code` (`course_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程表';

-- =========================================
-- 6. 授课表
-- =========================================
CREATE TABLE IF NOT EXISTS `course_teachings` (
    `teaching_id` INT NOT NULL AUTO_INCREMENT COMMENT '授课ID',
    `course_id` INT NOT NULL COMMENT '课程ID',
    `teacher_id` INT NOT NULL COMMENT '教师ID',
    `semester` VARCHAR(20) DEFAULT NULL COMMENT '学期',
    `classroom` VARCHAR(50) DEFAULT NULL COMMENT '教室',
    `schedule` VARCHAR(100) DEFAULT NULL COMMENT '上课时间安排',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`teaching_id`),
    KEY `idx_course_id` (`course_id`),
    KEY `idx_teacher_id` (`teacher_id`),
    CONSTRAINT `fk_teaching_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_teaching_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`teacher_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='授课表';

-- =========================================
-- 7. 选课表
-- =========================================
CREATE TABLE IF NOT EXISTS `course_selections` (
    `selection_id` INT NOT NULL AUTO_INCREMENT COMMENT '选课ID',
    `student_id` INT NOT NULL COMMENT '学生ID',
    `teaching_id` INT NOT NULL COMMENT '授课ID',
    `selection_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '选课时间',
    `status` TINYINT DEFAULT 1 COMMENT '状态(1-已选,2-退课)',
    PRIMARY KEY (`selection_id`),
    KEY `idx_student_id` (`student_id`),
    KEY `idx_teaching_id` (`teaching_id`),
    CONSTRAINT `fk_selection_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_selection_teaching` FOREIGN KEY (`teaching_id`) REFERENCES `course_teachings` (`teaching_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='选课表';

-- =========================================
-- 8. 成绩表
-- =========================================
CREATE TABLE IF NOT EXISTS `scores` (
    `score_id` INT NOT NULL AUTO_INCREMENT COMMENT '成绩ID',
    `student_id` INT NOT NULL COMMENT '学生ID',
    `teaching_id` INT NOT NULL COMMENT '授课ID',
    `usual_score` DECIMAL(5,2) DEFAULT NULL COMMENT '平时成绩',
    `final_score` DECIMAL(5,2) DEFAULT NULL COMMENT '期末成绩',
    `total_score` DECIMAL(5,2) DEFAULT NULL COMMENT '总成绩',
    `grade_point` DECIMAL(3,2) DEFAULT NULL COMMENT '绩点',
    `semester` VARCHAR(20) DEFAULT NULL COMMENT '学期',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`score_id`),
    KEY `idx_student_id` (`student_id`),
    KEY `idx_teaching_id` (`teaching_id`),
    KEY `idx_semester` (`semester`),
    CONSTRAINT `fk_score_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_score_teaching` FOREIGN KEY (`teaching_id`) REFERENCES `course_teachings` (`teaching_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成绩表';

-- =========================================
-- 9. 对话会话表
-- =========================================
CREATE TABLE IF NOT EXISTS `conversations` (
    `conversation_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '对话ID',
    `account` VARCHAR(50) NOT NULL COMMENT '账号(学号/工号)',
    `user_role` VARCHAR(20) DEFAULT NULL COMMENT '用户角色',
    `title` VARCHAR(100) DEFAULT '新对话' COMMENT '对话标题',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`conversation_id`),
    KEY `idx_account` (`account`),
    KEY `idx_updated_at` (`updated_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话会话表';

-- =========================================
-- 10. 聊天消息表
-- =========================================
CREATE TABLE IF NOT EXISTS `messages` (
    `message_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '消息ID',
    `conversation_id` BIGINT NOT NULL COMMENT '所属对话ID',
    `role` ENUM('user', 'assistant') NOT NULL COMMENT '消息角色',
    `content` TEXT NOT NULL COMMENT '消息内容',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`message_id`),
    KEY `idx_conversation_id` (`conversation_id`),
    CONSTRAINT `fk_message_conversation` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`conversation_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='聊天消息表';
