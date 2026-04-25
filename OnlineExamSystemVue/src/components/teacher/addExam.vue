<!-- 添加考试 - 现代化设计 -->
<template>
    <div class="add-exam-container">
        <!-- 页面标题 -->
        <div class="page-header">
            <div class="header-content">
                <div class="header-icon">
                    <i class="el-icon-document-add"></i>
                </div>
                <div class="header-text">
                    <h2 class="page-title">创建新考试</h2>
                    <p class="page-subtitle">填写考试信息，创建新的考试试卷</p>
                </div>
            </div>
        </div>

        <!-- 表单卡片 -->
        <div class="form-card">
            <el-form ref="form" :model="form" :rules="rules" label-width="100px" class="modern-form">
                <!-- 基本信息区域 -->
                <div class="form-section">
                    <div class="section-title">
                        <i class="el-icon-info"></i>
                        <span>基本信息</span>
                    </div>
                    
                    <el-row :gutter="20">
                        <el-col :span="12">
                            <el-form-item label="试卷名称" prop="source">
                                <el-input
                                    v-model="form.source"
                                    placeholder="请输入试卷名称"
                                    prefix-icon="el-icon-edit">
                                </el-input>
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="考试类型" prop="type">
                                <el-select
                                    v-model="form.type"
                                    placeholder="请选择考试类型"
                                    style="width: 100%">
                                    <el-option label="期末考试" value="期末考试">
                                        <i class="el-icon-trophy"></i> 期末考试
                                    </el-option>
                                    <el-option label="期中考试" value="期中考试">
                                        <i class="el-icon-medal"></i> 期中考试
                                    </el-option>
                                    <el-option label="随堂测试" value="随堂测试">
                                        <i class="el-icon-edit-outline"></i> 随堂测试
                                    </el-option>
                                    <el-option label="课程作业" value="课程作业">
                                        <i class="el-icon-document"></i> 课程作业
                                    </el-option>
                                </el-select>
                            </el-form-item>
                        </el-col>
                    </el-row>

                    <el-form-item label="试卷介绍" prop="description">
                        <el-input
                            v-model="form.description"
                            placeholder="请输入试卷介绍"
                            type="textarea"
                            :rows="3"
                            maxlength="200"
                            show-word-limit>
                        </el-input>
                    </el-form-item>
                </div>

                <!-- 学院专业信息 -->
                <div class="form-section">
                    <div class="section-title">
                        <i class="el-icon-school"></i>
                        <span>学院专业</span>
                    </div>
                    
                    <el-row :gutter="20">
                        <el-col :span="8">
                            <el-form-item label="所属学院" prop="institute">
                                <el-input
                                    v-model="form.institute"
                                    placeholder="请输入所属学院"
                                    prefix-icon="el-icon-office-building">
                                </el-input>
                            </el-form-item>
                        </el-col>
                        <el-col :span="8">
                            <el-form-item label="所属专业" prop="major">
                                <el-input
                                    v-model="form.major"
                                    placeholder="请输入所属专业"
                                    prefix-icon="el-icon-reading">
                                </el-input>
                            </el-form-item>
                        </el-col>
                        <el-col :span="8">
                            <el-form-item label="年级" prop="grade">
                                <el-input
                                    v-model="form.grade"
                                    placeholder="如：2024级"
                                    prefix-icon="el-icon-user">
                                </el-input>
                            </el-form-item>
                        </el-col>
                    </el-row>
                </div>

                <!-- 考试安排 -->
                <div class="form-section">
                    <div class="section-title">
                        <i class="el-icon-time"></i>
                        <span>考试安排</span>
                    </div>
                    
                    <el-row :gutter="20">
                        <el-col :span="12">
                            <el-form-item label="考试日期" prop="examDate">
                                <el-date-picker
                                    v-model="form.examDate"
                                    type="date"
                                    placeholder="选择考试日期"
                                    style="width: 100%"
                                    value-format="yyyy-MM-dd"
                                    prefix-icon="el-icon-date">
                                </el-date-picker>
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="持续时间" prop="totalTime">
                                <el-input
                                    v-model="form.totalTime"
                                    placeholder="请输入考试时长（分钟）"
                                    type="number"
                                    prefix-icon="el-icon-timer">
                                    <template slot="append">分钟</template>
                                </el-input>
                            </el-form-item>
                        </el-col>
                    </el-row>

                    <el-row :gutter="20">
                        <el-col :span="12">
                            <el-form-item label="开考时间">
                                <el-time-picker v-model="form.examStartTime"
                                    placeholder="开考时间（不填表示全天均可）"
                                    format="HH:mm" value-format="HH:mm" style="width:100%"/>
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="截止时间">
                                <el-time-picker v-model="form.examEndTime"
                                    placeholder="截止时间（不填表示永不过期）"
                                    format="HH:mm" value-format="HH:mm" style="width:100%"/>
                            </el-form-item>
                        </el-col>
                    </el-row>
                </div>

                <!-- 考生须知 -->
                <div class="form-section">
                    <div class="section-title">
                        <i class="el-icon-warning"></i>
                        <span>考生须知</span>
                    </div>
                    
                    <el-form-item label="考生提示" prop="tips">
                        <el-input
                            v-model="form.tips"
                            type="textarea"
                            :rows="4"
                            placeholder="请输入考生须知和注意事项"
                            maxlength="500"
                            show-word-limit>
                        </el-input>
                    </el-form-item>
                </div>

                <!-- 操作按钮 -->
                <el-form-item class="form-actions">
                    <el-button
                        type="primary"
                        @click="onSubmit()"
                        icon="el-icon-check"
                        size="medium"
                        class="submit-btn">
                        立即创建
                    </el-button>
                    <el-button
                        @click="resetForm()"
                        icon="el-icon-refresh-left"
                        size="medium">
                        重置
                    </el-button>
                    <el-button
                        @click="goBack()"
                        icon="el-icon-back"
                        size="medium"
                        type="info">
                        返回
                    </el-button>
                </el-form-item>
            </el-form>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            form: {
                //表单数据初始化
                source: null,
                description: null,
                institute: null,
                major: null,
                grade: null,
                examDate: null,
                totalTime: null,
                totalScore: null,
                type: null,
                tips: null,
                paperId: null,
                examStartTime: null,
                examEndTime: null,
            },
            // 表单验证规则
            rules: {
                source: [
                    { required: true, message: '请输入试卷名称', trigger: 'blur' }
                ],
                type: [
                    { required: true, message: '请选择考试类型', trigger: 'change' }
                ],
                description: [
                    { required: true, message: '请输入试卷介绍', trigger: 'blur' }
                ],
                institute: [
                    { required: true, message: '请输入所属学院', trigger: 'blur' }
                ],
                major: [
                    { required: true, message: '请输入所属专业', trigger: 'blur' }
                ],
                grade: [
                    { required: true, message: '请输入年级', trigger: 'blur' }
                ],
                examDate: [
                    { required: true, message: '请选择考试日期', trigger: 'change' }
                ],
                totalTime: [
                    { required: true, message: '请输入持续时间', trigger: 'blur' }
                ],
                tips: [
                    { required: true, message: '请输入考生提示', trigger: 'blur' }
                ]
            }
        };
    },
    methods: {
        /**
         * 日期格式化
         * @param {Date} date 日期对象
         * @return {String} 格式化后的日期字符串 yyyy-MM-dd HH:mm:ss
         */
        formatTime(date) {
            let year = date.getFullYear();
            let month =
                date.getMonth() + 1 < 10
                    ? "0" + (date.getMonth() + 1)
                    : date.getMonth() + 1;
            let day =
                date.getDate() < 10 ? "0" + date.getDate() : date.getDate();
            let hours =
                date.getHours() < 10 ? "0" + date.getHours() : date.getHours();
            let minutes =
                date.getMinutes() < 10
                    ? "0" + date.getMinutes()
                    : date.getMinutes();
            let seconds =
                date.getSeconds() < 10
                    ? "0" + date.getSeconds()
                    : date.getSeconds();
            return (
                year + "-" + month + "-" + day + " " +
                hours + ":" + minutes + ":" + seconds
            );
        },
        /**
         * 提交表单 - 使用 el-form 的 validate 方法进行校验
         */
        onSubmit() {
            this.$refs.form.validate((valid) => {
                if (valid) {
                    this.$axios(`/api/examManagePaperId`).then((res) => {
                        this.form.paperId = res.data.data.paperId + 1;
                        this.$axios({
                            url: "/api/exam",
                            method: "post",
                            data: {
                                ...this.form,
                            },
                        }).then((res) => {
                            if (res.data.code == 200) {
                                this.$message({
                                    message: "考试创建成功",
                                    type: "success",
                                });
                                this.$router.push({ path: "/selectExam" });
                            }
                        });
                    });
                } else {
                    this.$message({
                        message: '请填写完整的考试信息',
                        type: 'warning'
                    });
                    return false;
                }
            });
        },
        /**
         * 重置表单
         */
        resetForm() {
            this.$refs.form.resetFields();
        },
        /**
         * 返回考试列表页
         */
        goBack() {
            this.$router.push({ path: '/selectExam' });
        }
    },
};
</script>
<style lang="less" scoped>
/* 现代化添加考试页面样式 */
.add-exam-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px;
    animation: fadeInUp 0.5s ease;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 页面标题 */
