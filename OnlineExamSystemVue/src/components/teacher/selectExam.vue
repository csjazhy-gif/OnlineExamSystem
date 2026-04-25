<!-- 考试管理 - 若依风格 -->
<template>
  <div class="ruoyi-container">
    <!-- 查询表单 -->
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
        <el-form-item label="所属专业" prop="major">
          <el-input
            v-model="queryParams.major"
            placeholder="请输入所属专业"
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

    <!-- 操作按钮 -->
    <div class="ruoyi-card toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button
            type="primary"
            plain
            icon="el-icon-plus"
            @click="handleAdd"
          >新增考试</el-button>
          <el-button
            type="danger"
            plain
            icon="el-icon-delete"
            :disabled="multiple"
            @click="handleDelete"
          >批量删除</el-button>
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
        :data="filteredRecords" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
        class="ruoyi-table">
        <el-table-column type="selection" width="50" align="center" />
        <el-table-column prop="examCode" label="考试编号" width="120" align="center" />
        <el-table-column prop="source" label="试卷名称" width="150" align="center" show-overflow-tooltip />
        <el-table-column prop="description" label="介绍" width="150" align="center" show-overflow-tooltip />
        <el-table-column prop="institute" label="所属学院" width="120" align="center" />
        <el-table-column prop="major" label="所属专业" width="150" align="center" />
        <el-table-column prop="grade" label="年级" width="80" align="center" />
        <el-table-column prop="examDate" label="考试日期" width="120" align="center">
          <template slot-scope="scope">
            {{ scope.row.examDate.substr(0, 10) }}
          </template>
        </el-table-column>
        <el-table-column prop="totalTime" label="持续时间" width="100" align="center">
          <template slot-scope="scope">
            <el-tag size="mini" type="info">{{ scope.row.totalTime }}分钟</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="totalScore" label="总分" width="80" align="center">
          <template slot-scope="scope">
            <el-tag size="mini" type="warning">{{ scope.row.totalScore }}分</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="试卷类型" width="100" align="center">
          <template slot-scope="scope">
            <el-tag :type="getTypeTagType(scope.row.type)" size="mini">
              {{ scope.row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="200" class-name="small-padding fixed-width">
        <template slot-scope="scope">
            <el-button
              size="mini"
              type="text"
              icon="el-icon-view"
              @click="getExamDetail(scope.row.examCode, scope.row.paperId)"
            >试题详情</el-button>
          <el-button
              size="mini"
              type="text"
              icon="el-icon-edit"
            @click="edit(scope.row.examCode)"
            >编辑</el-button>
          <el-button
              size="mini"
              type="text"
              icon="el-icon-delete"
              class="delete-btn"
              @click="deleteRecord(scope.row)"
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
      title="编辑试卷信息"
      :visible.sync="dialogVisible"
      width="30%"
      :before-close="handleClose"
    >
      <section class="update">
        <el-form ref="form" :model="form" label-width="80px">
          <el-form-item label="试卷名称">
            <el-input v-model="form.source"></el-input>
          </el-form-item>
          <el-form-item label="介绍">
            <el-input v-model="form.description"></el-input>
          </el-form-item>
          <el-form-item label="所属学院">
            <el-input v-model="form.institute"></el-input>
          </el-form-item>
          <el-form-item label="所属专业">
            <el-input v-model="form.major"></el-input>
          </el-form-item>
          <el-form-item label="年级">
            <el-input v-model="form.grade"></el-input>
          </el-form-item>
          <el-form-item label="考试日期">
            <el-col :span="11">
              <el-date-picker
                type="date"
                placeholder="选择日期"
                v-model="form.examDate"
                value-format="yyyy-MM-dd"
                style="width: 100%"
              ></el-date-picker>
            </el-col>
          </el-form-item>
          <el-form-item label="持续时间">
            <el-input v-model="form.totalTime"></el-input>
          </el-form-item>
          <!-- <el-form-item label="总分">
            <el-input v-model="form.totalScore"></el-input>
          </el-form-item> -->
          <el-form-item label="试卷类型">
            <el-select v-model="form.type" placeholder="请选择试卷类型" style="width: 100%">
              <el-option label="期末考试" value="期末考试" />
              <el-option label="期中考试" value="期中考试" />
              <el-option label="随堂测试" value="随堂测试" />
              <el-option label="课程作业" value="课程作业" />
            </el-select>
          </el-form-item>
          <el-form-item label="考生提示">
            <el-input type="textarea" v-model="form.tips"></el-input>
          </el-form-item>
        </el-form>
      </section>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submit()">确 定</el-button>
      </span>
    </el-dialog>

    <!-- 查询试卷对话框 -->
    <el-dialog title="试卷内容" :visible.sync="showExamDetail" width="60%">
      <span>
        <div class="content">
          <el-collapse v-model="activeName">
            <el-collapse-item class="header" name="0">
              <template slot="title">
                <div class="title">
                  <span>{{ examData.source }}</span
                  ><i class="header-icon el-icon-info"></i>
                  <span class="time"
                    >{{ score[0] + score[1] + score[2] }}分 /
                    {{ examData.totalTime }}分钟</span
                  >
                </div>
              </template>
              <el-collapse class="inner">
                <el-collapse-item>
                  <template slot="title">
                    <div class="titlei">
                      选择题 (共{{ topicCount[0] }}题 共计{{ score[0] }}分)
                    </div>
                  </template>
                  <div class="contenti">
                    <ul
                      class="question"
                      v-for="(list, index) in topic[1]"
                      :key="index"
                    >
                      <li>
                        {{ index + 1 }}. {{ list.question }} {{ list.score }}分
                        <a style="color: red" href="#" @click.prevent="deleteQuestion(1, list.questionId)">删除</a>
                      </li>
                    </ul>
                  </div>
                </el-collapse-item>
                <el-collapse-item>
                  <template slot="title">
                    <div class="titlei">
                      填空题 (共{{ topicCount[1] }}题 共计{{ score[1] }}分)
                    </div>
                  </template>
                  <div class="contenti">
                    <ul
                      class="question"
                      v-for="(list, index) in topic[2]"
                      :key="index"
                    >
                      <li>
                        {{ topicCount[0] + index + 1 }}.{{ list.question }}
                        {{ list.score }}分
                        <a style="color: red" href="#" @click.prevent="deleteQuestion(2, list.questionId)">删除</a>
                      </li>
                    </ul>
                  </div>
                </el-collapse-item>
                <el-collapse-item>
                  <template slot="title">
                    <div class="titlei">
                      判断题 (共{{ topicCount[2] }}题 共计{{ score[2] }}分)
                    </div>
                  </template>
                  <div class="contenti">
                    <ul
                      class="question"
                      v-for="(list, index) in topic[3]"
                      :key="index"
                    >
                      <li>
                        {{ topicCount[0] + topicCount[1] + index + 1 }}.
                        {{ list.question }} {{ list.score }}分
                        <a style="color: red" href="#" @click.prevent="deleteQuestion(3, list.questionId)">删除</a>
                      </li>
                    </ul>
                  </div>
                </el-collapse-item>
                <el-collapse-item>
                  <template slot="title">
                    <div class="titlei">
                      主观题 (共{{ topicCount[3] || 0 }}题 共计{{ score[3] || 0 }}分)
                    </div>
                  </template>
                  <div class="contenti">
                    <ul
                      class="question"
                      v-for="(list, index) in topic[4]"
                      :key="index"
                    >
                      <li>
                        {{ (topicCount[0] || 0) + (topicCount[1] || 0) + (topicCount[2] || 0) + index + 1 }}.
                        {{ list.question }} {{ list.score }}分
                        <a style="color: red" href="#" @click.prevent="deleteQuestion(4, list.questionId)">删除</a>
                      </li>
                    </ul>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </el-collapse-item>
          </el-collapse>
        </div>
      </span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="showExamDetail = false">取 消</el-button>
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
      // 查询参数
      queryParams: {
        source: null,
        institute: null,
        major: null,
        type: null
      },
      form: {}, //保存点击以后当前试卷的信息
      pagination: {
        //分页后的考试信息
        current: 1, //当前页
        total: 0, //记录条数
        size: 10, //每页条数
        records: []
      },
      dialogVisible: false,
      showExamDetail: false, //是否展示试卷
      activeName: '0',  //默认打开序号
      topicCount: [],//每种类型题目的总数
      score: [],  //每种类型分数的总数
      examData: { //考试信息
        // source: null,
        // totalScore: null,
      },
      topic: {  //试卷信息

      },
      examDetailCode: "",   // 当前查看试题详情中，考试编码code
      examDetailPaperId: "",    // 当前查看的试题详情中，试卷id
    };
  },
  computed: {
    /**
     * 根据搜索条件过滤试卷列表
     * @return {Array} 过滤后的记录数组
     */
    filteredRecords() {
      if (!this.pagination.records) return [];
      return this.pagination.records.filter(item => {
        var matchSource = !this.queryParams.source || 
          (item.source && item.source.indexOf(this.queryParams.source) > -1);
        var matchInstitute = !this.queryParams.institute ||
          (item.institute && item.institute.indexOf(this.queryParams.institute) > -1);
        var matchMajor = !this.queryParams.major ||
          (item.major && item.major.indexOf(this.queryParams.major) > -1);
        var matchType = !this.queryParams.type || item.type === this.queryParams.type;
        return matchSource && matchInstitute && matchMajor && matchType;
      });
    }
  },
  created() {
    this.getExamInfo();
    
  },
  methods: {
    /** 查询考试列表 */
    getList() {
      this.loading = true;
      this.getExamInfo();
    },
    /** 搜索按钮操作 */
    handleQuery() {
      this.pagination.current = 1;
      this.getExamInfo();
    },
    /** 重置按钮操作 */
    resetQuery() {
      this.$refs.queryForm.resetFields();
      this.handleQuery();
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.$router.push({path: '/addExam'});
    },
    /** 多选框选中数据 */
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.examCode);
      this.single = selection.length !== 1;
      this.multiple = !selection.length;
    },
    /** 批量删除操作 */
    handleDelete() {
      const examCodes = this.ids;
      this.$confirm('是否确认删除考试编号为"' + examCodes + '"的数据项？', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 批量删除逻辑
        this.$message.success("删除成功");
        this.getList();
      });
    },
    /** 试卷类型标签类型 */
    getTypeTagType(type) {
      const typeMap = {
        '期末考试': 'danger',
        '期中考试': 'warning', 
        '随堂测试': '',
        '课程作业': 'info'
      };
      return typeMap[type] || 'info';
    },
    deleteQuestion(type, questionId) {
      // type: 1选择 2填空 3判断
      var paperId = this.examDetailPaperId;
      this.$confirm("确认从试卷中移除该试题？")
        .then((_) => {
          this.$axios(`/api/paper/delete/${paperId}/${type}/${questionId}`).then(res => {  //通过examCode请求试卷详细信息
            this.getExamDetail(this.examDetailCode, paperId);
          })  
        })
        .catch((_) => {});
    },
    getExamDetail(examCode, paperId) {
      this.examDetailCode = examCode;
      this.examDetailPaperId = paperId;
      this.topicCount = [];
      this.score = [];
      this.examData = {},
      this.topic = {},

      this.showExamDetail = true;

      this.$axios(`/api/exam/${examCode}`).then(res => {  //通过examCode请求试卷详细信息
        res.data.data.examDate = res.data.data.examDate.substr(0,10)
        this.examData = { ...res.data.data}
        let paperId = this.examData.paperId
        this.$axios(`/api/paper/${paperId}`).then(res => {  //通过paperId获取试题题目信息
          this.topic = {...res.data}
          let keys = Object.keys(this.topic) //对象转数组
          keys.forEach(e => {
            let data = this.topic[e]
            this.topicCount.push(data.length)
            let currentScore = 0
            for(let i = 0; i< data.length; i++) { //循环每种题型,计算出总分
              currentScore += data[i].score
            }
            this.score.push(currentScore) //把每种题型总分存入score
          })
        })
      })
    },
    edit(examCode) {
      //编辑试卷
      this.dialogVisible = true;
      this.$axios(`/api/exam/${examCode}`).then((res) => {
        //根据试卷id请求后台
        if (res.data.code == 200) {
          this.form = res.data.data;
        }
      });
    },
    handleClose(done) {
      //关闭提醒
      this.$confirm("确认关闭？")
        .then((_) => {
          done();
        })
        .catch((_) => {});
    },
    submit() {
      //提交修改后的试卷信息
      if (this.form.source == null || this.form.source == "") {
                this.$message({
                    message: "试卷名称不能为空",
                    type: "error",
                });
                return;
            }
            if (this.form.description == null || this.form.description == "") {
                this.$message({
                    message: "介绍不能为空",
                    type: "error",
                });
                return;
            }
            if (this.form.institute == null || this.form.institute == "") {
                this.$message({
                    message: "所属学院不能为空",
                    type: "error",
                });
                return;
            }
            if (this.form.major == null || this.form.major == "") {
                this.$message({
                    message: "所属专业不能为空",
                    type: "error",
                });
                return;
            }
            if (this.form.grade == null || this.form.grade == "") {
                this.$message({
                    message: "年级不能为空",
                    type: "error",
                });
                return;
            }
            if (this.form.examDate == null || this.form.examDate == "") {
                this.$message({
                    message: "考试日期不能为空",
                    type: "error",
                });
                return;
            }
            if (this.form.totalTime == null || this.form.totalTime == "") {
                this.$message({
                    message: "持续时间不能为空",
                    type: "error",
                });
                return;
            }
            if (this.form.type == null || this.form.type == "") {
                this.$message({
                    message: "考试类型不能为空",
                    type: "error",
                });
                return;
            }
            if (this.form.tips == null || this.form.tips == "") {
                this.$message({
                    message: "考生提示不能为空",
                    type: "error",
                });
                return;
            }
      this.dialogVisible = false;
      
      this.$axios({
        url: "/api/exam",
        method: "put",
        data: {
          ...this.form,
        },
      }).then((res) => {
        if (res.data.code == 200) {
          this.$message({
            //成功修改提示
            message: "更新成功",
            type: "success",
          });
        }
        this.getExamInfo();
      });
    },
    deleteRecord(row) {
      this.$confirm(`确定删除试卷"${row.source}"吗？删除后无法恢复!`, "警告", {
        confirmButtonText: "确定删除",
        cancelButtonText: "取消",
        type: "warning",
      })
        .then(() => {
          //确认删除
          this.$axios({
            url: `/api/exam/${row.examCode}`,
            method: "delete",
          }).then((res) => {
            if (res.data.code === 200) {
              this.$message.success("删除成功");
            this.getExamInfo();
            } else {
              this.$message.error(res.data.message || "删除失败");
            }
          }).catch(error => {
            this.$message.error("网络错误，请稍后重试");
          });
        })
        .catch(() => {
          this.$message.info("已取消删除");
        });
    },
    getExamInfo() {
      //分页查询所有试卷信息
      this.loading = true;
      this.$axios(
        `/api/exams/${this.pagination.current}/${this.pagination.size}`
      )
        .then((res) => {
          this.pagination = res.data.data;
          this.loading = false;
        })
        .catch((error) => {
          this.loading = false;
        });
    },
    //改变当前记录条数
    handleSizeChange(val) {
      this.pagination.size = val;
      this.getExamInfo();
    },
    //改变当前页码，重新发送请求
    handleCurrentChange(val) {
      this.pagination.current = val;
      this.getExamInfo();
    },
  },
};
</script>
<style lang="less" scoped>
/* 若依风格考试管理页面样式 */
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
/* 自定义删除按钮样式 */
.delete-btn {
  color: #f56c6c;
  &:hover {
    color: #f78989;
  }
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

/* 对话框样式优化 */
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

/* 试题详情对话框样式 */
.content {
  .header .title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    
    .time {
      color: #909399;
      font-size: 14px;
    }
  }
  
  .titlei {
    font-weight: 600;
    color: #303133;
  }
  
  .contenti {
    .question {
      margin: 16px 0;
      
      li {
        line-height: 1.6;
        color: #606266;
        
        a {
          color: #f56c6c;
          margin-left: 16px;
          
          &:hover {
            color: #f78989;
          }
        }
      }
    }
  }
}
</style>
