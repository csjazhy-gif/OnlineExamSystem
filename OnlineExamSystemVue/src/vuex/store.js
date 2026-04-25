/*
 * @Description: 
 * 
 * @Date: 2023-03-08 20:38:49
 */
import VUE from 'vue'
import VUEX from 'vuex'

VUE.use(VUEX)

const state = {
  isPractice: false, //练习模式标志
  flag: false, //菜单栏左右滑动标志
  userInfo: null,
  menu: [
    {
      index: '0',
      title: '首页',
      icon: 'el-icon-s-home',
      content: [{ item1: '数据看板', path: '/dashboard', icon: "el-icon-monitor" }],
    },
    {
      index: '1',
      title: '考试管理',
      icon: 'el-icon-a-061',
      content: [{ item2: '考试查询', path: '/selectExam', icon: "el-icon-a-042" }, { item3: '添加考试', path: '/addExam', icon: "el-icon-a-07" }],
    },
    {
      index: '2',
      title: '题库管理',
      icon: 'el-icon-a-011',
      content: [{ item2: '题目列表', path: '/selectAnswer', icon: "el-icon-a-041" }, { item3: '新增题目', path: '/addAnswer', icon: "el-icon-a-07" }, { item1: '主观题管理', path: '/subjectiveManage', icon: "el-icon-edit-outline" }, { path: '/addAnswerChildren' }],
    },
    {
      index: '3',
      title: '成绩查询',
      icon: 'el-icon-a-021',
      content: [{ item1: '学生成绩查询', path: '/allStudentsGrade', icon: "el-icon-a-042" }, { path: '/grade' }, { item2: '成绩分段查询', path: '/selectExamToPart', icon: "el-icon-a-042" }, { path: '/scorePart' }, { item3: '试卷质量评价', path: '/paperQuality', icon: "el-icon-data-analysis" }, { item4: '考试违规记录', path: '/violationRecords', icon: "el-icon-warning" }],
    },
    {
      index: '4',
      title: '学生管理',
      icon: 'el-icon-a-01',
      content: [{ item1: '学生管理', path: '/studentManage', icon: "el-icon-a-041" }, { item2: '添加学生', path: '/addStudent', icon: "el-icon-a-07" }, { item3: '人脸修改审批', path: '/faceChangeManage', icon: "el-icon-user" }],
    },
    {
      index: '6',
      title: 'AI智能出题',
      icon: 'el-icon-magic-stick',
      content: [{ item1: 'AI出题', path: '/aiQuestionGenerate', icon: "el-icon-edit-outline" }, { item2: '遗传算法组卷', path: '/geneticPaper', icon: "el-icon-cpu" }, { item3: '生成记录', path: '/generationRecords', icon: "el-icon-document-copy" }],
    },
    {
      index: '7',
      title: '学习报告',
      icon: 'el-icon-data-line',
      content: [{ item1: '学生报告', path: '/studentReport', icon: "el-icon-document" }, { item2: '学生画像', path: '/studentProfile', icon: "el-icon-data-analysis" }],
    },
    {
      index: '8',
      title: '阅卷系统',
      icon: 'el-icon-document-checked',
      content: [{ item1: '主观题阅卷', path: '/scoringSystem', icon: "el-icon-edit" }, { item2: '阅卷记录', path: '/gradingRecords', icon: "el-icon-finished" }],
    },
    {
      index: '9',
      title: '公告管理',
      icon: 'el-icon-bell',
      content: [{ item1: '公告管理', path: '/announcementManage', icon: "el-icon-document-add" }],
    },
    {
      index: '10',
      title: '个人中心',
      icon: 'el-icon-user',
      content: [{ item1: '个人信息', path: '/teacherCenter', icon: "el-icon-setting" }],
    },
    // {
    //   index: '5',
    //   title: '教师管理',
    //   icon: 'icon-Userselect',
    //   content:[{item1:'教师管理',path:'/teacherManage'},{item2: '添加教师',path: '/addTeacher'}],
    // },
    // {
    //   index: '7',
    //   title: '模块管理',
    //   icon: 'icon-module4mokuai',
    //   content:[{item1:'模块操作',path:'/module'}],
    // }
  ],
}
const mutations = {
  practice(state, status) {
    state.isPractice = status
  },
  toggle(state) {
    state.flag = !state.flag
  },
  changeUserInfo(state, info) {
    state.userInfo = info
  }
}
const getters = {

}
const actions = {
  getUserInfo(context, info) {
    context.commit('changeUserInfo', info)
  },
  getPractice(context, status) {
    context.commit('practice', status)
  }
}
export default new VUEX.Store({
  state,
  mutations,
  getters,
  actions,
  // store
})
