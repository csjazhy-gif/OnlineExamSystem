import Vue from 'vue'
import Router from 'vue-router'
Vue.use(Router)



const VueRouterPush = Router.prototype.push

Router.prototype.push = function push(to) {
  return VueRouterPush.call(this, to).catch(err => err)
}

export default new Router({
  routes: [
    {
      path: '/',
      name: 'login', //登录界面
      component: () => import('@/components/common/login.vue')
    },
    {
      path: '/auth', //登录注册页面
      name: 'auth',
      component: () => import('@/components/common/auth.vue')
    },
    {
      path: '/demo', //演示页面
      name: 'demo',
      component: () => import('@/components/common/demo.vue')
    },
    {
      path: '/forgotPassword', //忘记密码
      name: 'forgotPassword',
      component: () => import('@/components/common/forgotPassword.vue')
    },
    {
      path: '/index', //教师主页
      component: () => import('@/components/admin/index.vue'),
      children: [
        {
          path: '/', //首页默认路由
          component: () => import('@/components/common/hello.vue')
        },
        {
          path: '/dashboard', //首页明确路由
          component: () => import('@/components/common/hello.vue')
        },
        {
          path: '/grade', //学生成绩
          component: () => import('@/components/charts/grade.vue')
        },
        {
          path: '/selectExamToPart', //学生分数段
          component: () => import('@/components/teacher/selectExamToPart.vue')
        },
        {
          path: '/scorePart',
          component: () => import('@/components/charts/scorePart.vue')
        },
        {
          path: '/allStudentsGrade', //所有学生成绩统计
          component: () => import('@/components/teacher/allStudentsGrade.vue')
        },
        // {
        //   path: '/examDescription', //考试管理功能描述
        //   component: () => import('@/components/teacher/examDescription')
        // },
        {
          path: '/selectExam', //查询所有考试
          component: () => import('@/components/teacher/selectExam.vue')
        },
        {
          path: '/addExam', //添加考试
          component: () => import('@/components/teacher/addExam.vue')
        },
        // {
        //   path: '/answerDescription', //题库管理功能介绍
        //   component: ()=> import('@/components/teacher/answerDescription')
        // },
        {
          path: '/selectAnswer', //查询所有题库
          component: () => import('@/components/teacher/selectAnswer.vue')
        },
        {
          path: '/addAnswer', //增加题库主界面
          component: () => import('@/components/teacher/addAnswer.vue')
        },
        {
          path: '/editAnswerChildren', //编辑题库主界面
          component: () => import('@/components/teacher/editAnswerChildren.vue')
        },
        {
          path: '/addAnswerChildren', //点击试卷跳转到添加题库页面
          component: () => import('@/components/teacher/addAnswerChildren.vue')
        },
        {
          path: '/studentManage', //学生管理界面
          component: () => import('@/components/teacher/studentManage.vue')
        },
        {
          path: '/addStudent', //添加学生
          component: () => import('@/components/teacher/addStudent.vue')
        },
        {
          path: '/teacherManage',
          component: () => import('@/components/admin/teacherManage.vue')
        },
        {
          path: '/addTeacher',
          component: () => import('@/components/admin/addTeacher.vue')
        },
        {
          path: '/aiQuestionGenerate', //AI智能出题（通用）
          component: () => import('@/components/admin/aiQuestionGenerate.vue')
        },
        {
          path: '/studentReport', //学生学习报告
          component: () => import('@/components/teacher/studentReport.vue')
        },
        {
          path: '/subjectiveManage', //主观题管理
          component: () => import('@/components/teacher/subjectiveManage.vue')
        },
        {
          path: '/scoringSystem', //阅卷系统
          component: () => import('@/components/teacher/scoringSystem.vue')
        },
        {
          path: '/gradingRecords', //阅卷记录
          component: () => import('@/components/teacher/gradingRecords.vue')
        },
        {
          path: '/geneticPaper', //遗传算法智能组卷
          component: () => import('@/components/teacher/geneticPaper.vue')
        },
        {
          path: '/generationRecords', //生成记录管理
          component: () => import('@/components/teacher/generationRecords.vue')
        },
        {
          path: '/studentProfile', //学生群体画像
          component: () => import('@/components/teacher/studentProfile.vue')
        },
        {
          path: '/faceChangeManage', //人脸修改审批
          component: () => import('@/components/teacher/faceChangeManage.vue')
        },
        {
          path: '/paperQuality', //试卷质量评价
          component: () => import('@/components/teacher/paperQuality.vue')
        },
        {
          path: '/violationRecords', //考试违规记录
          component: () => import('@/components/teacher/violationRecords.vue')
        },
        {
          path: '/teacherCenter', //教师个人中心
          component: () => import('@/components/teacher/teacherCenter.vue')
        },
        {
          path: '/announcementManage', //公告管理
          component: () => import('@/components/teacher/announcementManage.vue')
        },
        {
          path: '/systemLog', //系统日志（管理员）
          component: () => import('@/components/admin/systemLog.vue')
        },
        {
          path: '/systemSettings', //系统设置（管理员）
          component: () => import('@/components/admin/systemSettings.vue')
        }
      ]
    },
    {
      path: '/student',
      component: () => import('@/components/student/index.vue'),
      children: [
        { path: "/", component: () => import('@/components/student/myExam.vue') },
        { path: '/startExam', component: () => import('@/components/student/startExam.vue') },
        { path: '/manager', component: () => import('@/components/student/manager.vue') },
        { path: '/examMsg', component: () => import('@/components/student/examMsg.vue') },
        { path: '/message', component: () => import('@/components/student/message.vue') },
        { path: '/studentScore', component: () => import("@/components/student/answerScore.vue") },
        { path: '/scoreTable', component: () => import("@/components/student/scoreTable.vue") },
        { path: '/wrongBook', component: () => import('@/components/student/wrongBook.vue') },
        { path: '/studyCurve', component: () => import('@/components/student/studyCurve.vue') },
        { path: '/selfExam', component: () => import('@/components/student/selfExam.vue') },
        { path: '/smartPractice', component: () => import('@/components/student/smartPractice.vue') },
        { path: '/weakPoints', component: () => import('@/components/student/weakPoints.vue') },
        { path: '/mockExam', component: () => import('@/components/student/mockExam.vue') },
        { path: '/examHistory', component: () => import('@/components/student/examHistory.vue') },
        { path: '/studentCenter', component: () => import('@/components/student/studentCenter.vue') },
        { path: '/studentAnnouncement', component: () => import('@/components/student/studentAnnouncement.vue') }
      ]
    },
    { path: '/answer', component: () => import('@/components/student/answer.vue') }
  ]
})
