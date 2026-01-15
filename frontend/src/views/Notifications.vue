<template>
  <div class="notifications-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>
        <el-icon><Bell /></el-icon>
        通知中心
      </h1>
      <p class="page-subtitle">查看系统通知和提醒</p>
    </div>

    <!-- 操作栏 -->
    <el-card class="actions-card" shadow="never">
      <div class="actions-content">
        <div class="filter-buttons">
          <el-button-group>
            <el-button
              :type="filterStatus === null ? 'primary' : 'default'"
              @click="changeFilter(null)"
            >
              全部
            </el-button>
            <el-button
              :type="filterStatus === 0 ? 'primary' : 'default'"
              @click="changeFilter(0)"
            >
              未读
            </el-button>
            <el-button
              :type="filterStatus === 1 ? 'primary' : 'default'"
              @click="changeFilter(1)"
            >
              已读
            </el-button>
          </el-button-group>
        </div>
        <div class="action-buttons">
          <el-button
            type="primary"
            :loading="markingAll"
            @click="markAllAsRead"
            :disabled="!hasUnread"
          >
            <template #icon>
              <el-icon><Check /></el-icon>
            </template>
            全部标记已读
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 通知列表 -->
    <div v-loading="loading" class="notifications-list">
      <div v-if="notifications.length === 0" class="empty-notifications">
        <el-empty description="暂无通知">
          <el-button type="primary" @click="fetchNotifications">
            刷新
          </el-button>
        </el-empty>
      </div>

      <div v-else class="notifications-container">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          :class="['notification-item', { unread: !notification.is_read }]"
          @click="toggleReadStatus(notification)"
        >
          <!-- 通知图标 -->
          <div class="notification-icon">
            <el-icon :size="24" :color="getNotificationIcon(notification).color">
              <component :is="getNotificationIcon(notification).icon" />
            </el-icon>
          </div>

          <!-- 通知内容 -->
          <div class="notification-content">
            <div class="notification-header">
              <h4 class="notification-title">{{ notification.title }}</h4>
              <div class="notification-meta">
                <span class="notification-time">{{ formatRelativeTime(notification.created_at) }}</span>
                <el-tag
                  v-if="!notification.is_read"
                  size="small"
                  type="danger"
                  effect="plain"
                  class="unread-badge"
                >
                  未读
                </el-tag>
              </div>
            </div>
            
            <div class="notification-body">
              <p class="notification-message">{{ notification.message }}</p>
            </div>

            <!-- 通知操作 -->
            <div class="notification-actions">
              <el-button
                v-if="notification.related_url"
                type="text"
                size="small"
                @click.stop="goToRelatedUrl(notification)"
              >
                查看详情
              </el-button>
              <el-button
                v-if="!notification.is_read"
                type="text"
                size="small"
                @click.stop="markAsRead(notification.id)"
                :loading="markingId === notification.id"
              >
                标记已读
              </el-button>
            </div>
          </div>

          <!-- 选中状态指示器 -->
          <div v-if="!notification.is_read" class="unread-indicator"></div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="notifications.length > 0" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="totalNotifications"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        background
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Bell,
  Check,
  CircleCheck,
  CircleClose,
  Warning,
  InfoFilled,
  Clock,
  Document,
  User
} from '@element-plus/icons-vue'
import {
  getNotifications,
  markAsRead as markAsReadApi,
  readAllNotifications as readAllNotificationsApi
} from '@/api/notification'

const router = useRouter()

// 响应式数据
const notifications = ref([])
const loading = ref(false)
const markingAll = ref(false)
const markingId = ref(null)
const filterStatus = ref(null) // null:全部, 0:未读, 1:已读

// 分页数据
const currentPage = ref(1)
const pageSize = ref(20)
const totalNotifications = ref(0)

// 计算属性
const hasUnread = computed(() => {
  return notifications.value.some(notification => !notification.is_read)
})

