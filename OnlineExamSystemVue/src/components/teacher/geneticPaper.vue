<template>
  <div class="genetic-paper-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-icon">
        <i class="el-icon-cpu"></i>
      </div>
      <div class="header-text">
        <h2>智能组卷</h2>
        <p>基于遗传算法自动生成满足约束条件的最优试卷</p>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 左侧配置面板 -->
      <el-col :span="10">
        <el-card class="config-card">
          <div slot="header" class="card-header">
            <i class="el-icon-setting"></i>
            <span>组卷配置</span>
          </div>

          <el-form :model="config" label-width="100px" class="config-form">
            <!-- 基本配置 -->
            <div class="form-section">
              <div class="section-title">
                <i class="el-icon-document"></i>
                <span>基本配置</span>
              </div>

              <el-form-item label="选择科目">
                <el-select v-model="config.subjects" multiple placeholder="请选择科目" style="width: 100%;">
                  <el-option v-for="subject in subjects" :key="subject" :label="subject" :value="subject"/>
                </el-select>
              </el-form-item>

              <el-form-item label="目标难度">
                <el-slider v-model="config.targetDifficulty" :min="1" :max="5" :step="0.1"
                           :marks="difficultyMarks" show-stops/>
              </el-form-item>

              <el-form-item label="难度容差" style="margin-top: 40px;">
                <el-input-number v-model="config.difficultyTolerance" :min="0.1" :max="2" :step="0.1" :precision="1"/>
              </el-form-item>
            </div>

            <!-- 题型配置 -->
            <div class="form-section">
              <div class="section-title">
                <i class="el-icon-tickets"></i>
                <span>题型配置</span>
              </div>

              <div style="margin-left: -70px;">
                <el-row :gutter="24" style="margin-bottom: 28px;">
                  <el-col :span="12">
                    <el-form-item label="选择题">
                      <el-input-number v-model="config.multiCount" :min="0" :max="50"/>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="每题分值">
                      <el-input-number v-model="config.multiScore" :min="1" :max="20"/>
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="24" style="margin-bottom: 28px;">
                  <el-col :span="12">
                    <el-form-item label="填空题">
                      <el-input-number v-model="config.fillCount" :min="0" :max="30"/>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="每题分值">
                      <el-input-number v-model="config.fillScore" :min="1" :max="20"/>
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="24" style="margin-bottom: 28px;">
                  <el-col :span="12">
                    <el-form-item label="判断题">
                      <el-input-number v-model="config.judgeCount" :min="0" :max="30"/>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="每题分值">
                      <el-input-number v-model="config.judgeScore" :min="1" :max="20"/>
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="24" style="margin-bottom: 28px;">
                  <el-col :span="12">
                    <el-form-item label="主观题">
                      <el-input-number v-model="config.subjectiveCount" :min="0" :max="20"/>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="每题分值">
                      <el-input-number v-model="config.subjectiveScore" :min="1" :max="50"/>
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>

              <div class="total-score">
                预计总分: <span class="score-value">{{ expectedTotalScore }}</span> 分
              </div>
            </div>

            <!-- 高级配置 -->
            <el-collapse v-model="activeCollapse" class="advanced-collapse">
              <el-collapse-item name="advanced" title="高级配置">
                <el-form-item label="种群大小" style="margin-bottom: 24px;">
                  <el-input-number v-model="config.populationSize" :min="20" :max="200"/>
                  <span class="form-tip">种群越大，搜索空间越广</span>
                </el-form-item>

                <el-form-item label="迭代次数" style="margin-bottom: 24px;">
                  <el-input-number v-model="config.maxGenerations" :min="50" :max="500"/>
                  <span class="form-tip">迭代次数越多，结果越优</span>
                </el-form-item>

                <el-form-item label="交叉概率" style="margin-bottom: 24px;">
                  <el-slider v-model="config.crossoverRate" :min="0.5" :max="1" :step="0.05" show-input/>
                </el-form-item>

                <el-form-item label="变异概率" style="margin-bottom: 24px;">
                  <el-slider v-model="config.mutationRate" :min="0.01" :max="0.3" :step="0.01" show-input/>
                </el-form-item>
              </el-collapse-item>
            </el-collapse>

            <!-- 操作按钮 -->
            <div class="form-actions">
              <el-button type="primary" @click="generatePaper" :loading="generating" size="large" icon="el-icon-magic-stick">
                {{ generating ? '正在进化...' : '智能组卷' }}
              </el-button>
              <el-button @click="resetConfig" size="large" icon="el-icon-refresh">重置</el-button>
            </div>
          </el-form>
        </el-card>

        <!-- 题库统计 -->
        <el-card class="stats-card" v-if="questionStats">
          <div slot="header" class="card-header">
            <i class="el-icon-data-analysis"></i>
            <span>题库统计</span>
          </div>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ questionStats.totalQuestions }}</div>
              <div class="stat-label">总题目数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ questionStats.multiQuestionCount }}</div>
              <div class="stat-label">选择题</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ questionStats.fillQuestionCount }}</div>
              <div class="stat-label">填空题</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ questionStats.judgeQuestionCount }}</div>
              <div class="stat-label">判断题</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ questionStats.subjectiveQuestionCount || 0 }}</div>
              <div class="stat-label">主观题</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧结果面板 -->
      <el-col :span="14">
        <!-- 组卷结果 -->
        <el-card class="result-card" v-if="paperResult">
          <div slot="header" class="card-header">
            <div>
              <i class="el-icon-document-checked"></i>
              <span>组卷结果</span>
            </div>
            <div class="header-actions">
              <el-button type="primary" size="small" @click="showCreateExamDialog" icon="el-icon-plus">创建考试</el-button>
              <el-button type="success" size="small" @click="exportPaper" icon="el-icon-download">导出试卷</el-button>
            </div>
          </div>

          <!-- 统计信息 -->
          <div class="result-stats" v-if="paperResult.stats">
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="result-stat-item">
                  <div class="stat-icon success"><i class="el-icon-s-data"></i></div>
                  <div class="stat-content">
                    <div class="stat-value">{{ paperResult.stats.totalScore }}</div>
                    <div class="stat-label">总分</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="result-stat-item">
                  <div class="stat-icon primary"><i class="el-icon-tickets"></i></div>
                  <div class="stat-content">
                    <div class="stat-value">{{ paperResult.stats.totalQuestions }}</div>
                    <div class="stat-label">题目数</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="result-stat-item">
                  <div class="stat-icon warning"><i class="el-icon-star-off"></i></div>
                  <div class="stat-content">
                    <div class="stat-value">{{ paperResult.stats.averageDifficulty }}</div>
                    <div class="stat-label">平均难度</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="result-stat-item">
                  <div class="stat-icon danger"><i class="el-icon-aim"></i></div>
                  <div class="stat-content">
                    <div class="stat-value">{{ paperResult.stats.fitness }}%</div>
                    <div class="stat-label">匹配度</div>
                  </div>
                </div>
              </el-col>
            </el-row>

            <div class="generation-info">
              <i class="el-icon-time"></i>
              组卷耗时: {{ paperResult.stats.generationTime }}ms
            </div>

            <!-- 相似度展示条 -->
            <div v-if="similarityResult || formalExamResult" class="similarity-bar" :class="'sim-' + similarityLevel">
              <i :class="similarityLevelIcon" style="margin-right:6px;"></i>
              <span>相似度检测：{{ combinedMessage }}</span>
              <el-button
                type="text"
                size="mini"
                @click="similarityDialogVisible = true"
                style="margin-left:10px;">
                查看详情
              </el-button>
              <el-button
                type="text"
                size="mini"
                @click="checkAllSimilarity"
                :loading="checkingSimilarity"
                style="margin-left:4px;">刷新
              </el-button>
            </div>
            <div v-else-if="checkingsilimilarity === false" class="similarity-checking">
              <i class="el-icon-loading"></i> 相似度检测中...
            </div>
          </div>

          <!-- 难度分布图表 -->
          <div class="charts-container" v-if="paperResult.stats">
            <el-row :gutter="20">
              <el-col :span="12">
                <div class="chart-title">难度分布</div>
                <div ref="difficultyChart" class="chart-box"></div>
              </el-col>
              <el-col :span="12">
                <div class="chart-title">题型分布</div>
                <div ref="typeChart" class="chart-box"></div>
              </el-col>
            </el-row>
          </div>

          <!-- 题目列表 -->
          <el-tabs v-model="activeTab" class="question-tabs">
            <el-tab-pane :label="'选择题 (' + (paperResult.multiQuestions ? paperResult.multiQuestions.length : 0) + ')'" name="multi">
              <div class="question-list">
                <div v-for="(q, index) in paperResult.multiQuestions" :key="'m' + index" class="question-item">
                  <div class="question-header">
                    <span class="question-number">{{ index + 1 }}.</span>
                    <span class="question-level" :class="'level-' + q.level">难度{{ q.level }}</span>
                    <span class="question-score">{{ q.score }}分</span>
                  </div>
                  <div class="question-content">{{ q.question }}</div>
                  <div class="question-options">
                    <div class="option-item" :class="{correct: q.rightAnswer === 'A'}">A. {{ q.answerA }}</div>
                    <div class="option-item" :class="{correct: q.rightAnswer === 'B'}">B. {{ q.answerB }}</div>
                    <div class="option-item" :class="{correct: q.rightAnswer === 'C'}">C. {{ q.answerC }}</div>
                    <div class="option-item" :class="{correct: q.rightAnswer === 'D'}">D. {{ q.answerD }}</div>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane :label="'填空题 (' + (paperResult.fillQuestions ? paperResult.fillQuestions.length : 0) + ')'" name="fill">
              <div class="question-list">
                <div v-for="(q, index) in paperResult.fillQuestions" :key="'f' + index" class="question-item">
                  <div class="question-header">
                    <span class="question-number">{{ index + 1 }}.</span>
                    <span class="question-level" :class="'level-' + q.level">难度{{ q.level }}</span>
                    <span class="question-score">{{ q.score }}分</span>
                  </div>
                  <div class="question-content">{{ q.question }}</div>
                  <div class="question-answer">
                    <span class="answer-label">答案:</span>
                    <span class="answer-value">{{ q.answer }}</span>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane :label="'判断题 (' + (paperResult.judgeQuestions ? paperResult.judgeQuestions.length : 0) + ')'" name="judge">
              <div class="question-list">
                <div v-for="(q, index) in paperResult.judgeQuestions" :key="'j' + index" class="question-item">
                  <div class="question-header">
                    <span class="question-number">{{ index + 1 }}.</span>
                    <span class="question-level" :class="'level-' + q.level">难度{{ q.level }}</span>
                    <span class="question-score">{{ q.score }}分</span>
                  </div>
                  <div class="question-content">{{ q.question }}</div>
                  <div class="question-answer">
                    <span class="answer-label">答案:</span>
                    <el-tag :type="q.answer === 'T' ? 'success' : 'danger'" size="small">
                      {{ q.answer === 'T' ? '正确' : '错误' }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane :label="'主观题 (' + (paperResult.subjectiveQuestions ? paperResult.subjectiveQuestions.length : 0) + ')'" name="subjective">
              <div class="question-list">
                <div v-for="(q, index) in paperResult.subjectiveQuestions" :key="'s' + index" class="question-item">
                  <div class="question-header">
                    <span class="question-number">{{ index + 1 }}.</span>
                    <span class="question-level" :class="'level-' + q.level">难度{{ q.level }}</span>
                    <span class="question-score">{{ q.score }}分</span>
                  </div>
                  <div class="question-content">{{ q.question }}</div>
                  <div class="question-answer">
                    <span class="answer-label">参考答案:</span>
                    <span class="answer-value">{{ q.referenceAnswer }}</span>
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>

        <!-- 空状态 -->
        <el-card class="empty-card" v-else>
          <div class="empty-state">
            <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPGcgZmlsbD0ibm9uZSI+CiAgICA8cmVjdCB3aWR0aD0iMTYwIiBoZWlnaHQ9IjEyMCIgeD0iMjAiIHk9IjQwIiByeD0iOCIgZmlsbD0iI2YwZjJmNSIgc3Ryb2tlPSIjZTRlN2VkIiBzdHJva2Utd2lkdGg9IjIiLz4KICAgIDxjaXJjbGUgY3g9IjEwMCIgY3k9IjEwMCIgcj0iMzAiIGZpbGw9IiNlMGU2ZWQiLz4KICAgIDx0ZXh0IHg9IjEwMCIgeT0iMTA1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjYThhZGI1IiBmb250LXNpemU9IjI0Ij7wn6eRPC90ZXh0PgogICAgPGxpbmUgeDE9IjQwIiB5MT0iNzAiIHgyPSIxMjAiIHkyPSI3MCIgc3Ryb2tlPSIjZTRlN2VkIiBzdHJva2Utd2lkdGg9IjIiLz4KICAgIDxsaW5lIHgxPSI0MCIgeTE9IjkwIiB4Mj0iMTAwIiB5Mj0iOTAiIHN0cm9rZT0iI2U0ZTdlZCIgc3Ryb2tlLXdpZHRoPSIyIi8+CiAgPC9nPgo8L3N2Zz4=" alt="Empty"/>
            <h3>配置参数后点击"智能组卷"</h3>
            <p>遗传算法将自动优化题目组合，生成满足约束条件的最优试卷</p>
            <div class="algorithm-intro">
              <div class="intro-item">
                <i class="el-icon-sort"></i>
                <span>选择算子</span>
              </div>
              <div class="intro-item">
                <i class="el-icon-connection"></i>
                <span>交叉算子</span>
              </div>
              <div class="intro-item">
                <i class="el-icon-refresh-right"></i>
                <span>变异算子</span>
              </div>
              <div class="intro-item">
                <i class="el-icon-trophy"></i>
                <span>精英保留</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 相似度警告弹窗 -->
    <el-dialog
      title="试卷相似度检测报告"
      :visible.sync="similarityDialogVisible"
      width="680px"
      :close-on-click-modal="false"
      :append-to-body="true"
      :modal-append-to-body="true">
      <div v-if="formalExamResult">
        <!-- 相似度总览 -->
        <div class="similarity-overview" :class="similarityLevelClass">
          <div class="similarity-icon"><i :class="similarityLevelIcon"></i></div>
          <div class="similarity-info">
            <div class="similarity-value">{{ combinedMaxSimilarity }}%</div>
            <div class="similarity-label">与正式考试试卷相似度</div>
          </div>
          <div class="similarity-badge">
            <el-tag :type="similarityTagType" size="large" effect="dark">{{ similarityLevelText }}</el-tag>
          </div>
        </div>

        <!-- 相似度进度条 -->
        <div class="similarity-progress">
          <div class="progress-labels">
            <span>安全区域 (≤ 30%)</span>
            <span>警截区域 (30-50%)</span>
            <span>危险区域 (> 50%)</span>
          </div>
          <el-progress
            :percentage="Math.min(combinedMaxSimilarity, 100)"
            :color="similarityProgressColor"
            :stroke-width="16"
            :show-text="false"/>
          <div class="progress-pointer" :style="{ left: Math.min(combinedMaxSimilarity, 100) + '%' }">
            {{ combinedMaxSimilarity }}%
          </div>
        </div>

        <!-- 标记线 -->
        <div class="threshold-line">
          <div class="threshold safe">30%</div>
          <div class="threshold danger">50%</div>
        </div>

        <!-- 正式考试试卷对比详情 -->
        <div v-if="formalExamResult.details && formalExamResult.details.length > 0" class="similarity-details">
          <div class="detail-title">
            <i class="el-icon-s-check"></i>
            对比正式考试试卷（共 {{ formalExamResult.totalCompared }} 张）
          </div>
          <el-table :data="formalExamResult.details" size="small" border stripe>
            <el-table-column prop="examName" label="考试名称" min-width="140"/>
            <el-table-column prop="totalQuestions" label="试卷题数" width="90" align="center"/>
            <el-table-column prop="commonCount" label="重干题数" width="90" align="center">
              <template slot-scope="scope">
                <el-tag type="danger" size="mini" v-if="scope.row.commonCount > 0">{{ scope.row.commonCount }}题</el-tag>
                <span v-else class="text-success">0题</span>
              </template>
            </el-table-column>
            <el-table-column prop="similarity" label="Jaccard 相似度" width="150" align="center">
              <template slot-scope="scope">
                <el-progress
                  :percentage="scope.row.similarity"
                  :color="scope.row.similarity > 50 ? '#f56c6c' : scope.row.similarity > 30 ? '#e6a23c' : '#67c23a'"
                  :stroke-width="8"/>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else class="no-history">
          <i class="el-icon-info"></i>
          {{ formalExamResult.message }}
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="similarityDialogVisible = false">{{ combinedWarning ? '忽略警告，保留试卷' : '确 定' }}</el-button>
        <el-button
          type="danger"
          v-if="combinedWarning"
          @click="regeneratePaper"
          :loading="generating"
          icon="el-icon-refresh">
          重新组卷
        </el-button>
      </span>
    </el-dialog>

    <!-- 创建考试对话框 -->
    <el-dialog
      title="创建考试"
      :visible.sync="examDialogVisible"
      width="600px"
      :close-on-click-modal="false"
      :append-to-body="true"
      :modal-append-to-body="true">
      <el-form :model="examForm" label-width="100px" class="exam-form">
        <el-form-item label="试卷名称" required>
          <el-input v-model="examForm.source" placeholder="请输入试卷名称"></el-input>
        </el-form-item>
        <el-form-item label="考试类型" required>
          <el-select v-model="examForm.type" placeholder="请选择考试类型" style="width: 100%">
            <el-option label="正式考试" value="正式考试"></el-option>
            <el-option label="练习测验" value="练习测验"></el-option>
            <el-option label="模拟考试" value="模拟考试"></el-option>
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="考试日期" required>
              <el-date-picker v-model="examForm.examDate" type="date" placeholder="选择日期"
                value-format="yyyy-MM-dd" style="width: 100%"></el-date-picker>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="考试时长" required>
              <el-input-number v-model="examForm.totalTime" :min="30" :max="300" style="width: 100%"></el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所属学院">
              <el-input v-model="examForm.institute" placeholder="请输入学院"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属专业">
              <el-input v-model="examForm.major" placeholder="请输入专业"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="年级">
              <el-input v-model="examForm.grade" placeholder="请输入年级"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学期">
              <el-input v-model="examForm.term" placeholder="请输入学期"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="考试说明">
          <el-input type="textarea" v-model="examForm.description" :rows="2" placeholder="请输入考试说明"></el-input>
        </el-form-item>
        <el-form-item label="考生提示">
          <el-input type="textarea" v-model="examForm.tips" :rows="2" placeholder="请输入考生提示"></el-input>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开放时间">
              <el-time-picker v-model="examForm.examStartTime" placeholder="考试开始时间"
                format="HH:mm" value-format="HH:mm" style="width:100%"></el-time-picker>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="截止时间">
              <el-time-picker v-model="examForm.examEndTime" placeholder="考试截止时间"
                format="HH:mm" value-format="HH:mm" style="width:100%"></el-time-picker>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="examDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="createExam" :loading="creatingExam">创建考试</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'GeneticPaper',
  data() {
    return {
      generating: false,
      subjects: [],
      questionStats: null,
      paperResult: null,
      activeTab: 'multi',
      activeCollapse: [],

      config: {
        subjects: [],
        targetDifficulty: 3,
        difficultyTolerance: 0.5,
        multiCount: 10,
        fillCount: 4,
        judgeCount: 10,
        subjectiveCount: 1,
        multiScore: 2,
        fillScore: 5,
        judgeScore: 5,
        subjectiveScore: 10,
        populationSize: 50,
        maxGenerations: 100,
        crossoverRate: 0.8,
        mutationRate: 0.1
      },

      difficultyMarks: {
        1: '简单',
        2: '较易',
        3: '中等',
        4: '较难',
        5: '困难'
      },

      // 创建考试相关
      examDialogVisible: false,
      creatingExam: false,
      examForm: {
        source: '',
        description: '',
        examDate: '',
        totalTime: 120,
        grade: '',
        term: '',
        major: '',
        institute: '',
        type: '',
        tips: '请认真答题，考试期间禁止作弊。',
        examStartTime: '00:00',
        examEndTime: '23:59'
      },

      // 相似度检测相关
      similarityDialogVisible: false,
      formalExamResult: null,
      checkingSimilarity: false
    }
  },
  computed: {
    expectedTotalScore() {
      return this.config.multiCount * this.config.multiScore +
             this.config.fillCount * this.config.fillScore +
             this.config.judgeCount * this.config.judgeScore +
             this.config.subjectiveCount * this.config.subjectiveScore
    },
    similarityLevel() {
      if (!this.formalExamResult) return 'unknown'
      const v = this.formalExamResult.maxSimilarity || 0
      if (v <= 30) return 'safe'
      if (v <= 50) return 'warn'
      return 'danger'
    },
    similarityLevelText() {
      const map = { safe: '多样性良好', warn: '较高相似', danger: '警告！相似度过高', unknown: '-' }
      return map[this.similarityLevel]
    },
    similarityLevelClass() {
      return 'sim-overview-' + this.similarityLevel
    },
    similarityLevelIcon() {
      const map = { safe: 'el-icon-circle-check', warn: 'el-icon-warning', danger: 'el-icon-warning-outline', unknown: 'el-icon-info' }
      return map[this.similarityLevel]
    },
    similarityTagType() {
      const map = { safe: 'success', warn: 'warning', danger: 'danger', unknown: 'info' }
      return map[this.similarityLevel]
    },
    similarityProgressColor() {
      const v = this.formalExamResult ? (this.formalExamResult.maxSimilarity || 0) : 0
      if (v <= 30) return '#67c23a'
      if (v <= 50) return '#e6a23c'
      return '#f56c6c'
    },
    combinedMaxSimilarity() {
      return this.formalExamResult ? (this.formalExamResult.maxSimilarity || 0) : 0
    },
    combinedWarning() {
      return this.formalExamResult && this.formalExamResult.warning
    },
    combinedMessage() {
      if (!this.formalExamResult) return '-'
      return this.formalExamResult.message || '-'
    }
  },
  created() {
    this.loadSubjects()
    this.loadQuestionStats()
  },
  methods: {
    async loadSubjects() {
      try {
        const res = await this.$axios.get('/api/genetic/subjects')
        if (res.data.code === 200) {
          this.subjects = res.data.data || []
        }
      } catch (error) {
        console.error('加载科目失败', error)
      }
    },

    async loadQuestionStats() {
      try {
        const res = await this.$axios.get('/api/genetic/stats')
        if (res.data.code === 200) {
          this.questionStats = res.data.data
        }
      } catch (error) {
        console.error('加载统计失败', error)
      }
    },

    async generatePaper() {
      if (this.config.multiCount + this.config.fillCount + this.config.judgeCount + this.config.subjectiveCount === 0) {
        this.$message.warning('请至少设置一种题型的数量')
        return
      }
    
      this.generating = true
      this.formalExamResult = null
    
      // 添加学生 ID
      const studentId = this.$cookies.get("cid")
      if (studentId) {
        this.config.studentId = parseInt(studentId)
      }
    
      try {
        const res = await this.$axios.post('/api/genetic/generate', this.config)
    
        if (res.data.code === 200) {
          this.paperResult = res.data.data
          this.$message.success('智能组卷完成！匹配度: ' + this.paperResult.stats.fitness + '%')
    
          this.$nextTick(() => {
            this.renderCharts()
          })
    
          // 并行运行两种相似度检测（提升效率）
          await this.checkAllSimilarity()
        } else {
          this.$message.error(res.data.message || '组卷失败')
        }
      } catch (error) {
        this.$message.error('组卷请求失败：' + (error.message || '未知错误'))
      } finally {
        this.generating = false
      }
    },
    
    // 并行执行两种相似度检测
    async checkAllSimilarity() {
      if (!this.paperResult) return
      this.checkingSimilarity = true
      try {
        await this.checkFormalExamSimilarity()
      } finally {
        this.checkingSimilarity = false
      }
      if (this.combinedWarning) {
        this.$nextTick(() => { this.similarityDialogVisible = true })
        this.$message.warning('试卷相似度过高！建议重新组卷')
      }
    },
    
    // 遗传算法历史组卷相似度
    async checkSimilarity() {
      if (!this.paperResult) return
      try {
        const res = await this.$axios.post('/api/genetic/compare', {
          subjects: this.config.subjects,
          paperResult: this.paperResult
        })
        if (res.data.code === 200 && res.data.data) {
          this.similarityResult = res.data.data
        }
      } catch (e) {
        console.warn('遗传算法相似度检测失败', e)
      }
    },
    
    // 正式考试试卷相似度
    async checkFormalExamSimilarity() {
      if (!this.paperResult) return
      try {
        const res = await this.$axios.post('/api/genetic/compareExam', {
          subjects: this.config.subjects,
          paperResult: this.paperResult
        })
        if (res.data.code === 200 && res.data.data) {
          this.formalExamResult = res.data.data
        }
      } catch (e) {
        console.warn('正式考试相似度检测失败', e)
      }
    },
    
    // 重新组卷
    async regeneratePaper() {
      this.similarityDialogVisible = false
      await this.generatePaper()
    },

    renderCharts() {
      if (!this.paperResult || !this.paperResult.stats) return

      // 难度分布图
      const difficultyChart = echarts.init(this.$refs.difficultyChart)
      const diffData = this.paperResult.stats.difficultyDistribution || {}
      difficultyChart.setOption({
        tooltip: { trigger: 'item' },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          data: Object.entries(diffData).map(([name, value]) => ({
            name: '难度' + name,
            value
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: { show: true, formatter: '{b}: {c}题' }
        }]
      })

      // 题型分布图
      const typeChart = echarts.init(this.$refs.typeChart)
      const typeData = this.paperResult.stats.questionTypeDistribution || {}
      typeChart.setOption({
        tooltip: { trigger: 'item' },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          data: Object.entries(typeData).map(([name, value]) => ({
            name,
            value
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: { show: true, formatter: '{b}: {c}题' }
        }]
      })
    },

    resetConfig() {
      this.config = {
        subjects: [],
        targetDifficulty: 3,
        difficultyTolerance: 0.5,
        multiCount: 10,
        fillCount: 4,
        judgeCount: 10,
        subjectiveCount: 1,
        multiScore: 2,
        fillScore: 5,
        judgeScore: 5,
        subjectiveScore: 10,
        populationSize: 50,
        maxGenerations: 100,
        crossoverRate: 0.8,
        mutationRate: 0.1
      }
      this.paperResult = null
      this.similarityResult = null
    },

    exportPaper() {

      let content = '='.repeat(50) + '\n'
      content += '         遗传算法智能组卷试卷\n'
      content += '='.repeat(50) + '\n\n'
      content += `总分：${this.paperResult.stats.totalScore}分  题目数：${this.paperResult.stats.totalQuestions}题\n`
      content += `平均难度：${this.paperResult.stats.averageDifficulty}  匹配度：${this.paperResult.stats.fitness}%\n\n`

      if (this.paperResult.multiQuestions && this.paperResult.multiQuestions.length > 0) {
        content += '-'.repeat(30) + '\n'
        content += '一、选择题\n'
        content += '-'.repeat(30) + '\n'
        this.paperResult.multiQuestions.forEach((q, i) => {
          content += `${i + 1}. ${q.question}\n`
          content += `   A. ${q.answerA}\n`
          content += `   B. ${q.answerB}\n`
          content += `   C. ${q.answerC}\n`
          content += `   D. ${q.answerD}\n`
          content += `   答案: ${q.rightAnswer}\n\n`
        })
      }

      if (this.paperResult.fillQuestions && this.paperResult.fillQuestions.length > 0) {
        content += '-'.repeat(30) + '\n'
        content += '二、填空题\n'
        content += '-'.repeat(30) + '\n'
        this.paperResult.fillQuestions.forEach((q, i) => {
          content += `${i + 1}. ${q.question}\n`
          content += `   答案: ${q.answer}\n\n`
        })
      }

      if (this.paperResult.judgeQuestions && this.paperResult.judgeQuestions.length > 0) {
        content += '-'.repeat(30) + '\n'
        content += '三、判断题\n'
        content += '-'.repeat(30) + '\n'
        this.paperResult.judgeQuestions.forEach((q, i) => {
          content += `${i + 1}. ${q.question}\n`
          content += `   答案: ${q.answer === 'T' ? '正确' : '错误'}\n\n`
        })
      }

      if (this.paperResult.subjectiveQuestions && this.paperResult.subjectiveQuestions.length > 0) {
        content += '-'.repeat(30) + '\n'
        content += '四、主观题\n'
        content += '-'.repeat(30) + '\n'
        this.paperResult.subjectiveQuestions.forEach((q, i) => {
          content += `${i + 1}. ${q.question}\n`
          content += `   参考答案: ${q.referenceAnswer}\n\n`
        })
      }

      const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = '智能组卷试卷_' + new Date().getTime() + '.txt'
      link.click()
    },

    showCreateExamDialog() {
      console.log('点击了创建考试按钮')
      console.log('paperResult:', this.paperResult)
      if (!this.paperResult) {
        this.$message.warning('请先进行智能组卷')
        return
      }
      // 预填试卷名称
      const subjects = this.config.subjects.length > 0 ? this.config.subjects.join('/') : '综合'
      this.examForm.source = subjects + '-智能组卷试卷'
      this.examForm.description = `本试卷由遗传算法智能组卷生成，包含${this.paperResult.stats.totalQuestions}道题目，总分${this.paperResult.stats.totalScore}分，平均难度${this.paperResult.stats.averageDifficulty}。`
      console.log('设置 examDialogVisible = true')
      this.examDialogVisible = true
    },

    async createExam() {
      // 表单验证
      if (!this.examForm.source) {
        this.$message.error('请输入试卷名称')
        return
      }
      if (!this.examForm.type) {
        this.$message.error('请选择考试类型')
        return
      }
      if (!this.examForm.examDate) {
        this.$message.error('请选择考试日期')
        return
      }

      this.creatingExam = true

      try {
        const res = await this.$axios.post('/api/genetic/createExam', {
          examInfo: this.examForm,
          paperResult: this.paperResult
        })

        if (res.data.code === 200) {
          this.$message.success('考试创建成功！学生现在可以看到此考试')
          this.examDialogVisible = false
          // 重置表单
          this.examForm = {
            source: '',
            description: '',
            examDate: '',
            totalTime: 120,
            grade: '',
            term: '',
            major: '',
            institute: '',
            type: '',
            tips: '请认真答题，考试期间禁止作弊。',
            examStartTime: '00:00',
            examEndTime: '23:59'
          }
        } else {
          this.$message.error(res.data.message || '创建失败')
        }
      } catch (error) {
        this.$message.error('创建考试失败：' + (error.message || '未知错误'))
      } finally {
        this.creatingExam = false
      }
    }
  }
}
</script>

<style scoped>
.genetic-paper-container {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
  min-height: calc(100vh - 60px);
}

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

.header-icon i {
  font-size: 32px;
}

.header-text h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.header-text p {
  margin: 0;
  opacity: 0.9;
}

.config-card, .result-card, .stats-card, .empty-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  font-size: 16px;
}

.card-header i {
  margin-right: 8px;
  color: #667eea;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.form-section {
  margin-bottom: 28px;
  padding-bottom: 24px;
  border-bottom: 1px dashed #e8e8e8;
}

.section-title {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

.section-title i {
  margin-right: 8px;
  color: #667eea;
}

.config-form /deep/ .el-slider__marks-text {
  white-space: nowrap;
}

.config-form /deep/ .el-form-item {
  margin-bottom: 0;
}

.config-form /deep/ .el-input-number {
  line-height: 38px;
}

.config-form /deep/ .el-input-number .el-input__inner {
  height: 38px;
  line-height: 38px;
}

.config-form /deep/ .el-input-number__decrease,
.config-form /deep/ .el-input-number__increase {
  height: 38px;
  line-height: 38px;
}

.total-score {
  text-align: center;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
  font-weight: 500;
}

.score-value {
  font-size: 24px;
  font-weight: 700;
  margin: 0 4px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.form-actions .el-button {
  flex: 1;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.stat-item {
  text-align: center;
  padding: 16px 8px;
  background: #f8f9fa;
  border-radius: 12px;
}

.stat-item .stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
}

.stat-item .stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.result-stats {
  margin-bottom: 24px;
}

.result-stat-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.stat-icon i {
  font-size: 24px;
  color: white;
}

.stat-icon.success { background: linear-gradient(135deg, #36d1dc 0%, #5b86e5 100%); }
.stat-icon.primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-icon.warning { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-icon.danger { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }

.stat-content .stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #333;
}

.stat-content .stat-label {
  font-size: 12px;
  color: #909399;
}

.generation-info {
  text-align: center;
  margin-top: 16px;
  color: #909399;
  font-size: 13px;
}

.charts-container {
  margin: 24px 0;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
}

.chart-title {
  text-align: center;
  font-weight: 600;
  margin-bottom: 12px;
  color: #333;
}

.chart-box {
  height: 200px;
}

.question-list {
  max-height: 500px;
  overflow-y: auto;
}

.question-item {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 12px;
}

.question-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.question-number {
  font-weight: 700;
  color: #667eea;
  margin-right: 12px;
}

.question-level {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 12px;
}

.level-1 { background: #e8f5e9; color: #4caf50; }
.level-2 { background: #e3f2fd; color: #2196f3; }
.level-3 { background: #fff3e0; color: #ff9800; }
.level-4 { background: #fce4ec; color: #e91e63; }
.level-5 { background: #f3e5f5; color: #9c27b0; }

.question-score {
  font-size: 12px;
  color: #909399;
}

.question-content {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  margin-bottom: 12px;
}

.question-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.option-item {
  padding: 8px 12px;
  background: white;
  border-radius: 8px;
  font-size: 13px;
  color: #666;
}

.option-item.correct {
  background: #e8f5e9;
  color: #4caf50;
  font-weight: 500;
}

.question-answer {
  display: flex;
  align-items: center;
}

.answer-label {
  font-weight: 500;
  margin-right: 8px;
  color: #666;
}

.answer-value {
  color: #4caf50;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-state img {
  width: 160px;
  margin-bottom: 24px;
  opacity: 0.7;
}

.empty-state h3 {
  margin: 0 0 12px 0;
  color: #333;
}

.empty-state p {
  color: #909399;
  margin: 0 0 30px 0;
}

.algorithm-intro {
  display: flex;
  justify-content: center;
  gap: 30px;
}

.intro-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.intro-item i {
  font-size: 32px;
  color: #667eea;
}

.intro-item span {
  font-size: 12px;
  color: #909399;
}

.advanced-collapse {
  margin-top: 16px;
}

/* 美化计数器样式 */
/deep/ .el-input-number {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  
  &:hover {
    border-color: #409eff;
  }

  .el-input__inner {
    border: none !important;
    text-align: center;
    padding-left: 50px;
    padding-right: 50px;
  }

  .el-input-number__decrease,
  .el-input-number__increase {
    background: #f5f7fa;
    border-right: 1px solid #dcdfe6;
    color: #606266;
    width: 40px;
    
    &:hover {
      color: #409eff;
      background: #ecf5ff;
    }
  }

  .el-input-number__increase {
    border-right: none;
    border-left: 1px solid #dcdfe6;
  }
}

/* 美化滚动条 */
.question-list::-webkit-scrollbar {
  width: 6px;
}

.question-list::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}

.question-list::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}
/* 相似度组件样式 */
.similarity-bar {
  display: flex;
  align-items: center;
  margin-top: 12px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
}
.sim-safe   { background: #f0f9eb; color: #67c23a; border: 1px solid #c2e7b0; }
.sim-warn   { background: #fdf6ec; color: #e6a23c; border: 1px solid #f5dab1; }
.sim-danger { background: #fef0f0; color: #f56c6c; border: 1px solid #fbc4c4; }

.similarity-overview {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  gap: 16px;
}
.sim-overview-safe   { background: linear-gradient(135deg, #f0f9eb, #e1f5d3); border: 2px solid #c2e7b0; }
.sim-overview-warn   { background: linear-gradient(135deg, #fdf6ec, #fce8ca); border: 2px solid #f5dab1; }
.sim-overview-danger { background: linear-gradient(135deg, #fef0f0, #fde2e2); border: 2px solid #fbc4c4; }

.similarity-icon { font-size: 40px; }
.sim-overview-safe   .similarity-icon { color: #67c23a; }
.sim-overview-warn   .similarity-icon { color: #e6a23c; }
.sim-overview-danger .similarity-icon { color: #f56c6c; }

.similarity-info { flex: 1; }
.similarity-value { font-size: 36px; font-weight: 700; }
.similarity-label { font-size: 13px; color: #666; margin-top: 4px; }

.similarity-progress { margin: 0 0 8px 0; position: relative; padding-bottom: 20px; }
.progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #999;
  margin-bottom: 6px;
}
.progress-pointer {
  position: absolute;
  bottom: 0;
  transform: translateX(-50%);
  font-size: 12px;
  font-weight: 600;
  color: #333;
}
.threshold-line {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  position: relative;
}
.threshold {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
}
.threshold.safe   { background: #f0f9eb; color: #67c23a; margin-left: 30%; }
.threshold.danger { background: #fef0f0; color: #f56c6c; margin-left: 20%; }

.similarity-details { margin-top: 16px; }
.detail-title {
  font-weight: 600;
  margin-bottom: 10px;
  color: #555;
  font-size: 14px;
}
.detail-title i { margin-right: 6px; color: #667eea; }
.no-history {
  text-align: center;
  padding: 30px;
  color: #909399;
  font-size: 14px;
}
.no-history i { margin-right: 6px; }
.text-success { color: #67c23a; }
.similarity-checking {
  margin-top: 12px;
  text-align: center;
  color: #909399;
  font-size: 13px;
}
</style>
