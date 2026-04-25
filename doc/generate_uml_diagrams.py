# -*- coding: utf-8 -*-
"""
在线考试系统 — 全量 UML 图自动生成脚本
生成 8 种标准 UML 图的 PlantUML 源文件 (.puml) 并尝试渲染为 PNG 图片。
包含：用例图、活动图、状态图、顺序图、协作图、类图、构件图、部署图
"""

import os, subprocess, urllib.request, urllib.error, pathlib

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uml_diagrams")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# 1. 用例图 (Use Case Diagram)
# ─────────────────────────────────────────────
USE_CASE = r"""@startuml 用例图_在线考试系统
left to right direction
skinparam packageStyle rectangle
skinparam actorStyle awesome
skinparam usecase {
  BackgroundColor #EEF5FF
  BorderColor #3B82F6
  ArrowColor #334155
}
skinparam actor {
  BackgroundColor #3B82F6
  BorderColor #1E40AF
}

actor "学生" as Student
actor "教师" as Teacher
actor "管理员" as Admin

rectangle "在线考试系统" {

  ' ============ 公共功能 ============
  usecase "用户登录" as UC_Login
  usecase "验证码校验" as UC_Captcha
  usecase "人脸识别验证" as UC_Face
  usecase "修改密码" as UC_ChangePwd
  usecase "查看公告" as UC_ViewAnnouncement

  ' ============ 学生功能 ============
  usecase "参加正式考试" as UC_TakeExam
  usecase "答题交卷" as UC_Submit
  usecase "自动阅卷(客观题)" as UC_AutoGrade
  usecase "查看成绩" as UC_ViewScore
  usecase "查看考试历史" as UC_ExamHistory
  usecase "模拟考试" as UC_MockExam
  usecase "智能专项练习" as UC_SmartPractice
  usecase "错题本" as UC_WrongBook
  usecase "重做错题" as UC_Redo
  usecase "学习曲线" as UC_StudyCurve
  usecase "薄弱知识点分析" as UC_WeakPoints
  usecase "个人中心" as UC_StudentCenter
  usecase "消息通知" as UC_Message

  ' ============ 教师功能 ============
  usecase "管理题库" as UC_ManageQuestion
  usecase "管理选择题" as UC_ManageMulti
  usecase "管理填空题" as UC_ManageFill
  usecase "管理判断题" as UC_ManageJudge
  usecase "管理主观题" as UC_ManageSubjective
  usecase "组卷管理" as UC_ManagePaper
  usecase "遗传算法智能组卷" as UC_GeneticPaper
  usecase "发布考试" as UC_PublishExam
  usecase "批阅主观题" as UC_Scoring
  usecase "系统自动阅卷" as UC_SysAutoGrade
  usecase "管理学生" as UC_ManageStudent
  usecase "查看所有成绩" as UC_AllGrades
  usecase "学生画像分析" as UC_Profile
  usecase "试卷质量分析" as UC_PaperQuality
  usecase "发布公告" as UC_PubAnnouncement
  usecase "违规记录查看" as UC_Violation
  usecase "教师中心" as UC_TeacherCenter

  ' ============ 管理员功能 ============
  usecase "管理教师" as UC_ManageTeacher
  usecase "AI智能出题" as UC_AIQuestion
  usecase "系统设置" as UC_SysSettings
  usecase "系统日志" as UC_SysLog

  ' ─── 学生关联 ───
  Student --> UC_Login
  Student --> UC_TakeExam
  Student --> UC_ViewScore
  Student --> UC_ExamHistory
  Student --> UC_MockExam
  Student --> UC_SmartPractice
  Student --> UC_WrongBook
  Student --> UC_StudyCurve
  Student --> UC_WeakPoints
  Student --> UC_StudentCenter
  Student --> UC_ViewAnnouncement
  Student --> UC_Message
  Student --> UC_ChangePwd

  ' ─── 教师关联 ───
  Teacher --> UC_Login
  Teacher --> UC_ManageQuestion
  Teacher --> UC_ManagePaper
  Teacher --> UC_GeneticPaper
  Teacher --> UC_PublishExam
  Teacher --> UC_Scoring
  Teacher --> UC_ManageStudent
  Teacher --> UC_AllGrades
  Teacher --> UC_Profile
  Teacher --> UC_PaperQuality
  Teacher --> UC_PubAnnouncement
  Teacher --> UC_Violation
  Teacher --> UC_TeacherCenter
  Teacher --> UC_AIQuestion
  Teacher --> UC_ChangePwd

  ' ─── 管理员关联 ───
  Admin --> UC_Login
  Admin --> UC_ManageTeacher
  Admin --> UC_AIQuestion
  Admin --> UC_SysSettings
  Admin --> UC_SysLog
  Admin --> UC_ChangePwd

  ' ─── include 关系 ───
  UC_Login ..> UC_Captcha : <<include>>
  UC_TakeExam ..> UC_Face : <<include>>
  UC_TakeExam ..> UC_Submit : <<include>>
  UC_Submit ..> UC_AutoGrade : <<include>>

  ' ─── extend 关系 ───
  UC_WrongBook <.. UC_Redo : <<extend>>
  UC_Scoring <.. UC_SysAutoGrade : <<extend>>
  UC_ManageQuestion <.. UC_ManageMulti : <<extend>>
  UC_ManageQuestion <.. UC_ManageFill : <<extend>>
  UC_ManageQuestion <.. UC_ManageJudge : <<extend>>
  UC_ManageQuestion <.. UC_ManageSubjective : <<extend>>
}
@enduml
"""

