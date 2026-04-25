<template>
  <div id="studyCurve">
    <div class="title">学习曲线</div>
    
    <!-- 概览卡片 -->
    <div class="overview-row">
      <div class="overview-card">
        <div class="card-icon practice"><i class="el-icon-document-copy"></i></div>
        <div class="card-info">
          <span class="card-value">{{ overview.practiceCount || 0 }}</span>
          <span class="card-label">练习次数</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="card-icon questions"><i class="el-icon-edit"></i></div>
        <div class="card-info">
          <span class="card-value">{{ overview.totalQuestions || 0 }}</span>
          <span class="card-label">做题总数</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="card-icon correct"><i class="el-icon-success"></i></div>
        <div class="card-info">
          <span class="card-value">{{ overview.totalCorrect || 0 }}</span>
          <span class="card-label">正确数</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="card-icon accuracy"><i class="el-icon-data-line"></i></div>
        <div class="card-info">
          <span class="card-value">{{ formatAccuracy(overview.avgAccuracy) }}%</span>
          <span class="card-label">平均正确率</span>
        </div>
      </div>
    </div>
    
    <!-- 时间范围选择 -->
    <div class="time-filter">
      <el-radio-group v-model="days" @change="loadCurveData">
        <el-radio-button :label="7">最近7天</el-radio-button>
        <el-radio-button :label="14">最近14天</el-radio-button>
        <el-radio-button :label="30">最近30天</el-radio-button>
      </el-radio-group>
    </div>
    
    <!-- 曲线图 -->
    <div class="chart-container">
      <div class="chart-card">
        <div class="chart-header">
          <h3>学习进度曲线</h3>
          <p>记录你每天的练习情况和正确率变化</p>
        </div>
        <div class="chart-wrapper" v-loading="loading">
          <div ref="curveChart" class="curve-chart"></div>
        </div>
      </div>
    </div>
    
    <!-- 正确率分布图 -->
    <div class="chart-container">
      <div class="chart-card">
        <div class="chart-header">
          <h3>正确率趋势</h3>
          <p>查看你的正确率变化趋势</p>
        </div>
        <div class="chart-wrapper">
          <div ref="accuracyChart" class="accuracy-chart"></div>
        </div>
      </div>
    </div>
    
    <!-- 最近练习记录 -->
    <div class="record-section">
      <h3 class="section-title">最近练习记录</h3>
      <div class="record-list">
        <div 
          class="record-item" 
          v-for="(record, index) in recentRecords" 
          :key="index"
        >
          <div class="record-date">
            <span class="date-day">{{ formatDay(record.practiceDate) }}</span>
            <span class="date-month">{{ formatMonth(record.practiceDate) }}</span>
          </div>
          <div class="record-info">
            <div class="record-type">{{ getTypeName(record.practiceType) }}</div>
            <div class="record-stats">
              <span>做题 {{ record.totalQuestions }} 题</span>
              <span class="correct">对 {{ record.correctCount }}</span>
              <span class="wrong">错 {{ record.wrongCount }}</span>
            </div>
          </div>
          <div class="record-accuracy" :class="getAccuracyClass(record.accuracy)">
            {{ formatAccuracy(record.accuracy) }}%
          </div>
        </div>
        
        <div v-if="recentRecords.length === 0" class="empty-record">
          <i class="el-icon-document"></i>
          <p>暂无练习记录</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'StudyCurve',
  data() {
    return {
      loading: false,
      days: 30,
      overview: {},
      curveData: [],
      recentRecords: [],
      studentId: null,
      curveChartInstance: null,
      accuracyChartInstance: null
    }
  },
  created() {
    this.studentId = this.$cookies.get('cid')
    if (!this.studentId) {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        try {
          const userData = JSON.parse(userStr)
          this.studentId = userData.studentId || userData.cardId
        } catch (e) {
          console.error('Failed to parse user data from localStorage', e)
        }
      }
    }
  },
  mounted() {
    this.loadOverview()
    this.loadCurveData()
    this.loadRecentRecords()
    
    // 监听窗口大小变化
    var self = this
    window.addEventListener('resize', function() {
      if (self.curveChartInstance) {
        self.curveChartInstance.resize()
      }
      if (self.accuracyChartInstance) {
        self.accuracyChartInstance.resize()
      }
    })
  },
  beforeDestroy() {
    if (this.curveChartInstance) {
      this.curveChartInstance.dispose()
    }
    if (this.accuracyChartInstance) {
      this.accuracyChartInstance.dispose()
    }
  },
  methods: {
    async loadOverview() {
      try {
        var res = await this.$axios.get('/api/study/overview/' + this.studentId)
        if (res.data.code === 200) {
          this.overview = res.data.data || {}
        }
      } catch (error) {
        console.error('加载概览失败:', error)
      }
    },
    async loadCurveData() {
      this.loading = true
      try {
        var res = await this.$axios.get('/api/study/curve/' + this.studentId + '?days=' + this.days)
        if (res.data.code === 200) {
          this.curveData = res.data.data || []
          this.renderCurveChart()
          this.renderAccuracyChart()
        }
      } catch (error) {
        console.error('加载曲线数据失败:', error)
      } finally {
        this.loading = false
      }
    },
    async loadRecentRecords() {
      try {
        var res = await this.$axios.get('/api/study/record/' + this.studentId)
        if (res.data.code === 200) {
          this.recentRecords = (res.data.data || []).slice(0, 10)
        }
      } catch (error) {
        console.error('加载记录失败:', error)
      }
    },
    renderCurveChart() {
      var self = this
      if (!this.$refs.curveChart) return
      
      if (this.curveChartInstance) {
        this.curveChartInstance.dispose()
      }
      
      this.curveChartInstance = echarts.init(this.$refs.curveChart)
      
      var dates = []
      var totalQuestions = []
      var correctCount = []
      var wrongCount = []
      
      this.curveData.forEach(function(item) {
        dates.push(self.formatChartDate(item.date))
        totalQuestions.push(item.totalQuestions || 0)
        correctCount.push(item.correctCount || 0)
        wrongCount.push(item.wrongCount || 0)
      })
      
      var option = {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255,255,255,0.95)',
          borderColor: '#e4e7ed',
          borderWidth: 1,
          textStyle: { color: '#303133' }
        },
        legend: {
          data: ['做题数', '正确数', '错误数'],
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
          boundaryGap: false,
          data: dates,
          axisLine: { lineStyle: { color: '#e4e7ed' } },
          axisLabel: { color: '#909399' }
        },
        yAxis: {
          type: 'value',
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f0f0f0' } },
          axisLabel: { color: '#909399' }
        },
        series: [
          {
            name: '做题数',
            type: 'line',
            smooth: true,
            data: totalQuestions,
            lineStyle: { color: '#409EFF', width: 3 },
            itemStyle: { color: '#409EFF' },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(64,158,255,0.3)' },
                  { offset: 1, color: 'rgba(64,158,255,0.05)' }
                ]
              }
            }
          },
          {
            name: '正确数',
            type: 'line',
            smooth: true,
            data: correctCount,
            lineStyle: { color: '#67C23A', width: 3 },
            itemStyle: { color: '#67C23A' }
          },
          {
            name: '错误数',
            type: 'line',
            smooth: true,
            data: wrongCount,
            lineStyle: { color: '#F56C6C', width: 3 },
            itemStyle: { color: '#F56C6C' }
          }
        ]
      }
      
      this.curveChartInstance.setOption(option)
    },
    renderAccuracyChart() {
      var self = this
      if (!this.$refs.accuracyChart) return
      
      if (this.accuracyChartInstance) {
        this.accuracyChartInstance.dispose()
      }
      
      this.accuracyChartInstance = echarts.init(this.$refs.accuracyChart)
      
      var dates = []
      var accuracyData = []
      
      this.curveData.forEach(function(item) {
        dates.push(self.formatChartDate(item.date))
        accuracyData.push(item.avgAccuracy ? Math.round(item.avgAccuracy * 10) / 10 : 0)
      })
      
      var option = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}<br/>正确率: {c}%'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLine: { lineStyle: { color: '#e4e7ed' } },
          axisLabel: { color: '#909399' }
        },
        yAxis: {
          type: 'value',
          max: 100,
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f0f0f0' } },
          axisLabel: { color: '#909399', formatter: '{value}%' }
        },
        series: [{
          type: 'bar',
          data: accuracyData,
          itemStyle: {
            color: function(params) {
              var value = params.value
              if (value >= 80) return '#67C23A'
              if (value >= 60) return '#E6A23C'
              return '#F56C6C'
            },
            borderRadius: [4, 4, 0, 0]
          },
          barWidth: '60%'
        }]
      }
      
      this.accuracyChartInstance.setOption(option)
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
    formatDay(dateStr) {
      if (!dateStr) return ''
      return new Date(dateStr).getDate()
    },
    formatMonth(dateStr) {
      if (!dateStr) return ''
      return (new Date(dateStr).getMonth() + 1) + '月'
    },
    getTypeName(type) {
      var types = { 1: '随机练习', 2: '错题练习', 3: '正式考试', 4: '试卷练习', 5: '自主测试' }
      return types[type] || '练习'
    },
    getAccuracyClass(accuracy) {
      if (accuracy >= 80) return 'high'
      if (accuracy >= 60) return 'medium'
      return 'low'
    }
  }
}
</script>

