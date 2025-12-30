<template>
  <div class="my-reservation">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的预约</span>
          <el-button-group>
            <el-button
              :type="filterStatus === '' ? 'primary' : 'info'"
              @click="filterStatus = ''"
            >
              全部
            </el-button>
            <el-button
              :type="filterStatus === 'waiting' ? 'primary' : 'info'"
              @click="filterStatus = 'waiting'"
            >
              等待中
            </el-button>
            <el-button
              :type="filterStatus === 'notified' ? 'primary' : 'info'"
              @click="filterStatus = 'notified'"
            >
              已通知
            </el-button>
            <el-button
              :type="filterStatus === 'cancelled' ? 'primary' : 'info'"
              @click="filterStatus = 'cancelled'"
            >
              已取消
            </el-button>
          </el-button-group>
        </div>
</template>
      
      <el-empty v-if="reservations.length === 0" description="暂无预约" />
      
      <el-row v-else :gutter="20">
        <el-col v-for="res in reservations" :key="res.id" :xs="24" :sm="12" :md="8">
          <el-card class="reservation-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="book-title">{{ res.book_title }}</span>
                <el-tag
                  :type="res.status === 'waiting' ? 'warning' :  res.status === 'notified' ? 'success' : 'info'"
                >
                  {{ statusText(res.status) }}
                </el-tag>
              </div>
</template>
            
            <el-descriptions :column="1" size="small">
              <el-descriptions-item label="队列位置">
                第 {{ res.queue_position }} 位
              </el-descriptions-item>
              <el-descriptions-item label="预约时间">
                {{ formatDate(res.reserve_time) }}
              </el-descriptions-item>
              <el-descriptions-item label="预约状态">
                <el-tag>{{ statusText(res.status) }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>
            
            <div class="actions">
              <el-button
                v-if="res.status !== 'cancelled'"
                type="danger"
                size="small"
                @click="cancelReservation(res.id)"
                :loading="cancelingId === res.id"
              >
                取消预约
              </el-button>
              <el-button
                type="primary"
                size="small"
                @click="goToBookDetail(res.book_id)"
              >
                查看图书
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMyReservations, cancelReservation as cancelReservationApi } from '@/api/reservation'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

const reservations = ref([])
const filterStatus = ref('')
const cancelingId = ref(null)

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const statusText = (status) => {
  const statusMap = {
    'waiting': '等待中',
    'notified':  '已通知',
    'cancelled': '已取消',
    'finished': '已完成'
  }
  return statusMap[status] || status
}

const fetchReservations = async () => {
  try {
    const res = await getMyReservations({
      status: filterStatus.value || undefined
    })
    
    if (res.code === 200) {
      reservations.value = res.data
    } else {
      ElMessage.error('获取预约记录失败')
    }
  } catch (error) {
    ElMessage.error('获取预约记录失败')
  }
}

const cancelReservation = async (reservationId) => {
  try {
    await ElMessageBox.confirm('确定取消此预约吗？', '提示', {
      confirmButtonText:  '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    cancelingId.value = reservationId
    const res = await cancelReservationApi(reservationId)
    
    if (res.code === 200) {
      ElMessage.success('取消成功')
      fetchReservations()
    } else {
      ElMessage.error(res.msg || '取消失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  } finally {
    cancelingId.value = null
  }
}

const goToBookDetail = (bookId) => {
  router.push(`/books/${bookId}`)
}

watch(() => filterStatus.value, () => {
  fetchReservations()
})

onMounted(() => {
  fetchReservations()
})
</script>

<style scoped>
.my-reservation {
  padding-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 10px;
}

.book-title {
  flex: 1;
  font-weight: bold;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.reservation-card {
  height: 100%;
}

.reservation-card :deep(.el-card__header) {
  padding: 15px;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.actions :deep(.el-button) {
  flex: 1;
}
</style>