# ─────────────────────────────────────────────
# 2. 活动图 (Activity Diagram) — 考试流程
# ─────────────────────────────────────────────
ACTIVITY = r"""@startuml 活动图_考试流程
skinparam activity {
  BackgroundColor #EEF5FF
  BorderColor #3B82F6
  ArrowColor #334155
}
skinparam swimlane {
  BorderColor #3B82F6
}

|学生|
start
:登录系统;
:输入账号密码;
:验证码校验;
if (登录成功?) then (是)
  :进入学生首页;
else (否)
  :提示错误信息;
  stop
endif

:选择考试;

if (需要人脸识别?) then (是)
  :人脸识别验证;
  if (验证通过?) then (是)
  else (否)
    :提示验证失败;
    stop
  endif
else (否)
endif

if (考试时间窗口内?) then (是)
  :进入答题页面;
else (否)
  :提示不在考试时间;
  stop
endif

:开始倒计时;

repeat
  :作答题目;
  note right
    选择题 → 选择 ABCD
    填空题 → 输入答案
    判断题 → 选择对/错
    主观题 → 文本作答
  end note
  :切换下一题;
repeat while (还有未答题目?) is (是)

if (主动交卷 / 时间到?) then (交卷)
  :提交答案;
else (继续)
  :继续作答;
  stop
endif

|系统|
:客观题自动阅卷;
note right
  选择题: 比对正确答案
  填空题: 多答案匹配
  判断题: T/F 比对
end note
:计算客观题得分(ptScore);
:保存成绩记录;
:记录错题到错题本;

if (含主观题?) then (是)
  :etScore 设为 -1 (待批阅);
  |教师|
  :查看待批阅试卷;
  :逐题评分主观题;
  if (使用系统自动阅卷?) then (是)
    :NLP关键词+相似度评分;
  else (否)
    :教师手动打分;
  endif
  :计算最终成绩;
  note right
    etScore = ptScore + 主观题得分
  end note
  :更新 etScore 和 score;
else (否)
  :etScore = ptScore;
  :成绩即时生效;
endif

|学生|
:查看最终成绩;
:查看答题详情;

stop
@enduml
"""

