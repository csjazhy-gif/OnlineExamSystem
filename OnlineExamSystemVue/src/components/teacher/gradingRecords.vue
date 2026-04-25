<template>
  <div id="gradingRecords" class="page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h2 class="page-title">
          <i class="el-icon-finished"></i>
          阅卷记录
        </h2>
        <p class="page-desc">查看所有已完成批阅的主观题记录</p>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <span class="stat-value">{{ total }}</span>
          <span class="stat-label">已批阅</span>
        </div>
      </div>
    </div>

    <!-- 筛选区 -->
    <div class="ruoyi-card search-card">
      <el-form :inline="true" class="search-form">
        <el-form-item label="考试">
          <el-select v-model="filterExam" placeholder="全部考试" clearable style="width:220px" @change="onExamChange">
            <el-option v-for="exam in examList" :key="exam.examCode" :label="exam.source" :value="exam.examCode" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="loadData">搜索</el-button>
          <el-button icon="el-icon-refresh" @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <div class="ruoyi-card table-card">
      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        border
        style="width:100%"
        :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: '600' }"
      >
        <el-table-column prop="answerId" label="ID" width="70" align="center" />
        <el-table-column prop="studentName" label="学生" width="110" align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.studentName || '学生' + scope.row.studentId }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="subject" label="科目" width="130" align="center">
          <template slot-scope="scope">
            <el-tag type="info" size="mini">{{ scope.row.subject }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="question" label="题目" min-width="200" show-overflow-tooltip />
        <el-table-column prop="studentAnswer" label="学生答案" min-width="180" show-overflow-tooltip>
          <template slot-scope="scope">
            <span :class="scope.row.studentAnswer ? '' : 'empty-answer'">
              {{ scope.row.studentAnswer || '（未作答）' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="得分" width="120" align="center">
          <template slot-scope="scope">
            <span class="score-text" :class="getScoreClass(scope.row.teacherScore, scope.row.maxScore)">
              {{ scope.row.teacherScore }}
            </span>
            <span class="score-max"> / {{ scope.row.maxScore }}</span>
          </template>
        </el-table-column>
        <el-table-column label="得分率" width="100" align="center">
          <template slot-scope="scope">
            <el-progress
              :percentage="calcRatio(scope.row.teacherScore, scope.row.maxScore)"
              :color="getRatioColor(scope.row.teacherScore, scope.row.maxScore)"
              :stroke-width="6"
              :show-text="false"
              style="margin-top:2px"
            />
            <span class="ratio-text">{{ calcRatio(scope.row.teacherScore, scope.row.maxScore) }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="teacherComment" label="评语" width="160" show-overflow-tooltip>
          <template slot-scope="scope">
            <span class="comment-text">{{ scope.row.teacherComment || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="批阅时间" width="150" align="center">
          <template slot-scope="scope">
            {{ formatTime(scope.row.scoredTime) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center" fixed="right">
          <template slot-scope="scope">
            <el-button type="text" size="mini" icon="el-icon-view" @click="viewDetail(scope.row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        background
        layout="total, prev, pager, next, sizes"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        :page-sizes="[20, 50, 100]"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
        style="margin-top:20px; display:flex; justify-content:flex-end"
      />
    </div>

    <!-- 详情弹窗 -->
    <el-dialog title="阅卷详情" :visible.sync="detailVisible" width="680px" :close-on-click-modal="false" append-to-body custom-class="grading-detail-dialog">
      <div class="detail-wrap" v-if="currentRecord">
        <!-- 基本信息 -->
        <div class="detail-info-row">
          <div class="info-chip">
            <i class="el-icon-user"></i>
            <span>{{ currentRecord.studentName || '学生' + currentRecord.studentId }}</span>
          </div>
          <div class="info-chip">
            <i class="el-icon-collection-tag"></i>
            <span>{{ currentRecord.subject }}</span>
          </div>
          <div class="info-chip score-chip" :class="getScoreClass(currentRecord.teacherScore, currentRecord.maxScore)">
            <i class="el-icon-star-on"></i>
            <span>{{ currentRecord.teacherScore }} / {{ currentRecord.maxScore }} 分</span>
          </div>
          <div class="info-chip time-chip">
            <i class="el-icon-time"></i>
            <span>{{ formatTime(currentRecord.scoredTime) }}</span>
          </div>
        </div>

        <!-- 题目 -->
        <div class="detail-section">
          <div class="section-label"><i class="el-icon-document"></i> 题目</div>
          <div class="section-content question-box">{{ currentRecord.question }}</div>
        </div>

        <!-- 参考答案 -->
        <div class="detail-section">
          <div class="section-label">
            <i class="el-icon-check"></i> 参考答案
            <el-button type="text" size="mini" @click="showRef = !showRef" style="margin-left:8px">
              {{ showRef ? '收起' : '展开' }}
            </el-button>
          </div>
          <div class="section-content ref-box" v-show="showRef">{{ currentRecord.referenceAnswer || '（无参考答案）' }}</div>
        </div>

        <!-- 学生答案 -->
        <div class="detail-section">
          <div class="section-label"><i class="el-icon-edit-outline"></i> 学生答案</div>
          <div class="section-content student-box">{{ currentRecord.studentAnswer || '（未作答）' }}</div>
        </div>

        <!-- 评分 + 评语 -->
        <div class="detail-score-row">
          <div class="score-display">
            <div class="score-circle-mini">
              <span class="s-num">{{ currentRecord.teacherScore }}</span>
              <span class="s-max"> / {{ currentRecord.maxScore }}</span>
            </div>
            <el-progress
              :percentage="calcRatio(currentRecord.teacherScore, currentRecord.maxScore)"
              :color="getRatioColor(currentRecord.teacherScore, currentRecord.maxScore)"
              :stroke-width="10"
              style="width:160px"
            />
          </div>
          <div class="comment-display" v-if="currentRecord.teacherComment">
            <div class="section-label" style="margin-bottom:8px"><i class="el-icon-chat-line-round"></i> 评语</div>
            <div class="comment-bubble">{{ currentRecord.teacherComment }}</div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'GradingRecords',
  data() {
    return {
      loading: false,
      tableData: [],
      total: 0,
      currentPage: 1,
      pageSize: 20,
      filterExam: null,
      examList: [],
      detailVisible: false,
      currentRecord: null,
      showRef: true
    }
  },
  mounted() {
    this.loadExamList()
    this.loadData()
  },
  methods: {
    loadExamList() {
      var self = this
      this.$axios.get('/api/exams/1/100').then(function(res) {
        if (res.data.code === 200) self.examList = res.data.data.records || []
      })
    },

    loadData() {
      var self = this
      this.loading = true
      var baseUrl = this.filterExam
        ? '/api/scoring/graded/exam/' + this.filterExam
        : '/api/scoring/graded'

      this.$axios.get(baseUrl, {
        params: { page: this.currentPage, size: this.pageSize }
      }).then(function(res) {
        self.loading = false
        if (res.data.code === 200 && res.data.data) {
          self.tableData = res.data.data.records || []
          self.total = res.data.data.total || 0
        } else {
          self.$message.warning(res.data.message || '暂无数据')
        }
      }).catch(function(err) {
        self.loading = false
        var status = err.response && err.response.status
        if (status === 404) {
          self.$message.error('接口不存在，请重启后端服务后刷新')
        } else {
          self.$message.error('加载数据失败，请检查后端服务是否正常运行')
        }
      })
    },

    onExamChange() {
      this.currentPage = 1
      this.loadData()
    },

    resetFilter() {
      this.filterExam = null
      this.currentPage = 1
      this.loadData()
    },

    handlePageChange(page) {
      this.currentPage = page
      this.loadData()
    },

    handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      this.loadData()
    },

    viewDetail(row) {
      this.currentRecord = row
      this.showRef = true
      this.detailVisible = true
    },

    calcRatio(score, max) {
      if (!max || max === 0) return 0
      return Math.round((score / max) * 100)
    },

    getScoreClass(score, max) {
      var ratio = max > 0 ? score / max : 0
      if (ratio >= 0.8) return 'score-high'
      if (ratio >= 0.6) return 'score-mid'
      if (ratio >= 0.4) return 'score-low'
      return 'score-fail'
    },

    getRatioColor(score, max) {
      var ratio = max > 0 ? score / max : 0
      if (ratio >= 0.8) return '#67C23A'
      if (ratio >= 0.6) return '#409EFF'
      if (ratio >= 0.4) return '#E6A23C'
      return '#F56C6C'
    },

    formatTime(time) {
      if (!time) return '-'
      var d = new Date(time)
      var p = function(n) { return n < 10 ? '0' + n : n }
      return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) +
             ' ' + p(d.getHours()) + ':' + p(d.getMinutes())
    }
  }
}
</script>

<style lang="less" scoped>
.page-container {
  padding: 20px;
  background: #f0f2f5;
  min-height: calc(100vh - 120px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  border-radius: 12px;
  padding: 24px 30px;
  color: #fff;
  margin-bottom: 20px;
  box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-desc { margin: 0; opacity: 0.9; font-size: 14px; }

.header-stats { text-align: center; }

.stat-item { display: flex; flex-direction: column; align-items: center; }
.stat-value { font-size: 36px; font-weight: 700; }
.stat-label { font-size: 14px; opacity: 0.9; }

.search-card { margin-bottom: 16px; }

.table-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

// 得分颜色
.score-text { font-weight: 700; font-size: 16px; }
.score-high { color: #67C23A; }
.score-mid  { color: #409EFF; }
.score-low  { color: #E6A23C; }
.score-fail { color: #F56C6C; }
.score-max  { font-size: 12px; color: #909399; }

.ratio-text { font-size: 12px; color: #606266; display: block; text-align: center; margin-top: 2px; }

.empty-answer { color: #c0c4cc; font-style: italic; }
.comment-text { color: #606266; font-size: 13px; }

// 详情弹窗
.detail-wrap { padding: 4px 0; }

.detail-info-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.info-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: #f5f7fa;
  border-radius: 20px;
  font-size: 14px;
  color: #606266;
  i { color: #909399; }
}

.score-chip {
  font-weight: 700;
  &.score-high { background: #f0f9eb; color: #67C23A; i { color: #67C23A; } }
  &.score-mid  { background: #ecf5ff; color: #409EFF; i { color: #409EFF; } }
  &.score-low  { background: #fdf6ec; color: #E6A23C; i { color: #E6A23C; } }
  &.score-fail { background: #fef0f0; color: #F56C6C; i { color: #F56C6C; } }
}

.time-chip { color: #909399; }

.detail-section { margin-bottom: 16px; }

.section-label {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-content {
  padding: 14px 16px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
}

.question-box { background: #f5f7fa; border-left: 4px solid #409EFF; }
.ref-box { background: #f0f9eb; border-left: 4px solid #67C23A; color: #67C23A; }
.student-box { background: #fdf6ec; border-left: 4px solid #E6A23C; min-height: 60px; }

.detail-score-row {
  display: flex;
  gap: 24px;
  align-items: flex-start;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
  flex-wrap: wrap;
}

.score-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.score-circle-mini {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.s-num { font-size: 40px; font-weight: 700; color: #409EFF; line-height: 1; }
.s-max { font-size: 16px; color: #909399; }

.comment-display { flex: 1; }

.comment-bubble {
  background: #f0f9ff;
  border: 1px solid #d0e8ff;
  border-radius: 10px;
  padding: 12px 16px;
  font-size: 14px;
  color: #606266;
  line-height: 1.7;
}
</style>

<!-- 居中样式：全局，不加 scoped -->
<style>
.grading-detail-dialog {
  margin: 0 !important;
  position: absolute;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
}
</style>
