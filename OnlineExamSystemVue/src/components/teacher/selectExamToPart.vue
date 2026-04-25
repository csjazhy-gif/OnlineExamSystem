<template>
  <div class="part-page">

    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-icon-box">
        <i class="el-icon-data-analysis"></i>
      </div>
      <div class="header-text">
        <h2 class="header-title">成绩分段查询</h2>
        <p class="header-sub">选择一场考试，查看详细的成绩分段分析报告</p>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchKey"
        placeholder="搜索试卷名称..."
        prefix-icon="el-icon-search"
        clearable
        class="search-input"
        @keyup.enter.native="doSearch"
      />
      <el-button type="primary" icon="el-icon-search" @click="doSearch">搜索</el-button>
      <el-button icon="el-icon-refresh" @click="resetSearch">重置</el-button>
    </div>

    <!-- 考试卡片 -->
    <div class="exam-grid" v-loading="loading">
      <div
        v-for="item in list"
        :key="item.examCode"
        class="exam-card"
        @click="toPart(item.examCode, item.source)"
      >
        <!-- 类型标签 -->
        <div class="type-badge" :class="getBadgeClass(item.type)">
          {{ item.type || '常规考试' }}
        </div>

        <!-- 卡片内容 -->
        <div class="card-body">
          <h3 class="exam-name">{{ item.source }}</h3>
          <p class="exam-desc">{{ item.description || '暂无描述' }}</p>

          <div class="meta-grid">
            <div class="meta-item">
              <i class="el-icon-date meta-icon"></i>
              <span>{{ formatDate(item.examDate) }}</span>
            </div>
            <div class="meta-item">
              <i class="el-icon-timer meta-icon"></i>
              <span>{{ item.totalTime || '--' }} 分钟</span>
            </div>
            <div class="meta-item">
              <i class="el-icon-trophy meta-icon"></i>
              <span>{{ item.totalScore || '--' }} 分</span>
            </div>
            <div class="meta-item" v-if="item.grade">
              <i class="el-icon-user meta-icon"></i>
              <span>{{ item.grade }}</span>
            </div>
          </div>

          <div class="card-org" v-if="item.institute">
            <i class="el-icon-office-building"></i>
            {{ item.institute }}{{ item.major ? ' · ' + item.major : '' }}
          </div>
        </div>

        <!-- 卡片底部 -->
        <div class="card-footer">
          <el-button size="small" type="primary" icon="el-icon-data-analysis" round>
            查看分段分析
          </el-button>
          <span class="exam-code-tag">No.{{ item.examCode }}</span>
        </div>

        <!-- 悬浮浮层提示 -->
        <div class="card-hover-mask">
          <i class="el-icon-data-analysis mask-icon"></i>
          <span>点击查看分段分析</span>
        </div>
      </div>

      <!-- 空状态 -->
      <div class="empty-state" v-if="!loading && list.length === 0">
        <i class="el-icon-folder-opened empty-icon"></i>
        <p class="empty-text">暂无考试数据</p>
        <p class="empty-sub">请先在考试管理中创建考试</p>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrap" v-if="pagination.total > 0">
      <el-pagination
        background
        layout="total, prev, pager, next"
        :current-page="pagination.current"
        :page-size="pagination.size"
        :total="pagination.total"
        @current-change="handleCurrentChange"
      />
    </div>

  </div>
</template>