# ─────────────────────────────────────────────
# 3. 状态图 (State Diagram) — 成绩状态
# ─────────────────────────────────────────────
STATE = r"""@startuml 状态图_成绩生命周期
skinparam state {
  BackgroundColor #EEF5FF
  BorderColor #3B82F6
  ArrowColor #334155
}

[*] --> 未参加 : 考试已发布

未参加 --> 答题中 : 学生开始考试
答题中 --> 答题中 : 切换题目/修改答案
答题中 --> 已交卷 : 主动交卷/倒计时结束

已交卷 --> 客观题已批 : 系统自动阅卷\n计算ptScore

客观题已批 --> 待教师批阅 : 含主观题\netScore = -1
客观题已批 --> 成绩已确认 : 纯客观题\netScore = ptScore

待教师批阅 --> 批阅中 : 教师开始批阅
批阅中 --> 批阅中 : 逐题评分
批阅中 --> 成绩已确认 : 所有主观题评分完成\netScore = ptScore + 主观得分

成绩已确认 --> [*]

state 答题中 {
  [*] --> 选择题
  选择题 --> 填空题
  填空题 --> 判断题
  判断题 --> 主观题
  主观题 --> [*]
}

state 违规监控 {
  [*] --> 正常答题
  正常答题 --> 检测到违规 : 切屏/复制/粘贴
  检测到违规 --> 正常答题 : 记录违规
  检测到违规 --> 强制交卷 : 违规次数超限
}
@enduml
"""

# ─────────────────────────────────────────────
# 4. 顺序图 (Sequence Diagram) — 考试交卷流程
# ─────────────────────────────────────────────
SEQUENCE = r"""@startuml 顺序图_考试交卷流程
skinparam sequence {
  ArrowColor #334155
  LifeLineBorderColor #3B82F6
  ParticipantBackgroundColor #EEF5FF
  ParticipantBorderColor #3B82F6
}

actor 学生
participant "answer.vue\n(答题前端)" as FE
participant "ScoreController\n(成绩控制器)" as SC
participant "AnswerMapper\n(答案持久层)" as AM
participant "ScoreMapper\n(成绩持久层)" as SM
participant "WrongQuestionMapper\n(错题持久层)" as WM
database "MySQL" as DB

学生 -> FE : 点击交卷
activate FE

FE -> FE : 客观题自动判分\n(选择/填空/判断)
note right of FE
  objScore = 选择题得分
        + 填空题得分
        + 判断题得分
end note

FE -> FE : 统计 correctCount

alt 含主观题
  FE -> FE : etScore = -1\n(待教师批阅)
else 纯客观题
  FE -> FE : etScore = objScore
end

FE -> AM : POST /answer/add\n提交各题答案
activate AM
AM -> DB : INSERT answer
AM --> FE : 保存成功
deactivate AM

FE -> SC : POST /score\n{ptScore, etScore, score}
activate SC
SC -> SM : add(Score)
activate SM
SM -> DB : INSERT score
SM --> SC : 成功
deactivate SM
SC --> FE : 200 OK
deactivate SC

FE -> WM : POST /study/wrong/record\n记录错题
activate WM
WM -> DB : INSERT/UPDATE wrong_question
WM --> FE : 成功
deactivate WM

FE -> FE : POST /study/record\n保存学习记录

FE --> 学生 : 跳转交卷结果页\n(answerScore.vue)
deactivate FE

== 教师批阅阶段 (如有主观题) ==

actor 教师
participant "ScoringController\n(阅卷控制器)" as GC
participant "SubjectiveAnswerMapper" as SAM

教师 -> GC : POST /scoring/score\n{answerId, teacherScore}
activate GC
GC -> SAM : 更新主观题评分
activate SAM
SAM -> DB : UPDATE subjective_answer
SAM --> GC : 更新成功
deactivate SAM

GC -> SM : 查询 ptScore
activate SM
SM --> GC : ptScore 值
deactivate SM

GC -> GC : finalScore = ptScore + 主观题总分

GC -> SM : updateEtScore\n{etScore, score}
activate SM
SM -> DB : UPDATE score\nSET etScore=?, score=?
SM --> GC : 更新成功
deactivate SM

GC --> 教师 : 批阅完成
deactivate GC
@enduml
"""

