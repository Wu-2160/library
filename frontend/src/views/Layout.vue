[file name]: Layout(2).vue
<template>
  <el-container>
    <!-- 顶部导航 - 应用深度渐变背景 -->
    <el-header class="header">
      <div class="header-left">
        <!-- 本地图片图标占位 -->
        <img v-if="logoUrl" :src="logoUrl" alt="系统图标" class="header-logo" />
        <!-- 系统标题 - 应用优雅宋体 -->
        <h2>图书馆管理系统</h2>
      </div>
      <div class="header-right">
        <!-- 通知铃铛按钮 -->
        <div class="notifications-btn-wrapper" @click="goToNotifications">
          <el-badge 
            :value="unreadCount" 
            :max="99" 
            :hidden="unreadCount === 0"
            class="notifications-badge"
          >
            <div class="bell-container">
              <el-icon size="20" class="bell-icon">
                <Bell />
              </el-icon>
              <span class="bell-glow"></span>
            </div>
          </el-badge>
          <span class="notifications-tooltip">通知中心</span>
        </div>
        
        <el-dropdown @command="handleCommand">
          <span class="user-menu">
            {{ authStore.user.username }}
            <i class="el-icon-arrow-down"></i>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人信息
              </el-dropdown-item>
              <el-dropdown-item command="notifications">
                <el-icon><Bell /></el-icon>
                通知中心
                <el-badge 
                  v-if="unreadCount > 0" 
                  :value="unreadCount" 
                  :max="99" 
                  class="dropdown-badge"
                />
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    
    <el-container>
      <!-- 左侧菜单 - 背景改为白色 -->
      <el-aside class="sidebar">
        <el-menu
          router
          :default-active="currentRoute.path"
        >
          <el-menu-item index="/">
            <el-icon><House /></el-icon>
            <template #title>
              <span>首页</span>
            </template>
          </el-menu-item>
          
          <el-menu-item index="/books">
            <el-icon><Reading /></el-icon>
            <template #title>
              <span>图书浏览</span>
            </template>
          </el-menu-item>
          
          <el-menu-item index="/my-borrow">
            <el-icon><Notebook /></el-icon>
            <template #title>
              <span>我的借阅</span>
            </template>
          </el-menu-item>
          
          <el-menu-item index="/my-reservation">
            <el-icon><Clock /></el-icon>
            <template #title>
              <span>我的预约</span>
            </template>
          </el-menu-item>
          
          <el-menu-item index="/notifications">
            <el-icon><Bell /></el-icon>
            <template #title>
              <span>通知中心</span>
              <el-badge 
                v-if="unreadCount > 0" 
                :value="unreadCount" 
                :max="99" 
                class="menu-badge"
              />
            </template>
          </el-menu-item>
          
          <!-- 管理员菜单 -->
          <template v-if="authStore.userRole === 'admin'">
            <el-divider />
            <el-sub-menu index="admin">
              <template #title>
                <el-icon><Setting /></el-icon>
                <span>管理员功能</span>
              </template>
              <el-menu-item index="/admin/dashboard">
                <el-icon><DataAnalysis /></el-icon>
                <span>仪表盘</span>
              </el-menu-item>
              <el-menu-item index="/admin/users">
                <el-icon><UserFilled /></el-icon>
                <span>用户管理</span>
              </el-menu-item>
              <el-menu-item index="/admin/books">
                <el-icon><Notebook /></el-icon>
                <span>图书管理</span>
              </el-menu-item>
              <el-menu-item index="/admin/statistics">
                <el-icon><TrendCharts /></el-icon>
                <span>数据统计</span>
              </el-menu-item>
            </el-sub-menu>
          </template>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { 
  Bell,
  User,
  SwitchButton,
  House,
  Reading,
  Notebook,
  Clock,
  Setting,
  DataAnalysis,
  UserFilled,
  TrendCharts
} from '@element-plus/icons-vue'
import { getNotifications } from '@/api/notification'

const router = useRouter()
const currentRoute = useRoute()
const authStore = useAuthStore()

// 本地图片路径 - 请根据实际路径修改
const logoUrl = ref('/src/assets/logo.png')

// 未读通知数量
const unreadCount = ref(0)

// 跳转到通知中心
const goToNotifications = () => {
  router.push('/notifications')
}

// 获取未读通知数量
const fetchUnreadNotifications = async () => {
  if (!authStore.isLoggedIn) return
  
  try {
    const res = await getNotifications({ is_read: 0 })
    if (res.code === 200) {
      unreadCount.value = res.data.length
    }
  } catch (error) {
    console.error('获取通知数量失败', error)
  }
}

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'notifications') {
    router.push('/notifications')
  }
}

// 监听路由变化，每次切换页面都刷新通知数量
watch(
  () => currentRoute.path,
  () => {
    fetchUnreadNotifications()
  },
  { immediate: true }
)

// 定期刷新通知数量（每5分钟）
onMounted(() => {
  fetchUnreadNotifications()
  
  // 定时刷新通知数量
  const intervalId = setInterval(fetchUnreadNotifications, 5 * 60 * 1000)
  
  // 组件卸载时清除定时器
  return () => clearInterval(intervalId)
})
</script>

<style scoped>
/* 顶部导航栏 - 深度渐变背景 */
.header {
  /* 经典深蓝渐变背景 */
  background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #1a237e 100%);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  height: 60px;
}

/* 可选：顶部光晕效果 */
.header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(100, 181, 246, 0.4) 50%, 
    transparent 100%);
  z-index: 1;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  z-index: 2;
}