<script>
export default {
  data() {
    return {
      loading: false,
      searchKey: '',
      list: [],
      pagination: {
        current: 1,
        total: 0,
        size: 9,
        records: []
      }
    }
  },
  created() {
    this.getExamInfo()
  },
  methods: {
    getExamInfo() {
      this.loading = true
      this.$axios(`/api/exams/${this.pagination.current}/${this.pagination.size}`)
        .then(res => {
          this.pagination = res.data.data
          this.list = this.pagination.records || []
          this.loading = false
        })
        .catch(() => { this.loading = false })
    },
    handleCurrentChange(val) {
      this.pagination.current = val
      this.getExamInfo()
    },
    doSearch() {
      if (!this.searchKey.trim()) {
        this.getExamInfo()
        return
      }
      this.loading = true
      this.$axios('/api/exams').then(res => {
        const all = res.data.data || []
        this.list = all.filter(e => e.source && e.source.includes(this.searchKey.trim()))
        this.pagination.total = this.list.length
        this.loading = false
      }).catch(() => { this.loading = false })
    },
    resetSearch() {
      this.searchKey = ''
      this.getExamInfo()
    },
    toPart(examCode, source) {
      this.$router.push({ path: '/scorePart', query: { examCode, source } })
    },
    formatDate(d) {
      if (!d) return '--'
      return String(d).substr(0, 10)
    },
    getBadgeClass(type) {
      if (!type) return 'badge-default'
      if (type.includes('期末')) return 'badge-danger'
      if (type.includes('期中')) return 'badge-warning'
      if (type.includes('随堂') || type.includes('测试')) return 'badge-info'
      if (type.includes('作业')) return 'badge-success'
      return 'badge-primary'
    }
  }
}
</script>

<style lang="less" scoped>
.part-page {
  padding: 24px 32px;
  background: #f5f7fa;
  min-height: 100%;
}

/* 页面标题 */
.page-header {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 24px;
  padding: 24px 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}
.header-icon-box {
  width: 56px;
  height: 56px;
  background: rgba(255,255,255,0.2);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
  flex-shrink: 0;
  backdrop-filter: blur(8px);
}
.header-title {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 4px 0;
}
.header-sub {
  font-size: 14px;
  color: rgba(255,255,255,0.85);
  margin: 0;
}

/* 搜索栏 */
.search-bar {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.search-input {
  width: 280px;
}

/* 考试卡片网格 */
.exam-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  min-height: 200px;
}

/* 考试卡片 */
.exam-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  display: flex;
  flex-direction: column;
  border: 1.5px solid #ebeef5;

  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 32px rgba(102,126,234,0.18);
    border-color: #667eea;

    .card-hover-mask {
      opacity: 1;
    }
  }
}

/* 类型角标 */
.type-badge {
  position: absolute;
  top: 14px;
  right: 14px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.badge-danger  { background: #fef0f0; color: #F56C6C; }
.badge-warning { background: #fdf6ec; color: #E6A23C; }
.badge-info    { background: #f4f4f5; color: #909399; }
.badge-success { background: #f0f9eb; color: #67C23A; }
.badge-primary { background: #ecf5ff; color: #409EFF; }
.badge-default { background: #f5f7fa; color: #606266; }

/* 卡片内容 */
.card-body {
  padding: 20px 20px 12px;
  flex: 1;
}
.exam-name {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
  padding-right: 64px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.exam-desc {
  font-size: 13px;
  color: #909399;
  margin: 0 0 14px 0;
  line-height: 1.5;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 40px;
}
.meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 12px;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: #606266;
}
.meta-icon {
  color: #909399;
  font-size: 14px;
}
.card-org {
  font-size: 12px;
  color: #b0b4bc;
  margin-top: 4px;
  i { margin-right: 4px; }
}

/* 卡片底部 */
.card-footer {
  padding: 12px 20px;
  background: #fafafa;
  border-top: 1px solid #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.exam-code-tag {
  font-size: 12px;
  color: #c0c4cc;
}

/* 悬浮遮罩 */
.card-hover-mask {
  position: absolute;
  inset: 0;
  background: rgba(102,126,234,0.88);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.25s;
  border-radius: 16px;
  backdrop-filter: blur(2px);
}
.mask-icon {
  font-size: 40px;
}

/* 空状态 */
.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #c0c4cc;
}
.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}
.empty-text {
  font-size: 16px;
  font-weight: 600;
  color: #909399;
  margin: 0 0 6px 0;
}
.empty-sub {
  font-size: 13px;
  color: #c0c4cc;
  margin: 0;
}

/* 分页 */
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 28px;
}

/* 响应式 */
@media (max-width: 1200px) {
  .exam-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .part-page { padding: 16px; }
  .exam-grid { grid-template-columns: 1fr; }
  .search-bar { flex-wrap: wrap; }
}
</style>
