<!-- 错题本 - 浅蓝色现代风格 -->
<template>
  <div class="wrong-book">
    <!-- 页面头部 -->
    <div class="page-banner">
      <div class="banner-bg"></div>
      <div class="banner-content">
        <div class="banner-left">
          <div class="banner-icon"><i class="el-icon-notebook-2"></i></div>
          <div>
            <h2>我的错题本</h2>
            <p class="banner-desc">智能归纳 · 精准复习 · 高效提升</p>
          </div>
        </div>
        <div class="banner-right">
          <div class="mastery-ring">
            <svg viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="8"/>
              <circle cx="50" cy="50" r="42" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round"
                :stroke-dasharray="masteryCircle" stroke-dashoffset="0" transform="rotate(-90 50 50)"/>
            </svg>
            <div class="mastery-text">
              <span class="mastery-val">{{ masteryRate }}%</span>
              <span class="mastery-label">掌握率</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card" v-for="(s, i) in statCards" :key="i">
        <div class="stat-icon-wrap" :style="{ background: s.gradient }">
          <i :class="s.icon"></i>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar-card">
      <div class="toolbar-left">
        <el-input v-model="searchKeyword" placeholder="搜索题目内容..." prefix-icon="el-icon-search"
          clearable size="small" style="width:260px;" @clear="handleFilter" @keyup.enter.native="handleFilter"></el-input>
        <el-radio-group v-model="filterType" size="small" @change="handleFilter">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="1">选择题</el-radio-button>
          <el-radio-button label="2">填空题</el-radio-button>
          <el-radio-button label="3">判断题</el-radio-button>
          <el-radio-button label="4">主观题</el-radio-button>
        </el-radio-group>
      </div>
      <div class="toolbar-right">
        <el-dropdown @command="changeSortType" trigger="click">
          <el-button size="small" plain>
            <i class="el-icon-sort"></i> {{ sortLabels[sortType] }} <i class="el-icon-arrow-down el-icon--right"></i>
          </el-button>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item command="recommend" :class="{ 'active-sort': sortType==='recommend' }">
              <i class="el-icon-star-on"></i> 推荐排序
            </el-dropdown-item>
            <el-dropdown-item command="wrongCount" :class="{ 'active-sort': sortType==='wrongCount' }">
              <i class="el-icon-warning"></i> 错误次数
            </el-dropdown-item>
            <el-dropdown-item command="latest" :class="{ 'active-sort': sortType==='latest' }">
              <i class="el-icon-time"></i> 最近出错
            </el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
        <el-button size="small" type="primary" plain icon="el-icon-refresh" @click="refreshAll">刷新</el-button>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-layout" v-loading="loading">
      <!-- 左侧科目分类 -->
      <div class="subject-panel">
        <div class="panel-title"><i class="el-icon-folder-opened"></i> 科目分类</div>
        <div class="subject-item" :class="{ active: selectedSubject === 'all' }" @click="selectSubject('all')">
          <div class="subj-icon" style="background:linear-gradient(135deg,#3B82F6,#60A5FA);"><i class="el-icon-files"></i></div>
          <span class="subj-name">全部科目</span>
          <span class="subj-badge">{{ wrongQuestions.length }}</span>
        </div>
        <div class="subject-item" v-for="(qs, name) in groupedBySubject" :key="name"
             :class="{ active: selectedSubject === name }" @click="selectSubject(name)">
          <div class="subj-icon" :style="{ background: getSubjectColor(name) }"><i :class="getSubjectIcon(name)"></i></div>
          <span class="subj-name">{{ name || '未分类' }}</span>
          <span class="subj-badge">{{ qs.length }}</span>
        </div>
      </div>

      <!-- 右侧内容 -->
      <div class="content-area">
        <div v-if="filteredQuestions.length === 0" class="empty-state">
          <div class="empty-icon-wrap"><i class="el-icon-folder-opened"></i></div>
          <p class="empty-title">暂无错题记录</p>
          <p class="empty-desc">继续练习，错题会自动收录到这里</p>
          <el-button type="primary" round size="small" @click="$router.push('/smartPractice')">
            <i class="el-icon-cpu"></i> 开始智能练习
          </el-button>
        </div>

        <template v-if="filteredQuestions.length > 0">
          <!-- 当前分类标题 -->
          <div class="section-head">
            <span class="section-title">{{ selectedSubject === 'all' ? '全部科目' : (selectedSubject || '未分类') }}</span>
            <span class="section-count">共 {{ filteredQuestions.length }} 题</span>
          </div>

          <!-- 错题卡片列表 -->
          <div class="question-card" v-for="(item, idx) in pagedQuestions" :key="item.id">
            <div class="qcard-top">
              <div class="qcard-meta">
                <span class="q-type-tag" :class="'qtype-' + item.questionType">{{ getTypeName(item.questionType) }}</span>
                <span class="q-wrong-badge"><i class="el-icon-warning-outline"></i> 错误 {{ item.wrongCount }} 次</span>
                <span class="q-subject-tag" v-if="selectedSubject === 'all' && item.subject">{{ item.subject }}</span>
              </div>
              <span class="q-time">{{ formatTime(item.lastWrongTime) }}</span>
            </div>
            <div class="qcard-body">
              <p class="q-text">{{ item.questionContent }}</p>
              <div class="answer-row">
                <div class="ans-box wrong-ans">
                  <div class="ans-label"><i class="el-icon-close"></i> 你的答案</div>
                  <div class="ans-val">{{ item.wrongAnswer || '未作答' }}</div>
                </div>
                <div class="ans-box right-ans">
                  <div class="ans-label"><i class="el-icon-check"></i> 正确答案</div>
                  <div class="ans-val">{{ item.correctAnswer }}</div>
                </div>
              </div>
              <!-- 解析 -->
              <div class="analysis-bar" v-if="item.analysis">
                <div class="analysis-toggle" @click="toggleAnalysis(item)">
                  <i class="el-icon-reading"></i> 查看解析
                  <i class="el-icon-arrow-down" :class="{ rotated: item.showAnalysis }"></i>
                </div>
                <transition name="slide-fade">
                  <div class="analysis-body" v-show="item.showAnalysis">{{ item.analysis }}</div>
                </transition>
              </div>
              <!-- 笔记 -->
              <div class="note-bar">
                <div class="note-toggle" @click="toggleNote(item)">
                  <i class="el-icon-edit-outline"></i> {{ item.showNote ? '收起笔记' : (item.note ? '查看笔记' : '添加笔记') }}
                </div>
                <transition name="slide-fade">
                  <div class="note-body" v-show="item.showNote">
                    <el-input type="textarea" v-model="item.note" :rows="2" placeholder="记录你的心得和思路..."
                      maxlength="500" show-word-limit size="small"></el-input>
                    <el-button class="action-btn btn-save-note" size="small" @click="saveNote(item)"><i class="el-icon-document-checked"></i> 保存笔记</el-button>
                  </div>
                </transition>
              </div>
            </div>
            <div class="qcard-footer">
              <div class="footer-left">
                <el-button class="action-btn btn-mastered" size="small" @click="markMastered(item)">
                  <i class="el-icon-check"></i> 已掌握
                </el-button>
                <el-button class="action-btn btn-redo" size="small" @click="openRedo(item)">
                  <i class="el-icon-refresh-right"></i> 重做
                </el-button>
                <el-button class="action-btn btn-delete" size="small" @click="deleteQuestion(item)">
                  <i class="el-icon-delete"></i> 删除
                </el-button>
              </div>
              <span class="q-id-tag">#{{ item.id }}</span>
            </div>
          </div>

          <!-- 分页 -->
          <div class="page-wrap" v-if="filteredQuestions.length > pageSize">
            <el-pagination background layout="prev, pager, next" :total="filteredQuestions.length"
              :page-size="pageSize" :current-page="currentPage" @current-change="handlePageChange"></el-pagination>
          </div>
        </template>
      </div>
    </div>

    <!-- 重做弹窗 -->
    <el-dialog :visible.sync="redoDialogVisible" width="560px" :close-on-click-modal="false" :append-to-body="true" center>
      <div slot="title" class="redo-title"><i class="el-icon-refresh-right"></i> 重做错题</div>
      <div v-if="redoItem" class="redo-wrap">
        <div class="redo-meta">
          <span class="q-type-tag" :class="'qtype-' + redoItem.questionType">{{ getTypeName(redoItem.questionType) }}</span>
          <span v-if="redoItem.subject" class="redo-subj">{{ redoItem.subject }}</span>
        </div>
        <div class="redo-question">{{ redoItem.questionContent }}</div>
        <div class="redo-input">
          <template v-if="redoItem.questionType == 1">
            <p class="redo-hint">请选择答案：</p>
            <el-radio-group v-model="redoAnswer">
              <el-radio label="A" border>A</el-radio>
              <el-radio label="B" border>B</el-radio>
              <el-radio label="C" border>C</el-radio>
              <el-radio label="D" border>D</el-radio>
            </el-radio-group>
          </template>
          <template v-else-if="redoItem.questionType == 2">
            <p class="redo-hint">请填写答案：</p>
            <el-input v-model="redoAnswer" placeholder="输入答案" clearable></el-input>
          </template>
          <template v-else-if="redoItem.questionType == 3">
            <p class="redo-hint">请判断正误：</p>
            <el-radio-group v-model="redoAnswer">
              <el-radio label="T" border><i class="el-icon-check"></i> 正确</el-radio>
              <el-radio label="F" border><i class="el-icon-close"></i> 错误</el-radio>
            </el-radio-group>
          </template>
          <template v-else>
            <p class="redo-hint">请作答：</p>
            <el-input type="textarea" v-model="redoAnswer" :rows="3" placeholder="输入答案"></el-input>
          </template>
        </div>
        <transition name="slide-fade">
          <div v-if="redoResult !== null" class="redo-result" :class="redoResult.correct ? 'success' : 'fail'">
            <i :class="redoResult.correct ? 'el-icon-success' : 'el-icon-error'" class="result-big-icon"></i>
            <div class="result-detail">
              <p class="result-label">{{ redoResult.correct ? '回答正确！' : '回答错误' }}</p>
              <p class="result-msg">{{ redoResult.message }}</p>
              <p class="result-correct" v-if="!redoResult.correct">正确答案：<strong>{{ redoResult.correctAnswer }}</strong></p>
              <div class="result-analysis" v-if="redoItem.analysis">
                <p class="ra-title"><i class="el-icon-reading"></i> 解析</p>
                <p class="ra-text">{{ redoItem.analysis }}</p>
              </div>
            </div>
          </div>
        </transition>
      </div>
      <div slot="footer">
        <el-button @click="redoDialogVisible = false">关闭</el-button>
        <el-button type="primary" :loading="redoLoading" :disabled="!redoAnswer || redoResult !== null" @click="submitRedo">
          <i class="el-icon-s-promotion"></i> 提交答案
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'WrongBook',
  data() {
    return {
      loading: false,
      filterType: 'all',
      sortType: 'recommend',
      searchKeyword: '',
      wrongQuestions: [],
      stats: { totalWrong: 0, multiWrong: 0, fillWrong: 0, judgeWrong: 0, subjectiveWrong: 0 },
      studentId: null,
      pageSize: 5,
      currentPage: 1,
      selectedSubject: 'all',
      sortLabels: { recommend: '推荐排序', wrongCount: '错误次数', latest: '最近出错' },
      // 重做
      redoDialogVisible: false,
      redoItem: null,
      redoAnswer: '',
      redoLoading: false,
      redoResult: null
    }
  },
  computed: {
    masteryRate() {
      const t = this.stats.totalWrong || 0
      if (t === 0) return 100
      const mastered = Math.max(0, t - this.wrongQuestions.length)
      return Math.round(mastered / t * 100)
    },
    masteryCircle() {
      const r = this.masteryRate / 100
      const c = 2 * Math.PI * 42
      return `${c * r} ${c * (1 - r)}`
    },
    statCards() {
      return [
        { label: '总错题', value: this.stats.totalWrong || 0, icon: 'el-icon-document', gradient: 'linear-gradient(135deg,#3B82F6,#60A5FA)' },
        { label: '选择题', value: this.stats.multiWrong || 0, icon: 'el-icon-edit', gradient: 'linear-gradient(135deg,#10B981,#34D399)' },
        { label: '填空题', value: this.stats.fillWrong || 0, icon: 'el-icon-edit-outline', gradient: 'linear-gradient(135deg,#F59E0B,#FBBF24)' },
        { label: '判断题', value: this.stats.judgeWrong || 0, icon: 'el-icon-question', gradient: 'linear-gradient(135deg,#8B5CF6,#A78BFA)' },
        { label: '主观题', value: this.stats.subjectiveWrong || 0, icon: 'el-icon-notebook-2', gradient: 'linear-gradient(135deg,#EC4899,#F472B6)' }
      ]
    },
    groupedBySubject() {
      const g = {}
      this.wrongQuestions.forEach(item => {
        const s = item.subject || '未分类'
        if (!g[s]) g[s] = []
        g[s].push(item)
      })
      return g
    },
    filteredQuestions() {
      let list = this.wrongQuestions
      if (this.selectedSubject !== 'all') {
        list = list.filter(q => (q.subject || '未分类') === this.selectedSubject)
      }
      if (this.searchKeyword) {
        const kw = this.searchKeyword.toLowerCase()
        list = list.filter(q => (q.questionContent || '').toLowerCase().includes(kw) || (q.correctAnswer || '').toLowerCase().includes(kw))
      }
      return list
    },
    pagedQuestions() {
      const s = (this.currentPage - 1) * this.pageSize
      return this.filteredQuestions.slice(s, s + this.pageSize)
    }
  },
  created() {
    this.studentId = this.$cookies.get('cid')
    this.loadStats()
    this.loadWrongQuestions(this.sortType)
  },
  methods: {
    async loadStats() {
      try {
        const res = await this.$axios.get('/api/study/wrong/stats/' + this.studentId)
        if (res.data.code === 200) this.stats = res.data.data
      } catch (e) { console.error('加载统计失败:', e) }
    },
    async loadWrongQuestions(sort) {
      this.loading = true
      try {
        let url = '/api/study/wrong/' + this.studentId
        if (this.filterType !== 'all') {
          url = '/api/study/wrong/' + this.studentId + '/type/' + this.filterType
        } else {
          url += '?sort=' + (sort || this.sortType)
        }
        const res = await this.$axios.get(url)
        if (res.data.code === 200) {
          this.wrongQuestions = (res.data.data || []).map(item => {
            item.showAnalysis = false
            item.showNote = false
            item.note = item.note || ''
            return item
          })
        }
      } catch (e) { console.error('加载错题失败:', e) }
      finally { this.loading = false }
    },
    handleFilter() { this.currentPage = 1; this.loadWrongQuestions(this.sortType) },
    changeSortType(type) { this.sortType = type; this.currentPage = 1; this.loadWrongQuestions(type) },
    selectSubject(s) { this.selectedSubject = s; this.currentPage = 1 },
    handlePageChange(p) { this.currentPage = p },
    refreshAll() { this.loadStats(); this.loadWrongQuestions(this.sortType) },
    toggleAnalysis(item) { this.$set(item, 'showAnalysis', !item.showAnalysis) },
    toggleNote(item) { this.$set(item, 'showNote', !item.showNote) },
    saveNote(item) {
      // 笔记保存到 localStorage（轻量级方案）
      const key = 'wrongNote_' + item.id
      localStorage.setItem(key, item.note)
      this.$message.success('笔记已保存')
      item.showNote = false
    },
    async markMastered(item) {
      try {
        await this.$axios.put('/api/study/wrong/master/' + item.id)
        this.$message.success('已标记为掌握')
        this.loadWrongQuestions(this.sortType)
        this.loadStats()
      } catch (e) { this.$message.error('操作失败') }
    },
    async deleteQuestion(item) {
      try {
        await this.$confirm('确定删除此错题？删除后无法恢复', '提示', { type: 'warning' })
        await this.$axios.delete(`/api/study/wrong/${this.studentId}/${item.questionType}/${item.questionId}`)
        this.$message.success('删除成功')
        this.loadWrongQuestions(this.sortType)
        this.loadStats()
      } catch (e) { if (e !== 'cancel') this.$message.error('删除失败') }
    },
    openRedo(item) {
      this.redoItem = item; this.redoAnswer = ''; this.redoResult = null; this.redoDialogVisible = true
    },
    async submitRedo() {
      if (!this.redoAnswer) return this.$message.warning('请先作答')
      this.redoLoading = true
      try {
        const res = await this.$axios.post('/api/study/wrong/redo', { wrongQuestionId: this.redoItem.id, userAnswer: this.redoAnswer })
        if (res.data.code === 200) {
          this.redoResult = res.data.data
          if (res.data.data.correct) { this.$message.success('回答正确！'); this.loadWrongQuestions(this.sortType); this.loadStats() }
          else { this.$message.error('回答错误，继续加油！'); this.loadWrongQuestions(this.sortType) }
        } else { this.$message.error(res.data.message || '提交失败') }
      } catch (e) { this.$message.error('提交失败') }
      finally { this.redoLoading = false }
    },
    getTypeName(t) { return { 1: '选择题', 2: '填空题', 3: '判断题', 4: '主观题' }[t] || '未知' },
    getSubjectIcon(s) {
      const m = { '语文':'el-icon-reading','数学':'el-icon-data-analysis','英语':'el-icon-chat-line-round','物理':'el-icon-aim','化学':'el-icon-magic-stick','计算机':'el-icon-monitor','编程':'el-icon-cpu' }
      return m[s] || 'el-icon-collection'
    },
    getSubjectColor(s) {
      const m = { '语文':'linear-gradient(135deg,#EF4444,#F87171)','数学':'linear-gradient(135deg,#3B82F6,#60A5FA)','英语':'linear-gradient(135deg,#8B5CF6,#A78BFA)','物理':'linear-gradient(135deg,#06B6D4,#22D3EE)','化学':'linear-gradient(135deg,#10B981,#34D399)','计算机':'linear-gradient(135deg,#6366F1,#818CF8)' }
      return m[s] || 'linear-gradient(135deg,#64748B,#94A3B8)'
    },
    formatTime(t) {
      if (!t) return ''
      const d = new Date(t), now = new Date(), diff = now - d
      if (diff < 0) return d.toLocaleDateString('zh-CN')
      const mins = Math.floor(diff / 60000), hrs = Math.floor(diff / 3600000), days = Math.floor(diff / 86400000)
      if (mins < 1) return '刚刚'
      if (mins < 60) return mins + '分钟前'
      if (hrs < 24) return hrs + '小时前'
      if (days < 7) return days + '天前'
      return d.toLocaleDateString('zh-CN')
    }
  }
}
</script>