// 获取通知类型对应的图标
const getNotificationIcon = (notification) => {
  const typeMap = {
    'borrow': { icon: Document, color: '#409eff' }, // 借阅相关
    'return': { icon: CircleCheck, color: '#67c23a' }, // 归还相关
    'reservation': { icon: Clock, color: '#e6a23c' }, // 预约相关
    'overdue': { icon: CircleClose, color: '#f56c6c' }, // 逾期相关
    'system': { icon: InfoFilled, color: '#909399' }, // 系统通知
    'warning': { icon: Warning, color: '#e6a23c' } // 警告通知
  }
  
  // 根据标题或类型判断
  const title = notification.title.toLowerCase()
  if (title.includes('借阅') || title.includes('借书')) return typeMap.borrow
  if (title.includes('归还')) return typeMap.return
  if (title.includes('预约')) return typeMap.reservation
  if (title.includes('逾期')) return typeMap.overdue
  if (title.includes('警告') || title.includes('注意')) return typeMap.warning
  
  return typeMap.system
}

// 修复：处理时区问题 - 将UTC时间转换为北京时间（UTC+8）
const adjustForTimezone = (date) => {
  if (!date || isNaN(date.getTime())) return date
  
  // 获取当前时区偏移（分钟）
  const localOffset = date.getTimezoneOffset()
  // 北京时间是UTC+8，即偏移量为 -480 分钟
  const beijingOffset = -480
  
  // 如果服务器返回的是UTC时间（时区偏移为0），我们需要转换为北京时间
  // 这里我们假设服务器返回的是UTC时间
  const isUTC = localOffset === 0
  
  if (isUTC) {
    // UTC时间 -> 北京时间（UTC+8）
    return new Date(date.getTime() + (8 * 60 * 60 * 1000))
  }
  
  return date
}

const parseTimeString = (timeString) => {
  if (!timeString) return null
  
  let date
  
  // 检测是否是UTC时间字符串
  const isUTCTime = timeString.endsWith('Z') || 
                    timeString.includes('T') || 
                    /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(timeString)
  
  if (isUTCTime) {
    // 明确处理为UTC时间
    if (!timeString.endsWith('Z') && timeString.includes('T')) {
      timeString = timeString + 'Z'
    }
    date = new Date(timeString)
    // UTC时间转换为北京时间
    return new Date(date.getTime() + (8 * 60 * 60 * 1000))
  }
  
  // 其他格式尝试直接解析
  date = new Date(timeString)
  
  if (isNaN(date.getTime())) {
    console.warn('无法解析时间字符串:', timeString)
    return null
  }
  
  return date
}

const formatRelativeTime = (timeString) => {
  const date = parseTimeString(timeString)
  if (!date) return '未知时间'
  
  const now = new Date()
  const diffMs = now - date
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffSeconds < 0) return '刚刚' // 如果时间在未来（由于时区调整可能导致）
  if (diffSeconds < 60) return '刚刚'
  if (diffMinutes < 60) return `${diffMinutes}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`
  
  // 超过7天显示具体日期
  return formatShortDate(date)
}

// 格式化短日期（用于超过7天的显示）
const formatShortDate = (date) => {
  const month = date.getMonth() + 1
  const day = date.getDate()
  const today = new Date()
  
  // 如果是今年，只显示月日
  if (date.getFullYear() === today.getFullYear()) {
    return `${month}月${day}日`
  }
  
  // 不同年份显示完整日期
  return `${date.getFullYear()}年${month}月${day}日`
}

// 获取通知列表
const fetchNotifications = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    
    if (filterStatus.value !== null) {
      params.is_read = filterStatus.value
    }
    
    const res = await getNotifications(params)
    
    if (res.code === 200) {
      notifications.value = res.data
      // 如果有分页信息，更新总数
      if (res.pagination) {
        totalNotifications.value = res.pagination.total
      } else {
        totalNotifications.value = res.data.length
      }
    } else {
      ElMessage.error(res.msg || '获取通知失败')
    }
  } catch (error) {
    console.error('获取通知失败:', error)
    ElMessage.error('获取通知失败')
  } finally {
    loading.value = false
  }
}

// 切换筛选状态
const changeFilter = (status) => {
  filterStatus.value = status
  currentPage.value = 1
  fetchNotifications()
}

