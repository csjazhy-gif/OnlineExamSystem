<!-- 新增题目 - 选择试卷 - 若依风格 -->
<template>
  <div class="ruoyi-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon">
          <i class="el-icon-document-add"></i>
        </div>
        <div class="header-text">
          <h2 class="page-title">新增题目</h2>
          <p class="page-subtitle">选择一份试卷，进入题目录入界面</p>
        </div>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="ruoyi-card search-card">
      <el-form :inline="true" :model="queryParams" class="search-form" ref="queryForm">
        <el-form-item label="试卷名称" prop="source">
          <el-input
            v-model="queryParams.source"
            placeholder="请输入试卷名称"
            clearable
            style="width: 200px"
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="所属学院" prop="institute">
          <el-input
            v-model="queryParams.institute"
            placeholder="请输入所属学院"
            clearable
            style="width: 200px"
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="试卷类型" prop="type">
          <el-select v-model="queryParams.type" placeholder="请选择试卷类型" clearable style="width: 200px">
            <el-option label="期末考试" value="期末考试" />
            <el-option label="期中考试" value="期中考试" />
            <el-option label="随堂测试" value="随堂测试" />
            <el-option label="课程作业" value="课程作业" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleQuery">搜索</el-button>
          <el-button icon="el-icon-refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 工具栏 -->
    <div class="ruoyi-card toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <span class="toolbar-tip">
            <i class="el-icon-info"></i>
            请选择一份试卷，点击「录入题目」进入题目添加界面
          </span>
        </div>
        <div class="toolbar-right">
          <el-tooltip content="刷新" placement="top">
            <el-button size="mini" circle icon="el-icon-refresh" @click="getExamInfo"></el-button>
          </el-tooltip>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="ruoyi-card table-card">
      <el-table
        :data="filteredRecords"
        v-loading="loading"
        class="ruoyi-table">
        <el-table-column prop="source" label="试卷名称" width="180" align="center" show-overflow-tooltip />
        <el-table-column prop="description" label="介绍" min-width="200" align="center" show-overflow-tooltip />
        <el-table-column prop="institute" label="所属学院" width="120" align="center" />
        <el-table-column prop="major" label="所属专业" width="150" align="center" show-overflow-tooltip />
        <el-table-column prop="grade" label="年级" width="80" align="center" />
        <el-table-column prop="examDate" label="考试日期" width="120" align="center">
          <template slot-scope="scope">
            {{ scope.row.examDate ? scope.row.examDate.substr(0, 10) : '' }}
          </template>
        </el-table-column>
        <el-table-column prop="totalTime" label="持续时间" width="100" align="center">
          <template slot-scope="scope">
            <el-tag size="mini" type="info">{{ scope.row.totalTime }}分钟</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="试卷类型" width="100" align="center">
          <template slot-scope="scope">
            <el-tag :type="getTypeTagType(scope.row.type)" size="mini">
              {{ scope.row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="140" class-name="small-padding fixed-width">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="text"
              icon="el-icon-edit-outline"
              @click="add(scope.row.paperId, scope.row.source)"
              class="action-btn"
            >录入题目</el-button>
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
</template>

<script>
export default {
  data() {
    return {
      // 遮罩层
      loading: true,
      // 查询参数
      queryParams: {
        source: '',
        institute: '',
        type: ''
      },
      // 分页数据
      pagination: {
        current: 1,
        total: 0,
        size: 10,
        records: []
      }
    }
  },
  computed: {
    /**
     * 根据搜索条件过滤试卷列表（前端过滤）
     * @return {Array} 过滤后的记录数组
     */
    filteredRecords() {
      if (!this.pagination.records) return [];
      return this.pagination.records.filter(item => {
        var matchSource = !this.queryParams.source || 
          (item.source && item.source.indexOf(this.queryParams.source) > -1);
        var matchInstitute = !this.queryParams.institute || 
          (item.institute && item.institute.indexOf(this.queryParams.institute) > -1);
        var matchType = !this.queryParams.type || item.type === this.queryParams.type;
        return matchSource && matchInstitute && matchType;
      });
    }
  },
  created() {
    this.getExamInfo()
  },
  methods: {
    /**
     * 分页查询所有试卷信息
     */
    getExamInfo() {
      this.loading = true;
      this.$axios(`/api/exams/${this.pagination.current}/${this.pagination.size}`).then(res => {
        this.pagination = res.data.data;
        this.loading = false;
      }).catch(error => {
        this.loading = false;
      })
    },
    /**
     * 搜索按钮操作
     */
    handleQuery() {
      this.pagination.current = 1;
      this.getExamInfo();
    },
    /**
     * 重置搜索条件
     */
    resetQuery() {
      this.$refs.queryForm.resetFields();
      this.handleQuery();
    },
    /**
     * 改变当前页码，重新发送请求
     * @param {Number} val 新页码
     */
    handleCurrentChange(val) {
      this.pagination.current = val;
      this.getExamInfo();
    },
    /**
     * 跳转到题目录入页面
     * @param {Number} paperId 试卷ID
     * @param {String} source 试卷名称（科目）
     */
    add(paperId, source) {
      this.$router.push({ path: '/addAnswerChildren', query: { paperId: paperId, subject: source } })
    },
    /**
     * 获取试卷类型对应的标签颜色
     * @param {String} type 试卷类型
     * @return {String} 标签类型
     */
    getTypeTagType(type) {
      var typeMap = {
        '期末考试': 'danger',
        '期中考试': 'warning',
        '随堂测试': '',
        '课程作业': 'info'
      };
      return typeMap[type] || 'info';
    }
  }
};
</script>
<style lang="less" scoped>
/* 若依风格 - 新增题目页面样式 */
.ruoyi-container {
  padding: 20px;
  background-color: #f0f2f5;
}

/* 页面标题 */
.page-header {
  margin-bottom: 20px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.3);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 52px;
  height: 52px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  color: #fff;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  margin: 0;
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

.search-form .el-form-item {
  margin-bottom: 16px;
  margin-right: 16px;
}

/* 工具栏样式 */
.toolbar-card {
  padding: 14px 20px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.toolbar-tip {
  font-size: 13px;
  color: #909399;
  
  i {
    margin-right: 4px;
    color: #409eff;
  }
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 表格样式 */
.table-card {
  padding: 0;
}

.ruoyi-table {
  width: 100%;
}

/* 操作按钮样式 */
.action-btn {
  font-weight: 500;
  color: #409eff !important;
  
  &:hover {
    color: #66b1ff !important;
  }
}

/* 标签样式 */
.el-tag {
  border: none;
  border-radius: 12px;
  font-size: 12px;
  padding: 2px 8px;
}

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

/* 响应式设计 */
@media (max-width: 768px) {
  .ruoyi-container {
    padding: 10px;
  }
  
  .page-header {
    padding: 16px;
  }
  
  .header-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  
  .page-title {
    font-size: 18px;
  }
  
  .search-card {
    padding: 16px;
  }
}

.el-loading-mask {
  background-color: rgba(255, 255, 255, 0.9);
}
</style>
