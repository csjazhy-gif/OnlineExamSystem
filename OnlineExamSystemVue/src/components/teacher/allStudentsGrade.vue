<!-- 所有学生成绩管理 - 若依风格 -->
<template>
  <div class="ruoyi-page-wrapper">
  <div class="ruoyi-container">
    <!-- 查询表单 -->
    <div class="ruoyi-card search-card">
      <el-form :model="condition" ref="queryForm" label-width="80px" size="small">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="学生姓名" prop="name">
              <el-input v-model="condition.name" placeholder="请输入学生姓名" clearable @keyup.enter.native="handleQuery"/>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="所属学院" prop="institute">
              <el-input v-model="condition.institute" placeholder="请输入所属学院" clearable @keyup.enter.native="handleQuery"/>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="所属专业" prop="major">
              <el-input v-model="condition.major" placeholder="请输入所属专业" clearable @keyup.enter.native="handleQuery"/>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="年级" prop="grade">
              <el-input v-model="condition.grade" placeholder="请输入年级" clearable @keyup.enter.native="handleQuery"/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="班级" prop="clazz">
              <el-input v-model="condition.clazz" placeholder="请输入班级" clearable @keyup.enter.native="handleQuery"/>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="联系方式" prop="tel">
              <el-input v-model="condition.tel" placeholder="请输入联系方式" clearable @keyup.enter.native="handleQuery"/>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label=" " class="search-buttons">
              <el-button class="btn-search" icon="el-icon-search" @click="handleQuery">搜索</el-button>
              <el-button class="btn-reset" icon="el-icon-refresh" @click="resetQuery">重置</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <div class="ruoyi-card table-card">
      <!-- 卡片头部 -->
      <div style="padding:16px 20px;border-bottom:1px solid #f0f0f0;display:flex;justify-content:space-between;align-items:center;">
        <span style="font-weight:600;color:#303133;"><i class="el-icon-user"></i> 学生列表</span>
        <el-button type="warning" icon="el-icon-data-analysis" size="small" @click="statsDialogVisible = true">
          考试统计分析
        </el-button>
      </div>
      <el-table 
        :data="pagination.records" 
        v-loading="loading"
        class="ruoyi-table">
        <el-table-column prop="studentName" label="学生姓名" width="120" align="center" show-overflow-tooltip />
        <el-table-column prop="institute" label="所属学院" min-width="150" align="center" show-overflow-tooltip />
        <el-table-column prop="major" label="所属专业" min-width="150" align="center" show-overflow-tooltip />
        <el-table-column prop="grade" label="年级" width="100" align="center" />
        <el-table-column prop="clazz" label="班级" width="100" align="center" />
        <el-table-column prop="sex" label="性别" width="80" align="center">
          <template slot-scope="scope">
            <el-tag :type="scope.row.sex === '男' ? '' : 'success'" size="mini">
              {{ scope.row.sex }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tel" label="联系方式" width="130" align="center" />
        <el-table-column label="操作" align="center" width="150">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="text"
              icon="el-icon-view"
              @click="checkGrade(scope.row.studentId)"
            >查看成绩</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        @current-change="handleCurrentChange"
        :current-page="pagination.current"
        :page-size="pagination.size"
        layout="total, prev, pager, next, jumper"
        :total="pagination.total"
        class="ruoyi-pagination">
      </el-pagination>
    </div>
  </div>

  <!-- 统计分析对话框 -->
  <el-dialog title="📊 考试成绩统计分析" :visible.sync="statsDialogVisible" width="820px" @open="initChart">
    <div style="margin-bottom:16px;display:flex;gap:12px;align-items:center;">
      <el-input v-model="statsExamCode" placeholder="请输入考试编号" size="small" style="width:200px;"
        @keyup.enter.native="loadStats"/>
      <el-button type="primary" size="small" icon="el-icon-search" :loading="statsLoading" @click="loadStats">查询</el-button>
    </div>
    <div v-if="stats" style="display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap;">
      <div class="stat-box" v-for="item in statsCards" :key="item.label">
        <div class="stat-val" :style="{color: item.color}">{{ item.val }}</div>
        <div class="stat-lbl">{{ item.label }}</div>
      </div>
    </div>
    <div v-if="stats" ref="statsChart" style="width:100%;height:280px;"></div>
    <el-empty v-else description="请输入考试编号查询成绩分布" :image-size="80"></el-empty>
    <div slot="footer"><el-button @click="statsDialogVisible = false">关闭</el-button></div>
  </el-dialog>
  </div><!-- end ruoyi-page-wrapper -->
</template>

<script>
export default {
  data() {
    return {
      // 遁罩层
      loading: true,
      pagination: {
        current: 1,
        total: 0,
        size: 10,
        records: []
      },
      condition: { name: "", tel: "", grade: "", clazz: "", major: "", institute: "" },
      // 统计分析
      statsDialogVisible: false,
      statsExamCode: '',
      statsLoading: false,
      stats: null,
      statsChart: null
    };
  },
  created() {
    this.getStudentGrade();
  },
  methods: {
    /** 查询学生列表 */
    getList() {
      this.loading = true;
      this.getStudentGrade();
    },
    getStudentGrade() {
      // 根据条件获取学生成绩
      this.loading = true;
      var name = (this.condition.name.trim() == "" ? "@" : this.condition.name);
      var grade = (this.condition.grade.trim() == "" ? "@" : this.condition.grade);
      var tel = (this.condition.tel.trim() == "" ? "@" : this.condition.tel);
      var institute = (this.condition.institute.trim() == "" ? "@" : this.condition.institute);
      var major = (this.condition.major.trim() == "" ? "@" : this.condition.major);
      var clazz = (this.condition.clazz.trim() == "" ? "@" : this.condition.clazz);
      this.$axios(`/api/students/${this.pagination.current}/${this.pagination.size}/${name}/${grade}/${tel}/${institute}/${major}/${clazz}`).then(res => {
        this.pagination = res.data.data;
        this.loading = false;
      }).catch(error => {
        this.loading = false;
      });
    },
    /** 搜索按钮操作 */
    handleQuery() {
      this.pagination.current = 1;
      this.getStudentGrade();
    },
    /** 重置按钮操作 */
    resetQuery() {
      this.$refs.queryForm.resetFields();
      this.handleQuery();
    },
    //改变当前记录条数
    handleSizeChange(val) {
      this.pagination.size = val;
      this.getStudentGrade();
    },
    //改变当前页码，重新发送请求
    handleCurrentChange(val) {
      this.pagination.current = val;
      this.getStudentGrade();
    },
    checkGrade(studentId) {
      this.$router.push({ path: "/grade", query: { studentId: studentId } });
    },
    // -------- 统计分析 --------
    async loadStats() {
      if (!this.statsExamCode) { this.$message.warning('请输入考试编号'); return }
      this.statsLoading = true
      try {
        const res = await this.$axios.get(`/api/scores/${this.statsExamCode}`)
        const scores = (res.data.data || []).filter(s => s.etScore !== -1 && s.etScore !== '-1')
        if (!scores.length) { this.$message.warning('该考试暂无有效成绩'); this.stats = null; return }
        const vals = scores.map(s => parseFloat(s.etScore)).filter(v => !isNaN(v))
        const avg = (vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(1)
        const max = Math.max(...vals)
        const min = Math.min(...vals)
        const pass = vals.filter(v => v >= 60).length
        // 分段分布: [0-59],[60-69],[70-79],[80-89],[90-100]
        const buckets = [0, 0, 0, 0, 0]
        vals.forEach(v => {
          if (v < 60) buckets[0]++
          else if (v < 70) buckets[1]++
          else if (v < 80) buckets[2]++
          else if (v < 90) buckets[3]++
          else buckets[4]++
        })
        this.stats = { vals, avg, max, min, pass, total: vals.length, buckets }
        this.$nextTick(() => this.renderChart())
      } catch (e) {
        this.$message.error('查询失败')
      } finally {
        this.statsLoading = false
      }
    },
    initChart() {
      // 对话框打开时重置
      this.stats = null
    },
    renderChart() {
      const echarts = require('echarts')
      if (this.statsChart) this.statsChart.dispose()
      const dom = this.$refs.statsChart
      if (!dom) return
      this.statsChart = echarts.init(dom)
      this.statsChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: ['<60', '60-69', '70-79', '80-89', '90-100'],
                 axisLabel: { color: '#606266' } },
        yAxis: { type: 'value', name: '人数', minInterval: 1 },
        series: [{
          name: '人数', type: 'bar', data: this.stats.buckets,
          itemStyle: {
            color: (params) => ['#F56C6C','#E6A23C','#409EFF','#67C23A','#2A9D8F'][params.dataIndex]
          },
          label: { show: true, position: 'top' }
        }]
      })
    }
  },
  computed: {
    statsCards() {
      if (!this.stats) return []
      const r = (this.stats.pass / this.stats.total * 100).toFixed(1)
      return [
        { label: '参考人数', val: this.stats.total, color: '#409EFF' },
        { label: '平均分', val: this.stats.avg, color: '#67C23A' },
        { label: '最高分', val: this.stats.max, color: '#2A9D8F' },
        { label: '最低分', val: this.stats.min, color: '#E6A23C' },
        { label: '及格率', val: r + '%', color: r >= 60 ? '#67C23A' : '#F56C6C' },
      ]
    }
  }
};
</script>
<style lang="less" scoped>
/* 若依风格学生成绩管理页面样式 */
.ruoyi-container {
  padding: 20px;
  background-color: #f0f2f5;
}

