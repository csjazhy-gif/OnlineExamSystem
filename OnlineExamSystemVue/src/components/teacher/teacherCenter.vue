<!-- 教师/管理员个人中心 - 浅蓝色大气风格 -->
<template>
  <div class="teacher-center">
    <!-- 页面头部 -->
    <div class="profile-banner">
      <div class="banner-bg"></div>
      <div class="banner-content">
        <div class="avatar-section">
          <div class="avatar-ring">
            <el-avatar :size="90" icon="el-icon-user-solid" class="main-avatar"></el-avatar>
          </div>
          <div class="user-brief">
            <h2 class="user-name">{{ form.teacherName || form.adminName || '--' }}</h2>
            <div class="user-meta">
              <el-tag :type="isAdmin ? 'danger' : ''" size="small" effect="dark" class="role-tag">
                {{ isAdmin ? '系统管理员' : '教师' }}
              </el-tag>
              <span class="meta-item" v-if="!isAdmin && form.institute">
                <i class="el-icon-office-building"></i> {{ form.institute }}
              </span>
              <span class="meta-item" v-if="!isAdmin && form.type">
                <i class="el-icon-medal"></i> {{ form.type }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主体内容 -->
    <el-row :gutter="24" class="main-body">
      <!-- 左侧信息卡片 -->
      <el-col :span="8">
        <div class="side-card">
          <div class="side-card-head">
            <i class="el-icon-postcard"></i>
            <span>基本资料</span>
          </div>
          <div class="info-items">
            <div class="info-item" v-for="item in infoList" :key="item.label">
              <div class="info-icon"><i :class="item.icon"></i></div>
              <div class="info-content">
                <div class="info-label">{{ item.label }}</div>
                <div class="info-value">{{ item.value || '未设置' }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 安全信息 -->
        <div class="side-card mt-20">
          <div class="side-card-head">
            <i class="el-icon-lock"></i>
            <span>账号安全</span>
          </div>
          <div class="security-list">
            <div class="security-item">
              <div class="security-left">
                <i class="el-icon-key"></i>
                <span>登录密码</span>
              </div>
              <el-button type="text" @click="activeTab = 'pwd'">修改</el-button>
            </div>
            <div class="security-item">
              <div class="security-left">
                <i class="el-icon-user"></i>
                <span>账号ID</span>
              </div>
              <span class="security-value">{{ isAdmin ? form.adminId : form.teacherId }}</span>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 右侧编辑区域 -->
      <el-col :span="16">
        <div class="edit-card">
          <el-tabs v-model="activeTab" class="custom-tabs">
            <el-tab-pane label="编辑资料" name="info">
              <div class="form-section">
                <el-form :model="form" label-width="110px" class="profile-form" label-position="right">
                  <el-row :gutter="24">
                    <el-col :span="12">
                      <el-form-item label="姓名">
                        <el-input v-model="editName" prefix-icon="el-icon-user" placeholder="请输入姓名"></el-input>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="性别">
                        <el-radio-group v-model="form.sex" class="sex-radio">
                          <el-radio label="男"><i class="el-icon-male"></i> 男</el-radio>
                          <el-radio label="女"><i class="el-icon-female"></i> 女</el-radio>
                        </el-radio-group>
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="24" v-if="!isAdmin">
                    <el-col :span="12">
                      <el-form-item label="所属学院">
                        <el-input v-model="form.institute" prefix-icon="el-icon-office-building" placeholder="请输入学院"></el-input>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="职称">
                        <el-input v-model="form.type" prefix-icon="el-icon-medal" placeholder="请输入职称"></el-input>
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="24">
                    <el-col :span="12">
                      <el-form-item label="联系电话">
                        <el-input v-model="form.tel" prefix-icon="el-icon-phone" placeholder="请输入手机号"></el-input>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="电子邮箱">
                        <el-input v-model="form.email" prefix-icon="el-icon-message" placeholder="请输入邮箱"></el-input>
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-form-item label="身份证号">
                    <el-input v-model="form.cardId" prefix-icon="el-icon-postcard" placeholder="请输入身份证号"></el-input>
                  </el-form-item>
                  <el-form-item class="form-actions">
                    <el-button type="primary" icon="el-icon-check" @click="saveProfile" :loading="saving">保存修改</el-button>
                    <el-button icon="el-icon-refresh" @click="loadProfile">重新加载</el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>

            <el-tab-pane label="修改密码" name="pwd">
              <div class="form-section">
                <div class="pwd-tip">
                  <i class="el-icon-warning-outline"></i>
                  修改密码后需要重新登录，请牢记新密码
                </div>
                <el-form :model="pwdForm" label-width="110px" class="profile-form" style="max-width:520px;">
                  <el-form-item label="当前密码">
                    <el-input v-model="pwdForm.oldPwd" type="password" show-password prefix-icon="el-icon-lock" placeholder="请输入当前密码"></el-input>
                  </el-form-item>
                  <el-form-item label="新密码">
                    <el-input v-model="pwdForm.newPwd" type="password" show-password prefix-icon="el-icon-key" placeholder="请输入新密码"></el-input>
                  </el-form-item>
                  <el-form-item label="确认新密码">
                    <el-input v-model="pwdForm.confirmPwd" type="password" show-password prefix-icon="el-icon-key" placeholder="请再次输入新密码"></el-input>
                  </el-form-item>
                  <el-form-item class="form-actions">
                    <el-button type="warning" icon="el-icon-refresh" @click="changePwd" :loading="pwdSaving">修改密码</el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'TeacherCenter',
  data() {
    return {
      activeTab: 'info',
      isAdmin: false,
      form: {},
      saving: false,
      pwdSaving: false,
      pwdForm: { oldPwd: '', newPwd: '', confirmPwd: '' }
    }
  },
  computed: {
    editName: {
      get() { return this.isAdmin ? this.form.adminName : this.form.teacherName },
      set(v) { this.isAdmin ? this.form.adminName = v : this.form.teacherName = v }
    },
    infoList() {
      const list = [
        { icon: 'el-icon-user', label: '姓名', value: this.form.teacherName || this.form.adminName },
        { icon: 'el-icon-male', label: '性别', value: this.form.sex },
        { icon: 'el-icon-phone', label: '电话', value: this.form.tel },
        { icon: 'el-icon-message', label: '邮箱', value: this.form.email },
        { icon: 'el-icon-postcard', label: '身份证', value: this.form.cardId ? this.form.cardId.replace(/^(.{6})(.+)(.{4})$/, '$1****$3') : '' }
      ]
      if (!this.isAdmin) {
        list.splice(2, 0,
          { icon: 'el-icon-office-building', label: '学院', value: this.form.institute },
          { icon: 'el-icon-medal', label: '职称', value: this.form.type }
        )
      }
      return list
    }
  },
  created() {
    this.isAdmin = this.$cookies.get('role') == 0
    this.loadProfile()
  },
  methods: {
    async loadProfile() {
      const id = this.$cookies.get('cid')
      if (!id) return
      try {
        const url = this.isAdmin ? `/admin/${id}` : `/teacher/${id}`
        const res = await this.$axios.get(url)
        if (res.data.code === 200 && res.data.data) {
          this.form = { ...res.data.data }
        }
      } catch (e) {
        this.$message.error('加载个人信息失败')
      }
    },
    async saveProfile() {
      this.saving = true
      try {
        const url = this.isAdmin ? `/admin/${this.form.adminId}` : '/teacher'
        const res = await this.$axios.put(url, this.form)
        if (res.data.code === 200) {
          this.$message.success('保存成功')
        } else {
          this.$message.error(res.data.message || '保存失败')
        }
      } catch (e) {
        this.$message.error('保存失败')
      } finally {
        this.saving = false
      }
    },
    async changePwd() {
      if (!this.pwdForm.oldPwd || !this.pwdForm.newPwd) {
        return this.$message.warning('请填写完整')
      }
      if (this.pwdForm.newPwd !== this.pwdForm.confirmPwd) {
        return this.$message.warning('两次密码不一致')
      }
      this.pwdSaving = true
      try {
        const id = this.$cookies.get('cid')
        let res
        if (this.isAdmin) {
          res = await this.$axios.get(`/admin/resetPsw/${id}/${this.pwdForm.oldPwd}/${this.pwdForm.newPwd}`)
        } else {
          res = await this.$axios.put('/teacher', {
            ...this.form,
            pwd: this.pwdForm.newPwd
          })
        }
        if (res.data.code === 200) {
          this.$message.success('密码修改成功')
          this.pwdForm = { oldPwd: '', newPwd: '', confirmPwd: '' }
        } else {
          this.$message.error('密码修改失败')
        }
      } catch (e) {
        this.$message.error('密码修改失败')
      } finally {
        this.pwdSaving = false
      }
    }
  }
}
</script>

<style scoped>
/* ====== 顶部资料横幅 ====== */
.profile-banner {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 24px;
  height: 160px;
}

.banner-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 40%, #93C5FD 100%);
}

