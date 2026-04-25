<template>
  <div class="student-profile-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <i class="el-icon-data-analysis header-icon"></i>
          <div class="title-text">
            <h1>学生群体画像</h1>
            <p>基于K-Means聚类算法的学生分析</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" icon="el-icon-refresh" @click="loadData" :loading="loading">
            刷新数据
          </el-button>
        </div>
      </div>
    </div>

    <!-- 聚类统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <div class="stat-card total">
          <div class="stat-icon"><i class="el-icon-user"></i></div>
          <div class="stat-info">
            <div class="stat-value">{{ totalStudents }}</div>
            <div class="stat-label">学生总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6" v-for="cluster in clusterStats" :key="cluster.cluster">
        <div class="stat-card" :class="'cluster-' + cluster.cluster">
          <div class="stat-icon">
            <i :class="clusterIcons[cluster.cluster]"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ cluster.count }}</div>
            <div class="stat-label">{{ cluster.name }}</div>
            <div class="stat-desc">平均分: {{ cluster.avgScore || 0 }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 主要内容区域 -->
    <el-row :gutter="20" class="main-content">
      <!-- 散点图 -->
      <el-col :span="14">
        <div class="chart-card">
          <div class="card-header">
            <span class="card-title"><i class="el-icon-pie-chart"></i> 学生群体散点图</span>
            <div class="card-actions">
              <el-select v-model="xAxis" size="small" @change="updateChart" style="width: 120px; margin-right: 10px;">
                <el-option label="平均分" value="avgScore"></el-option>
                <el-option label="答题速度" value="answerSpeed"></el-option>
                <el-option label="得分方差" value="scoreVariance"></el-option>
              </el-select>
              <el-select v-model="yAxis" size="small" @change="updateChart" style="width: 120px;">
                <el-option label="平均分" value="avgScore"></el-option>
                <el-option label="答题速度" value="answerSpeed"></el-option>
                <el-option label="得分方差" value="scoreVariance"></el-option>
              </el-select>
            </div>
          </div>
          <div ref="scatterChart" class="scatter-chart"></div>
        </div>
      </el-col>

      <!-- 聚类详情 -->
      <el-col :span="10">
        <div class="detail-card">
          <div class="card-header">
            <span class="card-title"><i class="el-icon-document"></i> 聚类详情</span>
          </div>
          <div class="cluster-details">
            <div class="cluster-item" v-for="cluster in clusterStats" :key="cluster.cluster"
                 :class="{ active: selectedCluster === cluster.cluster }"
                 @click="selectCluster(cluster.cluster)">
              <div class="cluster-badge" :class="'badge-' + cluster.cluster">
                {{ cluster.cluster + 1 }}
              </div>
              <div class="cluster-info">
                <div class="cluster-name">{{ cluster.name }}</div>
                <div class="cluster-desc">{{ cluster.description }}</div>
                <div class="cluster-stats">
                  <span><i class="el-icon-user"></i> {{ cluster.count }}人</span>
                  <span><i class="el-icon-trophy"></i> {{ cluster.avgScore || 0 }}分</span>
                  <span><i class="el-icon-data-analysis"></i> 方差: {{ cluster.avgVariance || 0 }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 学生列表 -->
    <div class="student-list-card">
      <div class="card-header">
        <span class="card-title"><i class="el-icon-s-custom"></i> 学生详情列表</span>
        <div class="card-actions">
          <el-input v-model="searchKeyword" placeholder="搜索学生姓名" size="small" 
                    prefix-icon="el-icon-search" style="width: 200px; margin-right: 10px;"
                    clearable @clear="filterStudents" @keyup.enter.native="filterStudents">
          </el-input>
          <el-select v-model="filterCluster" size="small" placeholder="筛选类型" clearable
                     @change="filterStudents" style="width: 120px;">
            <el-option label="全部" :value="null"></el-option>
            <el-option v-for="cluster in clusterStats" :key="cluster.cluster"
                       :label="cluster.name" :value="cluster.cluster">
            </el-option>
          </el-select>
        </div>
      </div>
      <el-table :data="filteredProfiles" stripe style="width: 100%" max-height="400">
        <el-table-column prop="studentId" label="学号" width="100"></el-table-column>
        <el-table-column prop="studentName" label="姓名" width="100"></el-table-column>
        <el-table-column prop="clazz" label="班级" min-width="150"></el-table-column>
        <el-table-column prop="avgScore" label="平均分" width="100">
          <template slot-scope="scope">
            <span :class="getScoreClass(scope.row.avgScore)">
              {{ (scope.row.avgScore || 0).toFixed(1) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="answerSpeed" label="答题速度" width="100">
          <template slot-scope="scope">
            {{ (scope.row.answerSpeed || 0).toFixed(2) }} 题/分
          </template>
        </el-table-column>
        <el-table-column prop="scoreVariance" label="得分方差" width="110">
          <template slot-scope="scope">
            <span :class="getVarianceClass(scope.row.scoreVariance)">
              {{ (scope.row.scoreVariance || 0).toFixed(1) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="clusterName" label="类型" width="120">
          <template slot-scope="scope">
            <el-tag :type="getClusterTagType(scope.row.cluster)" size="small">
              {{ scope.row.clusterName }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="examCount" label="考试次数" width="100"></el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentProfile',
  data() {
    return {
      loading: false,
      profiles: [],
      clusterStats: [],
      totalStudents: 0,
      xAxis: 'avgScore',
      yAxis: 'scoreVariance',
      selectedCluster: null,
      searchKeyword: '',
      filterCluster: null,
      filteredProfiles: [],
      chart: null,
      clusterIcons: {
        0: 'el-icon-warning-outline',
        1: 'el-icon-time',
        2: 'el-icon-star-on'
      },
      clusterColors: ['#F56C6C', '#E6A23C', '#67C23A']
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    loadData() {
      var self = this
      self.loading = true
      
      this.$axios.get('/api/kmeans/statistics')
        .then(function(res) {
          if (res.data.code === 200) {
            var data = res.data.data
            self.profiles = data.profiles || []
            self.clusterStats = data.clusters || []
            self.totalStudents = data.totalStudents || 0
            self.filteredProfiles = self.profiles
            self.initChart()
          }
        })
        .catch(function(err) {
          self.$message.error('加载数据失败')
          console.error(err)
        })
        .finally(function() {
          self.loading = false
        })
    },
    
    initChart() {
      var self = this
      if (!this.$refs.scatterChart) return
      
      if (this.chart) {
        this.chart.dispose()
      }
      
      this.chart = this.$echarts.init(this.$refs.scatterChart)
      this.updateChart()
      
      // 点击事件
      this.chart.on('click', function(params) {
        if (params.data && params.data.studentId) {
          self.$message.info('学生: ' + params.data.name)
        }
      })
    },
    
    updateChart() {
      if (!this.chart) return
      
      var self = this
      var axisLabels = {
        avgScore: '平均分',
        answerSpeed: '答题速度 (题/分)',
        scoreVariance: '得分方差'
      }
      
      // 按聚类分组数据
      var seriesData = []
      for (var i = 0; i < 3; i++) {
        var clusterName = self.clusterStats[i] ? self.clusterStats[i].name : '类型' + (i + 1)
        var data = []
        
        for (var j = 0; j < self.profiles.length; j++) {
          var p = self.profiles[j]
          if (p.cluster === i) {
            var xVal = p[self.xAxis] || 0
            var yVal = p[self.yAxis] || 0
            
            data.push({
              value: [xVal, yVal],
              name: p.studentName,
              studentId: p.studentId,
              cluster: i
            })
          }
        }
        
        seriesData.push({
          name: clusterName,
          type: 'scatter',
          symbolSize: 14,
          data: data,
          itemStyle: {
            color: self.clusterColors[i]
          }
        })
      }
      
      var option = {
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            var xLabel = axisLabels[self.xAxis]
            var yLabel = axisLabels[self.yAxis]
            return params.data.name + '<br/>' +
                   xLabel + ': ' + params.data.value[0].toFixed(1) + '<br/>' +
                   yLabel + ': ' + params.data.value[1].toFixed(1)
          }
        },
        legend: {
          data: seriesData.map(function(s) { return s.name }),
          bottom: 10
        },
        grid: {
          left: '10%',
          right: '5%',
          top: '10%',
          bottom: '20%'
        },
        xAxis: {
          name: axisLabels[self.xAxis],
          nameLocation: 'center',
          nameGap: 30,
          type: 'value',
          splitLine: { show: true, lineStyle: { type: 'dashed' } }
        },
        yAxis: {
          name: axisLabels[self.yAxis],
          nameLocation: 'center',
          nameGap: 40,
          type: 'value',
          splitLine: { show: true, lineStyle: { type: 'dashed' } }
        },
        series: seriesData
      }
      
      this.chart.setOption(option)
    },
    
    selectCluster(cluster) {
      this.selectedCluster = this.selectedCluster === cluster ? null : cluster
      this.filterCluster = this.selectedCluster
      this.filterStudents()
    },
    
    filterStudents() {
      var self = this
      self.filteredProfiles = self.profiles.filter(function(p) {
        var matchKeyword = !self.searchKeyword || 
          (p.studentName && p.studentName.indexOf(self.searchKeyword) > -1)
        var matchCluster = self.filterCluster === null || p.cluster === self.filterCluster
        return matchKeyword && matchCluster
      })
    },
    
    getScoreClass(score) {
      if (score >= 80) return 'score-high'
      if (score >= 60) return 'score-mid'
      return 'score-low'
    },
    
    getVarianceClass(variance) {
      if (variance <= 50)  return 'score-high'  // 方差小 = 稳定
      if (variance <= 200) return 'score-mid'
      return 'score-low'                        // 方差大 = 不稳定
    },
    getErrorClass(rate) {
      if (rate <= 0.2) return 'error-low'
      if (rate <= 0.4) return 'error-mid'
      return 'error-high'
    },
    
    getClusterTagType(cluster) {
      var types = ['danger', 'warning', 'success']
      return types[cluster] || 'info'
    }
  },
  beforeDestroy() {
    if (this.chart) {
      this.chart.dispose()
    }
  }
}
</script>

<style scoped>
.student-profile-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 24px 32px;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  font-size: 40px;
  color: #fff;
}

.title-text h1 {
  color: #fff;
  margin: 0 0 4px;
  font-size: 24px;
}

.title-text p {
  color: rgba(255,255,255,0.8);
  margin: 0;
  font-size: 14px;
}

.header-actions .el-button {
  background: rgba(255,255,255,0.2);
  border-color: rgba(255,255,255,0.3);
  color: #fff;
}

.header-actions .el-button:hover {
  background: rgba(255,255,255,0.3);
}

/* 统计卡片 */
.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon i {
  font-size: 28px;
  color: #fff;
}

.stat-card.total .stat-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
.stat-card.cluster-0 .stat-icon { background: linear-gradient(135deg, #F56C6C, #f78989); }
.stat-card.cluster-1 .stat-icon { background: linear-gradient(135deg, #E6A23C, #f0b86e); }
.stat-card.cluster-2 .stat-icon { background: linear-gradient(135deg, #67C23A, #85ce61); }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-desc {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 4px;
}

/* 图表卡片 */
.chart-card, .detail-card, .student-list-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  overflow: hidden;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.card-title i {
  margin-right: 8px;
  color: #667eea;
}

.scatter-chart {
  height: 400px;
  padding: 20px;
}

/* 聚类详情 */
.cluster-details {
  padding: 16px;
}

.cluster-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  border-radius: 10px;
  background: #f8f9fa;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.cluster-item:hover {
  background: #e0e7ff;
}

.cluster-item.active {
  background: #e0e7ff;
  border-left: 4px solid #667eea;
}

.cluster-badge {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.badge-0 { background: linear-gradient(135deg, #F56C6C, #f78989); }
.badge-1 { background: linear-gradient(135deg, #E6A23C, #f0b86e); }
.badge-2 { background: linear-gradient(135deg, #67C23A, #85ce61); }

.cluster-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.cluster-desc {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.cluster-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #606266;
}

.cluster-stats i {
  margin-right: 4px;
  color: #667eea;
}

/* 学生列表 */
.student-list-card {
  margin-top: 20px;
}

.main-content {
  margin-bottom: 20px;
}

.score-high { color: #67C23A; font-weight: 600; }
.score-mid { color: #E6A23C; font-weight: 600; }
.score-low { color: #F56C6C; font-weight: 600; }

.error-low { color: #67C23A; }
.error-mid { color: #E6A23C; }
.error-high { color: #F56C6C; }
</style>
