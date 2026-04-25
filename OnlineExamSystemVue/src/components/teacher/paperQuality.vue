<template>
  <div class="paper-quality-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <i class="el-icon-data-analysis header-icon"></i>
        <div class="header-text">
          <h1>试卷质量评价</h1>
          <p>基于经典测量理论（CTT）的多维度试卷质量分析系统</p>
        </div>
      </div>
    </div>

    <!-- 考试选择 -->
    <div class="select-section">
      <el-card shadow="hover">
        <div slot="header" class="card-header">
          <span><i class="el-icon-document"></i> 选择考试</span>
        </div>
        <el-form :inline="true" class="search-form">
          <el-form-item label="考试">
            <el-select v-model="selectedExamCode" placeholder="请选择考试" filterable clearable style="width: 300px">
              <el-option v-for="exam in examList" :key="exam.examCode" :label="exam.source" :value="exam.examCode">
                <span>{{ exam.source }}</span>
                <span style="float: right; color: #909399; font-size: 12px">{{ exam.examDate }}</span>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="evaluatePaper" :loading="loading" icon="el-icon-s-data">
              开始评价
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 评价结果 -->
    <div v-if="result" class="result-section">
      <!-- 质量等级 + 基本信息 -->
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card shadow="hover" class="info-card">
            <div slot="header" class="card-header">
              <span><i class="el-icon-info"></i> {{ result.examName }}</span>
              <div class="header-badges">
                <el-tag :type="getGradeTagType(result.qualityGrade)" size="medium" effect="dark" class="grade-tag">
                  {{ result.qualityGrade }}级 · {{ result.qualityScore }}分
                </el-tag>
                <el-tag type="primary" size="small">{{ result.totalStudents }}人参考</el-tag>
                <el-tag type="info" size="small">{{ result.totalQuestions }}道题</el-tag>
              </div>
            </div>
            <el-row :gutter="16">
              <el-col :span="4" v-for="stat in basicStats" :key="stat.label">
                <div class="stat-item">
                  <div class="stat-icon" :style="{ background: stat.gradient }">
                    <i :class="stat.icon"></i>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ stat.value }}</div>
                    <div class="stat-label">{{ stat.label }}</div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </el-col>
      </el-row>

      <!-- 雷达图 + 核心指标 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="12">
          <el-card shadow="hover" class="quality-card">
            <div slot="header" class="card-header">
              <span><i class="el-icon-data-board"></i> 多维质量评价</span>
              <el-tag :type="getGradeTagType(result.qualityGrade)" size="small">{{ result.qualityGrade }}级</el-tag>
            </div>
            <div ref="radarChart" style="height: 320px"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover" class="quality-card">
            <div slot="header" class="card-header">
              <span><i class="el-icon-s-data"></i> 高级统计量</span>
            </div>
            <div class="advanced-stats">
              <div class="adv-stat-row">
                <div class="adv-stat-item">
                  <span class="adv-label">偏度 (Skewness)</span>
                  <span class="adv-value" :class="getSkewnessClass(result.skewness)">{{ result.skewness }}</span>
                </div>
                <div class="adv-stat-item">
                  <span class="adv-label">峰度 (Kurtosis)</span>
                  <span class="adv-value" :class="getKurtosisClass(result.kurtosis)">{{ result.kurtosis }}</span>
                </div>
              </div>
              <div class="adv-stat-row">
                <div class="adv-stat-item">
                  <span class="adv-label">弗格森系数 (δ)</span>
                  <span class="adv-value">{{ result.fergusonDelta }}</span>
                </div>
                <div class="adv-stat-item">
                  <span class="adv-label">变异系数 (CV)</span>
                  <span class="adv-value">{{ result.coefficientOfVariation }}</span>
                </div>
              </div>
              <div class="adv-stat-row">
                <div class="adv-stat-item">
                  <span class="adv-label">中位数</span>
                  <span class="adv-value">{{ result.medianScore }}</span>
                </div>
                <div class="adv-stat-item">
                  <span class="adv-label">极差</span>
                  <span class="adv-value">{{ result.maxScoreValue }} - {{ result.minScoreValue }}</span>
                </div>
              </div>
              <div class="normality-box">
                <i class="el-icon-warning-outline"></i>
                <span>{{ result.normalityAssessment }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 信度和效度 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="12">
          <el-card shadow="hover" class="quality-card">
            <div slot="header" class="card-header">
              <span><i class="el-icon-s-check"></i> 信度分析</span>
              <el-tag :type="getReliabilityTagType(result.reliabilityLevel)">{{ result.reliabilityLevel }}</el-tag>
            </div>
            <div class="quality-content">
              <div class="quality-score">
                <el-progress type="dashboard" :percentage="Math.round(result.reliability * 100)" :color="getProgressColor(result.reliability)" :width="120">
                  <template slot-scope="">
                    <span class="percentage-value">{{ result.reliability }}</span>
                    <span class="percentage-label">α系数</span>
                  </template>
                </el-progress>
              </div>
              <div class="quality-desc">
                <p class="desc-text">{{ result.reliabilityDesc }}</p>
                <div class="reliability-detail" v-if="result.splitHalfReliability != null">
                  <el-tag size="mini" type="info">折半信度: {{ result.splitHalfReliability }}</el-tag>
                </div>
                <div class="quality-scale">
                  <div class="scale-item"><span class="dot excellent"></span>≥0.9 非常好</div>
                  <div class="scale-item"><span class="dot good"></span>0.7-0.9 良好</div>
                  <div class="scale-item"><span class="dot fair"></span>0.5-0.7 一般</div>
                  <div class="scale-item"><span class="dot poor"></span>&lt;0.5 较差</div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover" class="quality-card">
            <div slot="header" class="card-header">
              <span><i class="el-icon-aim"></i> 效度分析（内容效度）</span>
              <el-tag :type="getValidityTagType(result.validityLevel)">{{ result.validityLevel }}</el-tag>
            </div>
            <div class="quality-content">
              <div class="quality-score">
                <el-progress type="dashboard" :percentage="Math.min(100, Math.round(result.validity * 200))" :color="getProgressColor(result.validity * 2)" :width="120">
                  <template slot-scope="">
                    <span class="percentage-value">{{ result.validity }}</span>
                    <span class="percentage-label">平均rpb</span>
                  </template>
                </el-progress>
              </div>
              <div class="quality-desc">
                <p class="desc-text">{{ result.validityDesc }}</p>
                <div class="quality-scale">
                  <div class="scale-item"><span class="dot excellent"></span>≥0.4 非常好</div>
                  <div class="scale-item"><span class="dot good"></span>0.3-0.4 良好</div>
                  <div class="scale-item"><span class="dot fair"></span>0.2-0.3 一般</div>
                  <div class="scale-item"><span class="dot poor"></span>&lt;0.2 较差</div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 难度-区分度散点图 + 成绩分布 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="12">
          <el-card shadow="hover">
            <div slot="header" class="card-header">
              <span><i class="el-icon-s-grid"></i> 难度-区分度散点图</span>
              <span class="header-info">理想区域：难度0.3-0.7 × 区分度≥0.3</span>
            </div>
            <div ref="scatterChart" style="height: 320px"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <div slot="header" class="card-header">
              <span><i class="el-icon-pie-chart"></i> 成绩分布与正态拟合</span>
            </div>
            <div ref="scoreChart" style="height: 320px"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 难度/区分度饼图 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="12">
          <el-card shadow="hover">
            <div slot="header" class="card-header">
              <span><i class="el-icon-s-grid"></i> 难度分布</span>
              <span class="header-info">平均难度：{{ result.averageDifficulty }}</span>
            </div>
            <div class="distribution-content">
              <div ref="difficultyChart" style="height: 220px"></div>
              <div class="distribution-legend">
                <div class="legend-item"><span class="legend-dot easy"></span>简单（&lt;0.3）：{{ result.easyCount }}题</div>
                <div class="legend-item"><span class="legend-dot medium"></span>中等（0.3-0.7）：{{ result.mediumCount }}题</div>
                <div class="legend-item"><span class="legend-dot hard"></span>困难（&gt;0.7）：{{ result.hardCount }}题</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <div slot="header" class="card-header">
              <span><i class="el-icon-s-marketing"></i> 区分度分布</span>
              <span class="header-info">平均区分度：{{ result.averageDiscrimination }}</span>
            </div>
            <div class="distribution-content">
              <div ref="discriminationChart" style="height: 220px"></div>
              <div class="distribution-legend">
                <div class="legend-item"><span class="legend-dot good"></span>良好（≥0.3）：{{ result.goodDiscrimination }}题</div>
                <div class="legend-item"><span class="legend-dot fair"></span>一般（0.2-0.3）：{{ result.fairDiscrimination }}题</div>
                <div class="legend-item"><span class="legend-dot poor"></span>较差（&lt;0.2）：{{ result.poorDiscrimination }}题</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 题目详细分析 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="24">
          <el-card shadow="hover">
            <div slot="header" class="card-header">
              <span><i class="el-icon-document-checked"></i> 题目详细分析</span>
              <span class="header-info">共{{ result.totalQuestions }}道题目</span>
            </div>
            <el-table :data="result.questionAnalysisList" stripe style="width: 100%" max-height="400">
              <el-table-column prop="questionTypeName" label="题型" width="80" align="center">
                <template slot-scope="scope">
                  <el-tag size="mini" :type="getQuestionTypeTag(scope.row.questionType)">{{ scope.row.questionTypeName }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="questionContent" label="题目内容" min-width="160" show-overflow-tooltip />
              <el-table-column prop="difficulty" label="难度" width="110" align="center" sortable>
                <template slot-scope="scope">
                  <el-progress :percentage="Math.round(scope.row.difficulty * 100)" :color="getDifficultyColor(scope.row.difficulty)" :show-text="false" :stroke-width="8" />
                  <span class="progress-text">{{ scope.row.difficulty }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="discrimination" label="区分度" width="110" align="center" sortable>
                <template slot-scope="scope">
                  <el-progress :percentage="Math.max(0, Math.round(scope.row.discrimination * 100))" :color="getDiscriminationColor(scope.row.discrimination)" :show-text="false" :stroke-width="8" />
                  <span class="progress-text">{{ scope.row.discrimination }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="pointBiserial" label="rpb" width="80" align="center" sortable>
                <template slot-scope="scope">
                  <span :style="{ color: scope.row.pointBiserial >= 0.3 ? '#67C23A' : (scope.row.pointBiserial >= 0.2 ? '#E6A23C' : '#F56C6C') }">
                    {{ scope.row.pointBiserial }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="正确率" width="80" align="center">
                <template slot-scope="scope">
                  {{ scope.row.totalCount > 0 ? Math.round((scope.row.correctCount / scope.row.totalCount) * 100) : 0 }}%
                </template>
              </el-table-column>
              <el-table-column prop="itemQuality" label="质量" width="80" align="center">
                <template slot-scope="scope">
                  <el-tag size="mini" :type="getItemQualityTag(scope.row.itemQuality)">{{ scope.row.itemQuality }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <!-- 综合评价和建议 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="24">
          <el-card shadow="hover" class="assessment-card">
            <div slot="header" class="card-header">
              <span><i class="el-icon-s-comment"></i> 综合评价与改进建议</span>
              <el-tag :type="getGradeTagType(result.qualityGrade)" effect="dark">{{ result.qualityGrade }}级</el-tag>
            </div>
            <div class="assessment-content">
              <div class="overall-assessment">
                <i class="el-icon-document-checked"></i>
                <p>{{ result.overallAssessment }}</p>
              </div>
              <div class="suggestions" v-if="result.suggestions && result.suggestions.length > 0">
                <h4><i class="el-icon-warning-outline"></i> 改进建议</h4>
                <ul>
                  <li v-for="(s, i) in result.suggestions" :key="i">
                    <i class="el-icon-caret-right"></i>{{ s }}
                  </li>
                </ul>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div v-if="!result && !loading" class="empty-state">
      <i class="el-icon-data-analysis"></i>
      <p>请选择考试后点击"开始评价"</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PaperQuality',
  data() {
    return {
      loading: false,
      selectedExamCode: null,
      examList: [],
      result: null
    }
  },
  computed: {
    basicStats() {
      if (!this.result) return []
      return [
        { label: '平均分', value: this.result.averageScore, icon: 'el-icon-s-data', gradient: 'linear-gradient(135deg, #409EFF, #66b1ff)' },
        { label: '及格率', value: this.result.passRate + '%', icon: 'el-icon-check', gradient: 'linear-gradient(135deg, #67C23A, #85ce61)' },
        { label: '优秀率', value: this.result.excellentRate + '%', icon: 'el-icon-trophy', gradient: 'linear-gradient(135deg, #E6A23C, #f0b86e)' },
        { label: '标准差', value: this.result.standardDeviation, icon: 'el-icon-s-operation', gradient: 'linear-gradient(135deg, #909399, #b4b4b4)' },
        { label: '信度α', value: this.result.reliability, icon: 'el-icon-s-check', gradient: 'linear-gradient(135deg, #6366f1, #818cf8)' },
        { label: '效度rpb', value: this.result.validity, icon: 'el-icon-aim', gradient: 'linear-gradient(135deg, #ec4899, #f472b6)' }
      ]
    }
  },
  mounted() {
    this.loadExamList()
  },
  methods: {
    async loadExamList() {
      try {
        const res = await this.$axios.get('/api/exams/1/100')
        if (res.data.code === 200 && res.data.data) {
          this.examList = res.data.data.records || []
        }
      } catch (e) { console.error('加载考试列表失败:', e) }
    },
    async evaluatePaper() {
      if (!this.selectedExamCode) {
        this.$message.warning('请选择考试')
        return
      }
      this.loading = true
      try {
        const res = await this.$axios.get(`/api/paper-quality/evaluate/${this.selectedExamCode}`)
        if (res.data.code === 200) {
          this.result = res.data.data
          this.$nextTick(() => { this.renderCharts() })
        } else {
          this.$message.error(res.data.message || '评价失败')
        }
      } catch (e) {
        console.error('评价失败:', e)
        this.$message.error('评价失败，请重试')
      } finally { this.loading = false }
    },
    renderCharts() {
      this.renderRadarChart()
      this.renderScatterChart()
      this.renderScoreChart()
      this.renderDifficultyChart()
      this.renderDiscriminationChart()
    },
    renderRadarChart() {
      if (!this.$refs.radarChart || !this.result.radarData) return
      const chart = this.$echarts.init(this.$refs.radarChart)
      const keys = Object.keys(this.result.radarData)
      const values = Object.values(this.result.radarData)
      chart.setOption({
        tooltip: {},
        radar: {
          indicator: keys.map(k => ({ name: k, max: 100 })),
          shape: 'polygon',
          splitNumber: 5,
          axisName: { color: '#606266', fontSize: 12 },
          splitArea: { areaStyle: { color: ['rgba(64,158,255,0.05)', 'rgba(64,158,255,0.1)', 'rgba(64,158,255,0.05)', 'rgba(64,158,255,0.1)', 'rgba(64,158,255,0.05)'] } }
        },
        series: [{
          type: 'radar',
          data: [{ value: values, name: '质量评分', areaStyle: { color: 'rgba(64,158,255,0.3)' }, lineStyle: { color: '#409EFF', width: 2 }, itemStyle: { color: '#409EFF' } }]
        }]
      })
    },
    renderScatterChart() {
      if (!this.$refs.scatterChart || !this.result.scatterData) return
      const chart = this.$echarts.init(this.$refs.scatterChart)
      const data = this.result.scatterData
      const typeColors = { '选择题': '#409EFF', '填空题': '#67C23A', '判断题': '#E6A23C', '主观题': '#F56C6C' }
      const series = {}
      data.forEach(d => {
        const t = d.type || '其他'
        if (!series[t]) series[t] = []
        series[t].push([d.difficulty, d.discrimination, d.id, d.quality, d.pointBiserial])
      })
      chart.setOption({
        tooltip: {
          formatter: function(p) {
            const d = p.data
            return `题目 #${d[2]}<br/>难度: ${d[0]}<br/>区分度: ${d[1]}<br/>rpb: ${d[4]}<br/>质量: ${d[3]}`
          }
        },
        grid: { left: '12%', right: '5%', bottom: '12%', top: '8%' },
        xAxis: { type: 'value', name: '难度', min: 0, max: 1, splitLine: { lineStyle: { type: 'dashed' } } },
        yAxis: { type: 'value', name: '区分度', min: -0.1, max: 1, splitLine: { lineStyle: { type: 'dashed' } } },
        series: [
          ...Object.keys(series).map(t => ({
            name: t, type: 'scatter', data: series[t], symbolSize: 12,
            itemStyle: { color: typeColors[t] || '#909399' }
          })),
          {
            type: 'line', markArea: {
              silent: true, itemStyle: { color: 'rgba(103,194,58,0.08)', borderColor: '#67C23A', borderWidth: 1, borderType: 'dashed' },
              data: [[{ xAxis: 0.3, yAxis: 0.3 }, { xAxis: 0.7, yAxis: 1 }]]
            }, data: []
          }
        ],
        legend: { data: Object.keys(series), bottom: 0 }
      })
    },
    renderScoreChart() {
      if (!this.$refs.scoreChart) return
      const chart = this.$echarts.init(this.$refs.scoreChart)
      const freq = this.result.scoreFrequency || []
      const normal = this.result.normalCurveData || []
      const dist = this.result.scoreDistribution || {}
      const hasFreq = freq.length > 0
      chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '8%', right: '8%', bottom: '12%', top: '8%', containLabel: true },
        xAxis: { type: 'category', data: hasFreq ? freq.map(f => f.range) : Object.keys(dist), axisLabel: { interval: 0, rotate: hasFreq ? 30 : 0, fontSize: 11 } },
        yAxis: [{ type: 'value', name: '人数' }, { type: 'value', name: '拟合', show: false }],
        series: [
          {
            name: '实际人数', type: 'bar', barWidth: '50%',
            data: hasFreq ? freq.map(f => f.count) : Object.values(dist),
            itemStyle: {
              color: function(p) {
                const colors = ['#F56C6C', '#F56C6C', '#F56C6C', '#F56C6C', '#F56C6C', '#F56C6C', '#E6A23C', '#E6A23C', '#67C23A', '#409EFF']
                return hasFreq ? (colors[p.dataIndex] || '#409EFF') : ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399'][p.dataIndex]
              },
              borderRadius: [4, 4, 0, 0]
            },
            label: { show: true, position: 'top', fontSize: 11 }
          },
          normal.length > 0 ? {
            name: '正态拟合', type: 'line', smooth: true, yAxisIndex: 0,
            data: normal.map((_, i) => {
              const binIdx = Math.floor(i / (normal.length / (hasFreq ? freq.length : 5)))
              return normal[i].y
            }),
            lineStyle: { color: '#F56C6C', width: 2, type: 'dashed' },
            itemStyle: { opacity: 0 }, symbol: 'none'
          } : null
        ].filter(Boolean)
      })
    },
    renderDifficultyChart() {
      if (!this.$refs.difficultyChart) return
      const chart = this.$echarts.init(this.$refs.difficultyChart)
      chart.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c}题 ({d}%)' },
        series: [{
          type: 'pie', radius: ['40%', '70%'], avoidLabelOverlap: false,
          itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
          label: { show: false },
          emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
          data: [
            { value: this.result.easyCount, name: '简单', itemStyle: { color: '#67C23A' } },
            { value: this.result.mediumCount, name: '中等', itemStyle: { color: '#E6A23C' } },
            { value: this.result.hardCount, name: '困难', itemStyle: { color: '#F56C6C' } }
          ]
        }]
      })
    },
    renderDiscriminationChart() {
      if (!this.$refs.discriminationChart) return
      const chart = this.$echarts.init(this.$refs.discriminationChart)
      chart.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c}题 ({d}%)' },
        series: [{
          type: 'pie', radius: ['40%', '70%'], avoidLabelOverlap: false,
          itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
          label: { show: false },
          emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
          data: [
            { value: this.result.goodDiscrimination, name: '良好', itemStyle: { color: '#67C23A' } },
            { value: this.result.fairDiscrimination, name: '一般', itemStyle: { color: '#E6A23C' } },
            { value: this.result.poorDiscrimination, name: '较差', itemStyle: { color: '#F56C6C' } }
          ]
        }]
      })
    },
    // === 样式辅助 ===
    getGradeTagType(g) { return { A: 'success', B: 'primary', C: 'warning', D: 'danger', E: 'danger' }[g] || 'info' },
    getReliabilityTagType(l) { return { '非常好': 'success', '良好': 'primary', '一般': 'warning', '较差': 'danger' }[l] || 'info' },
    getValidityTagType(l) { return { '非常好': 'success', '良好': 'primary', '一般': 'warning', '较差': 'danger' }[l] || 'info' },
    getProgressColor(v) { return v >= 0.7 ? '#67C23A' : (v >= 0.5 ? '#E6A23C' : '#F56C6C') },
    getQuestionTypeTag(t) { return { 1: '', 2: 'success', 3: 'warning', 4: 'danger' }[t] || 'info' },
    getDifficultyColor(v) { return v < 0.3 ? '#67C23A' : (v < 0.7 ? '#E6A23C' : '#F56C6C') },
    getDiscriminationColor(v) { return v >= 0.3 ? '#67C23A' : (v >= 0.2 ? '#E6A23C' : '#F56C6C') },
    getItemQualityTag(q) { return { '优秀': 'success', '良好': 'primary', '一般': 'warning', '较差': 'danger', '极差': 'danger' }[q] || 'info' },
    getSkewnessClass(v) { return Math.abs(v) < 0.5 ? 'stat-good' : (Math.abs(v) < 1 ? 'stat-warn' : 'stat-bad') },
    getKurtosisClass(v) { return Math.abs(v) < 1 ? 'stat-good' : (Math.abs(v) < 2 ? 'stat-warn' : 'stat-bad') }
  }
}
</script>