.page-header {
    margin-bottom: 24px;
    padding: 24px;
    background: linear-gradient(135deg, #26a69a 0%, #4db6ac 100%);
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(38, 166, 154, 0.3);
    position: relative;
    overflow: hidden;
}

.page-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
    animation: rotate 20s linear infinite;
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.header-content {
    display: flex;
    align-items: center;
    gap: 20px;
    position: relative;
    z-index: 1;
}

.header-icon {
    width: 64px;
    height: 64px;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    color: #fff;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.header-text {
    flex: 1;
}

.page-title {
    font-size: 28px;
    font-weight: 700;
    color: #fff;
    margin: 0 0 8px 0;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.page-subtitle {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.9);
    margin: 0;
}

/* 表单卡片 */
.form-card {
    background: #fff;
    border-radius: 16px;
    padding: 32px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    border: 1px solid #e4e7ed;
}

/* 表单样式 */
.modern-form {
    .el-form-item {
        margin-bottom: 24px;
    }

    .el-form-item__label {
        font-weight: 500;
        color: #303133;
        line-height: 40px;
    }

    .el-input__inner,
    .el-textarea__inner {
        border-radius: 8px;
        border: 1.5px solid #dcdfe6;
        transition: all 0.3s ease;
        
        &:hover {
            border-color: #c0c4cc;
        }
        
        &:focus {
            border-color: #26a69a;
            box-shadow: 0 0 0 3px rgba(38, 166, 154, 0.1);
        }
    }

    .el-select {
        width: 100%;
    }
}

/* 表单分区 */
.form-section {
    margin-bottom: 32px;
    padding: 24px;
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    border-radius: 12px;
    border: 1px solid #e4e7ed;
    transition: all 0.3s ease;
}

.form-section:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    transform: translateY(-2px);
}

