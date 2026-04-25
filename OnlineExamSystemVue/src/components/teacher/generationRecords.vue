<template>
  <div class="ruoyi-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-icon">
        <i class="el-icon-document"></i>
      </div>
      <div class="header-text">
        <h2>生成记录管理</h2>
        <p>查看AI出题和智能组卷的历史记录</p>
      </div>
    </div>

    <!-- 标签切换 -->
    <el-tabs v-model="activeTab" type="card" class="record-tabs">
      <!-- AI出题记录 -->
      <el-tab-pane label="AI出题记录" name="ai">
        <div class="ruoyi-card table-card">
          <el-table :data="aiRecords.records" v-loading="aiLoading" class="ruoyi-table">
            <el-table-column prop="id" label="ID" width="80" align="center"/>
            <el-table-column prop="subject" label="科目" min-width="150" align="center"/>
            <el-table-column prop="questionType" label="题目类型" width="120" align="center">
              <template slot-scope="scope">
                <el-tag :type="getQuestionTypeTag(scope.row.questionType)" size="small">
                  {{ getQuestionTypeName(scope.row.questionType) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="questionCount" label="生成数量" width="100" align="center"/>
            <el-table-column prop="difficulty" label="难度" width="100" align="center"/>
            <el-table-column prop="savedCount" label="已保存" width="100" align="center">
              <template slot-scope="scope">
                <span :class="scope.row.savedCount > 0 ? 'text-success' : 'text-muted'">
                  {{ scope.row.savedCount }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="createTime" label="创建时间" width="180" align="center">
              <template slot-scope="scope">
                {{ formatDate(scope.row.createTime) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" align="center">
              <template slot-scope="scope">
                <el-button size="mini" type="text" icon="el-icon-view" @click="viewAiDetail(scope.row)">查看</el-button>
                <el-button size="mini" type="text" icon="el-icon-delete" style="color: #f56c6c" @click="deleteAiRecord(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            @current-change="handleAiPageChange"
            :current-page="aiRecords.current"
            :page-size="aiRecords.size"
            layout="total, prev, pager, next, jumper"
            :total="aiRecords.total"
            class="ruoyi-pagination">
          </el-pagination>
        </div>
      </el-tab-pane>

      <!-- 组卷记录 -->
      <el-tab-pane label="组卷记录" name="genetic">
        <div class="ruoyi-card table-card">
          <el-table :data="geneticRecords.records" v-loading="geneticLoading" class="ruoyi-table">
            <el-table-column prop="id" label="ID" width="80" align="center"/>
            <el-table-column prop="subjects" label="科目" min-width="150" align="center" show-overflow-tooltip/>
            <el-table-column prop="targetDifficulty" label="目标难度" width="100" align="center"/>
            <el-table-column label="题型配置" width="180" align="center">
              <template slot-scope="scope">
                <span>选{{ scope.row.multiCount }} / 填{{ scope.row.fillCount }} / 判{{ scope.row.judgeCount }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="totalScore" label="总分" width="80" align="center"/>
            <el-table-column prop="avgDifficulty" label="平均难度" width="100" align="center"/>
            <el-table-column prop="fitness" label="匹配度" width="100" align="center">
              <template slot-scope="scope">
                <span class="text-success">{{ scope.row.fitness }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="isCreatedExam" label="已创建考试" width="100" align="center">
              <template slot-scope="scope">
                <el-tag :type="scope.row.isCreatedExam ? 'success' : 'info'" size="small">
                  {{ scope.row.isCreatedExam ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createTime" label="创建时间" width="180" align="center">
              <template slot-scope="scope">
                {{ formatDate(scope.row.createTime) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" align="center">
              <template slot-scope="scope">
                <el-button size="mini" type="text" icon="el-icon-view" @click="viewGeneticDetail(scope.row)">查看</el-button>
                <el-button size="mini" type="text" icon="el-icon-delete" style="color: #f56c6c" @click="deleteGeneticRecord(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            @current-change="handleGeneticPageChange"
            :current-page="geneticRecords.current"
            :page-size="geneticRecords.size"
            layout="total, prev, pager, next, jumper"
            :total="geneticRecords.total"
            class="ruoyi-pagination">
          </el-pagination>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- AI出题详情对话框 -->
    <el-dialog title="AI出题详情" :visible.sync="aiDetailVisible" width="800px" append-to-body>
      <div v-if="aiDetailData" class="detail-content">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="科目">{{ aiDetailData.subject }}</el-descriptions-item>
          <el-descriptions-item label="题型">{{ getQuestionTypeName(aiDetailData.questionType) }}</el-descriptions-item>
          <el-descriptions-item label="难度">{{ aiDetailData.difficulty }}</el-descriptions-item>
          <el-descriptions-item label="生成数量">{{ aiDetailData.questionCount }}</el-descriptions-item>
          <el-descriptions-item label="已保存">{{ aiDetailData.savedCount }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(aiDetailData.createTime) }}</el-descriptions-item>
        </el-descriptions>
        <div class="questions-preview" v-if="aiDetailData.questionsJson">
          <h4>生成的题目</h4>
          <pre>{{ formatJson(aiDetailData.questionsJson) }}</pre>
        </div>
      </div>
    </el-dialog>

    <!-- 组卷详情对话框 -->
    <el-dialog title="组卷详情" :visible.sync="geneticDetailVisible" width="900px" append-to-body>
      <div v-if="geneticDetailData" class="detail-content">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="科目">{{ geneticDetailData.subjects }}</el-descriptions-item>
          <el-descriptions-item label="目标难度">{{ geneticDetailData.targetDifficulty }}</el-descriptions-item>
          <el-descriptions-item label="平均难度">{{ geneticDetailData.avgDifficulty }}</el-descriptions-item>
          <el-descriptions-item label="选择题">{{ geneticDetailData.multiCount }}道</el-descriptions-item>
          <el-descriptions-item label="填空题">{{ geneticDetailData.fillCount }}道</el-descriptions-item>
          <el-descriptions-item label="判断题">{{ geneticDetailData.judgeCount }}道</el-descriptions-item>
          <el-descriptions-item label="总分">{{ geneticDetailData.totalScore }}分</el-descriptions-item>
          <el-descriptions-item label="匹配度">{{ geneticDetailData.fitness }}%</el-descriptions-item>
          <el-descriptions-item label="组卷耗时">{{ geneticDetailData.generationTime }}ms</el-descriptions-item>
          <el-descriptions-item label="已创建考试">{{ geneticDetailData.isCreatedExam ? '是' : '否' }}</el-descriptions-item>
          <el-descriptions-item label="考试编号">{{ geneticDetailData.examCode || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(geneticDetailData.createTime) }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'GenerationRecords',
  data() {
    return {
      activeTab: 'ai',
      aiLoading: false,
      geneticLoading: false,
      aiRecords: { records: [], current: 1, size: 10, total: 0 },
      geneticRecords: { records: [], current: 1, size: 10, total: 0 },
      aiDetailVisible: false,
      geneticDetailVisible: false,
      aiDetailData: null,
      geneticDetailData: null
    }
  },
  created() {
    this.loadAiRecords()
    this.loadGeneticRecords()
  },
  methods: {
    async loadAiRecords() {
      this.aiLoading = true
      try {
        const res = await this.$axios.get(`/api/generation-records/ai/${this.aiRecords.current}/${this.aiRecords.size}`)
        if (res.data.code === 200) {
          this.aiRecords = res.data.data
        }
      } catch (e) {
        console.error('加载AI出题记录失败', e)
      } finally {
        this.aiLoading = false
      }
    },
    async loadGeneticRecords() {
      this.geneticLoading = true
      try {
        const res = await this.$axios.get(`/api/generation-records/genetic/${this.geneticRecords.current}/${this.geneticRecords.size}`)
        if (res.data.code === 200) {
          this.geneticRecords = res.data.data
        }
      } catch (e) {
        console.error('加载组卷记录失败', e)
      } finally {
        this.geneticLoading = false
      }
    },
    handleAiPageChange(page) {
      this.aiRecords.current = page
      this.loadAiRecords()
    },
    handleGeneticPageChange(page) {
      this.geneticRecords.current = page
      this.loadGeneticRecords()
    },
    async viewAiDetail(row) {
      try {
        const res = await this.$axios.get(`/api/generation-records/ai/detail/${row.id}`)
        if (res.data.code === 200) {
          this.aiDetailData = res.data.data
          this.aiDetailVisible = true
        }
      } catch (e) {
        this.$message.error('获取详情失败')
      }
    },
    async viewGeneticDetail(row) {
      try {
        const res = await this.$axios.get(`/api/generation-records/genetic/detail/${row.id}`)
        if (res.data.code === 200) {
          this.geneticDetailData = res.data.data
          this.geneticDetailVisible = true
        }
      } catch (e) {
        this.$message.error('获取详情失败')
      }
    },
    deleteAiRecord(row) {
      this.$confirm('确定删除该AI出题记录吗？', '提示', { type: 'warning' }).then(async () => {
        try {
          const res = await this.$axios.delete(`/api/generation-records/ai/${row.id}`)
          if (res.data.code === 200) {
            this.$message.success('删除成功')
            this.loadAiRecords()
          }
        } catch (e) {
          this.$message.error('删除失败')
        }
      }).catch(() => {})
    },
    deleteGeneticRecord(row) {
      this.$confirm('确定删除该组卷记录吗？', '提示', { type: 'warning' }).then(async () => {
        try {
          const res = await this.$axios.delete(`/api/generation-records/genetic/${row.id}`)
          if (res.data.code === 200) {
            this.$message.success('删除成功')
            this.loadGeneticRecords()
          }
        } catch (e) {
          this.$message.error('删除失败')
        }
      }).catch(() => {})
    },
    getQuestionTypeName(type) {
      const map = { 'multiple': '选择题', 'fill': '填空题', 'judge': '判断题', 'subjective': '主观题' }
      return map[type] || type
    },
    getQuestionTypeTag(type) {
      const map = { 'multiple': 'primary', 'fill': 'success', 'judge': 'warning', 'subjective': 'danger' }
      return map[type] || 'info'
    },
    formatDate(date) {
      if (!date) return '-'
      return new Date(date).toLocaleString('zh-CN')
    },
    formatJson(json) {
      try {
        return JSON.stringify(JSON.parse(json), null, 2)
      } catch (e) {
        return json
      }
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
}
.header-icon {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
}
.header-icon i { font-size: 32px; }
.header-text h2 { margin: 0 0 8px 0; font-size: 24px; font-weight: 600; }
.header-text p { margin: 0; opacity: 0.9; }
.record-tabs { margin-top: 20px; }
.text-success { color: #67c23a; font-weight: 600; }
.text-muted { color: #909399; }
.detail-content { padding: 10px 0; }
.questions-preview { margin-top: 20px; }
.questions-preview h4 { margin-bottom: 10px; color: #303133; }
.questions-preview pre {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  max-height: 400px;
  overflow: auto;
  font-size: 12px;
}
</style>
