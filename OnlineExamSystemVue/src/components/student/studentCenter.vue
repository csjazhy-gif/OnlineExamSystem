<!-- 学生个人中心 -->
<template>
  <div class="student-center">
    <div class="page-header">
      <h2><i class="el-icon-user"></i> 个人中心</h2>
      <p class="subtitle">查看和编辑您的个人信息</p>
    </div>

    <div class="center-content">
      <!-- 个人信息卡片 -->
      <div class="profile-card">
        <div class="avatar-section">
          <el-avatar :size="100" :src="require('@/assets/img/avatar.jpg')" class="profile-avatar"></el-avatar>
          <h3 class="profile-name">{{ form.studentName }}</h3>
          <el-tag type="primary" size="small">{{ form.clazz ? form.clazz + '班' : '学生' }}</el-tag>
        </div>
        <div class="info-stats">
          <div class="stat-item">
            <div class="stat-value">{{ form.grade || '--' }}</div>
            <div class="stat-label">年级</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ form.major || '--' }}</div>
            <div class="stat-label">专业</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ form.institute || '--' }}</div>
            <div class="stat-label">学院</div>
          </div>
        </div>
      </div>

      <!-- 编辑表单 -->
      <div class="form-card">
        <div class="card-title">
          <span>基本信息</span>
          <el-button v-if="!editing" type="primary" size="small" icon="el-icon-edit" @click="editing = true">编辑</el-button>
          <div v-else>
            <el-button type="success" size="small" icon="el-icon-check" @click="saveProfile">保存</el-button>
            <el-button size="small" icon="el-icon-close" @click="cancelEdit">取消</el-button>
          </div>
        </div>

        <el-form :model="form" label-width="100px" class="profile-form" :disabled="!editing">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="学号">
                <el-input v-model="form.studentId" disabled prefix-icon="el-icon-postcard"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="姓名">
                <el-input v-model="form.studentName" prefix-icon="el-icon-user"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="性别">
                <el-select v-model="form.sex" style="width:100%">
                  <el-option label="男" value="男"></el-option>
                  <el-option label="女" value="女"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="身份证号">
                <el-input v-model="form.cardId" prefix-icon="el-icon-postcard"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="电话">
                <el-input v-model="form.tel" prefix-icon="el-icon-phone"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="邮箱">
                <el-input v-model="form.email" prefix-icon="el-icon-message"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="年级">
                <el-input v-model="form.grade" prefix-icon="el-icon-date"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="班级">
                <el-input v-model="form.clazz" prefix-icon="el-icon-office-building"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="专业">
                <el-input v-model="form.major" prefix-icon="el-icon-collection"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="学院">
                <el-input v-model="form.institute" prefix-icon="el-icon-school"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>

      <!-- 修改密码 -->
      <div class="form-card">
        <div class="card-title"><span>修改密码</span></div>
        <el-form :model="pwdForm" label-width="100px" class="pwd-form">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="原密码">
                <el-input v-model="pwdForm.oldPwd" type="password" show-password prefix-icon="el-icon-lock"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="新密码">
                <el-input v-model="pwdForm.newPwd" type="password" show-password prefix-icon="el-icon-key"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="确认密码">
                <el-input v-model="pwdForm.confirmPwd" type="password" show-password prefix-icon="el-icon-key"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <el-button type="warning" icon="el-icon-refresh" @click="changePwd">修改密码</el-button>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentCenter',
  data() {
    return {
      editing: false,
      form: {
        studentId: '',
        studentName: '',
        sex: '',
        cardId: '',
        tel: '',
        email: '',
        grade: '',
        clazz: '',
        major: '',
        institute: ''
      },
      originalForm: {},
      pwdForm: { oldPwd: '', newPwd: '', confirmPwd: '' }
    }
  },
  created() {
    this.loadProfile()
  },
  methods: {
    async loadProfile() {
      const sid = this.$cookies.get('cid')
      if (!sid) return
      try {
        const res = await this.$axios.get(`/student/${sid}`)
        if (res.data.code === 200 && res.data.data) {
          const d = res.data.data
          this.form = {
            studentId: d.studentId,
            studentName: d.studentName || '',
            sex: d.sex || '',
            cardId: d.cardId || '',
            tel: d.tel || '',
            email: d.email || '',
            grade: d.grade || '',
            clazz: d.clazz || '',
            major: d.major || '',
            institute: d.institute || ''
          }
          this.originalForm = { ...this.form }
        }
      } catch (e) {
        this.$message.error('加载个人信息失败')
      }
    },
    async saveProfile() {
      try {
        const res = await this.$axios.put('/student', this.form)
        if (res.data.code === 200) {
          this.$message.success('保存成功')
          this.editing = false
          this.originalForm = { ...this.form }
        } else {
          this.$message.error(res.data.message || '保存失败')
        }
      } catch (e) {
        this.$message.error('保存失败')
      }
    },
    cancelEdit() {
      this.form = { ...this.originalForm }
      this.editing = false
    },
    async changePwd() {
      if (!this.pwdForm.oldPwd || !this.pwdForm.newPwd) {
        return this.$message.warning('请填写完整')
      }
      if (this.pwdForm.newPwd !== this.pwdForm.confirmPwd) {
        return this.$message.warning('两次密码不一致')
      }
      try {
        const res = await this.$axios.put('/studentPWD', {
          studentId: this.form.studentId,
          pwd: this.pwdForm.newPwd
        })
        if (res.data.code === 200) {
          this.$message.success('密码修改成功')
          this.pwdForm = { oldPwd: '', newPwd: '', confirmPwd: '' }
        } else {
          this.$message.error('密码修改失败')
        }
      } catch (e) {
        this.$message.error('密码修改失败')
      }
    }
  }
}
</script>

<style scoped>
.student-center { max-width: 1000px; margin: 0 auto; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 22px; color: #303133; margin: 0 0 8px 0; display: flex; align-items: center; gap: 8px; }
.page-header .subtitle { color: #909399; font-size: 14px; margin: 0; }
.center-content { display: flex; flex-direction: column; gap: 20px; }

.profile-card {
  background: linear-gradient(135deg, var(--theme-primary, #409EFF), #66b1ff);
  border-radius: 16px; padding: 32px; color: #fff;
  display: flex; align-items: center; gap: 40px;
  box-shadow: 0 8px 24px rgba(64,158,255,0.3);
}
.avatar-section { text-align: center; }
.profile-avatar { border: 3px solid rgba(255,255,255,0.5); }
.profile-name { margin: 12px 0 8px; font-size: 20px; }
.info-stats { display: flex; gap: 40px; flex: 1; justify-content: center; }
.stat-item { text-align: center; }
.stat-value { font-size: 18px; font-weight: 600; margin-bottom: 4px; }
.stat-label { font-size: 13px; opacity: 0.85; }

.form-card {
  background: #fff; border-radius: 12px; padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.card-title {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid #ebeef5;
  font-size: 16px; font-weight: 600; color: #303133;
}
.profile-form, .pwd-form { margin-top: 8px; }
</style>
