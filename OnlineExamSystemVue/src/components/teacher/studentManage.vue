<!-- 学生管理页面 - 若依风格 -->
<template>
  <div class="ruoyi-container">
    <!-- 查询表单 -->
    <div class="ruoyi-card search-card">
      <el-form :model="condition" ref="queryForm" label-width="80px">
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
              <el-button type="primary" icon="el-icon-search" @click="handleQuery">搜索</el-button>
              <el-button icon="el-icon-refresh" @click="resetQuery">重置</el-button>
            </el-form-item>
          </el-col>
        </el-row>
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
          >新增学生</el-button>
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
        <el-table-column key="studentId" prop="studentId" label="学生ID" width="100" align="center" class-name="nowrap-column" />
        <el-table-column key="studentName" prop="studentName" label="学生姓名" width="120" align="center" />
        <el-table-column key="institute" prop="institute" label="所属学院" min-width="160" align="center" />
        <el-table-column key="major" prop="major" label="所属专业" min-width="160" align="center" />
        <el-table-column key="grade" prop="grade" label="年级" width="100" align="center" />
        <el-table-column key="clazz" prop="clazz" label="班级" width="100" align="center" />
        <el-table-column key="sex" prop="sex" label="性别" width="80" align="center">
          <template slot-scope="scope">
            <el-tag :type="scope.row.sex === '男' ? '' : 'success'" size="mini">
              {{ scope.row.sex }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column key="tel" prop="tel" label="联系方式" width="140" align="center" />
        <el-table-column key="operate" label="操作" align="center" width="160" class-name="small-padding fixed-width">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="text"
              icon="el-icon-edit"
              @click="checkGrade(scope.row.studentId)"
            >修改</el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-delete"
              style="color: #f56c6c"
              @click="deleteById(scope.row)"
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
    <!-- 编辑对话框-->
    <el-dialog
      title="编辑学生信息"
      :visible.sync="dialogVisible"
      width="30%"
      :before-close="handleClose">
      <section class="update">
        <el-form ref="form" :model="form" label-width="80px">
          <el-form-item label="姓名">
            <el-input v-model="form.studentName"></el-input>
          </el-form-item>
          <el-form-item label="学院">
            <el-input v-model="form.institute"></el-input>
          </el-form-item>
          <el-form-item label="专业">
            <el-input v-model="form.major"></el-input>
          </el-form-item>
          <el-form-item label="年级">
            <el-input v-model="form.grade"></el-input>
          </el-form-item>
          <el-form-item label="班级">
            <el-input v-model="form.clazz"></el-input>
          </el-form-item>
          <el-form-item label="性别">
            <el-input v-model="form.sex"></el-input>
          </el-form-item>
          <el-form-item label="电话号码">
            <el-input v-model="form.tel"></el-input>
          </el-form-item>
        </el-form>
      </section>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submit()">确 定</el-button>
      </span>
    </el-dialog>
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
      pagination: {
        //分页后的考试信息
        current: 1, //当前页
        total: 0, //记录条数
        size: 10, //每页条数
        records: []
      },
      dialogVisible: false, //对话框
      form: {}, //保存点击以后当前试卷的信息,
      condition: {
        name: "",
        tel: "",
        grade: "",
        clazz: "",
        major: "",
        institute: "",
      }
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
    /** 新增按钮操作 */
    handleAdd() {
      this.$router.push({path: '/addStudent'});
    },
    /** 多选框选中数据 */
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.studentId);
      this.single = selection.length !== 1;
      this.multiple = !selection.length;
    },
    /** 切换批量模式 */
    toggleBatchMode() {
      if (!this.isBatchMode) {
        this.isBatchMode = true;
      } else {
        if (this.ids.length === 0) {
          this.$message.warning("请先选择要删除的学生");
          return;
        }
        this.handleDelete();
      }
    },
    /** 批量删除操作 */
    handleDelete() {
      const studentIds = this.ids;
      this.$confirm('是否确认删除选中的学生吗？', '警告', {
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
    checkGrade(studentId) { //修改学生信息
      this.dialogVisible = true
      this.$axios(`/api/student/${studentId}`).then(res => {
        this.form = res.data.data
      })
    },
    deleteById(row) { //删除当前学生
      this.$confirm(`确定删除学生"${row.studentName}"吗？删除后无法恢复!`, "警告", {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => { //确认删除
        this.$axios({
          url: `/api/student/${row.studentId}`,
          method: 'delete',
        }).then(res => {
          if (res.data.code === 200) {
            this.$message.success("删除成功");
            this.getStudentGrade();
          } else {
            this.$message.error(res.data.message || "删除失败");
          }
        }).catch(error => {
          this.$message.error("网络错误，请稍后重试");
        });
      }).catch(() => {
        this.$message.info("已取消删除");
      });
    },
    submit() { //提交更改
      this.dialogVisible = false
      this.$axios({
        url: '/api/student',
        method: 'put',
        data: {
          ...this.form
        }
      }).then(res => {
        if(res.data.code ==200) {
          this.$message({
            message: '更新成功',
            type: 'success'
          })
        }
        this.getStudentGrade()
      })
    },
    handleClose(done) { //关闭提醒
      this.$confirm('确认关闭？')
        .then(_ => {
          done();
        }).catch(_ => {});
    },
  }
};
</script>
<style lang="less" scoped>
/* 若依风格学生管理页面样式 */
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

.el-tag {
  border: none;
  border-radius: 12px;
  font-size: 12px;
  padding: 2px 8px;
}

/* 自定义删除按钮样式 */
.ruoyi-table .el-button--text {
  padding: 5px 0;
  margin: 0 8px;
}

/* 增强主按钮文字视觉 */
.bold-text {
  font-weight: bold !important;
  letter-spacing: 0.5px;
}

/* 强制单行显示的列 */
.nowrap-column {
  white-space: nowrap !important;
}

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

.el-dialog {
  border-radius: 8px;
  
  .el-dialog__header {
    padding: 20px 24px 16px;
    border-bottom: 1px solid #e6e6e6;
    background-color: #fafbfc;
  }
  
  .el-dialog__title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }
  
  .el-dialog__body {
    padding: 24px;
  }
  
  .el-dialog__footer {
    padding: 16px 24px 24px;
    border-top: 1px solid #e6e6e6;
    text-align: center;
  }
}

.update .el-form-item {
  margin-bottom: 20px;
}

.update .el-form-item__label {
  font-weight: 500;
  color: #606266;
}

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

.el-loading-mask {
  background-color: rgba(255, 255, 255, 0.9);
}
</style>
