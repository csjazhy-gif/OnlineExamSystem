<template>
  <div class="weak-points-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <i class="el-icon-data-analysis"></i>
          智能分析
        </h1>
        <p class="page-desc">基于你的学习数据，AI为你分析薄弱知识点并推荐针对性练习</p>
      </div>
      <el-button type="primary" icon="el-icon-refresh" @click="refreshAnalysis" :loading="loading">
        重新分析
      </el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-animation">
        <i class="el-icon-loading"></i>
        <p>AI正在分析你的学习数据...</p>
      </div>
    </div>

    <!-- 分析结果 -->
    <div v-else class="analysis-content">
      <!-- 总体评估卡片 -->
      <div class="overview-card">
        <div class="overview-icon">
          <i class="el-icon-cpu"></i>
        </div>
        <div class="overview-content">
          <h2>AI分析总结</h2>
          <p class="assessment-text">{{ analysis.overallAssessment || '暂无分析数据，快去做些练习吧！' }}</p>
          <div class="stats-row">
            <div class="stat-item">
              <span class="stat-value">{{ analysis.totalWrongQuestions || 0 }}</span>
              <span class="stat-label">待攻克错题</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ (analysis.weakSubjects || []).length }}</span>
              <span class="stat-label">薄弱科目</span>
            </div>
          </div>
        </div>
        <div class="overview-action">
          <el-button type="success" size="large" @click="startSmartPractice" :loading="generating" class="smart-practice-btn">
            <i class="el-icon-magic-stick"></i>
            开始专项练习
          </el-button>
          <p class="action-tip">根据你的学习情况智能组卷</p>
        </div>
      </div>

      <!-- 薄弱科目分析 -->
      <div class="section-card" v-if="analysis.subjectAnalysis && analysis.subjectAnalysis.length > 0">
        <h3 class="section-title">
          <i class="el-icon-warning-outline"></i>
          薄弱科目分析
        </h3>
        <div class="subject-list">
          <div v-for="(item, index) in analysis.subjectAnalysis" :key="index" class="subject-card"
               :class="getWeaknessClass(item.weaknessScore)">
            <div class="subject-header">
              <div class="subject-info">
                <span class="subject-name">{{ item.subject }}</span>
                <el-tag :type="getTagType(item.level)" size="small">{{ item.level }}</el-tag>
              </div>
              <div class="weakness-score">
                <span class="score-value">{{ item.weaknessScore }}</span>
                <span class="score-label">薄弱指数</span>
              </div>
            </div>

            <div class="subject-stats">
              <div class="stat">
                <i class="el-icon-document"></i>
                <span>{{ item.wrongCount }} 道错题</span>
              </div>
              <div class="stat">
                <i class="el-icon-warning"></i>
                <span>累计错误 {{ item.totalWrongTimes }} 次</span>
              </div>
            </div>

            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: item.weaknessScore + '%' }"></div>
            </div>

            <p class="suggestion">
              <i class="el-icon-info"></i>
              {{ item.suggestion }}
            </p>

            <!-- 典型错题 -->
            <div class="typical-wrongs" v-if="item.typicalWrongs && item.typicalWrongs.length > 0">
              <p class="wrongs-title">典型错题示例：</p>
              <div v-for="(wq, wIndex) in item.typicalWrongs" :key="wIndex" class="wrong-item">
                <span class="wrong-content">{{ truncateText(wq.questionContent, 50) }}</span>
                <span class="wrong-count">错{{ wq.wrongCount }}次</span>
              </div>
            </div>

            <el-button type="primary" size="small" @click="startPractice(item.subject)"
                       :loading="subjectGenerating[item.subject]" class="practice-btn">
              <i class="el-icon-magic-stick" v-if="!subjectGenerating[item.subject]"></i>
              {{ subjectGenerating[item.subject] ? '智能组卷中...' : '开始专项练习' }}
            </el-button>
          </div>
        </div>
      </div>

      <!-- 无薄弱点提示 -->
      <div class="empty-state" v-else>
        <div class="empty-icon">
          <i class="el-icon-trophy"></i>
        </div>
        <h3>太棒了！暂无薄弱知识点</h3>
        <p>继续保持学习，或者去做一些新的练习吧！</p>
        <el-button type="primary" @click="goToPractice">去练习</el-button>
      </div>

      <!-- AI推荐练习 -->
      <div class="section-card" v-if="recommendedQuestions.length > 0">
        <h3 class="section-title">
          <i class="el-icon-star-on"></i>
          AI推荐练习
          <span class="title-desc">基于薄弱点为你精选的练习题</span>
        </h3>
        <div class="recommend-list">
          <div v-for="(q, index) in recommendedQuestions" :key="index" class="recommend-item">
            <div class="recommend-info">
              <el-tag size="mini" :type="getQuestionTypeTag(q.type)">{{ q.typeName }}</el-tag>
              <span class="recommend-subject">{{ q.subject }}</span>
            </div>
            <span class="recommend-reason">{{ q.reason }}</span>
          </div>
        </div>
        <div class="recommend-actions">
          <el-button type="success" @click="startRecommendedPractice">
            <i class="el-icon-video-play"></i>
            开始推荐练习
          </el-button>
        </div>
      </div>

      <!-- 错题分布图表 -->
      <div class="section-card" v-if="analysis.totalWrongQuestions > 0">
        <h3 class="section-title">
          <i class="el-icon-pie-chart"></i>
          错题分布
        </h3>
        <div class="charts-row">
          <div class="chart-card">
             <div class="chart-container" ref="subjectChart"></div>
          </div>
          <div class="chart-card">
             <div class="chart-container" ref="typeChart"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'WeakPointsAnalysis',
  data() {
    return {
      loading: false,
      generating: false,
      subjectGenerating: {},  // 记录每个科目的组卷状态
      studentId: null,
      analysis: {},
      recommendedQuestions: [],
      recommendedQuestions: [],
      subjectChart: null,
      typeChart: null
    }
  },
  created() {
    this.studentId = this.$cookies.get('cid')
    this.loadAnalysis()
  },
  mounted() {
    // 监听窗口变化重绘图表
    window.addEventListener('resize', this.resizeChart)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeChart)
    if (this.subjectChart) this.subjectChart.dispose()
    if (this.typeChart) this.typeChart.dispose()
  },
  methods: {
    async loadAnalysis() {
      this.loading = true
      try {
        // 获取薄弱知识点分析
        var res = await this.$axios.get('/api/study/ai/weak-points/' + this.studentId)
        if (res.data.code === 200) {
          this.analysis = res.data.data || {}
          // 使用 setTimeout 确保 v-if 渲染完成
          setTimeout(() => {
            this.initCharts()
          }, 200)
        }

        // 获取推荐练习题
        var recRes = await this.$axios.get('/api/study/ai/recommend/' + this.studentId + '?count=10')
        if (recRes.data.code === 200) {
          this.recommendedQuestions = recRes.data.data || []
        }
      } catch (error) {
        console.error('加载分析失败:', error)
        this.$message.error('加载失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    refreshAnalysis() {
      this.loadAnalysis()
    },
    initCharts() {
      if (!this.analysis) return

      // 1. 科目分布图
      if (this.$refs.subjectChart) {
        try {
          if (this.subjectChart) this.subjectChart.dispose()
          this.subjectChart = echarts.init(this.$refs.subjectChart)
          
          var subjectData = (this.analysis.weakSubjects || []).map(item => ({
            name: item.subject || '未知',
            value: item.totalWrongCount || item.count || 0
          }))

          this.subjectChart.setOption({
              title: { text: '错题科目分布', left: 'center' },
              tooltip: { trigger: 'item' },
              legend: { orient: 'vertical', left: 'left' },
              series: [{
                name: '科目',
                type: 'pie',
                radius: '50%',
                data: subjectData,
                emphasis: {
                  itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                  }
                }
              }]
          })
        } catch (e) {
          console.error('Subject chart error:', e)
        }
      }

      // 2. 题型分布图
      if (this.$refs.typeChart) {
        try {
          if (this.typeChart) this.typeChart.dispose()
          this.typeChart = echarts.init(this.$refs.typeChart)

          var typeData = [
              { name: '选择题', value: this.analysis.multiWrong || 0 },
              { name: '填空题', value: this.analysis.fillWrong || 0 },
              { name: '判断题', value: this.analysis.judgeWrong || 0 }
          ]

          this.typeChart.setOption({
              title: { text: '错题题型分布', left: 'center' },
              tooltip: { trigger: 'item' },
              legend: { orient: 'vertical', left: 'left' },
              series: [{
                name: '题型',
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                  borderRadius: 10,
                  borderColor: '#fff',
                  borderWidth: 2
                },
                label: {
                  show: false,
                  position: 'center'
                },
                emphasis: {
                  label: {
                    show: true,
                    fontSize: '20',
                    fontWeight: 'bold'
                  }
                },
                labelLine: { show: false },
                data: typeData
              }]
          })
        } catch (e) {
          console.error('Type chart error:', e)
        }
      }
    },
    resizeChart() {
      if (this.subjectChart) this.subjectChart.resize()
      if (this.typeChart) this.typeChart.resize()
    },
    getWeaknessClass(score) {
      if (score >= 80) return 'severe'
      if (score >= 60) return 'moderate'
      if (score >= 30) return 'mild'
      return 'good'
    },
    getTagType(level) {
      var types = {
        '严重薄弱': 'danger',
        '比较薄弱': 'warning',
        '轻度薄弱': 'info',
        '掌握较好': 'success'
      }
      return types[level] || 'info'
    },
    getQuestionTypeTag(type) {
      var types = { 1: 'success', 2: 'warning', 3: 'primary' }
      return types[type] || 'info'
    },
    truncateText(text, length) {
      if (!text) return ''
      if (text.length <= length) return text
      return text.substring(0, length) + '...'
    },
    async startPractice(subject) {
      var self = this
      // 设置该科目的组卷状态
      this.$set(this.subjectGenerating, subject, true)

      try {
        // 调用遗传算法组卷API，针对该薄弱科目
        var requestData = {
          subjects: [subject],
          targetDifficulty: 3,
          difficultyTolerance: 1.0,
          multiCount: 5,
          fillCount: 3,
          judgeCount: 3,
          subjectiveCount: 0,
          multiScore: 5,
          fillScore: 5,
          judgeScore: 5,
          subjectiveScore: 20,
          populationSize: 50,
          maxGenerations: 100,
          crossoverRate: 0.8,
          mutationRate: 0.1,
          totalScore: 55,
          studentId: this.studentId
        }

        var res = await this.$axios.post('/api/genetic/generate', requestData)

        if (res.data.code === 200) {
          var result = res.data.data
          this.$message.success('「' + subject + '」专项练习组卷完成！匹配度: ' + result.stats.fitness + '%')

          // 保存到 sessionStorage，用于 smartPractice 加载
          sessionStorage.setItem('smartPractice', JSON.stringify(result))

          // 跳转到专项练习页面并自动开始
          this.$router.push({ path: '/smartPractice' })
        } else {
          this.$message.error(res.data.message || '组卷失败，请稍后重试')
        }
      } catch (error) {
        console.error('专项练习组卷失败:', error)
        this.$message.error('组卷失败，请稍后重试')
      } finally {
        self.$set(self.subjectGenerating, subject, false)
      }
    },
    startRecommendedPractice() {
      // 跳转到随机练习并传递推荐科目
      var subjects = []
      var self = this
      this.recommendedQuestions.forEach(function(q) {
        if (q.subject && subjects.indexOf(q.subject) === -1) {
          subjects.push(q.subject)
        }
      })
      this.$router.push({ path: '/selfExam', query: { subject: subjects[0] } })
    },
    goToPractice() {
      this.$router.push('/selfExam')
    },
    async startSmartPractice() {
      this.generating = true
      try {
        var res = await this.$axios.post('/api/study/ai/smart-practice/' + this.studentId)
        if (res.data.code === 200) {
          var result = res.data.data
          this.$message.success('AI已根据你的学习情况组卷完成！')
          sessionStorage.setItem('smartPractice', JSON.stringify(result))
          this.$router.push({ path: '/smartPractice' })
        } else {
          this.$message.error(res.data.message || '组卷失败，请稍后重试')
        }
      } catch (error) {
        console.error('智能组卷失败:', error)
        this.$message.error('组卷失败，请稍后重试')
      } finally {
        this.generating = false
      }
    }
  }
}
</script>