# ─────────────────────────────────────────────
# 5. 协作图 (Communication/Collaboration Diagram)
# ─────────────────────────────────────────────
COLLABORATION = r"""@startuml 协作图_系统模块交互
skinparam object {
  BackgroundColor #EEF5FF
  BorderColor #3B82F6
}
skinparam arrow {
  Color #334155
}

object "Vue前端\n(学生/教师/管理员)" as FE
object "LoginController\n用户认证" as Login
object "ExamManageController\n考试管理" as Exam
object "PaperController\n试卷管理" as Paper
object "ScoreController\n成绩管理" as Score
object "ScoringController\n阅卷系统" as Scoring
object "StudyController\n学习中心" as Study
object "AIQuestionController\nAI出题" as AI
object "GeneticPaperController\n智能组卷" as Genetic
object "ViolationController\n违规监控" as Violation
object "AnnouncementController\n公告管理" as Announce
object "FaceRecognitionController\n人脸识别" as Face
object "KMeansClusterController\n学生画像" as KMeans
object "MySQL数据库" as DB

FE --> Login : 1.登录认证
FE --> Exam : 2.查询/发布考试
FE --> Paper : 3.组卷/查询试卷
FE --> Score : 4.提交/查询成绩
FE --> Scoring : 5.批阅主观题
FE --> Study : 6.模拟考试/练习/错题
FE --> AI : 7.AI智能出题
FE --> Genetic : 8.遗传算法组卷
FE --> Violation : 9.违规记录上报
FE --> Announce : 10.公告CRUD
FE --> Face : 11.人脸识别验证
FE --> KMeans : 12.聚类分析

Login --> DB : 1.1 查询用户表
Exam --> Paper : 2.1 关联试卷
Paper --> DB : 3.1 查询题库
Score --> DB : 4.1 读写成绩表
Scoring --> Score : 5.1 更新最终成绩
Study --> DB : 6.1 读写学习记录
Study --> Score : 6.2 保存模拟成绩
AI --> DB : 7.1 保存生成题目
Genetic --> Paper : 8.1 生成试卷
Genetic --> DB : 8.2 读取题库
Violation --> DB : 9.1 保存违规记录
KMeans --> Score : 12.1 读取成绩数据
KMeans --> Study : 12.2 读取学习数据
@enduml
"""