.header-logo {
  height: 38px;
  width: auto;
  transition: all 0.3s ease;
  /* 为浅蓝色图标添加发光效果 */
  filter: drop-shadow(0 0 8px rgba(100, 181, 246, 0.3));
}

.header-logo:hover {
  transform: scale(1.08);
  filter: drop-shadow(0 0 12px rgba(100, 181, 246, 0.5));
}

/* 系统标题 - 优雅宋体字体 */
.header-left h2 {
  margin: 0;
  font-size: 21px;
  /* 使用更优雅的宋体字体 */
  font-family: 'Source Han Serif SC', 'STZhongsong', 'SimSun', serif;
  font-weight: 700;
  color: white;
  letter-spacing: 0.8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  position: relative;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
  z-index: 2;
}

/* 通知按钮包装器 */
.notifications-btn-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  position: relative;
  transition: transform 0.3s ease;
}

.notifications-btn-wrapper:hover {
  transform: translateY(-2px);
}

.notifications-btn-wrapper:hover .bell-icon {
  animation: ring 0.5s ease-in-out;
}

.notifications-btn-wrapper:hover .notifications-tooltip {
  opacity: 1;
  transform: translateY(0);
}

/* 铃铛容器 */
.bell-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.notifications-btn-wrapper:hover .bell-container {
  background: rgba(100, 181, 246, 0.2);
  border-color: rgba(100, 181, 246, 0.3);
  box-shadow: 0 0 15px rgba(100, 181, 246, 0.3);
}

/* 铃铛图标 */
.bell-icon {
  color: #bbdefb;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.notifications-btn-wrapper:hover .bell-icon {
  color: #64b5f6;
}

/* 铃铛光晕效果 */
.bell-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background: radial-gradient(circle at center, rgba(100, 181, 246, 0.2) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.notifications-btn-wrapper:hover .bell-glow {
  opacity: 1;
}

/* 铃铛动画 */
@keyframes ring {
  0%, 100% {
    transform: rotate(0deg);
  }
  25% {
    transform: rotate(10deg);
  }
  75% {
    transform: rotate(-10deg);
  }
}

/* 通知徽章 */
.notifications-badge :deep(.el-badge__content) {
  top: 2px;
  right: 2px;
  border: 2px solid #1a237e;
  background: linear-gradient(135deg, #ff5252, #ff4081);
  font-size: 10px;
  font-weight: 600;
  height: 16px;
  line-height: 12px;
  min-width: 16px;
  box-shadow: 0 2px 8px rgba(255, 82, 82, 0.4);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 2px 8px rgba(255, 82, 82, 0.4);
  }
  50% {
    box-shadow: 0 2px 12px rgba(255, 82, 82, 0.6);
  }
}

/* 工具提示 */
.notifications-tooltip {
  position: absolute;
  bottom: -30px;
  left: 50%;
  transform: translateX(-50%) translateY(10px);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  transition: all 0.3s ease;
  pointer-events: none;
  z-index: 1000;
}

.notifications-tooltip::after {
  content: '';
  position: absolute;
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 4px;
  border-style: solid;
  border-color: transparent transparent rgba(0, 0, 0, 0.8) transparent;
}

.user-menu {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64b5f6;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.user-menu:hover {
  background-color: rgba(100, 181, 246, 0.15);
  color: #90caf9;
}

/* 左侧菜单栏 - 白色背景 */
.sidebar {
  background-color: #ffffff;
  padding-top: 20px;
  width: 220px !important;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  border-right: 1px solid #e4e7ed;
}

/* 菜单项样式 */
:deep(.el-menu) {
  border-right: none;
  background-color: #ffffff;
}

:deep(.el-menu-item) {
  transition: all 0.2s ease;
  margin: 4px 8px;
  border-radius: 6px;
  color: #606266;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

:deep(.el-menu-item:hover) {
  background-color: #f0f7ff;
  color: #409eff;
}

:deep(.el-menu-item.is-active) {
  background-color: #409eff;
  color: white;
}

:deep(.el-sub-menu__title) {
  color: #606266 !important;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

:deep(.el-sub-menu__title:hover) {
  color: #409eff !important;
}

/* 菜单项中的图标 */
:deep(.el-menu-item .el-icon),
:deep(.el-sub-menu__title .el-icon) {
  margin-right: 8px;
  font-size: 18px;
}

:deep(.el-menu-item.is-active .el-icon) {
  color: white !important;
}

/* 菜单项中的徽章 */
.menu-badge {
  position: absolute;
  right: 40px;
  top: 50%;
  transform: translateY(-50%);
}

.menu-badge :deep(.el-badge__content) {
  border: none;
  font-size: 10px;
  height: 16px;
  line-height: 12px;
  min-width: 16px;
  background: linear-gradient(135deg, #ff5252, #ff4081);
  box-shadow: 0 2px 4px rgba(255, 82, 82, 0.2);
}

/* 下拉菜单中的徽章 */
.dropdown-badge {
  margin-left: 8px;
}

.dropdown-badge :deep(.el-badge__content) {
  border: none;
  font-size: 10px;
  height: 16px;
  line-height: 12px;
  min-width: 16px;
  background: linear-gradient(135deg, #ff5252, #ff4081);
  box-shadow: 0 2px 4px rgba(255, 82, 82, 0.2);
}

/* 下拉菜单项 */
:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

:deep(.el-dropdown-menu__item .el-icon) {
  font-size: 16px;
  margin-right: 8px;
}

:deep(.el-divider) {
  border-color: #e4e7ed !important;
  margin: 12px 0 !important;
}

/* 主内容区 */
.main {
  padding: 24px;
  background-color: #f9fafb;
  min-height: calc(100vh - 60px);
}
</style>