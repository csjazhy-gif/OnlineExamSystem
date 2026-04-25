<!-- 公告管理（教师/管理员端） - 浅蓝色大气风格 -->
<template>
  <div class="announcement-manage">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon-wrap">
          <i class="el-icon-bell"></i>
        </div>
        <div>
          <h2>公告管理</h2>
          <p class="header-desc">发布与管理系统通知公告</p>
        </div>
      </div>
      <el-button type="primary" icon="el-icon-plus" @click="openDialog(null)">发布公告</el-button>
    </div>

    <!-- 统计栏 -->
    <div class="stat-row">
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #3B82F6, #60A5FA);">
          <i class="el-icon-document"></i>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ total }}</div>
          <div class="stat-label">公告总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #10B981, #34D399);">
          <i class="el-icon-circle-check"></i>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ publishedCount }}</div>
          <div class="stat-label">已发布</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #F59E0B, #FBBF24);">
          <i class="el-icon-edit"></i>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ draftCount }}</div>
          <div class="stat-label">草稿</div>
        </div>
      </div>
    </div>

    <!-- 表格区域 -->
    <div class="table-card-wrap">
      <div class="table-head">
        <span class="table-title"><i class="el-icon-document-copy"></i> 公告列表</span>
        <el-tooltip content="刷新" placement="top">
          <el-button size="mini" circle icon="el-icon-refresh" @click="loadData"></el-button>
        </el-tooltip>
      </div>

      <el-table :data="tableData" v-loading="loading" style="width: 100%"
                :header-cell-style="{ background: 'linear-gradient(to bottom, #F0F7FF, #E8F1FD)', color: '#1E293B', fontWeight: 600, fontSize: '14px', padding: '14px 0' }"
                :cell-style="{ padding: '16px 0', fontSize: '14px' }">
        <el-table-column prop="id" label="ID" width="70" align="center">
          <template slot-scope="scope">
            <span style="color:#94A3B8;font-weight:600;">#{{ scope.row.id }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="240" show-overflow-tooltip>
          <template slot-scope="scope">
            <div style="display:flex;align-items:center;gap:8px;">
              <i class="el-icon-document" style="color:#3B82F6;"></i>
              <span style="font-weight:600;color:#1E293B;">{{ scope.row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="targetRole" label="目标受众" width="120" align="center">
          <template slot-scope="scope">
            <el-tag :type="getTagType(scope.row.targetRole)" size="small" effect="light">
              {{ getTargetLabel(scope.row.targetRole) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'info'" size="small" effect="light">
              <i :class="scope.row.status === 1 ? 'el-icon-circle-check' : 'el-icon-edit'" style="margin-right:4px;"></i>
              {{ scope.row.status === 1 ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="publisherName" label="发布者" width="110" align="center">
          <template slot-scope="scope">
            <span style="font-weight:500;color:#64748B;">{{ scope.row.publisherName }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" align="center">
          <template slot-scope="scope">
            <span style="color:#94A3B8;font-size:13px;">
              <i class="el-icon-time" style="margin-right:4px;"></i>{{ scope.row.createTime }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template slot-scope="scope">
            <el-button type="primary" size="mini" icon="el-icon-edit" plain @click="openDialog(scope.row)">编辑</el-button>
            <el-button type="danger" size="mini" icon="el-icon-delete" plain @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination background layout="prev, pager, next, total, sizes"
          :total="total" :page-size.sync="pageSize" :current-page.sync="currentPage"
          :page-sizes="[10, 20, 50]" @current-change="loadData" @size-change="loadData">
        </el-pagination>
      </div>
    </div>

    <!-- 编辑/新增对话框 -->
    <el-dialog :title="dialogForm.id ? '编辑公告' : '发布公告'" :visible.sync="dialogVisible" width="640px" :close-on-click-modal="false">
      <el-form :model="dialogForm" label-width="90px" class="dialog-form">
        <el-form-item label="公告标题">
          <el-input v-model="dialogForm.title" placeholder="请输入公告标题" maxlength="100" show-word-limit prefix-icon="el-icon-document"></el-input>
        </el-form-item>
        <el-form-item label="公告内容">
          <el-input v-model="dialogForm.content" type="textarea" :rows="8" placeholder="请输入公告内容" maxlength="2000" show-word-limit></el-input>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="目标受众">
              <el-radio-group v-model="dialogForm.targetRole">
                <el-radio label="all">全体</el-radio>
                <el-radio label="student">学生</el-radio>
                <el-radio label="teacher">教师</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发布状态">
              <el-radio-group v-model="dialogForm.status">
                <el-radio :label="1">发布</el-radio>
                <el-radio :label="0">草稿</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAnnouncement" :loading="saving">
          {{ dialogForm.id ? '保存修改' : '发布公告' }}
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'AnnouncementManage',
  data() {
    return {
      tableData: [],
      loading: false,
      saving: false,
      total: 0,
      currentPage: 1,
      pageSize: 10,
      dialogVisible: false,
      dialogForm: { title: '', content: '', targetRole: 'all', status: 1 }
    }
  },
  computed: {
    publishedCount() {
      return this.tableData.filter(a => a.status === 1).length
    },
    draftCount() {
      return this.tableData.filter(a => a.status !== 1).length
    }
  },
  created() { this.loadData() },
  methods: {
    async loadData() {
      this.loading = true
      try {
        const res = await this.$axios.get(`/api/announcement/all/${this.currentPage}/${this.pageSize}`)
        if (res.data.code === 200 && res.data.data) {
          this.tableData = res.data.data.records || []
          this.total = res.data.data.total || 0
        }
      } catch (e) {
        this.$message.error('加载失败')
      } finally {
        this.loading = false
      }
    },
    openDialog(row) {
      if (row) {
        this.dialogForm = { ...row }
      } else {
        const userName = this.$cookies.get('cname') || '管理员'
        const role = this.$cookies.get('role')
        this.dialogForm = {
          title: '', content: '', targetRole: 'all', status: 1,
          publisherId: parseInt(this.$cookies.get('cid')) || 1,
          publisherName: userName,
          publisherRole: role == 0 ? 'admin' : 'teacher'
        }
      }
      this.dialogVisible = true
    },
    async saveAnnouncement() {
      if (!this.dialogForm.title || !this.dialogForm.content) {
        return this.$message.warning('请填写标题和内容')
      }
      this.saving = true
      try {
        let res
        if (this.dialogForm.id) {
          res = await this.$axios.put('/api/announcement', this.dialogForm)
        } else {
          res = await this.$axios.post('/api/announcement', this.dialogForm)
        }
        if (res.data.code === 200) {
          this.$message.success(this.dialogForm.id ? '更新成功' : '发布成功')
          this.dialogVisible = false
          this.loadData()
        } else {
          this.$message.error(res.data.message || '操作失败')
        }
      } catch (e) {
        this.$message.error('操作失败')
      } finally {
        this.saving = false
      }
    },
    handleDelete(id) {
      this.$confirm('确定删除此公告？', '提示', { type: 'warning' }).then(async () => {
        try {
          const res = await this.$axios.delete(`/api/announcement/${id}`)
          if (res.data.code === 200) {
            this.$message.success('删除成功')
            this.loadData()
          }
        } catch (e) {
          this.$message.error('删除失败')
        }
      }).catch(() => {})
    },
    getTagType(role) {
      const map = { all: '', student: 'success', teacher: 'warning' }
      return map[role] || 'info'
    },
    getTargetLabel(role) {
      const map = { all: '全体', student: '仅学生', teacher: '仅教师' }
      return map[role] || role
    }
  }
}
</script>

<style scoped>
/* ====== 页面头部 ====== */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid #DBEAFE;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 18px;
}

.header-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(135deg, #3B82F6, #60A5FA);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3);
}

.header-icon-wrap i {
  font-size: 24px;
  color: #fff;
}

.page-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: #1E293B;
  margin: 0 0 4px;
}

.header-desc {
  font-size: 14px;
  color: #94A3B8;
  margin: 0;
}

/* ====== 统计卡片 ====== */
.stat-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  background: #fff;
  border-radius: 14px;
  border: 1px solid rgba(59, 130, 246, 0.12);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.08);
  padding: 22px 24px;
  display: flex;
  align-items: center;
  gap: 18px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(59, 130, 246, 0.15);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
  flex-shrink: 0;
}

.stat-value {
  font-size: 26px;
  font-weight: 800;
  color: #1E293B;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #94A3B8;
  font-weight: 500;
  margin-top: 2px;
}

/* ====== 表格区域 ====== */
.table-card-wrap {
  background: #fff;
  border-radius: 14px;
  border: 1px solid rgba(59, 130, 246, 0.12);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.08);
  overflow: hidden;
}

.table-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid #F1F5F9;
  background: linear-gradient(to right, #F8FBFF, #FFF);
}

.table-title {
  font-size: 15px;
  font-weight: 700;
  color: #1E293B;
}

.table-title i {
  color: #3B82F6;
  margin-right: 8px;
}

.pagination-wrap {
  padding: 20px;
  text-align: center;
  border-top: 1px solid #F1F5F9;
  background: linear-gradient(to top, #FAFCFF, #FFF);
}

/* ====== 对话框表单 ====== */
.dialog-form .el-form-item {
  margin-bottom: 22px;
}
</style>
