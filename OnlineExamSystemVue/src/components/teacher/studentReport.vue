<template>
  <div id="studentReport">
    <div class="page-header">
      <h2>学生学习报告</h2>
      <p>查看学生的学习曲线和错题情况</p>
    </div>
    
    <!-- 搜索区域 -->
    <div class="search-section">
      <el-form :inline="true">
        <el-form-item label="班级">
          <el-select v-model="searchClazz" placeholder="请选择班级" clearable filterable style="width:200px">
            <el-option v-for="c in classList" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadClassOverview">
            <i class="el-icon-search"></i> 查询
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 班级概览列表 -->
    <div class="class-overview" v-if="!selectedStudent">
      <h3 class="section-title">班级学习概览</h3>
      <el-table 
        :data="classData" 
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="studentId" label="学号" width="100" align="center" />
        <el-table-column prop="studentName" label="姓名" min-width="120" align="center" />
        <el-table-column prop="clazz" label="班级" min-width="120" align="center" />
        <el-table-column prop="practiceCount" label="练习次数" width="100" align="center">
          <template slot-scope="scope">
            <span class="practice-count">{{ scope.row.practiceCount || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="totalQuestions" label="做题总数" width="100" align="center" />
        <el-table-column prop="avgAccuracy" label="平均正确率" width="120" align="center">
          <template slot-scope="scope">
            <span :class="getAccuracyClass(scope.row.avgAccuracy)">
              {{ formatAccuracy(scope.row.avgAccuracy) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center" class-name="small-padding fixed-width">
          <template slot-scope="scope">
            <el-button 
              type="text" 
              size="mini" 
              icon="el-icon-view"
              @click="viewReport(scope.row)"
            >查看报告</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 学生详细报告 -->
    <div class="student-detail" v-if="selectedStudent">
      <div class="detail-header">
        <el-button icon="el-icon-back" @click="backToList">返回列表</el-button>
        <div class="student-info">
          <el-avatar :size="50">{{ selectedStudent.studentName ? selectedStudent.studentName.charAt(0) : 'S' }}</el-avatar>
          <div class="info-text">
            <h3>{{ selectedStudent.studentName }}</h3>
            <p>{{ selectedStudent.clazz }} | 学号: {{ selectedStudent.studentId }}</p>
          </div>
        </div>
      </div>
      
      <!-- 学习概览 -->
      <div class="report-section">
        <h3 class="section-title">学习概览</h3>
        <div class="overview-grid">
          <div class="overview-item">
            <span class="item-value">{{ report.overview ? report.overview.practiceCount : 0 }}</span>
            <span class="item-label">练习次数</span>
          </div>
          <div class="overview-item">
            <span class="item-value">{{ report.overview ? report.overview.totalQuestions : 0 }}</span>
            <span class="item-label">做题总数</span>
          </div>
          <div class="overview-item">
            <span class="item-value correct">{{ report.overview ? report.overview.totalCorrect : 0 }}</span>
            <span class="item-label">正确数</span>
          </div>
          <div class="overview-item">
            <span class="item-value wrong">{{ report.overview ? report.overview.totalWrong : 0 }}</span>
            <span class="item-label">错误数</span>
          </div>
          <div class="overview-item">
            <span class="item-value accent">{{ report.overview ? formatAccuracy(report.overview.avgAccuracy) : 0 }}%</span>
            <span class="item-label">平均正确率</span>
          </div>
        </div>
      </div>
      
      <!-- 学习曲线 -->
      <div class="report-section">
        <h3 class="section-title">学习曲线（最近30天）</h3>
        <div class="chart-wrapper">
          <div ref="reportChart" class="report-chart"></div>
        </div>
      </div>
      
      <!-- 错题统计 -->
      <div class="report-section">
        <h3 class="section-title">错题统计</h3>
        <div class="wrong-stats">
          <div class="wrong-stat-item">
            <div class="stat-circle total">{{ report.wrongStats ? report.wrongStats.totalWrong : 0 }}</div>
            <span>总错题数</span>
          </div>
          <div class="wrong-stat-item">
            <div class="stat-circle multi">{{ report.wrongStats ? report.wrongStats.multiWrong : 0 }}</div>
            <span>选择题</span>
          </div>
          <div class="wrong-stat-item">
            <div class="stat-circle fill">{{ report.wrongStats ? report.wrongStats.fillWrong : 0 }}</div>
            <span>填空题</span>
          </div>
          <div class="wrong-stat-item">
            <div class="stat-circle judge">{{ report.wrongStats ? report.wrongStats.judgeWrong : 0 }}</div>
            <span>判断题</span>
          </div>
        </div>
      </div>
      
      <!-- 错题列表 -->
      <div class="report-section">
        <h3 class="section-title">错题详情</h3>
        <el-table 
          :data="report.wrongQuestions || []" 
          stripe
          max-height="400"
        >
          <el-table-column prop="questionContent" label="题目内容" min-width="300">
            <template slot-scope="scope">
              <div class="question-cell">{{ scope.row.questionContent }}</div>
            </template>
          </el-table-column>
          <el-table-column label="题型" width="80">
            <template slot-scope="scope">
              <el-tag size="small" :type="getTypeTagType(scope.row.questionType)">
                {{ getTypeName(scope.row.questionType) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="wrongAnswer" label="错误答案" width="120" />
          <el-table-column prop="correctAnswer" label="正确答案" width="120" />
          <el-table-column prop="wrongCount" label="错误次数" width="90">
            <template slot-scope="scope">
              <span class="wrong-count-badge">{{ scope.row.wrongCount }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'StudentReport',
  data() {
    return {
      loading: false,
      searchClazz: '',
      classList: [],
      classData: [],
      selectedStudent: null,
      report: {},
      chartInstance: null
    }
  },
  mounted() {
    this.loadClasses()
  },
  beforeDestroy() {
    if (this.chartInstance) {
      this.chartInstance.dispose()
    }
  },
  methods: {
    async loadClasses() {
      try {
        var res = await this.$axios.get('/api/student/classes')
        if (res.data.code === 200) this.classList = res.data.data || []
      } catch (e) { /* 静默失败 */ }
    },
    async loadClassOverview() {
      if (!this.searchClazz) {
        this.$message.warning('请输入班级名称')
        return
      }
      
      this.loading = true
      try {
        var res = await this.$axios.get('/api/study/class/overview?clazz=' + encodeURIComponent(this.searchClazz))
        if (res.data.code === 200) {
          this.classData = res.data.data || []
        }
      } catch (error) {
        console.error('加载班级数据失败:', error)
        this.$message.error('加载失败')
      } finally {
        this.loading = false
      }
    },
    async viewReport(student) {
      this.selectedStudent = student
      this.loading = true
      
      try {
        var res = await this.$axios.get('/api/study/report/' + student.studentId)
        if (res.data.code === 200) {
          this.report = res.data.data || {}
          this.$nextTick(function() {
            this.renderChart()
          })
        }
      } catch (error) {
        console.error('加载报告失败:', error)
        this.$message.error('加载报告失败')
      } finally {
        this.loading = false
      }
    },
    backToList() {
      this.selectedStudent = null
      this.report = {}
      if (this.chartInstance) {
        this.chartInstance.dispose()
        this.chartInstance = null
      }
    },
    renderChart() {
      var self = this
      if (!this.$refs.reportChart) return
      
      if (this.chartInstance) {
        this.chartInstance.dispose()
      }
      
      this.chartInstance = echarts.init(this.$refs.reportChart)
      
      var dailyStats = this.report.dailyStats || []
      var dates = []
      var accuracy = []
      var questions = []
      
      dailyStats.forEach(function(item) {
        dates.push(self.formatChartDate(item.date))
        accuracy.push(item.avgAccuracy ? Math.round(item.avgAccuracy * 10) / 10 : 0)
        questions.push(item.totalQuestions || 0)
      })
      
      var option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['正确率', '做题数'],
          bottom: 0
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLine: { lineStyle: { color: '#e4e7ed' } },
          axisLabel: { color: '#909399' }
        },
        yAxis: [
          {
            type: 'value',
            name: '正确率(%)',
            max: 100,
            axisLine: { show: false },
            splitLine: { lineStyle: { color: '#f0f0f0' } }
          },
          {
            type: 'value',
            name: '做题数',
            axisLine: { show: false },
            splitLine: { show: false }
          }
        ],
        series: [
          {
            name: '正确率',
            type: 'line',
            smooth: true,
            data: accuracy,
            lineStyle: { color: '#67C23A', width: 3 },
            itemStyle: { color: '#67C23A' }
          },
          {
            name: '做题数',
            type: 'bar',
            yAxisIndex: 1,
            data: questions,
            itemStyle: { 
              color: 'rgba(64, 158, 255, 0.6)',
              borderRadius: [4, 4, 0, 0]
            }
          }
        ]
      }
      
      this.chartInstance.setOption(option)
    },
    formatAccuracy(value) {
      if (!value) return 0
      return Math.round(value * 10) / 10
    },
    formatChartDate(dateStr) {
      if (!dateStr) return ''
      var date = new Date(dateStr)
      return (date.getMonth() + 1) + '/' + date.getDate()
    },
    getAccuracyClass(accuracy) {
      if (accuracy >= 80) return 'accuracy-high'
      if (accuracy >= 60) return 'accuracy-medium'
      return 'accuracy-low'
    },
    getTypeName(type) {
      var types = { 1: '选择', 2: '填空', 3: '判断' }
      return types[type] || '未知'
    },
    getTypeTagType(type) {
      var types = { 1: 'success', 2: 'warning', 3: '' }
      return types[type] || 'info'
    }
  }
}
</script>

<style lang="less" scoped>
#studentReport {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 10px;
}

.page-header p {
  color: #909399;
  margin: 0;
}

.search-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px;
  padding-left: 12px;
  border-left: 4px solid #409EFF;
}

.class-overview {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.practice-count {
  font-weight: 600;
  color: #409EFF;
}

.accuracy-high { color: #67C23A; font-weight: 600; }
.accuracy-medium { color: #E6A23C; font-weight: 600; }
.accuracy-low { color: #F56C6C; font-weight: 600; }

.detail-header {
  display: flex;
  align-items: center;
  gap: 30px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.student-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.info-text h3 {
  margin: 0 0 5px;
  font-size: 20px;
  color: #303133;
}

.info-text p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.report-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
}

.overview-item {
  text-align: center;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
}

.item-value {
  display: block;
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
}

.item-value.correct { color: #67C23A; }
.item-value.wrong { color: #F56C6C; }
.item-value.accent { color: #409EFF; }

.item-label {
  font-size: 14px;
  color: #909399;
}

.chart-wrapper {
  min-height: 300px;
}

.report-chart {
  width: 100%;
  height: 300px;
}

.wrong-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
}

.wrong-stat-item {
  text-align: center;
}

.stat-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0 auto 12px;
}

.stat-circle.total { background: linear-gradient(135deg, #409EFF, #66b1ff); }
.stat-circle.multi { background: linear-gradient(135deg, #67C23A, #85ce61); }
.stat-circle.fill { background: linear-gradient(135deg, #E6A23C, #f3d19e); }
.stat-circle.judge { background: linear-gradient(135deg, #F56C6C, #f89898); }

.question-cell {
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.wrong-count-badge {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(245, 108, 108, 0.1);
  color: #F56C6C;
  border-radius: 20px;
  font-weight: 600;
}

@media (max-width: 1024px) {
  .overview-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .wrong-stats {
    flex-wrap: wrap;
    gap: 20px;
  }
}
</style>
