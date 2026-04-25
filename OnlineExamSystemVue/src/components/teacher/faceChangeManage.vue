<template>
  <div class="face-change-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-icon">
        <i class="el-icon-user"></i>
      </div>
      <div class="header-text">
        <h2>人脸修改审批</h2>
        <p>审核学生的人脸修改申请</p>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-radio-group v-model="statusFilter" @change="loadData" size="medium">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="pending">
          <i class="el-icon-time"></i> 待审批
          <el-badge v-if="pendingCount > 0" :value="pendingCount" class="badge-item" />
        </el-radio-button>
        <el-radio-button label="approved">
          <i class="el-icon-check"></i> 已通过
        </el-radio-button>
        <el-radio-button label="rejected">
          <i class="el-icon-close"></i> 已拒绝
        </el-radio-button>
        <el-radio-button label="completed">
          <i class="el-icon-finished"></i> 已完成
        </el-radio-button>
      </el-radio-group>

      <el-button icon="el-icon-refresh" @click="loadData" circle size="small" title="刷新"></el-button>
    </div>

    <!-- 申请列表表格 -->
    <el-table
      :data="requestList"
      v-loading="loading"
      stripe
      border
      style="width: 100%"
      :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: '600' }"
    >
      <el-table-column prop="id" label="ID" width="70" align="center"></el-table-column>
      <el-table-column prop="studentId" label="学号" width="90" align="center"></el-table-column>
      <el-table-column prop="studentName" label="学生姓名" width="120" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.studentName || '未知' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="reason" label="申请原因" min-width="200" show-overflow-tooltip></el-table-column>
      <el-table-column prop="status" label="状态" width="110" align="center">
        <template slot-scope="scope">
          <el-tag :type="getStatusType(scope.row.status)" effect="dark" size="small">
            {{ getStatusLabel(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createTime" label="申请时间" width="170" align="center">
        <template slot-scope="scope">
          {{ formatTime(scope.row.createTime) }}
        </template>
      </el-table-column>
      <el-table-column prop="reviewerName" label="审批人" width="100" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.reviewerName || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="reviewComment" label="审批意见" width="160" show-overflow-tooltip>
        <template slot-scope="scope">
          <span>{{ scope.row.reviewComment || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" align="center" fixed="right">
        <template slot-scope="scope">
          <template v-if="scope.row.status === 'pending'">
            <div style="display:flex;justify-content:center;gap:8px;">
              <el-button type="success" size="mini" icon="el-icon-check" @click="handleReview(scope.row, 'approved')">通过</el-button>
              <el-button type="danger" size="mini" icon="el-icon-close" @click="handleReview(scope.row, 'rejected')">拒绝</el-button>
            </div>
          </template>
          <span v-else class="reviewed-text">
            {{ scope.row.updateTime ? formatTime(scope.row.updateTime) : '已处理' }}
          </span>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        background
        layout="total, prev, pager, next, sizes"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        :page-sizes="[10, 20, 50]"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      ></el-pagination>
    </div>

    <!-- 审批弹窗 -->
    <el-dialog
      :title="reviewAction === 'approved' ? '通过申请' : '拒绝申请'"
      :visible.sync="reviewDialogVisible"
      width="450px"
      class="review-dialog"
    >
      <div class="review-info">
        <p><strong>学生：</strong>{{ currentRequest.studentName }} (ID: {{ currentRequest.studentId }})</p>
        <p><strong>申请原因：</strong>{{ currentRequest.reason }}</p>
      </div>
      <el-form label-width="80px">
        <el-form-item label="审批意见">
          <el-input
            type="textarea"
            v-model="reviewComment"
            :rows="3"
            :placeholder="reviewAction === 'approved' ? '可选，如：审批通过，请尽快重新注册' : '请填写拒绝原因'"
          ></el-input>
        </el-form-item>
      </el-form>
      <div v-if="reviewAction === 'approved'" class="approve-warning">
        <i class="el-icon-warning"></i>
        <span>通过后将清除该学生的人脸数据，学生需重新注册人脸</span>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button
          :type="reviewAction === 'approved' ? 'success' : 'danger'"
          @click="submitReview"
          :loading="reviewLoading"
        >
          {{ reviewAction === 'approved' ? '确认通过' : '确认拒绝' }}
        </el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
/**
 * 人脸修改审批管理页面
 * 供管理员/教师查看和处理学生的人脸修改申请
 */
export default {
  name: 'FaceChangeManage',
  data() {
    return {
      requestList: [],
      loading: false,
      statusFilter: '',
      currentPage: 1,
      pageSize: 10,
      total: 0,
      pendingCount: 0,
      reviewDialogVisible: false,
      reviewAction: '',
      reviewComment: '',
      reviewLoading: false,
      currentRequest: {}
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    /**
     * 加载申请列表数据
     * 发送分页查询请求，支持按状态筛选
     */
    async loadData() {
      this.loading = true
      try {
        const res = await this.$axios.get('/api/faceChange/list', {
          params: {
            page: this.currentPage,
            pageSize: this.pageSize,
            status: this.statusFilter
          }
        })
        if (res.data.code === 200 && res.data.data) {
          this.requestList = res.data.data.records || []
          this.total = res.data.data.total || 0
        }

        // 额外查询待审批数量
        const pendingRes = await this.$axios.get('/api/faceChange/list', {
          params: { page: 1, pageSize: 1, status: 'pending' }
        })
        if (pendingRes.data.code === 200 && pendingRes.data.data) {
          this.pendingCount = pendingRes.data.data.total || 0
        }
      } catch (error) {
        console.error('加载数据失败:', error)
        this.$message.error('加载数据失败')
      } finally {
        this.loading = false
      }
    },

    /**
     * 打开审批弹窗
     * @param {Object} row 申请记录
     * @param {string} action 操作类型（approved/rejected）
     */
    handleReview(row, action) {
      this.currentRequest = row
      this.reviewAction = action
      this.reviewComment = ''
      this.reviewDialogVisible = true
    },

    /**
     * 提交审批结果
     * 向后端发送审批请求，成功后刷新列表
     */
    async submitReview() {
      if (this.reviewAction === 'rejected' && !this.reviewComment.trim()) {
        this.$message.warning('拒绝时请填写拒绝原因')
        return
      }

      this.reviewLoading = true
      try {
        // 获取当前登录用户信息
        var reviewerName = this.$cookies.get('cname') || '管理员'
        var reviewerId = parseInt(this.$cookies.get('cid')) || 0

        const res = await this.$axios.put('/api/faceChange/review', {
          id: this.currentRequest.id,
          status: this.reviewAction,
          reviewerId: reviewerId,
          reviewerName: reviewerName,
          reviewComment: this.reviewComment.trim() || null
        })

        if (res.data.code === 200) {
          this.$message.success(res.data.message)
          this.reviewDialogVisible = false
          this.loadData()
        } else {
          this.$message.error(res.data.message || '操作失败')
        }
      } catch (error) {
        console.error('审批操作失败:', error)
        this.$message.error('网络请求失败')
      } finally {
        this.reviewLoading = false
      }
    },

    /**
     * 获取状态标签类型（ElementUI Tag组件）
     * @param {string} status 状态值
     * @return {string} Tag类型
     */
    getStatusType(status) {
      var map = { pending: 'warning', approved: 'success', rejected: 'danger', completed: 'info' }
      return map[status] || 'info'
    },

    /**
     * 获取状态中文标签
     * @param {string} status 状态值
     * @return {string} 中文标签
     */
    getStatusLabel(status) {
      var map = { pending: '待审批', approved: '已通过', rejected: '已拒绝', completed: '已完成' }
      return map[status] || '未知'
    },

    /**
     * 格式化时间显示
     * @param {string|number} time 时间值
     * @return {string} 格式化后的时间字符串
     */
    formatTime(time) {
      if (!time) return '-'
      var d = new Date(time)
      var pad = function(n) { return n < 10 ? '0' + n : n }
      return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) +
             ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes())
    },

    /**
     * 处理页码变化
     * @param {number} page 新页码
     */
    handlePageChange(page) {
      this.currentPage = page
      this.loadData()
    },

    /**
     * 处理每页条数变化
     * @param {number} size 新的每页条数
     */
    handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      this.loadData()
    }
  }
}
</script>

<style lang="less" scoped>
.face-change-manage {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.header-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, #E6A23C 0%, #F5D79E 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  color: #fff;
}

.header-text {
  h2 {
    margin: 0 0 6px;
    font-size: 22px;
    font-weight: 700;
    color: #303133;
  }
  p {
    margin: 0;
    font-size: 14px;
    color: #909399;
  }
}

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.badge-item {
  margin-left: 6px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.review-info {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;

  p {
    margin: 0 0 8px;
    font-size: 14px;
    color: #606266;
    &:last-child { margin-bottom: 0; }
  }
}

.approve-warning {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fdf6ec;
  border-radius: 8px;
  border: 1px solid #faecd8;
  color: #E6A23C;
  font-size: 13px;
  margin-top: 12px;
}

.reviewed-text {
  font-size: 12px;
  color: #909399;
}
</style>