# ─────────────────────────────────────────────
# 6. 类图 (Class Diagram)
# ─────────────────────────────────────────────
CLASS = r"""@startuml 类图_核心实体关系
skinparam class {
  BackgroundColor #EEF5FF
  BorderColor #3B82F6
  ArrowColor #334155
  HeaderBackgroundColor #3B82F6
  HeaderFontColor #FFFFFF
}

package "用户模块" {
  class Student {
    - studentId : Integer
    - studentName : String
    - grade : String
    - major : String
    - clazz : String
    - institute : String
    - tel : String
    - email : String
    - pwd : String
    - cardId : String
    - sex : String
    - role : String
    - faceData : String
  }

  class Teacher {
    - teacherId : Integer
    - teacherName : String
    - institute : String
    - sex : String
    - tel : String
    - email : String
    - pwd : String
    - cardId : String
    - type : String
    - role : String
  }

  class Admin {
    - adminId : Integer
    - adminName : String
    - sex : String
    - tel : String
    - email : String
    - pwd : String
    - cardId : String
    - role : String
  }

  class Login {
    - username : Integer
    - password : String
    - role : Integer
  }
}

package "考试模块" {
  class ExamManage {
    - examCode : Integer
    - description : String
    - source : String
    - paperId : Integer
    - examDate : String
    - totalTime : Integer
    - totalScore : Integer
    - type : String
    - examStartTime : String
    - examEndTime : String
    - multiScore : Integer
    - fillScore : Integer
    - judgeScore : Integer
    - subjectiveScore : Integer
  }

  class PaperManage {
    - paperId : Integer
    - questionType : Integer
    - questionId : Integer
  }

  class Score {
    - scoreId : Integer
    - examCode : Integer
    - studentId : Integer
    - subject : String
    - ptScore : Integer
    - etScore : Integer
    - score : Integer
    - answerDate : String
  }
}

package "题库模块" {
  class MultiQuestion {
    - questionId : Integer
    - subject : String
    - section : String
    - question : String
    - answerA : String
    - answerB : String
    - answerC : String
    - answerD : String
    - rightAnswer : String
    - level : String
    - score : Integer
    - analysis : String
    - source : String
  }

  class FillQuestion {
    - questionId : Integer
    - subject : String
    - question : String
    - answer : String
    - score : Integer
    - level : String
    - section : String
    - analysis : String
    - source : String
  }

  class JudgeQuestion {
    - questionId : Integer
    - subject : String
    - question : String
    - answer : String
    - level : String
    - section : String
    - score : Integer
    - analysis : String
    - source : String
  }

  class SubjectiveQuestion {
    - questionId : Integer
    - subject : String
    - question : String
    - referenceAnswer : String
    - score : Integer
    - section : String
    - level : String
    - analysis : String
    - source : String
    - createTime : Date
  }
}

package "答题与阅卷模块" {
  class SubjectiveAnswer {
    - answerId : Integer
    - questionId : Integer
    - examCode : Integer
    - studentId : Integer
    - studentAnswer : String
    - teacherScore : Integer
    - teacherComment : String
    - scoredBy : Integer
    - scoredTime : Date
    - submitTime : Date
    - status : Integer
  }

  class ViolationRecord {
    - id : Integer
    - examCode : Integer
    - studentId : Integer
    - violationType : String
    - description : String
    - violationTime : String
    - clientIp : String
  }
}

package "学习中心模块" {
  class WrongQuestion {
    - id : Integer
    - studentId : Integer
    - questionType : Integer
    - questionId : Integer
    - wrongCount : Integer
    - lastWrongTime : Date
    - mastered : Integer
    - questionContent : String
    - correctAnswer : String
    - wrongAnswer : String
    - score : Integer
    - subject : String
    - analysis : String
  }

  class StudyRecord {
    - id : Integer
    - studentId : Integer
    - practiceDate : Date
    - practiceType : Integer
    - totalQuestions : Integer
    - correctCount : Integer
    - wrongCount : Integer
    - score : Integer
    - totalScore : Integer
    - accuracy : Double
    - duration : Integer
    - subject : String
    - examCode : Integer
  }

  class Announcement {
    - id : Integer
    - title : String
    - content : String
    - publisherId : Integer
    - publisherName : String
    - publisherRole : String
    - targetRole : String
    - createTime : Date
    - status : Integer
  }
}

' ── 关系 ──
Student "1" -- "*" Score : 参加考试 >
Student "1" -- "*" WrongQuestion : 错题记录 >
Student "1" -- "*" StudyRecord : 学习记录 >
Student "1" -- "*" SubjectiveAnswer : 提交答案 >
Student "1" -- "*" ViolationRecord : 违规记录 >

Teacher "1" -- "*" SubjectiveAnswer : 批阅 >
Teacher "1" -- "*" Announcement : 发布公告 >
Teacher "1" -- "*" ExamManage : 管理考试 >

ExamManage "1" -- "1" PaperManage : 关联试卷 >
ExamManage "1" -- "*" Score : 包含成绩 >
ExamManage "1" -- "*" ViolationRecord : 违规记录 >

PaperManage "*" -- "1" MultiQuestion : 选择题
PaperManage "*" -- "1" FillQuestion : 填空题
PaperManage "*" -- "1" JudgeQuestion : 判断题
PaperManage "*" -- "1" SubjectiveQuestion : 主观题

SubjectiveQuestion "1" -- "*" SubjectiveAnswer : 对应答案 >
@enduml
"""

