<template>
  <div id="violationRecords" class="page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h2 class="page-title">
          <i class="el-icon-warning"></i>
          考试违规记录
        </h2>
        <p class="page-desc">查看考试期间学生的违规行为（切屏、离焦等）</p>
      </div>
      <div class="header-stats" v-if="selectedExam">
        <div class="stat-item">
          <span class="stat-value">{{ total }}</span>
          <span class="stat-label">违规次数</span>
        </div>
        <div class="stat-item" style="margin-left:30px">
          <span class="stat-value">{{ affectedStudents }}</span>
          <span class="stat-label">涉及学生</span>
        </div>
      </div>
    </div>

    <!-- 筛选区 -->
    <div class="ruoyi-card search-card">
      <el-form :inline="true" class="search-form">
        <el-form-item label="选择考试">
          <el-select
            v-model="selectedExam"
            placeholder="请选择考试"
            clearable
            filterable
            style="width:260px"
            @change="onExamChange"
          >
            <el-option
              v-for="exam in examList"
              :key="exam.examCode"
              :label="exam.source + ' (考试号: ' + exam.examCode + ')'"
              :value="exam.examCode"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="违规类型">
          <el-select v-model="filterType" placeholder="全部类型" clearable style="width:160px" @change="applyFilter">
            <el-option label="切换标签页" value="tab_switch" />
            <el-option label="离开页面" value="blur" />
            <el-option label="复制粘贴" value="copy_paste" />
            <el-option label="全屏退出" value="fullscreen_exit" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="loadData" :disabled="!selectedExam">查询</el-button>
          <el-button icon="el-icon-refresh" @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 空状态 -->
    <div class="ruoyi-card empty-card" v-if="!selectedExam">
      <el-empty description="请先选择一场考试以查看违规记录">
        <i class="el-icon-warning empty-icon"></i>
      </el-empty>
    </div>

    <!-- 数据表格 -->
    <div class="ruoyi-card table-card" v-if="selectedExam">
      <!-- 统计概览 -->
      <div class="summary-row" v-if="tableData.length > 0">
        <div class="summary-chip" v-for="(count, type) in typeSummary" :key="type">
          <el-tag :type="getTypeTagType(type)" size="small">{{ getTypeLabel(type) }}</el-tag>
          <span class="chip-count">{{ count }} 次</span>
        </div>
      </div>

      <el-table
        :data="filteredData"
        v-loading="loading"
        stripe
        border
        style="width:100%"
        :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: '600' }"
        row-key="id"
      >
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="studentId" label="学生ID" width="100" align="center" />
        <el-table-column prop="violationType" label="违规类型" width="140" align="center">
          <template slot-scope="scope">
            <el-tag :type="getTypeTagType(scope.row.violationType)" size="small">
              {{ getTypeLabel(scope.row.violationType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="违规描述" min-width="220" show-overflow-tooltip />
        <el-table-column prop="violationTime" label="发生时间" width="160" align="center">
          <template slot-scope="scope">
            {{ formatTime(scope.row.violationTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="clientIp" label="IP地址" width="130" align="center">
          <template slot-scope="scope">
            <span class="ip-text">{{ scope.row.clientIp || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130" align="center" fixed="right">
          <template slot-scope="scope">
            <el-button type="text" size="mini" icon="el-icon-view" @click="viewDetail(scope.row)">详情</el-button>
            <el-button type="text" size="mini" icon="el-icon-delete" style="color:#F56C6C" @click="deleteRecord(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="table-footer">
        <span class="total-tip">共 {{ filteredData.length }} 条违规记录，来自 {{ affectedStudents }} 名学生</span>
        <el-button
          v-if="tableData.length > 0"
          type="danger"
          size="small"
          icon="el-icon-delete"
          plain
          @click="clearAll"
        >清空本场违规记录</el-button>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog title="违规详情" :visible.sync="detailVisible" width="560px" :close-on-click-modal="false">
      <div class="detail-wrap" v-if="currentRecord">
        <div class="detail-info-row">
          <div class="info-chip">
            <i class="el-icon-user"></i>
            <span>学生 {{ currentRecord.studentId }}</span>
          </div>
          <div class="info-chip">
            <el-tag :type="getTypeTagType(currentRecord.violationType)" size="small">
              {{ getTypeLabel(currentRecord.violationType) }}
            </el-tag>
          </div>
          <div class="info-chip time-chip">
            <i class="el-icon-time"></i>
            <span>{{ formatTime(currentRecord.violationTime) }}</span>
          </div>
        </div>

        <div class="detail-section">
          <div class="section-label"><i class="el-icon-document"></i> 违规描述</div>
          <div class="section-content desc-box">{{ currentRecord.description || '（无描述）' }}</div>
        </div>

        <div class="detail-section">
          <div class="section-label"><i class="el-icon-monitor"></i> 客户端信息</div>
          <div class="section-content info-box">
            <div class="info-line"><span class="il-label">IP地址：</span><span>{{ currentRecord.clientIp || '未知' }}</span></div>
            <div class="info-line"><span class="il-label">浏览器：</span><span class="ua-text">{{ currentRecord.userAgent || '未知' }}</span></div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'ViolationRecords',
  data() {
    return {
      loading: false,
      tableData: [],
      total: 0,
      selectedExam: null,
      filterType: '',
      examList: [],
      detailVisible: false,
      currentRecord: null
    }
  },
  computed: {
    filteredData() {
      if (!this.filterType) return this.tableData
      return this.tableData.filter(function(r) { return r.violationType === this.filterType }.bind(this))
    },
    affectedStudents() {
      var ids = new Set(this.filteredData.map(function(r) { return r.studentId }))
      return ids.size
    },
    typeSummary() {
      var map = {}
      this.tableData.forEach(function(r) {
        var t = r.violationType || 'other'
        map[t] = (map[t] || 0) + 1
      })
      return map
    }
  },
  mounted() {
    this.loadExamList()
  },
  methods: {
    loadExamList() {
      var self = this
      this.$axios.get('/api/exams/1/100').then(function(res) {
        if (res.data.code === 200) self.examList = res.data.data.records || []
      })
    },

    loadData() {
      if (!this.selectedExam) return
      var self = this
      this.loading = true
      this.$axios.get('/api/violation/exam/' + this.selectedExam).then(function(res) {
        self.loading = false
        if (res.data.code === 200) {
          self.tableData = res.data.data || []
          self.total = self.tableData.length
        } else {
          self.$message.warning('暂无违规记录')
          self.tableData = []
        }
      }).catch(function() {
        self.loading = false
        self.$message.error('加载失败，请检查后端服务')
      })
    },

    onExamChange() {
      this.filterType = ''
      this.tableData = []
      this.total = 0
      if (this.selectedExam) this.loadData()
    },

    applyFilter() {
      // computed filteredData 自动响应
    },

    resetFilter() {
      this.selectedExam = null
      this.filterType = ''
      this.tableData = []
      this.total = 0
    },

    viewDetail(row) {
      this.currentRecord = row
      this.detailVisible = true
    },

    deleteRecord(row) {
      this.$confirm('确认删除该条违规记录？', '提示', { type: 'warning' }).then(function() {
        this.$axios.delete('/api/violation/' + row.id).then(function(res) {
          if (res.data.code === 200) {
            this.$message.success('删除成功')
            this.loadData()
          } else {
            this.$message.error('删除失败')
          }
        }.bind(this))
      }.bind(this)).catch(function() {})
    },

    clearAll() {
      this.$confirm('确认清空本场考试的所有违规记录？此操作不可恢复！', '警告', {
        type: 'warning',
        confirmButtonText: '确认清空',
        confirmButtonClass: 'el-button--danger'
      }).then(function() {
        this.$axios.delete('/api/violation/exam/' + this.selectedExam).then(function(res) {
          if (res.data.code === 200) {
            this.$message.success('已清空')
            this.tableData = []
            this.total = 0
          }
        }.bind(this))
      }.bind(this)).catch(function() {})
    },

    getTypeLabel(type) {
      var map = {
        tab_switch: '切换标签页',
        blur: '离开页面',
        copy_paste: '复制粘贴',
        fullscreen_exit: '全屏退出',
        other: '其他'
      }
      return map[type] || type || '未知'
    },

    getTypeTagType(type) {
      var map = {
        tab_switch: 'danger',
        blur: 'warning',
        copy_paste: 'danger',
        fullscreen_exit: 'warning',
        other: 'info'
      }
      return map[type] || 'info'
    },

    formatTime(time) {
      if (!time) return '-'
      var d = new Date(time)
      if (isNaN(d.getTime())) return time
      var p = function(n) { return n < 10 ? '0' + n : n }
      return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) +
             ' ' + p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds())
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
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 12px;
  padding: 24px 30px;
  color: #fff;
  margin-bottom: 20px;
  box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
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

.header-stats { display: flex; }
.stat-item { display: flex; flex-direction: column; align-items: center; }
.stat-value { font-size: 36px; font-weight: 700; }
.stat-label { font-size: 14px; opacity: 0.9; }

.search-card { margin-bottom: 16px; }

.empty-card {
  background: #fff;
  border-radius: 12px;
  padding: 60px 20px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.empty-icon {
  font-size: 60px;
  color: #dcdfe6;
  display: block;
  margin-bottom: 16px;
}

.table-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.summary-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.summary-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f5f7fa;
  border-radius: 20px;
  padding: 4px 12px 4px 6px;
}

.chip-count {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.ip-text { font-family: monospace; font-size: 12px; color: #909399; }

.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.total-tip { font-size: 13px; color: #909399; }

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

.desc-box { background: #fef0f0; border-left: 4px solid #F56C6C; }
.info-box { background: #f5f7fa; border-left: 4px solid #909399; }

.info-line {
  display: flex;
  margin-bottom: 6px;
  &:last-child { margin-bottom: 0; }
}

.il-label { color: #909399; min-width: 70px; flex-shrink: 0; }

.ua-text {
  font-family: monospace;
  font-size: 12px;
  color: #606266;
  word-break: break-all;
}

.ruoyi-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  margin-bottom: 16px;
}
</style>
