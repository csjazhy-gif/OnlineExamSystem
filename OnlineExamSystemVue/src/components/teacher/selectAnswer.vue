<!-- 题库管理 - 若依风格 -->
<template>
  <div class="ruoyi-container">
    <!-- 查询表单 -->
    <div class="ruoyi-card search-card">
      <el-form :inline="true" :model="queryParams" class="search-form" ref="queryForm">
        <el-form-item label="试卷名称" prop="subject">
          <el-input
            v-model="queryParams.subject"
            placeholder="请输入试卷名称"
            clearable
            style="width: 200px"
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="所属章节" prop="section">
          <el-input
            v-model="queryParams.section"
            placeholder="请输入所属章节"
            clearable
            style="width: 200px"
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="题目内容" prop="question">
          <el-input
            v-model="queryParams.question"
            placeholder="请输入题目内容关键词"
            clearable
            style="width: 200px"
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="题目类型" prop="type">
          <el-select v-model="queryParams.type" placeholder="请选择题目类型" clearable style="width: 200px">
            <el-option label="选择题" value="1" />
            <el-option label="填空题" value="2" />
            <el-option label="判断题" value="3" />
            <el-option label="主观题" value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度等级" prop="level">
          <el-select v-model="queryParams.level" placeholder="请选择难度等级" clearable style="width: 200px">
            <el-option label="简单 (1)" value="1" />
            <el-option label="较易 (2)" value="2" />
            <el-option label="中等 (3)" value="3" />
            <el-option label="较难 (4)" value="4" />
            <el-option label="困难 (5)" value="5" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleQuery">搜索</el-button>
          <el-button icon="el-icon-refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 操作按钮 -->
    <div class="ruoyi-card toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button
            type="primary"
            icon="el-icon-plus"
            class="bold-text"
            @click="handleAdd"
          >新增题目</el-button>
          <el-button
            type="danger"
            icon="el-icon-delete"
            class="bold-text"
            @click="toggleBatchMode"
          >{{ isBatchMode ? '确认删除' : '批量删除' }}</el-button>
          <el-button
            v-if="isBatchMode"
            icon="el-icon-close"
            @click="isBatchMode = false"
          >取消</el-button>
        </div>
        <div class="toolbar-right">
          <el-tooltip content="刷新" placement="top">
            <el-button size="mini" circle icon="el-icon-refresh" @click="getList"></el-button>
          </el-tooltip>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="ruoyi-card table-card">
      <el-table 
        :key="isBatchMode"
        :data="pagination.records" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
        class="ruoyi-table">
        <el-table-column v-if="isBatchMode" key="selection" type="selection" width="50" align="center" />
        <el-table-column key="questionId" prop="questionId" label="题目ID" width="100" align="center" class-name="nowrap-column" />
        <el-table-column key="subject" prop="subject" label="试卷名称" width="180" align="center" />
        <el-table-column key="question" prop="question" label="题目信息" min-width="400" align="left" class-name="question-column" />
        <el-table-column key="section" prop="section" label="所属章节" width="180" align="center" />
        <el-table-column key="type" prop="type" label="题目类型" width="120" align="center">
          <template slot-scope="scope">
            <el-tag :type="getTypeTagType(scope.row.type)" size="mini">
              {{ getTypeName(scope.row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column key="score" prop="score" label="试题分数" width="110" align="center">
          <template slot-scope="scope">
            <el-tag size="mini" type="warning">{{ scope.row.score }}分</el-tag>
          </template>
        </el-table-column>
        <el-table-column key="level" prop="level" label="难度等级" width="140" align="center">
          <template slot-scope="scope">
            <el-tag :type="getLevelTagType(scope.row.level)" size="mini">
              {{ getLevelName(scope.row.level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column key="operate" label="操作" align="center" width="160" class-name="small-padding fixed-width">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="text"
              icon="el-icon-edit"
              @click="toEdit(scope.row.type, scope.row.questionId)"
            >编辑</el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-delete"
              @click="deleteById(scope.row)"
              style="color: #f56c6c"
            >删除</el-button>
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
      // 选中数组
      ids: [],
      // 非单个禁用
      single: true,
      // 非多个禁用
      multiple: true,
      // 批量删除模式
      isBatchMode: false,
      // 查询参数
      queryParams: {
        subject: "",
        section: "",
        question: "",
        type: null,
        level: null
      },
      pagination: {
        //分页后的题目信息
        current: 1, //当前页
        total: 0, //记录条数
        size: 10, //每页条数
        records: []
      }
    };
  },
  created() {
    this.getAnswerInfo();
  },
  methods: {
    /** 查询题目列表 */
    getList() {
      this.loading = true;
      this.getAnswerInfo();
    },
    /** 搜索按钮操作 */
    handleQuery() {
      this.pagination.current = 1;
      this.getAnswerInfo();
    },
    /** 重置按钮操作 */
    resetQuery() {
      this.$refs.queryForm.resetFields();
      this.handleQuery();
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.$router.push({path: '/addAnswer'});
    },
    /** 多选框选中数据 */
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.questionId);
      this.single = selection.length !== 1;
      this.multiple = !selection.length;
    },
    /** 切换批量模式 */
    toggleBatchMode() {
      if (!this.isBatchMode) {
        this.isBatchMode = true;
      } else {
        if (this.ids.length === 0) {
          this.$message.warning("请先选择要删除的题目");
          return;
        }
        this.handleDelete();
      }
    },
    /** 批量删除操作 */
    handleDelete() {
      const questionIds = this.ids;
      this.$confirm('是否确认删除选中的题目吗？', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 批量删除逻辑
        this.$message.success("删除成功");
        this.isBatchMode = false;
        this.getList();
      });
    },
    /** 题目类型标签类型 */
    getTypeTagType(type) {
      const typeMap = {
        '1': '',          // 选择题 - 默认蓝色
        '2': 'success',   // 填空题 - 绿色
        '3': 'warning',   // 判断题 - 橙色
        '4': 'danger'      // 主观题 - 红色
      };
      return typeMap[type] || 'info';
    },
    /** 题目类型名称 */
    getTypeName(type) {
      const typeMap = {
        '1': '选择题',
        '2': '填空题',
        '3': '判断题',
        '4': '主观题'
      };
      return typeMap[type] || '未知类型';
    },
    /** 难度等级标签类型 */
    getLevelTagType(level) {
      const levelMap = {
        '1': 'success',   // 简单 - 绿色
        '2': 'info',      // 较易 - 蓝色/浅灰
        '3': 'warning',   // 中等 - 橙色
        '4': 'danger',    // 较难 - 红色
        '5': 'danger'     // 困难 - 深红
      };
      return levelMap[level] || 'info';
    },
    /** 难度等级名称 */
    getLevelName(level) {
      const levelMap = {
        '1': '简单',
        '2': '较易',
        '3': '中等',
        '4': '较难',
        '5': '困难'
      };
      return levelMap[level] || '未知';
    },
    toEdit(type, id) { 
      // 前往编辑题目
      this.$router.push({path:'/editAnswerChildren',query: {type: type, questionId: id}})
    },
    deleteById(row) {
      this.$confirm(`确定删除题目"${row.question.substring(0, 30)}..."吗？删除后无法恢复!`, "警告", {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 删除题目逻辑
        this.$message.success("删除成功");
        this.getAnswerInfo();
      }).catch(() => {
        this.$message.info("已取消删除");
      });
    },
    getAnswerInfo(size, current) {
      //分页查询所有题目信息
      this.loading = true;
      if(typeof size === 'number' && !isNaN(size)) {
        this.pagination.size = size;
      }
      if(typeof current === 'number' && !isNaN(current)) {
        this.pagination.current = current;
      }
      
      var subject = this.queryParams.subject.trim() === "" ? "@" : this.queryParams.subject;
      var section = this.queryParams.section.trim() === "" ? "@" : this.queryParams.section;
      var question = this.queryParams.question.trim() === "" ? "@" : this.queryParams.question;
      var type = (this.queryParams.type === null || this.queryParams.type === "") ? "@" : this.queryParams.type;
      var level = (this.queryParams.level === null || this.queryParams.level === "") ? "@" : this.queryParams.level;
      
      this.$axios(
        `/api/answers/${this.pagination.current}/${this.pagination.size}/${subject}/${section}/${question}/${type}/${level}`
      )
        .then(res => {
          this.pagination = res.data.data;
          this.loading = false;
        })
        .catch(error => {
          this.loading = false;
        });
    },
    //改变当前记录条数
    handleSizeChange(val) {
      this.pagination.size = val;
      this.getAnswerInfo();
    },
    //改变当前页码，重新发送请求
    handleCurrentChange(val) {
      this.pagination.current = val;
      this.getAnswerInfo();
    }
  }
};
</script>
<style lang="less" scoped>
/* 若依风格题库管理页面样式 */
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

.search-form .el-form-item {
  margin-bottom: 16px;
  margin-right: 16px;
}

.search-form .el-form-item__label {
  font-weight: 500;
  color: #606266;
}

/* 工具栏样式 */
.toolbar-card {
  padding: 16px 20px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
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

/* 操作按钮样式 */
.ruoyi-table .el-button--text {
  padding: 5px 0;
  margin: 0 8px;
}

/* 强制单行显示的列 */
.nowrap-column {
  white-space: nowrap !important;
}

/* 增强主按钮文字视觉 */
.bold-text {
  font-weight: bold !important;
  letter-spacing: 0.5px;
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
  .toolbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
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
  
  .search-card,
  .toolbar-card {
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

/* 题目内容列样式优化 */
.ruoyi-table .question-column {
  text-align: left !important;
  padding-left: 16px;
}
.ruoyi-table th .question-column {
  text-align: center !important;
  padding-left: 0;
}
</style>