// 标记单条通知为已读
const markAsRead = async (notificationId) => {
  try {
    markingId.value = notificationId
    const res = await markAsReadApi(notificationId)
    
    if (res.code === 200) {
      ElMessage.success('标记已读成功')
      // 更新本地状态
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index !== -1) {
        notifications.value[index].is_read = true
      }
    } else {
      ElMessage.error(res.msg || '标记失败')
    }
  } catch (error) {
    console.error('标记失败:', error)
    ElMessage.error('标记失败')
  } finally {
    markingId.value = null
  }
}

// 点击通知切换已读状态
const toggleReadStatus = (notification) => {
  if (!notification.is_read) {
    markAsRead(notification.id)
  }
}

// 全部标记已读
const markAllAsRead = async () => {
  try {
    markingAll.value = true
    const res = await readAllNotificationsApi()
    
    if (res.code === 200) {
      ElMessage.success('全部标记已读成功')
      // 更新所有通知为已读状态
      notifications.value.forEach(notification => {
        notification.is_read = true
      })
    } else {
      ElMessage.error(res.msg || '操作失败')
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  } finally {
    markingAll.value = false
  }
}

// 跳转到相关链接
const goToRelatedUrl = (notification) => {
  if (notification.related_url) {
    router.push(notification.related_url)
  }
}

// 分页处理
const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
  fetchNotifications()
}

const handlePageChange = (newPage) => {
  currentPage.value = newPage
  fetchNotifications()
}

// 生命周期
onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped>
.notifications-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 120px);
}

/* 页面标题 */
.page-header {
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e8e8e8;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-header .el-icon {
  color: #3b82f6;
  font-size: 32px;
}

.page-subtitle {
  margin: 8px 0 0;
  color: #6b7280;
  font-size: 14px;
}

/* 操作栏 */
.actions-card {
  margin-bottom: 24px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.actions-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.filter-buttons .el-button-group {
  display: flex;
  gap: 1px;
}

.filter-buttons .el-button {
  border-radius: 6px;
  padding: 8px 20px;
}

.action-buttons .el-button {
  border-radius: 8px;
  padding: 8px 20px;
}

/* 通知列表 */
.notifications-list {
  min-height: 400px;
}

.empty-notifications {
  padding: 80px 0;
  text-align: center;
}

/* 通知项 */
.notifications-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notification-item {
  position: relative;
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 20px 24px;
  display: flex;
  gap: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.notification-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
}

.notification-item.unread {
  background: #f8fafc;
  border-left: 4px solid #3b82f6;
}

/* 未读指示器 */
.unread-indicator {
  position: absolute;
  top: 24px;
  right: 24px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 通知图标 */
.notification-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 通知内容 */
.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}

.notification-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  flex: 1;
  min-width: 200px;
}

.notification-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.notification-time {
  font-size: 13px;
  color: #6b7280;
  white-space: nowrap;
}

.unread-badge {
  font-size: 11px;
  padding: 2px 8px;
  height: auto;
  border-radius: 10px;
}

/* 通知正文 */
.notification-body {
  margin-bottom: 16px;
}

.notification-message {
  margin: 0;
  color: #4b5563;
  line-height: 1.6;
  font-size: 14px;
}

/* 通知操作 */
.notification-actions {
  display: flex;
  gap: 16px;
}

.notification-actions .el-button {
  padding: 4px 8px;
  font-size: 13px;
}

.notification-actions .el-button--text {
  color: #3b82f6;
}

.notification-actions .el-button--text:hover {
  color: #2563eb;
}

/* 分页 */
.pagination-container {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e8e8e8;
  display: flex;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .notifications-page {
    padding: 16px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .actions-content {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .filter-buttons {
    display: flex;
    justify-content: center;
  }
  
  .action-buttons {
    display: flex;
    justify-content: center;
  }
  
  .notification-item {
    padding: 16px;
    flex-direction: column;
    gap: 16px;
  }
  
  .notification-icon {
    width: 40px;
    height: 40px;
  }
  
  .notification-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .notification-title {
    min-width: auto;
  }
  
  .notification-meta {
    width: 100%;
    justify-content: space-between;
  }
  
  .unread-indicator {
    top: 16px;
    right: 16px;
  }
}

@media (max-width: 480px) {
  .notification-actions {
    flex-direction: column;
    gap: 8px;
  }
}
</style>