.banner-bg::after {
  content: '';
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.06'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.banner-content {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 40px;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 24px;
}

.avatar-ring {
  padding: 4px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(8px);
}

.main-avatar {
  background: linear-gradient(135deg, #fff 0%, #E0EDFF 100%) !important;
  color: #3B82F6 !important;
  font-size: 36px !important;
  border: 3px solid rgba(255, 255, 255, 0.5);
}

.user-name {
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 10px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.role-tag {
  font-weight: 600;
  letter-spacing: 0.5px;
}

.meta-item {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ====== 主体 ====== */
.main-body {
  margin-top: 0;
}

.mt-20 {
  margin-top: 20px;
}

/* ====== 侧边信息卡 ====== */
.side-card {
  background: #fff;
  border-radius: 14px;
  border: 1px solid rgba(59, 130, 246, 0.12);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.08);
  overflow: hidden;
}

.side-card-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 24px;
  background: linear-gradient(to right, #F8FBFF, #FFF);
  border-bottom: 1px solid #F1F5F9;
  font-size: 15px;
  font-weight: 700;
  color: #1E293B;
}

.side-card-head i {
  color: #3B82F6;
  font-size: 18px;
}

/* 信息列表 */
.info-items {
  padding: 8px 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 10px;
  border-bottom: 1px solid #F8FAFC;
  transition: background 0.2s;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item:hover {
  background: #F8FBFF;
  border-radius: 8px;
}

.info-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #EFF6FF;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.info-icon i {
  font-size: 16px;
  color: #3B82F6;
}

.info-label {
  font-size: 12px;
  color: #94A3B8;
  margin-bottom: 2px;
}

.info-value {
  font-size: 14px;
  color: #1E293B;
  font-weight: 500;
}

/* 安全列表 */
.security-list {
  padding: 8px 24px 16px;
}

.security-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid #F8FAFC;
}

.security-item:last-child {
  border-bottom: none;
}

.security-left {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #64748B;
  font-size: 14px;
}

.security-left i {
  color: #3B82F6;
}

.security-value {
  font-size: 13px;
  color: #94A3B8;
  font-family: monospace;
}

/* ====== 编辑区域 ====== */
.edit-card {
  background: #fff;
  border-radius: 14px;
  border: 1px solid rgba(59, 130, 246, 0.12);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.08);
  overflow: hidden;
}

.custom-tabs {
  padding: 0;
}

::v-deep .custom-tabs .el-tabs__header {
  padding: 0 32px;
  margin-bottom: 0;
  background: linear-gradient(to right, #F8FBFF, #FFF);
  border-bottom: 1px solid #F1F5F9;
}

::v-deep .custom-tabs .el-tabs__item {
  height: 56px;
  line-height: 56px;
  font-size: 15px;
}

.form-section {
  padding: 32px;
}

.profile-form .el-form-item {
  margin-bottom: 24px;
}

.form-actions {
  margin-top: 16px;
  padding-top: 24px;
  border-top: 2px solid #F1F5F9;
}

/* 密码提示 */
.pwd-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  background: #FFF7ED;
  border: 1px solid #FED7AA;
  border-radius: 10px;
  color: #C2410C;
  font-size: 14px;
  margin-bottom: 28px;
}

.pwd-tip i {
  font-size: 18px;
  color: #EA580C;
}

.sex-radio {
  padding-top: 8px;
}
</style>