.ruoyi-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  overflow: hidden;
}

/* 搜索表单样式 */
.search-card {
  padding: 20px;
}

.search-card .el-form-item {
  margin-bottom: 16px;
  margin-right: 16px;
}

.search-card .el-form-item__label {
  font-weight: 500;
  color: #606266;
}

.search-buttons {
  display: flex;
  align-items: center;
}

.search-buttons.el-form-item {
  margin-bottom: 16px;
}

/* 让按钮行与输入框对齐 */
/deep/ .search-buttons .el-form-item__content {
  display: flex;
  align-items: center;
  line-height: 34px;
  gap: 10px;
}

/deep/ .search-buttons .el-form-item__label {
  line-height: 34px;
}

/* 表格样式 */
.table-card {
  padding: 0;
}

.ruoyi-table {
  width: 100%;
  
  .el-table__header-wrapper {
    background-color: #fafafa;
  }
  
  .el-table__header th {
    background-color: #fafafa;
    color: #303133;
    font-weight: 500;
    border-bottom: 1px solid #ebeef5;
  }
  
  .el-table__row:hover > td {
    background-color: #f5f7fa;
  }
  
  .el-table__body tr td {
    border-bottom: 1px solid #ebeef5;
  }
}

/* 标签样式优化 */
.el-tag {
  border: none;
  border-radius: 12px;
  font-size: 12px;
  padding: 2px 8px;
}