.section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid #e4e7ed;
    
    i {
        font-size: 18px;
        color: #26a69a;
    }
}

/* 操作按钮 */
.form-actions {
    margin-top: 40px;
    padding-top: 24px;
    border-top: 2px solid #e4e7ed;
    text-align: center;
    
    .el-button {
        min-width: 140px;
        height: 44px;
        font-size: 15px;
        border-radius: 22px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .submit-btn {
        background: linear-gradient(135deg, #26a69a 0%, #4db6ac 100%);
        border: none;
        box-shadow: 0 4px 15px rgba(38, 166, 154, 0.4);
        
        &:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(38, 166, 154, 0.5);
        }
        
        &:active {
            transform: translateY(0);
        }
    }
}

/* 响应式设计 */
@media (max-width: 768px) {
    .add-exam-container {
        padding: 16px;
    }
    
    .page-header {
        padding: 20px;
    }
    
    .header-icon {
        width: 48px;
        height: 48px;
        font-size: 24px;
    }
    
    .page-title {
        font-size: 22px;
    }
    
    .form-card {
        padding: 20px;
    }
    
    .form-section {
        padding: 16px;
    }
    
    .el-col {
        margin-bottom: 0;
    }
}

/* 输入框图标颜色 */
::v-deep .el-input__prefix {
    color: #909399;
}

::v-deep .el-input__inner:focus ~ .el-input__prefix {
    color: #26a69a;
}

/* 日期选择器样式 */
::v-deep .el-date-editor {
    width: 100%;
    
    .el-input__inner {
        padding-left: 40px;
    }
}

/* 下拉选项样式 */
::v-deep .el-select-dropdown__item {
    padding: 12px 20px;
    
    i {
        margin-right: 8px;
        color: #26a69a;
    }
}
</style>

