<template>
  <div class="admin-dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-number">{{ stats.total_users }}</div>
          <div class="stat-label">总用户数</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon">📚</div>
          <div class="stat-number">{{ stats.total_books }}</div>
          <div class="stat-label">总图书数</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon">📖</div>
          <div class="stat-number">{{ stats.currently_borrowed }}</div>
          <div class="stat-label">当前借阅</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon">⏰</div>
          <div class="stat-number">{{ stats.overdue_books }}</div>
          <div class="stat-label">逾期图书</div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快捷导航 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="nav-card" @click="goToPage('/admin/users')">
          <div class="nav-icon">👤</div>
          <div class="nav-text">用户管理</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="nav-card" @click="goToPage('/admin/books')">
          <div class="nav-icon">📚</div>
          <div class="nav-text">图书管理</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="nav-card" @click="goToPage('/admin/statistics')">
          <div class="nav-icon">📊</div>
          <div class="nav-text">数据统计</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="nav-card">
          <div class="nav-icon">⚙️</div>
          <div class="nav-text">系统设置</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getOverviewStatistics } from '@/api/admin'
import { ElMessage } from 'element-plus'

const router = useRouter()

const stats = ref({
  total_users: 0,
  total_books: 0,
  currently_borrowed: 0,
  overdue_books: 0
})

const goToPage = (path) => {
  router.push(path)
}

const fetchStatistics = async () => {
  try {
    const res = await getOverviewStatistics()
    if (res.code === 200) {
      stats.value = res.data
    }
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
}

onMounted(() => {
  fetchStatistics()
})
</script>

<style scoped>
.admin-dashboard {
  padding-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 32px;
  margin:  10px 0;
}

.stat-number {
  font-size:  28px;
  font-weight:  bold;
  color: #667eea;
  margin: 10px 0;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.nav-card {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.nav-card:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.nav-icon {
  font-size: 40px;
  margin: 15px 0 10px;
}

.nav-text {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
}
</style>