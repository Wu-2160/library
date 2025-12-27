<template>
  <div class="user-profile">
    <el-row :gutter="20">
      <!-- 个人信息 -->
      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>个人信息</span>
              <el-button type="primary" size="small" @click="editMode = true">
                编辑
              </el-button>
            </div>
</template>
          
          <el-form v-if="! editMode" :model="userInfo" label-width="100px">
            <el-form-item label="用户名">
              {{ userInfo.username }}
            </el-form-item>
            <el-form-item label="姓名">
              {{ userInfo.real_name || '-' }}
            </el-form-item>
            <el-form-item label="邮箱">
              {{ userInfo.email || '-' }}
            </el-form-item>
            <el-form-item label="电话">
              {{ userInfo.phone || '-' }}
            </el-form-item>
            <el-form-item label="账户等级">
              <el-tag :type="userInfo.role === 'admin' ? 'danger' : 'success'">
                {{ userInfo.role === 'admin' ? '管理员' : '普通用户' }}
              </el-tag>
            </el-form-item>
            <el-form-item label="账户状态">
              <el-tag :type="userInfo.status === 'active' ? 'success' : 'danger'">
                {{ userInfo.status === 'active' ? '正常' : '冻结' }}
              </el-tag>
            </el-form-item>
            <el-form-item label="注册时间">
              {{ formatDate(userInfo.created_at) }}
            </el-form-item>
          </el-form>
          
          <el-form v-else :model="editForm" label-width="100px">
            <el-form-item label="姓名">
              <el-input v-model="editForm.real_name" placeholder="请输入姓名" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="editForm.email" type="email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="电话">
              <el-input v-model="editForm.phone" placeholder="请输入电话" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="updateProfile" :loading="updating">
                保存
              </el-button>
              <el-button @click="editMode = false">
                取消
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <!-- 修改密码 -->
      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>修改密码</span>
            </div>
</template>
          
          <el-form :model="passwordForm" label-width="100px">
            <el-form-item label="旧密码">
              <el-input
                v-model="passwordForm.old_password"
                type="password"
                placeholder="请输入旧密码"
              />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input
                v-model="passwordForm.new_password"
                type="password"
                placeholder="请输入新密码（至少6个字符）"
              />
            </el-form-item>
            <el-form-item label="确认密码">
              <el-input
                v-model="passwordForm.confirm_password"
                type="password"
                placeholder="请再次输入新密码"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="updatePassword" :loading="passwordUpdating">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getProfile, updateProfile as updateProfileApi, changePassword } from '@/api/user'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()

const userInfo = ref({...authStore.user})
const editMode = ref(false)
const updating = ref(false)
const passwordUpdating = ref(false)

const editForm = reactive({
  real_name: '',
  email: '',
  phone: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const fetchProfile = async () => {
  try {
    const res = await getProfile()
    if (res.code === 200) {
      userInfo.value = res.data
      editForm.real_name = res.data.real_name || ''
      editForm.email = res.data.email || ''
      editForm.phone = res.data.phone || ''
    }
  } catch (error) {
    ElMessage.error('获取个人信息失败')
  }
}

const updateProfile = async () => {
  try {
    updating.value = true
    const res = await updateProfileApi(editForm)
    
    if (res.code === 200) {
      ElMessage.success('更新成功')
      authStore.updateUser(res.data)
      userInfo.value = res.data
      editMode.value = false
    } else {
      ElMessage.error(res.msg || '更新失败')
    }
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    updating.value = false
  }
}

const updatePassword = async () => {
  if (!passwordForm.old_password) {
    ElMessage.warning('请输入旧密码')
    return
  }
  
  if (!passwordForm.new_password || passwordForm.new_password.length < 6) {
    ElMessage.warning('新密码至少6个字符')
    return
  }
  
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  
  try {
    passwordUpdating.value = true
    const res = await changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    
    if (res.code === 200) {
      ElMessage.success('密码修改成功')
      passwordForm.old_password = ''
      passwordForm.new_password = ''
      passwordForm.confirm_password = ''
    } else {
      ElMessage.error(res.msg || '密码修改失败')
    }
  } catch (error) {
    ElMessage.error('密码修改失败')
  } finally {
    passwordUpdating.value = false
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.user-profile {
  padding-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

:deep(.el-form-item__label) {
  color: #606266;
}
</style>