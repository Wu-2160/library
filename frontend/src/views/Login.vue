<template>
  <div class="login-container">
    <!-- 背景图片 -->
    <div class="background-image"></div>
    
    <!-- 半透明遮罩，确保文字可读性 -->
    <div class="overlay"></div>
    
    <div class="login-box">
      <!-- 标题区域 -->
      <div class="title-section">
        <img v-if="logoUrl" :src="logoUrl" alt="系统图标" class="title-logo" />
        <h1>图书馆管理系统</h1>
      </div>
      
      <el-tabs :model-value="activeTab" @tab-change="activeTab = $event" class="custom-tabs">
        <!-- 登录面板 -->
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            @submit.prevent="handleLogin"
            class="login-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="用户名"
                prefix-icon="User"
                size="large"
                class="custom-input"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                prefix-icon="Lock"
                size="large"
                class="custom-input"
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                @click="handleLogin"
                :loading="loading"
                class="full-width login-btn"
                size="large"
              >
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 注册面板 -->
        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            class="login-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="用户名（至少3个字符）"
                prefix-icon="User"
                size="large"
                class="custom-input"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码（至少6个字符）"
                prefix-icon="Lock"
                size="large"
                class="custom-input"
              />
            </el-form-item>
            
            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="确认密码"
                prefix-icon="Lock"
                size="large"
                class="custom-input"
              />
            </el-form-item>
            
            <el-form-item prop="realName">
              <el-input
                v-model="registerForm.realName"
                placeholder="真实姓名"
                prefix-icon="User"
                size="large"
                class="custom-input"
              />
            </el-form-item>
            
            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                type="email"
                placeholder="邮箱（可选）"
                prefix-icon="Message"
                size="large"
                class="custom-input"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="success"
                @click="handleRegister"
                :loading="loading"
                class="full-width register-btn"
                size="large"
              >
                注册
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { login, register } from '@/api/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

// 本地图片路径 - 与Layout保持一致
const logoUrl = ref('/src/assets/logo.png')

const activeTab = ref('login')
const loading = ref(false)
const loginFormRef = ref()
const registerFormRef = ref()

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username:  '',
  password: '',
  confirmPassword: '',
  realName: '',
  email: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger:  'blur' }
  ]
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名至少3个字符', trigger:  'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  email: [
    {
      type: 'email',
      message: '邮箱格式不正确',
      trigger: 'blur'
    }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    const res = await login(loginForm)
    if (res.code === 200) {
      authStore.login(res.data)
      ElMessage.success('登录成功')
      router.push('/')
    } else {
      ElMessage.error(res.msg || '登录失败')
    }
  } catch (error) {
    ElMessage.error('验证失败')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
    loading.value = true
    
    const res = await register({
      username: registerForm.username,
      password: registerForm.password,
      real_name: registerForm.realName,
      email: registerForm.email
    })
    
    if (res.code === 201) {
      ElMessage.success('注册成功，请登录')
      activeTab.value = 'login'
      loginForm.username = registerForm.username
    } else {
      ElMessage.error(res.msg || '注册失败')
    }
  } catch (error) {
    ElMessage.error('验证失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

/* 背景图片设置 */
.background-image {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url('https://images.unsplash.com/photo-1481627834876-b7833e8f5570?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  z-index: 1;
}

/* 半透明遮罩，确保文字可读性 */
.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 2;
}

/* 登录框 */
.login-box {
  width: 420px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.25);
  padding: 40px;
  position: relative;
  z-index: 3;
}

/* 标题区域 */
.title-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 30px;
}

.title-logo {
  height: 40px;
  width: auto;
  filter: drop-shadow(0 0 8px rgba(64, 158, 255, 0.4));
}

/* 系统标题 - 与Layout组件字体保持一致 */
.login-box h1 {
  text-align: center;
  margin: 0;
  color: #1a237e;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 0.8px;
  font-family: 'Source Han Serif SC', 'STZhongsong', 'SimSun', serif;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
}

/* 表单样式 */
.login-form {
  margin-top: 10px;
}

.custom-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.95);
  border: 1px solid #dcdfe6;
}

.custom-input :deep(.el-input__wrapper:hover) {
  border-color: #409eff;
  background-color: rgba(255, 255, 255, 1);
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

/* 按钮样式 */
.full-width {
  width: 100%;
}

.login-btn {
  background: #409eff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  height: 46px;
  transition: all 0.3s ease;
}

.login-btn:hover {
  background: #337ecc;
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.3);
}

.register-btn {
  background: #67c23a;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  height: 46px;
  transition: all 0.3s ease;
}

.register-btn:hover {
  background: #529b2e;
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(103, 194, 58, 0.3);
}

/* 标签页样式 */
.custom-tabs :deep(.el-tabs__header) {
  margin-bottom: 25px;
}

.custom-tabs :deep(.el-tabs__item) {
  font-weight: 600;
  font-size: 16px;
  color: #606266;
}

.custom-tabs :deep(.el-tabs__item.is-active) {
  color: #409eff;
}

.custom-tabs :deep(.el-tabs__active-bar) {
  background-color: #409eff;
  height: 3px;
}

/* 响应式调整 */
@media (max-width: 480px) {
  .login-box {
    width: 90%;
    padding: 30px 25px;
  }
  
  .title-section {
    flex-direction: column;
    gap: 10px;
  }
  
  .login-box h1 {
    font-size: 24px;
  }
}
</style>