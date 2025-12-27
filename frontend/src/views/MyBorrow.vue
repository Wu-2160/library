<template>
  <div class="my-borrow">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的借阅</span>
          <el-button-group>
            <el-button
              :type="filterStatus === '' ? 'primary' : 'info'"
              @click="filterStatus = ''"
            >
              全部
            </el-button>
            <el-button
              :type="filterStatus === 'borrowed' ? 'primary' : 'info'"
              @click="filterStatus = 'borrowed'"
            >
              借阅中
            </el-button>
            <el-button
              :type="filterStatus === 'returned' ? 'primary' : 'info'"
              @click="filterStatus = 'returned'"
            >
              已归还
            </el-button>
            <el-button
              :type="filterStatus === 'overdue' ? 'primary' :  'info'"
              @click="filterStatus = 'overdue'"
            >
              逾期
            </el-button>
          </el-button-group>
        </div>
</template>
      
      <el-table
        :data="borrowRecords"
        stripe
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="book" label="书名" width="200" />
        <el-table-column prop="user" label="借阅人" width="120" />
        <el-table-column prop="borrow_time" label="借阅时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.borrow_time) }}
</template>
        </el-table-column>
        <el-table-column prop="due_time" label="应还时间" width="160">
          <template #default="{ row }">
            <span :class="{ 'overdue-text': isOverdue(row) }">
              {{ formatDate(row.due_time) }}
            </span>
</template>
        </el-table-column>
        <el-table-column prop="days_left" label="剩余天数" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.days_left < 0 ? 'danger' : row.days_left < 7 ? 'warning' : 'success'"
            >
              {{ row.days_left }}天
            </el-tag>
</template>
        </el-table-column>
        <el-table-column prop="return_time" label="归还时间" width="160">
          <template #default="{ row }">
            {{ row.return_time ?  formatDate(row.return_time) : '-' }}
</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'returned' ? 'success' : row.status === 'overdue' ? 'danger' : 'info'"
            >
              {{ statusText(row.status) }}
            </el-tag>
</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'borrowed'"
              type="success"
              size="small"
              @click="returnBook(row.id)"
              :loading="returningId === row.id"
            >
              归还
            </el-button>
            <el-button
              v-if="row.status === 'borrowed' && row.renewal_count < 3"
              type="warning"
              size="small"
              @click="renewBook(row.id)"
              :loading="renewingId === row.id"
            >
              续借
            </el-button>
            <el-button
              type="info"
              size="small"
              @click="goToBookDetail(row.book_id)"
            >
              图书详情
            </el-button>
</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMyBorrowRecords, returnBook as returnBookApi, renewBook as renewBookApi } from '@/api/borrow'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

const borrowRecords = ref([])
const loading = ref(false)
const filterStatus = ref('')
const returningId = ref(null)
const renewingId = ref(null)

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const statusText = (status) => {
  const statusMap = {
    'borrowed':  '借阅中',
    'returned': '已归还',
    'overdue': '逾期'
  }
  return statusMap[status] || status
}

const isOverdue = (row) => {
  return row.days_left < 0
}

const fetchBorrowRecords = async () => {
  try {
    loading.value = true
    const res = await getMyBorrowRecords({
      status: filterStatus.value || undefined
    })
    
    if (res.code === 200) {
      borrowRecords.value = res.data
    } else {
      ElMessage.error('获取借阅记录失败')
    }
  } catch (error) {
    ElMessage.error('获取借阅记录失败')
  } finally {
    loading.value = false
  }
}

const returnBook = async (recordId) => {
  try {
    await ElMessageBox.confirm('确定归还此图书吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText:  '取消',
      type:  'warning'
    })
    
    returningId.value = recordId
    const res = await returnBookApi(recordId)
    
    if (res.code === 200) {
      ElMessage.success('归还成功')
      fetchBorrowRecords()
    } else {
      ElMessage.error(res.msg || '归还失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('归还失败')
    }
  } finally {
    returningId.value = null
  }
}

const renewBook = async (recordId) => {
  try {
    renewingId.value = recordId
    const res = await renewBookApi(recordId)
    
    if (res.code === 200) {
      ElMessage.success('续借成功')
      fetchBorrowRecords()
    } else {
      ElMessage.error(res.msg || '续借失败')
    }
  } catch (error) {
    ElMessage.error('续借失败')
  } finally {
    renewingId.value = null
  }
}

const goToBookDetail = (bookId) => {
  router.push(`/books/${bookId}`)
}

watch(() => filterStatus.value, () => {
  fetchBorrowRecords()
})

onMounted(() => {
  fetchBorrowRecords()
})
</script>

<style scoped>
.my-borrow {
  padding-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.overdue-text {
  color:  #f56c6c;
  font-weight: bold;
}

:deep(.el-table) {
  font-size: 14px;
}
</style>