<template>
  <div class="admin-users">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索用户名/姓名"
            style="width: 300px"
            clearable
            @input="searchUsers"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </template>
      
      <el-table
        :data="users"
        stripe
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="phone" label="电话" width="120" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'success'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '冻结' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'active'"
              type="danger"
              size="small"
              @click="freezeUser(row.id)"
              :loading="freezingId === row.id"
              plain
            >
              <el-icon><Lock /></el-icon>
              冻结
            </el-button>
            <el-button
              v-else
              type="success"
              size="small"
              @click="unfreezeUser(row.id)"
              :loading="freezingId === row.id"
              plain
            >
              <el-icon><Unlock /></el-icon>
              解冻
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :page-sizes="[10, 20, 50]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @change="fetchUsers"
        style="text-align: center; margin-top: 20px"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getAllUsers, freezeUser as freezeUserApi, unfreezeUser as unfreezeUserApi } from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Lock,
  Unlock
} from '@element-plus/icons-vue'

const users = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const freezingId = ref(null)

const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

const fetchUsers = async () => {
  try {
    loading.value = true
    const res = await getAllUsers({
      page: pagination.page,
      per_page: pagination.per_page,
      keyword: searchKeyword.value
    })
    
    if (res.code === 200) {
      users.value = res.data
      pagination.total = res.pagination.total
    }
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const searchUsers = () => {
  pagination.page = 1
  fetchUsers()
}

const freezeUser = async (userId) => {
  try {
    await ElMessageBox.confirm('确定冻结此用户吗？冻结后用户将无法登录系统', '确认冻结', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'freeze-confirm-btn',
      cancelButtonClass: 'freeze-cancel-btn'
    })
    
    freezingId.value = userId
    const res = await freezeUserApi(userId)
    
    if (res.code === 200) {
      ElMessage.success('冻结成功')
      fetchUsers()
    } else {
      ElMessage.error(res.msg || '冻结失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('冻结失败')
    }
  } finally {
    freezingId.value = null
  }
}

const unfreezeUser = async (userId) => {
  try {
    freezingId.value = userId
    const res = await unfreezeUserApi(userId)
    
    if (res.code === 200) {
      ElMessage.success('解冻成功')
      fetchUsers()
    } else {
      ElMessage.error(res.msg || '解冻失败')
    }
  } catch (error) {
    ElMessage.error('解冻失败')
  } finally {
    freezingId.value = null
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.admin-users {
  padding-bottom: 20px;
}

.card-header {
  width: 100%;
}

:deep(.freeze-confirm-btn) {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  border: none;
  color: white;
  font-weight: 600;
}

:deep(.freeze-confirm-btn:hover) {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
}

:deep(.freeze-cancel-btn) {
  font-weight: 500;
}
</style>