<style scoped>
.weak-points-page {
  padding: 20px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ee 100%);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  color: #fff;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-desc {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.loading-animation {
  text-align: center;
}

.loading-animation i {
  font-size: 48px;
  color: #667eea;
  animation: pulse 1.5s ease-in-out infinite;
}

.loading-animation p {
  margin-top: 20px;
  color: #606266;
  font-size: 16px;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.7; }
}

.overview-card {
  display: flex;
  gap: 30px;
  padding: 30px;
  background: #fff;
  border-radius: 20px;
  margin-bottom: 25px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  align-items: center;
}

.overview-action {
  text-align: center;
  padding-left: 30px;
  border-left: 1px solid #eee;
}

.smart-practice-btn {
  padding: 16px 32px;
  font-size: 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
  border: none;
}

.smart-practice-btn:hover {
  background: linear-gradient(135deg, #85ce61 0%, #67C23A 100%);
}

.action-tip {
  font-size: 12px;
  color: #909399;
  margin: 10px 0 0 0;
}

.overview-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.overview-icon i {
  font-size: 40px;
  color: #fff;
}

.overview-content {
  flex: 1;
}

.overview-content h2 {
  margin: 0 0 15px 0;
  font-size: 20px;
  color: #303133;
}

.assessment-text {
  font-size: 16px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 20px;
}

.stats-row {
  display: flex;
  gap: 40px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #667eea;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.section-card {
  background: #fff;
  border-radius: 20px;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-card {
  height: 350px;
  background: #f8f9fa; /* Slight background to see bounds */
  border-radius: 12px;
  padding: 10px;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #303133;
}

.section-title i {
  color: #667eea;
}

.title-desc {
  font-size: 13px;
  color: #909399;
  font-weight: 400;
  margin-left: 10px;
}

.subject-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.subject-card {
  padding: 20px;
  border-radius: 16px;
  border: 2px solid #e4e7ed;
  transition: all 0.3s ease;
}

.subject-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.subject-card.severe {
  border-color: #F56C6C;
  background: linear-gradient(to bottom right, rgba(245,108,108,0.05), transparent);
}

.subject-card.moderate {
  border-color: #E6A23C;
  background: linear-gradient(to bottom right, rgba(230,162,60,0.05), transparent);
}

.subject-card.mild {
  border-color: #409EFF;
  background: linear-gradient(to bottom right, rgba(64,158,255,0.05), transparent);
}

.subject-card.good {
  border-color: #67C23A;
  background: linear-gradient(to bottom right, rgba(103,194,58,0.05), transparent);
}

.subject-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.subject-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.subject-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.weakness-score {
  text-align: center;
}

.score-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #F56C6C;
}

.score-label {
  font-size: 12px;
  color: #909399;
}

.subject-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.subject-stats .stat {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: #606266;
}

.progress-bar {
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 15px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #F56C6C, #E6A23C);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.suggestion {
  font-size: 13px;
  color: #606266;
  margin: 0 0 15px 0;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.suggestion i {
  color: #409EFF;
  margin-top: 2px;
}

.typical-wrongs {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 15px;
}

.wrongs-title {
  font-size: 12px;
  color: #909399;
  margin: 0 0 10px 0;
}

.wrong-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px dashed #e4e7ed;
}

.wrong-item:last-child {
  border-bottom: none;
}

.wrong-content {
  font-size: 13px;
  color: #606266;
  flex: 1;
}

.wrong-count {
  font-size: 12px;
  color: #F56C6C;
  font-weight: 500;
}

.practice-btn {
  width: 100%;
  border-radius: 10px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: #fff;
  border-radius: 20px;
  margin-bottom: 25px;
}

.empty-icon {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #67C23A, #85ce61);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 25px;
}

.empty-icon i {
  font-size: 50px;
  color: #fff;
}

.empty-state h3 {
  font-size: 22px;
  color: #303133;
  margin: 0 0 10px 0;
}

.empty-state p {
  color: #909399;
  margin-bottom: 25px;
}

.recommend-list {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
}

.recommend-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s;
}

.recommend-item:hover {
  background: #f0f2f5;
}

.recommend-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.recommend-subject {
  font-weight: 500;
  color: #303133;
}

.recommend-reason {
  font-size: 13px;
  color: #909399;
}

.recommend-actions {
  text-align: center;
  padding-top: 10px;
}

.chart-container {
  height: 300px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }

  .overview-card {
    flex-direction: column;
  }

  .subject-list {
    grid-template-columns: 1fr;
  }

  .stats-row {
    gap: 20px;
  }
}
</style>