<style lang="less" scoped>
.paper-quality-container { padding: 20px; background: #f5f7fa; min-height: 100vh; }
.page-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3); }
.header-content { display: flex; align-items: center; gap: 20px; color: #fff; }
.header-icon { font-size: 48px; opacity: 0.9; }
.header-text h1 { margin: 0 0 8px; font-size: 28px; font-weight: 600; }
.header-text p { margin: 0; opacity: 0.85; font-size: 14px; }
.select-section { margin-bottom: 20px; }
.card-header { display: flex; align-items: center; justify-content: space-between; font-weight: 600; }
.card-header i { margin-right: 8px; }
.header-info { font-size: 12px; color: #909399; font-weight: normal; }
.header-badges { display: flex; gap: 8px; align-items: center; }
.grade-tag { font-size: 14px; font-weight: 700; padding: 4px 12px; }

.info-card .stat-item { display: flex; align-items: center; gap: 12px; padding: 12px; background: #f8f9fa; border-radius: 10px; }
.stat-icon { width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 20px; flex-shrink: 0; }
.stat-info { flex: 1; }
.stat-value { font-size: 20px; font-weight: 700; color: #303133; }
.stat-label { font-size: 12px; color: #909399; margin-top: 2px; }

.quality-card .quality-content { display: flex; align-items: center; gap: 30px; padding: 20px 0; }
.quality-score { flex-shrink: 0; }
.percentage-value { display: block; font-size: 24px; font-weight: 700; color: #303133; }
.percentage-label { display: block; font-size: 12px; color: #909399; }
.quality-desc { flex: 1; }
.desc-text { font-size: 14px; color: #606266; line-height: 1.6; margin-bottom: 12px; }
.reliability-detail { margin-bottom: 12px; }
.quality-scale { display: flex; flex-wrap: wrap; gap: 12px; }
.scale-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #909399; }
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot.excellent { background: #67C23A; }
.dot.good { background: #409EFF; }
.dot.fair { background: #E6A23C; }
.dot.poor { background: #F56C6C; }

.advanced-stats { padding: 10px 0; }
.adv-stat-row { display: flex; gap: 16px; margin-bottom: 16px; }
.adv-stat-item { flex: 1; background: #f8f9fa; border-radius: 10px; padding: 14px 16px; display: flex; justify-content: space-between; align-items: center; }
.adv-label { font-size: 13px; color: #606266; }
.adv-value { font-size: 18px; font-weight: 700; color: #303133; }
.adv-value.stat-good { color: #67C23A; }
.adv-value.stat-warn { color: #E6A23C; }
.adv-value.stat-bad { color: #F56C6C; }
.normality-box { padding: 12px 16px; background: linear-gradient(135deg, #f0f9ff, #e8f4fd); border-radius: 10px; font-size: 13px; color: #606266; display: flex; align-items: center; gap: 8px; }
.normality-box i { color: #409EFF; font-size: 16px; }

.distribution-content { padding: 10px 0; }
.distribution-legend { display: flex; justify-content: center; gap: 20px; margin-top: 12px; padding-top: 12px; border-top: 1px solid #ebeef5; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #606266; }
.legend-dot { width: 12px; height: 12px; border-radius: 3px; }
.legend-dot.easy { background: #67C23A; }
.legend-dot.medium { background: #E6A23C; }
.legend-dot.hard { background: #F56C6C; }
.legend-dot.good { background: #67C23A; }
.legend-dot.fair { background: #E6A23C; }
.legend-dot.poor { background: #F56C6C; }
.progress-text { font-size: 12px; color: #606266; margin-left: 8px; }

.assessment-card .assessment-content { padding: 10px 0; }
.overall-assessment { display: flex; align-items: flex-start; gap: 12px; padding: 20px; background: linear-gradient(135deg, #f0f9ff 0%, #e8f4fd 100%); border-radius: 12px; margin-bottom: 20px; }
.overall-assessment i { font-size: 24px; color: #409EFF; flex-shrink: 0; }
.overall-assessment p { margin: 0; font-size: 14px; color: #303133; line-height: 1.8; }
.suggestions h4 { display: flex; align-items: center; gap: 8px; margin: 0 0 15px; font-size: 15px; color: #E6A23C; }
.suggestions ul { list-style: none; padding: 0; margin: 0; }
.suggestions li { display: flex; align-items: center; gap: 8px; padding: 10px 15px; background: #fdf6ec; border-radius: 8px; margin-bottom: 10px; font-size: 14px; color: #606266; }
.suggestions li i { color: #E6A23C; }

.empty-state { text-align: center; padding: 80px 20px; color: #909399; }
.empty-state i { font-size: 64px; margin-bottom: 20px; opacity: 0.5; }
.empty-state p { font-size: 16px; }
</style>
