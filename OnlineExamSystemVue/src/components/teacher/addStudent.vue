<!--
 * @Description: 
 * 
 * @Date: 2023-03-08 20:38:49
-->
<!-- 添加学生 - 若依风格 -->
<template>
  <div class="ruoyi-container">
    <div class="ruoyi-card">
      <div class="card-header">
        <span class="card-title">
          <i class="el-icon-plus"></i>
          添加学生
        </span>
      </div>
      
      <el-form 
        ref="form" 
        :model="form" 
        :rules="rules"
        label-width="100px" 
        class="ruoyi-form">
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学生姓名" prop="studentName">
              <el-input 
                v-model="form.studentName" 
                placeholder="请输入学生姓名"
                clearable>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="sex">
              <el-select v-model="form.sex" placeholder="请选择性别" style="width: 100%">
                <el-option label="男" value="男"></el-option>
                <el-option label="女" value="女"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所属学院" prop="institute">
              <el-input 
                v-model="form.institute" 
                placeholder="请输入所属学院"
                clearable>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属专业" prop="major">
              <el-input 
                v-model="form.major" 
                placeholder="请输入所属专业"
                clearable>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="年级" prop="grade">
              <el-input 
                v-model="form.grade" 
                placeholder="请输入年级"
                clearable>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="班级" prop="clazz">
              <el-input 
                v-model="form.clazz" 
                placeholder="请输入班级"
                clearable>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="电话号码" prop="tel">
              <el-input 
                v-model="form.tel" 
                placeholder="请输入电话号码"
                clearable>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号" prop="cardId">
              <el-input 
                v-model="form.cardId" 
                placeholder="请输入身份证号"
                clearable>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input 
                v-model="form.email" 
                placeholder="请输入邮箱地址"
                clearable>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="初始密码" prop="pwd">
              <el-input 
                v-model="form.pwd" 
                type="password"
                placeholder="请输入初始密码"
                show-password
                clearable>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item class="form-buttons">
          <el-button type="primary" @click="onSubmit()" :loading="loading">
            <i class="el-icon-check"></i>
            提交
          </el-button>
          <el-button @click="cancel()">
            <i class="el-icon-refresh-left"></i>
            重置
          </el-button>
          <el-button type="info" @click="goBack()">
            <i class="el-icon-back"></i>
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
    // 手机号验证
    const validatePhone = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入电话号码'));
      } else if (!/^1[3-9]\d{9}$/.test(value)) {
        callback(new Error('请输入正确的手机号码'));
      } else {
        callback();
      }
    };
    
    // 身份证验证
    const validateIdCard = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入身份证号'));
      } else if (!/^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/.test(value)) {
        callback(new Error('请输入正确的身份证号码'));
      } else {
        callback();
      }
    };
    
    // 邮箱验证
    const validateEmail = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入邮箱地址'));
      } else if (!/^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/.test(value)) {
        callback(new Error('请输入正确的邮箱格式'));
      } else {
        callback();
      }
    };
    
    return {
      loading: false,
      form: { //表单数据初始化
        studentName: '',
        grade: '',
        major: '',
        clazz: '',
        institute: '',
        tel: '',
        email: '',
        pwd: '123456', // 默认密码
        cardId: '',
        sex: '',
        role: 2
      },
      rules: {
        studentName: [
          { required: true, message: '请输入学生姓名', trigger: 'blur' },
          { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ],
        sex: [
          { required: true, message: '请选择性别', trigger: 'change' }
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
        clazz: [
          { required: true, message: '请输入班级', trigger: 'blur' }
        ],
        tel: [
          { required: true, validator: validatePhone, trigger: 'blur' }
        ],
        cardId: [
          { required: true, validator: validateIdCard, trigger: 'blur' }
        ],
        email: [
          { required: true, validator: validateEmail, trigger: 'blur' }
        ],
        pwd: [
          { required: true, message: '请输入初始密码', trigger: 'blur' },
          { min: 6, max: 16, message: '长度在 6 到 16 个字符', trigger: 'blur' }
        ]
      }
    };
  },
  methods: {
    onSubmit() { //数据提交
      this.$refs.form.validate((valid) => {
        if (valid) {
          this.loading = true;
          this.$axios({
            url: '/api/student',
            method: 'post',
            data: {
              ...this.form
            }
          }).then(res => {
            this.loading = false;
            if(res.data.code == 200) {
              this.$message({
                message: '学生添加成功',
                type: 'success',
                duration: 3000
              });
              this.$router.push({path: '/studentManage'});
            } else {
              this.$message({
                message: res.data.message || '添加失败',
                type: 'error',
                duration: 3000
              });
            }
          }).catch(error => {
            this.loading = false;
            this.$message({
              message: '网络错误，请稍后重试',
              type: 'error',
              duration: 3000
            });
          });
        } else {
          this.$message({
            message: '请填写完整信息',
            type: 'warning',
            duration: 3000
          });
          return false;
        }
      });
    },
    cancel() { //重置按钮
      this.$refs.form.resetFields();
    },
    goBack() { //返回按钮
      this.$router.push({path: '/studentManage'});
    }
  }
};
</script>
<style lang="less" scoped>
/* 若依风格表单样式 */
.ruoyi-container {
  padding: 20px;
}

.ruoyi-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 0;
  margin-bottom: 20px;
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e6e6e6;
  background-color: #fafbfc;
  border-radius: 8px 8px 0 0;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  
  i {
    margin-right: 8px;
    color: #409eff;
  }
}

.ruoyi-form {
  padding: 24px;
}

.ruoyi-form .el-form-item {
  margin-bottom: 22px;
}

.ruoyi-form .el-form-item__label {
  font-weight: 500;
  color: #606266;
}

.ruoyi-form .el-input__inner {
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  height: 40px;
  line-height: 40px;
  padding: 0 15px;
  transition: border-color 0.2s cubic-bezier(0.645, 0.045, 0.355, 1);
}

.ruoyi-form .el-input__inner:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.ruoyi-form .el-select {
  width: 100%;
}

.ruoyi-form .el-select .el-input__inner {
  cursor: pointer;
}

.form-buttons {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e6e6e6;
  text-align: center;
}

.form-buttons .el-button {
  margin: 0 8px;
  padding: 10px 20px;
  font-weight: 500;
  border-radius: 4px;
  transition: all 0.3s;
}

.form-buttons .el-button--primary {
  background: #409eff;
  border-color: #409eff;
}

.form-buttons .el-button--primary:hover {
  background: #66b1ff;
  border-color: #66b1ff;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.3);
}

.form-buttons .el-button--info {
  color: #606266;
  border-color: #dcdfe6;
  background: #fff;
}

.form-buttons .el-button--info:hover {
  color: #409eff;
  border-color: #c6e2ff;
  background: #ecf5ff;
}

.form-buttons .el-button i {
  margin-right: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ruoyi-form {
    padding: 16px;
  }
  
  .el-col-12 {
    flex: 0 0 100%;
    max-width: 100%;
  }
}
</style>