# ─────────────────────────────────────────────
# 7. 构件图 (Component Diagram)
# ─────────────────────────────────────────────
COMPONENT = r"""@startuml 构件图_系统架构
skinparam component {
  BackgroundColor #EEF5FF
  BorderColor #3B82F6
  ArrowColor #334155
}
skinparam package {
  BackgroundColor #F8FAFC
  BorderColor #94A3B8
}

package "前端层 (Vue.js + Element UI)" {
  [登录注册模块] as C_Login
  [学生考试模块] as C_Exam
  [学习中心模块] as C_Study
  [教师管理模块] as C_Teacher
  [管理员模块] as C_Admin
  [数据可视化模块] as C_Charts
}

package "API网关层 (Nginx / Vite Proxy)" {
  [HTTP代理\n/api → :9201] as C_Proxy
}

package "后端服务层 (Spring Boot)" {

  package "控制器层 (Controller)" {
    [LoginController\n用户认证] as Ctrl_Login
    [ExamManageController\n考试管理] as Ctrl_Exam
    [PaperController\n试卷管理] as Ctrl_Paper
    [ScoreController\n成绩管理] as Ctrl_Score
    [ScoringController\n阅卷系统] as Ctrl_Scoring
    [StudyController\n学习中心] as Ctrl_Study
    [AIQuestionController\nAI出题] as Ctrl_AI
    [GeneticPaperController\n遗传算法组卷] as Ctrl_Genetic
    [ViolationController\n违规监控] as Ctrl_Violation
    [FaceRecognitionController\n人脸识别] as Ctrl_Face
    [KMeansClusterController\n聚类分析] as Ctrl_KMeans
    [AnnouncementController\n公告管理] as Ctrl_Announce
  }

  package "业务逻辑层 (Service)" {
    [ExamManageService] as Svc_Exam
    [PaperService] as Svc_Paper
    [ScoreService] as Svc_Score
    [StudyService] as Svc_Study
    [AIQuestionService] as Svc_AI
    [GeneticPaperService] as Svc_Genetic
    [ViolationService] as Svc_Violation
    [FaceRecognitionService] as Svc_Face
    [KMeansClusterService] as Svc_KMeans
  }

  package "工具层 (Util)" {
    [ScoreCalculator\n分数计算] as U_Calc
    [SubjectiveGradingUtil\n主观题NLP评分] as U_Grade
    [FillQuestionGrader\n填空题评分] as U_Fill
    [SparkAIClient\n星火AI接口] as U_Spark
    [CaptchaUtil\n验证码工具] as U_Captcha
  }

  package "数据访问层 (Mapper)" {
    [ScoreMapper] as M_Score
    [AnswerMapper] as M_Answer
    [StudentMapper] as M_Student
    [ExamManageMapper] as M_Exam
    [PaperMapper] as M_Paper
    [MultiQuestionMapper] as M_Multi
    [FillQuestionMapper] as M_Fill
    [JudgeQuestionMapper] as M_Judge
    [SubjectiveQuestionMapper] as M_Sub
    [WrongQuestionMapper] as M_Wrong
    [StudyRecordMapper] as M_Study
    [ViolationRecordMapper] as M_Viol
  }
}

package "数据层" {
  database "MySQL\nonline_exam_system" as DB
}

package "外部服务" {
  cloud "讯飞星火API\n(AI大模型)" as Spark
}

' ── 前端 → 代理 ──
C_Login --> C_Proxy
C_Exam --> C_Proxy
C_Study --> C_Proxy
C_Teacher --> C_Proxy
C_Admin --> C_Proxy
C_Charts --> C_Proxy

' ── 代理 → 控制器 ──
C_Proxy --> Ctrl_Login
C_Proxy --> Ctrl_Exam
C_Proxy --> Ctrl_Paper
C_Proxy --> Ctrl_Score
C_Proxy --> Ctrl_Scoring
C_Proxy --> Ctrl_Study
C_Proxy --> Ctrl_AI
C_Proxy --> Ctrl_Genetic
C_Proxy --> Ctrl_Violation
C_Proxy --> Ctrl_Face
C_Proxy --> Ctrl_KMeans
C_Proxy --> Ctrl_Announce

' ── 控制器 → 服务 ──
Ctrl_Exam --> Svc_Exam
Ctrl_Paper --> Svc_Paper
Ctrl_Score --> Svc_Score
Ctrl_Study --> Svc_Study
Ctrl_AI --> Svc_AI
Ctrl_Genetic --> Svc_Genetic
Ctrl_Violation --> Svc_Violation
Ctrl_Face --> Svc_Face
Ctrl_KMeans --> Svc_KMeans

' ── 服务 → 工具 ──
Ctrl_Scoring --> U_Grade
Ctrl_Scoring --> U_Fill
Ctrl_Study --> U_Calc
Ctrl_AI --> U_Spark

' ── 服务/Mapper → 数据库 ──
M_Score --> DB
M_Answer --> DB
M_Student --> DB
M_Exam --> DB
M_Paper --> DB
M_Multi --> DB
M_Fill --> DB
M_Judge --> DB
M_Sub --> DB
M_Wrong --> DB
M_Study --> DB
M_Viol --> DB

' ── AI外部调用 ──
U_Spark --> Spark
@enduml
"""

