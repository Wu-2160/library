<template>
  <el-container>
    <!-- 顶部导航 -->
    <el-header class="header">
      <div class="header-left">
        <h2>📚 图书馆管理系统</h2>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-menu">
            {{ authStore.user.username }}
            <i class="el-icon-arrow-down"></i>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="notifications">通知</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
</template>
        </el-dropdown>
      </div>
    </el-header>
    
    <el-container>
      <!-- 左侧菜单 -->
      <el-aside class="sidebar">
        <el-menu
          router
          :default-active="currentRoute.path"
        >
          <el-menu-item index="/">
            <template #title>
              <span>首页</span>
</template>
          </el-menu-item>
          
          <el-menu-item index="/books">
            <template #title>
              <span>图书浏览</span>
</template>
          </el-menu-item>
          
          <el-menu-item index="/my-borrow">
            <template #title>
              <span>我的借阅</span>
</template>
          </el-menu-item>
          
          <el-menu-item index="/my-reservation">
            <template #title>
              <span>我的预约</span>
</template>
          </el-menu-item>
          
          <!-- 管理员菜单 -->
          <template v-if="authStore.userRole === 'admin'">
            <el-divider />
            <el-sub-menu index="admin">
              <template #title>
                <span>管理员功能</span>
</template>
              <el-menu-item index="/admin/dashboard">仪表盘</el-menu-item>
              <el-menu-item index="/admin/users">用户管理</el-menu-item>
              <el-menu-item index="/admin/books">图书管理</el-menu-item>
              <el-menu-item index="/admin/statistics">数据统计</el-menu-item>
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
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const currentRoute = useRoute()
const authStore = useAuthStore()

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'notifications') {
    // 打开通知面板
  }
}
</script>

<style scoped>
.header {
  background-color: #333;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header-left h2 {
  margin: 0;
  font-size:  20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-menu {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.sidebar {
  background-color: #f5f7fa;
  padding-top: 20px;
  width: 200px ! important;
}

:deep(.el-menu) {
  border-right: none;
  background-color: #f5f7fa;
}

.main {
  padding: 20px;
}
</style>