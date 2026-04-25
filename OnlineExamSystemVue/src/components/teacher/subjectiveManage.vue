<template>
  <div id="subjectiveManage" class="ruoyi-container">
    <!-- 查询表单 -->
    <div class="ruoyi-card search-card">
      <el-form :inline="true" :model="searchForm" class="search-form" ref="queryForm">
        <el-form-item label="科目" prop="subject">
          <el-select v-model="searchForm.subject" placeholder="选择科目" clearable style="width: 200px;">
            <el-option v-for="s in subjects" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度" prop="level">
          <el-select v-model="searchForm.level" placeholder="选择难度" clearable style="width: 200px;">
            <el-option label="简单" value="1" />
            <el-option label="较易" value="2" />
            <el-option label="中等" value="3" />
            <el-option label="较难" value="4" />
            <el-option label="困难" value="5" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="loadData">搜索</el-button>
          <el-button icon="el-icon-refresh" @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </div>



    <!-- 数据表格 -->
    <div class="ruoyi-card table-card">
      <el-table :data="tableData" v-loading="loading" class="ruoyi-table">
        <el-table-column prop="questionId" label="ID" width="80" align="center" />
        <el-table-column prop="subject" label="科目" width="120" align="center" />
        <el-table-column prop="question" label="题目内容" min-width="300" show-overflow-tooltip>
          <template slot-scope="scope">
            <span>{{ scope.row.question }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="分值" width="80" align="center">
          <template slot-scope="scope">
            <el-tag type="warning" size="mini">{{ scope.row.score }}分</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="难度" width="80" align="center">
          <template slot-scope="scope">
            <el-tag :type="getLevelType(scope.row.level)" size="mini">{{ getLevelName(scope.row.level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="section" label="章节" width="140" align="center" show-overflow-tooltip />
        <el-table-column label="操作" width="180" align="center" class-name="small-padding fixed-width">
          <template slot-scope="scope">
            <el-button size="mini" type="text" icon="el-icon-view" @click="viewDetail(scope.row)">详情</el-button>
            <el-button size="mini" type="text" icon="el-icon-edit" @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button size="mini" type="text" icon="el-icon-delete" style="color: #F56C6C;" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        @current-change="handlePageChange"
        :current-page="currentPage"
        :page-size="pageSize"
        layout="total, prev, pager, next, jumper"
        :total="total"
        class="ruoyi-pagination">
      </el-pagination>
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="700px" :close-on-click-modal="false">
      <el-form :model="formData" :rules="formRules" ref="questionForm" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="科目" prop="subject">
              <el-select v-model="formData.subject" placeholder="选择科目" style="width: 100%;">
                <el-option v-for="s in subjects" :key="s" :label="s" :value="s" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="章节" prop="section">
              <el-input v-model="formData.section" placeholder="输入章节名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分值" prop="score">
              <el-input-number v-model="formData.score" :min="1" :max="100" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="难度" prop="level">
              <el-select v-model="formData.level" placeholder="选择难度" style="width: 100%;">
                <el-option label="简单" value="1" />
                <el-option label="较易" value="2" />
                <el-option label="中等" value="3" />
                <el-option label="较难" value="4" />
                <el-option label="困难" value="5" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="题目" prop="question">
          <el-input type="textarea" v-model="formData.question" :rows="4" placeholder="输入主观题题目内容" />
        </el-form-item>
        <el-form-item label="参考答案" prop="referenceAnswer">
          <el-input type="textarea" v-model="formData.referenceAnswer" :rows="5" placeholder="输入参考答案" />
        </el-form-item>
        <el-form-item label="解析" prop="analysis">
          <el-input type="textarea" v-model="formData.analysis" :rows="3" placeholder="输入题目解析（选填）" />
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">确定</el-button>
      </div>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog title="题目详情" :visible.sync="detailVisible" width="650px">
      <div class="detail-content" v-if="currentQuestion">
        <div class="detail-section">
          <div class="detail-label">科目</div>
          <div class="detail-value">{{ currentQuestion.subject }}</div>
        </div>
        <div class="detail-section">
          <div class="detail-label">题目</div>
          <div class="detail-value question-text">{{ currentQuestion.question }}</div>
        </div>
        <div class="detail-section">
          <div class="detail-label">参考答案</div>
          <div class="detail-value answer-text">{{ currentQuestion.referenceAnswer }}</div>
        </div>
        <div class="detail-section" v-if="currentQuestion.analysis">
          <div class="detail-label">解析</div>
          <div class="detail-value analysis-text">{{ currentQuestion.analysis }}</div>
        </div>
        <div class="detail-row">
          <div class="detail-item">
            <span class="label">分值：</span>
            <el-tag type="warning">{{ currentQuestion.score }}分</el-tag>
          </div>
          <div class="detail-item">
            <span class="label">难度：</span>
            <el-tag :type="getLevelType(currentQuestion.level)">{{ getLevelName(currentQuestion.level) }}</el-tag>
          </div>
          <div class="detail-item">
            <span class="label">章节：</span>
            <span>{{ currentQuestion.section || '未分类' }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'SubjectiveManage',
  data() {
    return {
      loading: false,
      submitting: false,
      tableData: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      searchForm: {
        subject: '',
        level: ''
      },
      subjects: ['计算机网络', '数据结构', 'Java程序设计', '高等数学', '数据库理论', '操作系统', '软件工程', '离散数学', 'C语言', 'Python程序设计', '大学英语', '大数据', '机器学习'],
      dialogVisible: false,
      dialogTitle: '添加主观题',
      formData: {
        questionId: null,
        subject: '',
        question: '',
        referenceAnswer: '',
        score: 10,
        level: '2',
        section: '',
        analysis: ''
      },
      formRules: {
        subject: [{ required: true, message: '请选择科目', trigger: 'change' }],
        question: [{ required: true, message: '请输入题目内容', trigger: 'blur' }],
        referenceAnswer: [{ required: true, message: '请输入参考答案', trigger: 'blur' }],
        score: [{ required: true, message: '请设置分值', trigger: 'change' }],
        level: [{ required: true, message: '请选择难度', trigger: 'change' }]
      },
      detailVisible: false,
      currentQuestion: null
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    loadData() {
      var self = this
      this.loading = true
      this.$axios.get('/api/subjective/list/' + this.currentPage + '/' + this.pageSize)
        .then(function(res) {
          self.loading = false
          if (res.data.code === 200) {
            var data = res.data.data
            self.tableData = data.records || []
            self.total = data.total || 0
          }
        })
        .catch(function() {
          self.loading = false
          self.$message.error('加载数据失败')
        })
    },
    resetSearch() {
      this.searchForm = { subject: '', level: '' }
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
    openAddDialog() {
      this.dialogTitle = '添加主观题'
      this.formData = {
        questionId: null,
        subject: '',
        question: '',
        referenceAnswer: '',
        score: 10,
        level: '2',
        section: '',
        analysis: ''
      }
      this.dialogVisible = true
      this.$nextTick(function() {
        if (this.$refs.questionForm) {
          this.$refs.questionForm.clearValidate()
        }
      })
    },
    openEditDialog(row) {
      this.dialogTitle = '编辑主观题'
      this.formData = {
        questionId: row.questionId,
        subject: row.subject,
        question: row.question,
        referenceAnswer: row.referenceAnswer,
        score: row.score,
        level: row.level,
        section: row.section,
        analysis: row.analysis
      }
      this.dialogVisible = true
    },
    submitForm() {
      var self = this
      this.$refs.questionForm.validate(function(valid) {
        if (valid) {
          self.submitting = true
          var url = self.formData.questionId ? '/api/subjective/update' : '/api/subjective/add'
          var method = self.formData.questionId ? 'put' : 'post'
          
          self.$axios({
            url: url,
            method: method,
            data: self.formData
          }).then(function(res) {
            self.submitting = false
            if (res.data.code === 200) {
              self.$message.success(self.formData.questionId ? '修改成功' : '添加成功')
              self.dialogVisible = false
              self.loadData()
            } else {
              self.$message.error(res.data.message || '操作失败')
            }
          }).catch(function() {
            self.submitting = false
            self.$message.error('操作失败')
          })
        }
      })
    },
    handleDelete(row) {
      var self = this
      this.$confirm('确定要删除这道题目吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(function() {
        self.$axios.delete('/api/subjective/delete/' + row.questionId)
          .then(function(res) {
            if (res.data.code === 200) {
              self.$message.success('删除成功')
              self.loadData()
            } else {
              self.$message.error(res.data.message || '删除失败')
            }
          })
      }).catch(function() {})
    },
    viewDetail(row) {
      this.currentQuestion = row
      this.detailVisible = true
    },
    getLevelName(level) {
      var levels = { '1': '简单', '2': '较易', '3': '中等', '4': '较难', '5': '困难' }
      return levels[level] || '中等'
    },
    getLevelType(level) {
      var types = { '1': 'success', '2': 'info', '3': 'warning', '4': 'danger', '5': 'danger' }
      return types[level] || ''
    }
  }
}
</script>

<style lang="less" scoped>
/* 详情对话框样式 */
.detail-content {
  padding: 10px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.detail-value {
  font-size: 15px;
  color: #303133;
  line-height: 1.8;
}

.question-text {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}

.answer-text {
  background: #f0f9eb;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #67C23A;
}

.analysis-text {
  background: #fdf6ec;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #E6A23C;
}

.detail-row {
  display: flex;
  gap: 30px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-item .label {
  color: #909399;
  font-size: 13px;
}
</style>