/* 搜索重置按钮样式 */
.btn-search {
  height: 34px;
  padding: 0 20px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 1px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.25s ease;
  cursor: pointer;
}
.btn-search:hover, .btn-search:focus {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(102, 126, 234, 0.55);
  background: linear-gradient(135deg, #7a8ef0 0%, #8a5ab5 100%);
  color: #fff;
}
.btn-search:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.35);
}

.btn-reset {
  height: 34px;
  padding: 0 20px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 1px;
  border: 1.5px solid #d1d5db;
  border-radius: 8px;
  background: #fff;
  color: #6b7280;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
  transition: all 0.25s ease;
  cursor: pointer;
}
.btn-reset:hover, .btn-reset:focus {
  transform: translateY(-2px);
  border-color: #667eea;
  color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
  background: #f5f3ff;
}
.btn-reset:active {
  transform: translateY(0);
}

/* 操作按钮样式 */

/* 分页样式 */
.ruoyi-pagination {
  padding: 20px;
  background-color: #fff;
  text-align: center;
  border-top: 1px solid #ebeef5;
}

.el-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.el-pagination button:disabled {
  color: #c0c4cc;
  cursor: not-allowed;
}

.el-pagination .el-pager li.active {
  color: #409eff;
  background-color: #ecf5ff;
  border-color: #b3d8ff;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .search-form {
    flex-direction: column;
  }
  
  .search-form .el-form-item {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .ruoyi-container {
    padding: 10px;
  }
  
  .ruoyi-card {
    margin-bottom: 10px;
  }
  
  .search-card {
    padding: 16px;
  }
  
  .el-table {
    font-size: 12px;
  }
  
  .ruoyi-pagination {
    padding: 16px;
  }
}

/* 加载状态 */
.el-loading-mask {
  background-color: rgba(255, 255, 255, 0.9);
}

/* 统计卡片 */
.stat-box {
  flex: 1;
  min-width: 110px;
  background: linear-gradient(135deg, #f8faff, #eef4ff);
  border-radius: 10px;
  padding: 14px 12px;
  text-align: center;
  border: 1px solid #dce8ff;
}
.stat-val {
  font-size: 26px;
  font-weight: 700;
  line-height: 1.2;
}
.stat-lbl {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