<style lang="less" scoped>
#studyCurve {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 30px;
  background: linear-gradient(45deg, #409EFF, #67C23A);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.overview-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.overview-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  color: #fff;
}

.card-icon.practice { background: linear-gradient(135deg, #409EFF, #66b1ff); }
.card-icon.questions { background: linear-gradient(135deg, #67C23A, #85ce61); }
.card-icon.correct { background: linear-gradient(135deg, #E6A23C, #f3d19e); }
.card-icon.accuracy { background: linear-gradient(135deg, #9b59b6, #c39bd3); }

.card-info {
  display: flex;
  flex-direction: column;
}

.card-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.card-label {
  font-size: 14px;
  color: #909399;
}

.time-filter {
  margin-bottom: 25px;
}

.chart-container {
  margin-bottom: 30px;
}

.chart-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.06);
}

.chart-header {
  margin-bottom: 20px;
}

.chart-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px;
}

.chart-header p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.curve-chart, .accuracy-chart {
  width: 100%;
  height: 350px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
}

.record-list {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.06);
}

.record-item {
  display: flex;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.3s ease;
}

.record-item:hover {
  background: #f8fafc;
}

.record-item:last-child {
  border-bottom: none;
}

.record-date {
  width: 60px;
  text-align: center;
  margin-right: 20px;
}

.date-day {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #409EFF;
}

.date-month {
  font-size: 12px;
  color: #909399;
}

.record-info {
  flex: 1;
}

.record-type {
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}

.record-stats {
  font-size: 13px;
  color: #909399;
}

.record-stats span {
  margin-right: 15px;
}

.record-stats .correct { color: #67C23A; }
.record-stats .wrong { color: #F56C6C; }

.record-accuracy {
  font-size: 20px;
  font-weight: 700;
  padding: 8px 16px;
  border-radius: 12px;
}

.record-accuracy.high { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.record-accuracy.medium { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }
.record-accuracy.low { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }

.empty-record {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-record i {
  font-size: 48px;
  margin-bottom: 15px;
  color: #dcdfe6;
}

@media (max-width: 1024px) {
  .overview-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .overview-row {
    grid-template-columns: 1fr;
  }
  
  .record-item {
    flex-wrap: wrap;
  }
  
  .record-accuracy {
    width: 100%;
    text-align: center;
    margin-top: 15px;
  }
}
</style>
