<template>
  <div id="scoringSystem" class="page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h2 class="page-title">
          <i class="el-icon-document-checked"></i>
          阅卷评分系统
        </h2>
        <p class="page-desc">审阅学生主观题答案并进行评分</p>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <span class="stat-value">{{ pendingCount }}</span>
          <span class="stat-label">待批阅</span>
        </div>
      </div>
      <!-- 一键系统阅卷（当有过滤考试时显示）-->
      <el-button v-if="filterExam" type="warning" icon="el-icon-cpu"
        :loading="batchAutoGrading" @click="batchAutoGrade">
        一键系统阅卷
      </el-button>
    </div>

    <!-- 筛选区域 -->
    <div class="ruoyi-card search-card">
      <el-form :inline="true" class="search-form">
        <el-form-item label="考试">
          <el-select v-model="filterExam" placeholder="选择考试" clearable style="width: 200px;" @change="loadPendingAnswers">
            <el-option v-for="exam in examList" :key="exam.examCode" :label="exam.source" :value="exam.examCode" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="loadPendingAnswers">搜索</el-button>
          <el-button icon="el-icon-refresh" @click="filterExam = null; loadPendingAnswers()">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 待批阅列表 -->
    <div class="scoring-content">
      <div class="list-panel">
        <div class="panel-header">
          <h3>待批阅答案</h3>
          <el-badge :value="pendingCount" type="warning" />
        </div>
        
        <div class="answer-list" v-loading="loading">
          <div v-if="answerList.length === 0" class="empty-state">
            <i class="el-icon-document-delete"></i>
            <p>暂无待批阅的答案</p>
          </div>
          <div v-for="answer in answerList" :key="answer.answerId" class="answer-card" 
               :class="{ active: currentAnswer && currentAnswer.answerId === answer.answerId }"
               @click="selectAnswer(answer)">
            <div class="card-header">
              <span class="student-name">{{ answer.studentName || '学生' + answer.studentId }}</span>
              <el-tag size="mini" :type="answer.status === 0 ? 'warning' : 'success'">
                {{ answer.status === 0 ? '待评分' : '已评分' }}
              </el-tag>
            </div>
            <div class="card-body">
              <p class="question-preview">{{ truncateText(answer.question, 50) }}</p>
            </div>
            <div class="card-footer">
              <span class="subject-tag">{{ answer.subject }}</span>
              <span class="max-score">满分：{{ answer.maxScore }}分</span>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="total > pageSize">
          <el-pagination small layout="prev, pager, next" :total="total" :page-size="pageSize"
            :current-page="currentPage" @current-change="handlePageChange" />
        </div>
      </div>

      <!-- 评分面板 -->
      <div class="scoring-panel" v-if="currentAnswer">
        <div class="panel-header">
          <h3>评分详情</h3>
          <div class="header-actions">
            <el-button size="small" icon="el-icon-arrow-left" @click="prevAnswer" :disabled="currentIndex <= 0">上一题</el-button>
            <el-button size="small" icon="el-icon-arrow-right" @click="nextAnswer" :disabled="currentIndex >= answerList.length - 1">下一题</el-button>
          </div>
        </div>

        <div class="scoring-form">
          <!-- 学生信息 -->
          <div class="info-row">
            <div class="info-item">
              <label>学生：</label>
              <span>{{ currentAnswer.studentName || '学生' + currentAnswer.studentId }}</span>
            </div>
            <div class="info-item">
              <label>科目：</label>
              <span>{{ currentAnswer.subject }}</span>
            </div>
            <div class="info-item">
              <label>满分：</label>
              <el-tag type="warning">{{ currentAnswer.maxScore }}分</el-tag>
            </div>
          </div>

          <!-- 题目 -->
          <div class="section">
            <div class="section-title">
              <i class="el-icon-document"></i>
              题目内容
            </div>
            <div class="question-box">{{ currentAnswer.question }}</div>
          </div>

          <!-- 参考答案 -->
          <div class="section">
            <div class="section-title">
              <i class="el-icon-check"></i>
              参考答案
              <el-button type="text" size="small" @click="showReference = !showReference">
                {{ showReference ? '收起' : '展开' }}
              </el-button>
            </div>
            <div class="reference-box" v-show="showReference">{{ currentAnswer.referenceAnswer }}</div>
          </div>

          <!-- 学生答案 -->
          <div class="section">
            <div class="section-title">
              <i class="el-icon-edit-outline"></i>
              学生答案
            </div>
            <div class="student-answer-box">{{ currentAnswer.studentAnswer || '（学生未作答）' }}</div>
          </div>

          <!-- 评分区域 -->
          <div class="section scoring-section">
            <div class="section-title">
              <i class="el-icon-star-on"></i>
              评分
            </div>
            <div class="score-input">
              <el-slider v-model="scoreValue" :max="currentAnswer.maxScore" :min="0" show-input style="flex: 1;" />
            </div>
            <div class="quick-scores">
              <el-button size="mini" @click="scoreValue = 0">0分</el-button>
              <el-button size="mini" @click="scoreValue = Math.round(currentAnswer.maxScore * 0.3)">30%</el-button>
              <el-button size="mini" @click="scoreValue = Math.round(currentAnswer.maxScore * 0.5)">50%</el-button>
              <el-button size="mini" @click="scoreValue = Math.round(currentAnswer.maxScore * 0.7)">70%</el-button>
              <el-button size="mini" type="success" @click="scoreValue = currentAnswer.maxScore">满分</el-button>
            </div>
          </div>

          <!-- 评语 -->
          <div class="section">
            <div class="section-title">
              <i class="el-icon-chat-line-round"></i>
              评语（选填）
            </div>
            <el-input type="textarea" v-model="commentValue" :rows="3" placeholder="输入评语或批注..." />
            <div class="comment-templates">
              <span class="template-label">快捷评语：</span>
              <el-button size="mini" type="text" @click="commentValue = '回答正确，理解到位。'">回答正确</el-button>
              <el-button size="mini" type="text" @click="commentValue = '回答部分正确，但不够完整。'">部分正确</el-button>
              <el-button size="mini" type="text" @click="commentValue = '答案有误，请复习相关知识点。'">答案有误</el-button>
              <el-button size="mini" type="text" @click="commentValue = '回答较好，继续保持！'">回答较好</el-button>
            </div>
          </div>

          <!-- 提交按钮 -->
          <div class="submit-actions">
            <el-button type="primary" size="large" :loading="submitting" @click="submitScore" icon="el-icon-check">
              提交评分
            </el-button>
            <el-button size="large" @click="submitAndNext" :loading="submitting" icon="el-icon-right">
              提交并下一题
            </el-button>
            <el-button type="warning" size="large" :loading="autoGrading" @click="previewAutoGrade" icon="el-icon-cpu">
              系统阅卷
            </el-button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div class="scoring-panel empty" v-else>
        <div class="empty-content">
          <i class="el-icon-mouse"></i>
          <p>请从左侧选择一个待批阅的答案</p>
        </div>
      </div>
    </div>

    <!-- 系统阅卷预览对话框 -->
    <el-dialog title="🤖 系统自动阅卷结果" :visible.sync="autoGradeDialogVisible"
      width="520px" @close="autoGradeResult = null">
      <div v-if="autoGradeResult" class="auto-grade-result">
        <!-- 分数显示 -->
        <div class="score-display">
          <div class="score-circle">
            <span class="score-num">{{ autoGradeResult.score }}</span>
            <span class="score-max">/ {{ currentAnswer ? currentAnswer.maxScore : '' }}</span>
          </div>
          <div class="score-ratio-bar">
            <div class="ratio-fill" :style="{ width: (autoGradeResult.score / (currentAnswer ? currentAnswer.maxScore : 1) * 100) + '%',
              background: getRatioColor(autoGradeResult.score, currentAnswer ? currentAnswer.maxScore : 1) }"></div>
          </div>
        </div>

        <!-- 系统评语 -->
        <div class="auto-comment-box">
          <i class="el-icon-info"></i> {{ autoGradeResult.comment }}
        </div>

        <!-- 评分明细 -->
        <div class="detail-table" v-if="autoGradeResult.detail">
          <div class="detail-title">评分维度明细</div>
          <table>
            <tr><th>维度</th><th>得分率</th><th>说明</th></tr>
            <tr>
              <td>🔑 关键词覆盖</td>
              <td><span class="score-badge" :class="getBadgeClass(autoGradeResult.detail.keyword)">{{ (autoGradeResult.detail.keyword * 100).toFixed(0) }}%</span></td>
              <td class="desc">参考答案中的关键词在学生答案中的出现比例（权重 35%）</td>
            </tr>
            <tr>
              <td>📊 Bigram 相似度</td>
              <td><span class="score-badge" :class="getBadgeClass(autoGradeResult.detail.bigram)">{{ (autoGradeResult.detail.bigram * 100).toFixed(0) }}%</span></td>
              <td class="desc">字符级双字组 Dice 系数，衡量文本整体相似程度（权重 35%）</td>
            </tr>
            <tr>
              <td>📍 长度合理性</td>
              <td><span class="score-badge" :class="getBadgeClass(autoGradeResult.detail.length)">{{ (autoGradeResult.detail.length * 100).toFixed(0) }}%</span></td>
              <td class="desc">答案长度与参考答案的比例是否合理（权重 15%）</td>
            </tr>
            <tr>
              <td>🎯 核心短语</td>
              <td><span class="score-badge" :class="getBadgeClass(autoGradeResult.detail.phrase)">{{ (autoGradeResult.detail.phrase * 100).toFixed(0) }}%</span></td>
              <td class="desc">3～5字核心表述短语的命中率（权重 15%）</td>
            </tr>
          </table>
        </div>

        <el-alert type="info" :closable="false" style="margin-top:12px">
          <span slot="title">系统评分供参考，最终分数由教师确认。您可採用系统分数或手动修改后提交。</span>
        </el-alert>
      </div>
      <div slot="footer">
        <el-button @click="autoGradeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="applyAutoScore">
          采用系统分数 ({{ autoGradeResult ? autoGradeResult.score : '' }}分)
        </el-button>
        <el-button type="success" @click="applyAndSubmitAutoScore" :loading="submitting">
          采用并提交
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'ScoringSystem',
  data() {
    return {
      loading: false,
      submitting: false,
      examList: [],
      filterExam: null,
      answerList: [],
      total: 0,
      currentPage: 1,
      pageSize: 20,
      pendingCount: 0,
      currentAnswer: null,
      currentIndex: -1,
      scoreValue: 0,
      commentValue: '',
      showReference: true,
      // 系统阅卷
      autoGrading: false,
      batchAutoGrading: false,
      autoGradeDialogVisible: false,
      autoGradeResult: null
    }
  },
  mounted() {
    this.loadExamList()
    this.loadPendingAnswers()
  },
  methods: {
    loadExamList() {
      var self = this
      this.$axios.get('/api/exams/1/100')
        .then(function(res) {
          if (res.data.code === 200) {
            self.examList = res.data.data.records || []
          }
        })
    },
    loadPendingAnswers() {
      var self = this
      this.loading = true
      var url = '/api/scoring/pending?page=' + this.currentPage + '&size=' + this.pageSize
      if (this.filterExam) {
        url = '/api/scoring/pending/exam/' + this.filterExam + '?page=' + this.currentPage + '&size=' + this.pageSize
      }
      
      this.$axios.get(url)
        .then(function(res) {
          self.loading = false
          if (res.data.code === 200) {
            var data = res.data.data
            self.answerList = data.records || []
            self.total = data.total || 0
            self.pendingCount = self.total
          }
        })
        .catch(function() {
          self.loading = false
        })
    },
    handlePageChange(page) {
      this.currentPage = page
      this.loadPendingAnswers()
    },
    selectAnswer(answer) {
      this.currentAnswer = answer
      this.currentIndex = this.answerList.indexOf(answer)
      this.scoreValue = answer.teacherScore || 0
      this.commentValue = answer.teacherComment || ''
    },
    prevAnswer() {
      if (this.currentIndex > 0) {
        this.currentIndex--
        this.selectAnswer(this.answerList[this.currentIndex])
      }
    },
    nextAnswer() {
      if (this.currentIndex < this.answerList.length - 1) {
        this.currentIndex++
        this.selectAnswer(this.answerList[this.currentIndex])
      }
    },
    submitScore() {
      var self = this
      if (!this.currentAnswer) return
      
      this.submitting = true
      this.$axios.post('/api/scoring/score', {
        answerId: this.currentAnswer.answerId,
        teacherScore: this.scoreValue,
        teacherComment: this.commentValue,
        scoredBy: parseInt(this.$cookies.get('cid'))
      }).then(function(res) {
        self.submitting = false
        if (res.data.code === 200) {
          const msg = res.data.message || '评分成功'
          if (msg.includes('最终成绩已更新')) {
            self.$notify({
              title: '成绩已更新',
              message: msg,
              type: 'success',
              duration: 4000
            })
          } else {
            self.$message.success('评分成功')
          }
          self.currentAnswer.status = 1
          self.currentAnswer.teacherScore = self.scoreValue
          self.loadPendingAnswers()
        } else {
          self.$message.error(res.data.message || '评分失败')
        }
      }).catch(function() {
        self.submitting = false
        self.$message.error('评分失败')
      })
    },
    submitAndNext() {
      var self = this
      this.submitScore()
      setTimeout(function() {
        if (self.currentIndex < self.answerList.length - 1) {
          self.nextAnswer()
        }
      }, 500)
    },
    truncateText(text, length) {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    },
    // 系统阅卷 - 预览当前题
    previewAutoGrade() {
      if (!this.currentAnswer) return
      var self = this
      this.autoGrading = true
      this.$axios.post('/api/scoring/auto/compute', {
        studentAnswer:   this.currentAnswer.studentAnswer || '',
        referenceAnswer: this.currentAnswer.referenceAnswer || '',
        maxScore:        this.currentAnswer.maxScore || 10
      }).then(function(res) {
        self.autoGrading = false
        if (res.data.code === 200) {
          self.autoGradeResult = res.data.data
          self.autoGradeDialogVisible = true
        } else {
          self.$message.error('系统评分失败')
        }
      }).catch(function() {
        self.autoGrading = false
        self.$message.error('系统评分请求失败')
      })
    },
    // 采用系统分数（仅填入滑块，不提交）
    applyAutoScore() {
      if (this.autoGradeResult) {
        this.scoreValue = this.autoGradeResult.score
        this.commentValue = this.autoGradeResult.comment
        this.autoGradeDialogVisible = false
        this.$message.success('已采用系统分数 ' + this.scoreValue + ' 分，请点击「提交评分」保存')
      }
    },
    // 采用并直接提交
    applyAndSubmitAutoScore() {
      if (!this.autoGradeResult) return
      this.scoreValue = this.autoGradeResult.score
      this.commentValue = this.autoGradeResult.comment
      this.autoGradeDialogVisible = false
      this.submitScore()
    },
    // 一键批量系统阅卷（当前筛选的考试）
    batchAutoGrade() {
      if (!this.filterExam) return
      var self = this
      this.$confirm(
        '将对【' + this.filterExam + '】考试的所有待批阅答案进行系统自动阅卷，老师可在之后对单题修改评分。确认进行？',
        '一键系统阅卷',
        { confirmButtonText: '确认执行', cancelButtonText: '取消', type: 'warning' }
      ).then(function() {
        self.batchAutoGrading = true
        self.$axios.post('/api/scoring/auto/exam/' + self.filterExam)
          .then(function(res) {
            self.batchAutoGrading = false
            if (res.data.code === 200) {
              var d = res.data.data
              self.$notify({
                title: '系统阅卷完成',
                message: '共处理 ' + d.success + ' 题，已更新 ' + d.updated + ' 位学生成绩',
                type: 'success',
                duration: 5000
              })
              self.loadPendingAnswers()
            } else {
              self.$message.error(res.data.message || '批量阅卷失败')
            }
          }).catch(function() {
            self.batchAutoGrading = false
            self.$message.error('批量阅卷请求失败')
          })
      }).catch(function() {})
    },
    // 辅助方法：根据得分率返回标记样式
    getBadgeClass(ratio) {
      if (ratio >= 0.8) return 'badge-green'
      if (ratio >= 0.6) return 'badge-blue'
      if (ratio >= 0.4) return 'badge-orange'
      return 'badge-red'
    },
    // 根据分数返回进度条颜色
    getRatioColor(score, maxScore) {
      var ratio = maxScore > 0 ? score / maxScore : 0
      if (ratio >= 0.8) return 'linear-gradient(90deg, #67C23A, #95d475)'
      if (ratio >= 0.6) return 'linear-gradient(90deg, #409EFF, #79bbff)'
      if (ratio >= 0.4) return 'linear-gradient(90deg, #E6A23C, #f0c070)'
      return 'linear-gradient(90deg, #F56C6C, #f89898)'
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 24px 30px;
  color: #fff;
  margin-bottom: 20px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-desc {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.header-stats {
  text-align: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.filter-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.scoring-content {
  display: flex;
  gap: 20px;
}

.list-panel {
  width: 360px;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  max-height: calc(100vh - 280px);
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.answer-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 12px;
}

.answer-card {
  background: #f8fafc;
  border-radius: 10px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.answer-card:hover {
  background: #f0f5ff;
  border-color: #409EFF;
}

.answer-card.active {
  background: #e6f7ff;
  border-color: #409EFF;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.student-name {
  font-weight: 600;
  color: #303133;
}

.question-preview {
  font-size: 13px;
  color: #606266;
  margin: 0;
  line-height: 1.6;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  font-size: 12px;
}

.subject-tag {
  background: #ecf5ff;
  color: #409EFF;
  padding: 2px 8px;
  border-radius: 4px;
}

.max-score {
  color: #E6A23C;
}

.scoring-panel {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  max-height: calc(100vh - 280px);
  overflow-y: auto;
}

.scoring-panel.empty {
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-content {
  text-align: center;
  color: #909399;
}

.empty-content i {
  font-size: 64px;
  margin-bottom: 16px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.info-row {
  display: flex;
  gap: 30px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 10px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-item label {
  color: #909399;
  font-size: 13px;
}

.section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.question-box {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 10px;
  line-height: 1.8;
  border-left: 4px solid #409EFF;
}

.reference-box {
  background: #f0f9eb;
  padding: 16px;
  border-radius: 10px;
  line-height: 1.8;
  border-left: 4px solid #67C23A;
  color: #67C23A;
}

.student-answer-box {
  background: #fdf6ec;
  padding: 16px;
  border-radius: 10px;
  line-height: 1.8;
  border-left: 4px solid #E6A23C;
  min-height: 80px;
}

.scoring-section {
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  padding: 20px;
  border-radius: 12px;
}

.score-input {
  margin-bottom: 12px;
}

.quick-scores {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.comment-templates {
  margin-top: 12px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;
}

.template-label {
  font-size: 12px;
  color: #909399;
}

.submit-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

/* 系统阅卷对话框 */
.auto-grade-result { padding: 4px 0; }

.score-display {
  text-align: center;
  margin-bottom: 20px;
}
.score-circle {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  font-weight: 700;
  margin-bottom: 12px;
}
.score-num { font-size: 52px; color: #409EFF; line-height: 1; }
.score-max { font-size: 20px; color: #909399; }

.score-ratio-bar {
  height: 10px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
  width: 80%;
  margin: 0 auto;
}
.ratio-fill { height: 100%; border-radius: 10px; transition: width 0.6s; }

.auto-comment-box {
  background: #f0f9eb;
  border-left: 4px solid #67C23A;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  color: #606266;
  line-height: 1.7;
  margin-bottom: 16px;
}

.detail-table {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}
.detail-title {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  padding: 8px 12px;
  background: #f5f7fa;
  border-bottom: 1px solid #eee;
}
.detail-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.detail-table th {
  background: #fafafa;
  color: #909399;
  padding: 8px 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
}
.detail-table td {
  padding: 8px 10px;
  border-bottom: 1px solid #f5f5f5;
  color: #303133;
}
.detail-table td.desc { color: #909399; font-size: 11px; }

.score-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 12px;
}
.badge-green  { background: #f0f9eb; color: #67C23A; }
.badge-blue   { background: #ecf5ff; color: #409EFF; }
.badge-orange { background: #fdf6ec; color: #E6A23C; }
.badge-red    { background: #fef0f0; color: #F56C6C; }
</style>