# ─────────────────────────────────────────────
# 8. 部署图 (Deployment Diagram)
# ─────────────────────────────────────────────
DEPLOYMENT = r"""@startuml 部署图_系统部署架构
skinparam node {
  BackgroundColor #EEF5FF
  BorderColor #3B82F6
}
skinparam artifact {
  BackgroundColor #F0FDF4
  BorderColor #22C55E
}
skinparam database {
  BackgroundColor #FEF9C3
  BorderColor #EAB308
}

node "客户端 (浏览器)" as Client {
  artifact "Vue.js SPA\n(学生端/教师端/管理员端)" as VueApp
  artifact "Element UI 组件库" as ElementUI
  artifact "ECharts 数据可视化" as ECharts
  artifact "Axios HTTP客户端" as Axios
}

node "Web服务器 (Nginx)" as WebServer {
  artifact "静态资源 (dist/)" as Static
  artifact "反向代理配置\n(/api → :9201)" as Proxy
}

node "应用服务器 (JVM)" as AppServer {
  artifact "Spring Boot 2.x\n(端口 9201)" as SpringBoot {
    artifact "Controller层\n(31个控制器)" as Controllers
    artifact "Service层\n(26个服务)" as Services
    artifact "Mapper层 (MyBatis)\n(23个数据映射)" as Mappers
    artifact "Util工具层\n(分数计算/NLP评分/AI客户端)" as Utils
  }
  artifact "Interceptor\n(登录拦截器)" as Interceptor
  artifact "GlobalExceptionHandler\n(全局异常处理)" as ExHandler
}

node "数据库服务器 (MySQL)" as DBServer {
  database "online_exam_system" as DB {
    artifact "student (学生表)" as T1
    artifact "teacher (教师表)" as T2
    artifact "admin (管理员表)" as T3
    artifact "exam_manage (考试表)" as T4
    artifact "paper_manage (试卷表)" as T5
    artifact "multi_question (选择题)" as T6
    artifact "fill_question (填空题)" as T7
    artifact "judge_question (判断题)" as T8
    artifact "subjective_question (主观题)" as T9
    artifact "score (成绩表)" as T10
    artifact "subjective_answer (主观答案)" as T11
    artifact "wrong_question (错题表)" as T12
    artifact "study_record (学习记录)" as T13
    artifact "violation_record (违规记录)" as T14
    artifact "announcement (公告表)" as T15
    artifact "system_log (系统日志)" as T16
  }
}

cloud "讯飞星火API\n(大语言模型)" as SparkCloud

Client --> WebServer : HTTPS
WebServer --> AppServer : HTTP :9201
AppServer --> DBServer : JDBC :3306
AppServer --> SparkCloud : WebSocket/HTTPS\n(AI出题 & 自动评分)
@enduml
"""

# ─────────────────────────────────────────────
# 汇总所有图
# ─────────────────────────────────────────────
DIAGRAMS = {
    "01_用例图_在线考试系统": USE_CASE,
    "02_活动图_考试流程": ACTIVITY,
    "03_状态图_成绩生命周期": STATE,
    "04_顺序图_考试交卷流程": SEQUENCE,
    "05_协作图_系统模块交互": COLLABORATION,
    "06_类图_核心实体关系": CLASS,
    "07_构件图_系统架构": COMPONENT,
    "08_部署图_系统部署架构": DEPLOYMENT,
}


def save_puml_files():
    """保存 .puml 源文件"""
    paths = []
    for name, content in DIAGRAMS.items():
        fpath = os.path.join(OUTPUT_DIR, f"{name}.puml")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content.strip())
        paths.append(fpath)
        print(f"  [OK] {name}.puml")
    return paths