<style lang="less" scoped>
/* ========== 浅蓝色主题变量 ========== */
@primary: #3B82F6;
@primary-light: #60A5FA;
@primary-lighter: #93C5FD;
@primary-bg: #EFF6FF;
@primary-bg2: #DBEAFE;
@text-dark: #1E293B;
@text-mid: #64748B;
@text-light: #94A3B8;
@radius: 14px;
@radius-sm: 10px;
@shadow: 0 4px 16px rgba(59, 130, 246, 0.08);
@shadow-hover: 0 8px 30px rgba(59, 130, 246, 0.15);

.wrong-book {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0;
}

/* ========== 横幅 ========== */
.page-banner {
  position: relative;
  border-radius: @radius;
  overflow: hidden;
  margin-bottom: 24px;
  .banner-bg {
    position: absolute; inset: 0;
    background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 50%, #60A5FA 100%);
  }
  .banner-content {
    position: relative; z-index: 1;
    display: flex; align-items: center; justify-content: space-between;
    padding: 32px 36px;
  }
  .banner-left {
    display: flex; align-items: center; gap: 18px;
  }
  .banner-icon {
    width: 56px; height: 56px; border-radius: 16px;
    background: rgba(255,255,255,0.2); backdrop-filter: blur(8px);
    display: flex; align-items: center; justify-content: center;
    i { font-size: 28px; color: #fff; }
  }
  h2 { font-size: 24px; font-weight: 700; color: #fff; margin: 0 0 4px; }
  .banner-desc { font-size: 14px; color: rgba(255,255,255,0.8); margin: 0; }
  .mastery-ring {
    width: 80px; height: 80px; position: relative;
    svg { width: 100%; height: 100%; }
    .mastery-text {
      position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center;
      .mastery-val { font-size: 18px; font-weight: 800; color: #fff; }
      .mastery-label { font-size: 11px; color: rgba(255,255,255,0.7); }
    }
  }
}

/* ========== 统计卡片 ========== */
.stats-row {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 20px;
}
.stat-card {
  background: #fff; border-radius: @radius; padding: 20px; display: flex; align-items: center; gap: 16px;
  border: 1px solid rgba(59,130,246,0.1); box-shadow: @shadow; transition: all 0.3s;
  &:hover { transform: translateY(-3px); box-shadow: @shadow-hover; }
}
.stat-icon-wrap {
  width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center;
  i { font-size: 22px; color: #fff; }
}
.stat-value { font-size: 26px; font-weight: 800; color: @text-dark; }
.stat-label { font-size: 13px; color: @text-light; font-weight: 500; }

/* ========== 工具栏 ========== */
.toolbar-card {
  background: #fff; border-radius: @radius; padding: 16px 24px; margin-bottom: 20px;
  border: 1px solid rgba(59,130,246,0.1); box-shadow: @shadow;
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
}
.toolbar-left { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.toolbar-right { display: flex; align-items: center; gap: 8px; }

/* ========== 主布局 ========== */
.main-layout { display: flex; gap: 20px; min-height: 400px; }

/* 科目面板 */
.subject-panel {
  width: 220px; flex-shrink: 0; background: #fff; border-radius: @radius; padding: 20px 16px;
  border: 1px solid rgba(59,130,246,0.1); box-shadow: @shadow; height: fit-content; position: sticky; top: 80px;
}
.panel-title {
  font-size: 15px; font-weight: 700; color: @text-dark; margin-bottom: 16px;
  padding-bottom: 12px; border-bottom: 2px solid @primary-bg2;
  i { color: @primary; margin-right: 8px; }
}
.subject-item {
  display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: @radius-sm;
  cursor: pointer; transition: all 0.25s; margin-bottom: 4px;
  &:hover { background: @primary-bg; }
  &.active {
    background: @primary-bg2; box-shadow: 0 2px 8px rgba(59,130,246,0.12);
    .subj-name { color: @primary; font-weight: 600; }
    .subj-badge { background: rgba(59,130,246,0.2); color: @primary; }
  }
}
.subj-icon {
  width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  i { font-size: 15px; color: #fff; }
}
.subj-name { flex: 1; font-size: 14px; color: @text-mid; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.subj-badge { font-size: 12px; font-weight: 700; color: @text-light; background: #F1F5F9; padding: 2px 8px; border-radius: 12px; }

/* 内容区 */
.content-area { flex: 1; min-width: 0; }
.section-head {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 16px; padding: 14px 20px; background: #fff; border-radius: @radius;
  border: 1px solid rgba(59,130,246,0.1); box-shadow: @shadow;
}
.section-title { font-size: 16px; font-weight: 700; color: @text-dark; }
.section-count { font-size: 13px; color: @text-light; background: @primary-bg; padding: 4px 14px; border-radius: 20px; font-weight: 600; }

/* ========== 错题卡片 ========== */
.question-card {
  background: #fff; border-radius: @radius; padding: 24px; margin-bottom: 16px;
  border: 1px solid rgba(59,130,246,0.1); box-shadow: @shadow;
  transition: all 0.3s; position: relative;
  &::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, @primary, @primary-light); border-radius: @radius @radius 0 0; opacity: 0; transition: opacity 0.3s; }
  &:hover { box-shadow: @shadow-hover; &::before { opacity: 1; } }
}
.qcard-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.qcard-meta { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.q-type-tag {
  padding: 4px 14px; border-radius: 16px; font-size: 12px; font-weight: 700; color: #fff;
  &.qtype-1 { background: linear-gradient(135deg, #10B981, #34D399); }
  &.qtype-2 { background: linear-gradient(135deg, #F59E0B, #FBBF24); }
  &.qtype-3 { background: linear-gradient(135deg, #8B5CF6, #A78BFA); }
  &.qtype-4 { background: linear-gradient(135deg, #EC4899, #F472B6); }
}
.q-wrong-badge { color: #EF4444; font-size: 12px; font-weight: 600; background: rgba(239,68,68,0.08); padding: 4px 10px; border-radius: 12px; }
.q-subject-tag { font-size: 12px; font-weight: 600; color: @primary; background: @primary-bg; padding: 4px 10px; border-radius: 12px; }
.q-time { font-size: 12px; color: @text-light; }

.qcard-body { margin-bottom: 16px; }
.q-text { font-size: 15px; line-height: 1.8; color: @text-dark; margin: 0 0 16px; font-weight: 500; }

.answer-row { display: flex; gap: 16px; }
.ans-box { flex: 1; padding: 16px; border-radius: @radius-sm; }
.wrong-ans { background: linear-gradient(135deg, rgba(239,68,68,0.06), rgba(248,113,113,0.03)); border: 1.5px solid rgba(239,68,68,0.15); }
.right-ans { background: linear-gradient(135deg, rgba(16,185,129,0.06), rgba(52,211,153,0.03)); border: 1.5px solid rgba(16,185,129,0.15); }
.ans-label { font-size: 11px; color: @text-light; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; i { margin-right: 4px; } }
.wrong-ans .ans-val { color: #EF4444; font-weight: 600; font-size: 14px; }
.right-ans .ans-val { color: #10B981; font-weight: 600; font-size: 14px; }

/* 解析 & 笔记 */
.analysis-bar, .note-bar { margin-top: 12px; padding-top: 12px; border-top: 1px dashed rgba(59,130,246,0.1); }
.analysis-toggle, .note-toggle {
  display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 13px; font-weight: 600; color: @primary;
  padding: 4px 0; transition: color 0.25s;
  &:hover { color: #1E40AF; }
  .el-icon-arrow-down { margin-left: auto; transition: transform 0.3s; &.rotated { transform: rotate(180deg); } }
}
.note-toggle { color: #F59E0B; &:hover { color: #D97706; } }
.analysis-body { margin-top: 10px; padding: 14px; background: @primary-bg; border-radius: @radius-sm; border-left: 3px solid @primary; font-size: 14px; line-height: 1.8; color: @text-mid; }
.note-body { margin-top: 10px; .action-btn { margin-top: 10px; } }
.btn-save-note {
  background: #10B981 !important;
  &:hover { background: #059669 !important; }
}

.qcard-footer {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 16px; border-top: 1px solid #F1F5F9;
}
.footer-left { display: flex; gap: 10px; }

/* 操作按钮统一样式 */
.action-btn {
  font-size: 13px !important;
  font-weight: 600 !important;
  letter-spacing: 0.5px;
  padding: 8px 18px !important;
  border-radius: 8px !important;
  border: none !important;
  color: #fff !important;
  transition: all 0.25s ease !important;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  i { margin-right: 4px; font-weight: bold; }
  &:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
  &:active { transform: translateY(0); }
}
.btn-mastered {
  background: #3B82F6 !important;
  &:hover { background: #2563EB !important; }
}
.btn-redo {
  background: #F59E0B !important;
  &:hover { background: #D97706 !important; }
}
.btn-delete {
  background: #EF4444 !important;
  &:hover { background: #DC2626 !important; }
}
.q-id-tag { font-size: 12px; color: @text-light; }

/* ========== 空状态 ========== */
.empty-state {
  text-align: center; padding: 80px 20px; background: #fff; border-radius: @radius;
  border: 2px dashed rgba(59,130,246,0.15);
}
.empty-icon-wrap i { font-size: 64px; color: @primary-lighter; margin-bottom: 16px; display: inline-block; }
.empty-title { font-size: 18px; color: @text-mid; font-weight: 600; margin: 8px 0; }
.empty-desc { font-size: 14px; color: @text-light; margin-bottom: 20px; }

/* ========== 分页 ========== */
.page-wrap { display: flex; justify-content: center; padding: 20px 0; }

/* ========== 重做弹窗 ========== */
.redo-title { display: flex; align-items: center; gap: 8px; font-size: 18px; font-weight: 700; color: @text-dark; i { color: #F59E0B; font-size: 22px; } }
.redo-wrap { padding: 0 4px; }
.redo-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
.redo-subj { font-size: 12px; font-weight: 600; color: @primary; background: @primary-bg; padding: 4px 12px; border-radius: 12px; }
.redo-question { padding: 16px; background: #F8FAFC; border-radius: @radius-sm; font-size: 15px; line-height: 1.8; color: @text-dark; margin-bottom: 16px; border: 1px solid #F1F5F9; }
.redo-input { margin-bottom: 16px; }
.redo-hint { font-size: 14px; color: @text-mid; font-weight: 600; margin-bottom: 10px; }
.redo-result {
  display: flex; align-items: flex-start; gap: 14px; padding: 16px; border-radius: @radius-sm; margin-top: 12px;
  &.success { background: rgba(16,185,129,0.08); border: 1.5px solid rgba(16,185,129,0.25); }
  &.fail { background: rgba(239,68,68,0.08); border: 1.5px solid rgba(239,68,68,0.25); }
}
.result-big-icon { font-size: 32px; flex-shrink: 0; }
.redo-result.success .result-big-icon { color: #10B981; }
.redo-result.fail .result-big-icon { color: #EF4444; }
.result-label { font-size: 15px; font-weight: 700; margin: 0 0 4px; }
.redo-result.success .result-label { color: #10B981; }
.redo-result.fail .result-label { color: #EF4444; }
.result-msg { font-size: 13px; color: @text-mid; margin: 0 0 4px; }
.result-correct { font-size: 13px; color: #EF4444; margin: 0; strong { color: #10B981; } }
.result-analysis { margin-top: 10px; padding: 12px; background: @primary-bg; border-radius: 8px; border-left: 3px solid @primary; }
.ra-title { font-size: 13px; font-weight: 700; color: @primary; margin: 0 0 4px; i { margin-right: 4px; } }
.ra-text { font-size: 13px; line-height: 1.7; color: @text-mid; margin: 0; }

/* ========== 过渡动画 ========== */
.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.3s ease; max-height: 400px; overflow: hidden; }
.slide-fade-enter, .slide-fade-leave-to { max-height: 0; opacity: 0; }

/* ========== 响应式 ========== */
@media (max-width: 960px) {
  .stats-row { grid-template-columns: repeat(3, 1fr); }
  .main-layout { flex-direction: column; }
  .subject-panel { width: 100%; position: static; }
}
@media (max-width: 640px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .answer-row { flex-direction: column; }
  .toolbar-card { flex-direction: column; align-items: flex-start; }
}
</style>
