<template>
  <div class="home">
    <el-row :gutter="20">
      <!-- 欢迎卡片 -->
      <el-col :xs="24" :sm="24" :md="24">
        <el-card class="welcome-card">
          <template #header>
            <div class="card-header">
              <span>欢迎来到图书馆</span>
            </div>
          </template>
          <p>您好，{{ authStore.user.real_name || authStore.user.username }}！</p>
          <p>这是您的个人图书馆管理系统。您可以浏览图书、借阅、预约和评论。</p>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快速统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ stats.borrowing }}</div>
          <div class="stat-label">正在借阅</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ stats.reserved }}</div>
          <div class="stat-label">预约中</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ stats.overdue }}</div>
          <div class="stat-label">逾期</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ stats.totalBooks }}</div>
          <div class="stat-label">总藏书</div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 热门图书 -->
    <el-card class="hot-books-card">
      <template #header>
        <div class="card-header">
          <span>热门图书</span>
          <router-link to="/books" class="view-all">查看全部 →</router-link>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col v-for="book in hotBooks" :key="book.id" :xs="24" :sm="12" :md="8" :lg="6">
          <div class="book-card">
            <div class="book-cover">
              <img :src="book.cover_url || 'https://via.placeholder.com/150x200?text=Book'" :alt="book.title">
            </div>
            <div class="book-info">
              <h3>{{ book.title }}</h3>
              <p class="author">{{ book.author }}</p>
              <p class="stats">
                <span>⭐ {{ book.avg_rating }}</span>
                <span>📖 {{ book.borrowed_count }}次</span>
              </p>
              <el-button
                type="primary"
                size="small"
                @click="goToBookDetail(book.id)"
              >
                详情
              </el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getPopularBooks } from '@/api/book'
import { getMyBorrowRecords, getOverdueRecords } from '@/api/borrow'
import { getMyReservations } from '@/api/reservation'
import { getImageUrl } from '@/api/book'

const router = useRouter()
const authStore = useAuthStore()

const hotBooks = ref([])
const stats = ref({
  borrowing: 0,
  reserved: 0,
  overdue: 0,
  totalBooks: 0
})



const goToBookDetail = (bookId) => {
  router.push(`/books/${bookId}`)
}

const fetchData = async () => {
  try {
    // 获取热门图书
    const booksRes = await getPopularBooks(8)
    if (booksRes.code === 200) {
      hotBooks.value = booksRes.data
    }
    
    // 获取借阅统计
    const borrowRes = await getMyBorrowRecords({ status: 'borrowed' })
    if (borrowRes.code === 200) {
      stats.value.borrowing = borrowRes.data.length
    }
    
    // 获取预约统计
    const reservRes = await getMyReservations({ status: 'waiting' })
    if (reservRes.code === 200) {
      stats.value.reserved = reservRes.data.length
    }
    
    // 获取逾期统计
    const overdueRes = await getOverdueRecords()
    if (overdueRes.code === 200) {
      stats.value.overdue = overdueRes.data.length
    }
  } catch (error) {
    console.error('获取数据失败', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.home {
  padding-bottom: 20px;
}

.welcome-card {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.welcome-card :deep(.el-card__header) {
  border-bottom: none;
}

.welcome-card p {
  margin: 10px 0;
  font-size: 14px;
}

.stats-row {
  margin:  20px 0;
}

.stat-card {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
}

.stat-number {
  font-size: 32px;
  font-weight:  bold;
  color: #667eea;
  margin: 20px 0 10px;
}

.stat-label {
  color: #606266;
  font-size:  14px;
}

.hot-books-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.view-all {
  color: #667eea;
  text-decoration: none;
  font-size: 12px;
}

.view-all:hover {
  text-decoration: underline;
}

.book-card {
  text-align: center;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
  transition: all 0.3s;
}

.book-card:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.book-cover {
  height: 180px;
  margin-bottom: 10px;
  overflow: hidden;
  border-radius: 4px;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-info h3 {
  font-size: 14px;
  margin: 10px 0 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.author {
  font-size: 12px;
  color: #909399;
  margin: 5px 0;
}

.stats {
  font-size: 11px;
  color: #606266;
  margin: 8px 0;
  display: flex;
  justify-content: center;
  gap: 10px;
}
</style>