def try_render_plantuml(puml_paths):
    """尝试使用本地 plantuml.jar 或在线服务渲染"""
    rendered = 0

    # 方式1: 尝试本地 plantuml.jar
    jar_candidates = [
        "plantuml.jar",
        os.path.expanduser("~/plantuml.jar"),
        r"C:\plantuml\plantuml.jar",
    ]
    jar_path = None
    for p in jar_candidates:
        if os.path.isfile(p):
            jar_path = p
            break

    if jar_path:
        print(f"\n[INFO] 找到 plantuml.jar: {jar_path}")
        for puml in puml_paths:
            try:
                subprocess.run(
                    ["java", "-jar", jar_path, "-charset", "UTF-8", "-tpng", puml],
                    check=True, capture_output=True, timeout=60,
                )
                rendered += 1
                base = os.path.splitext(os.path.basename(puml))[0]
                print(f"  [PNG] {base}.png 已生成")
            except Exception as e:
                print(f"  [WARN] 渲染失败: {os.path.basename(puml)} - {e}")
    else:
        # 方式2: 尝试 plantuml 命令行
        try:
            subprocess.run(["plantuml", "-version"], capture_output=True, check=True, timeout=10)
            print("\n[INFO] 找到 plantuml CLI")
            for puml in puml_paths:
                try:
                    subprocess.run(
                        ["plantuml", "-charset", "UTF-8", "-tpng", puml],
                        check=True, capture_output=True, timeout=60,
                    )
                    rendered += 1
                    base = os.path.splitext(os.path.basename(puml))[0]
                    print(f"  [PNG] {base}.png 已生成")
                except Exception as e:
                    print(f"  [WARN] 渲染失败: {os.path.basename(puml)} - {e}")
        except Exception:
            print("\n[INFO] 未找到本地 plantuml，跳过 PNG 渲染。")
            print("  提示: 可通过以下方式渲染:")
            print("    1. 安装 PlantUML: https://plantuml.com/download")
            print("    2. 在线渲染: https://www.plantuml.com/plantuml/uml/")
            print("    3. VSCode 插件: PlantUML (jebbs.plantuml)")
            print(f"    4. IDEA 插件: PlantUML Integration")

    return rendered


def render_online(puml_paths):
    """使用 requests 直接请求 PlantUML 在线服务 (GET 方式 + PlantUML 编码)"""
    import requests
    import zlib
    import base64

    rendered = 0
    for puml in puml_paths:
        base = os.path.splitext(os.path.basename(puml))[0]
        png_path = os.path.join(OUTPUT_DIR, f"{base}.png")
        try:
            with open(puml, 'r', encoding='utf-8') as f:
                content = f.read()

            # PlantUML 编码: 压缩 → deflate → 自定义 base64
            data = content.encode('utf-8')
            # 使用 -15 wbits 产生 raw deflate (无 zlib header)
            deflated = zlib.compress(data, 9)
            # 去掉 zlib header (2 bytes) and Adler-32 checksum (4 bytes)
            deflated_raw = deflated[2:-4]

            # PlantUML 自定义 base64 表
            b64 = base64.b64encode(deflated_raw).decode('ascii')
            table = str.maketrans(
                'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',
                '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_' 
            )
            encoded = b64.translate(table)

            url = f'http://www.plantuml.com/plantuml/png/{encoded}'
            resp = requests.get(url, timeout=120)

            if resp.status_code == 200 and len(resp.content) > 100:
                with open(png_path, 'wb') as out:
                    out.write(resp.content)
                rendered += 1
                size_kb = len(resp.content) / 1024
                print(f"  [PNG] {base}.png ({size_kb:.1f} KB)")
            else:
                print(f"  [WARN] {base}: HTTP {resp.status_code}, {len(resp.content)} bytes")
        except Exception as e:
            print(f"  [WARN] {base}: {str(e)[:150]}")
    return rendered


def main():
    print("=" * 60)
    print("   在线考试系统 — UML 图自动生成工具")
    print("=" * 60)
    print(f"\n输出目录: {OUTPUT_DIR}\n")

    print("【步骤 1】生成 PlantUML 源文件 (.puml)")
    paths = save_puml_files()
    print(f"\n共生成 {len(paths)} 个 .puml 文件")

    print("\n【步骤 2】尝试本地渲染 PNG 图片...")
    rendered = try_render_plantuml(paths)

    if rendered == 0:
        print("\n【步骤 3】使用在线服务渲染 PNG 图片...")
        rendered = render_online(paths)

    print("\n" + "=" * 60)
    print(f"完成! 共 {len(paths)} 个 .puml 源文件, {rendered} 个 PNG 图片")
    print(f"文件位置: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
