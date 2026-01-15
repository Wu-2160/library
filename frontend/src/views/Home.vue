<template>
  <div class="home">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1>欢迎来到图书馆</h1>
          <p class="greeting">您好，<span class="username">{{ authStore.user?.real_name || authStore.user?.username || '游客' }}</span>！</p>
          <p class="welcome-message">这里是您的个人图书馆系统，畅享阅读乐趣，探索知识海洋。</p>
          <div class="welcome-stats">
            <div class="stat-item">
              <el-icon><Collection /></el-icon>
              <span>海量藏书</span>
            </div>
            <div class="stat-item">
              <el-icon><Reading /></el-icon>
              <span>随时借阅</span>
            </div>
            <div class="stat-item">
              <el-icon><ChatDotRound /></el-icon>
              <span>自由评论</span>
            </div>
          </div>
        </div>
        <div class="welcome-illustration">
          <div class="book-stack">
            <div class="book book-1"></div>
            <div class="book book-2"></div>
            <div class="book book-3"></div>
            <div class="book book-4"></div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 快速统计 -->
    <el-row :gutter="24" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card stat-card-1" shadow="hover">
          <div class="stat-icon">
            <el-icon><Notebook /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.borrowing }}</div>
            <div class="stat-label">正在借阅</div>
          </div>
          <div class="stat-trend">
            <span v-if="authStore.isLoggedIn">近期活跃</span>
            <span v-else>请先登录</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card stat-card-2" shadow="hover">
          <div class="stat-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.reserved }}</div>
            <div class="stat-label">预约中</div>
          </div>
          <div class="stat-trend">
            <span v-if="authStore.isLoggedIn">待借图书</span>
            <span v-else>请先登录</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card stat-card-3" shadow="hover">
          <div class="stat-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.overdue }}</div>
            <div class="stat-label">逾期</div>
          </div>
          <div class="stat-trend">
            <span v-if="authStore.isLoggedIn">请及时归还</span>
            <span v-else>请先登录</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card stat-card-4" shadow="hover">
          <div class="stat-icon">
            <el-icon><Collection /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ totalCopies }}</div>
            <div class="stat-label">总馆藏数</div>
          </div>
          <div class="stat-trend">
            <span>{{ bookTypes }}种图书</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 热门图书 -->
    <el-card class="hot-books-card" shadow="never">
      <template #header>
        <div class="section-header">
          <div class="section-title">
            <el-icon><Star /></el-icon>
            <h2>热门图书推荐</h2>
          </div>
          <router-link to="/books" class="view-all">
            查看全部
            <el-icon><ArrowRight /></el-icon>
          </router-link>
        </div>
      </template>
      
      <div v-if="hotBooks.length > 0" class="books-container">
        <div 
          v-for="book in hotBooks" 
          :key="book.id" 
          class="book-item"
          @click="goToBookDetail(book.id)"
        >
          <div class="book-cover-container">
            <div class="book-cover">
              <div class="book-icon">
                <el-icon><Notebook /></el-icon>
              </div>
            </div>
            <div class="book-tag" :class="getCategoryClass(book.category_id)">
              {{ getCategoryName(book.category_id) }}
            </div>
          </div>
          
          <div class="book-details">
            <h3 class="book-title">{{ book.title }}</h3>
            <p class="book-author">
              <el-icon><User /></el-icon>
              {{ book.author || '未知作者' }}
            </p>
            
            <div class="book-info">
              <div class="info-item">
                <span class="info-label">ISBN:</span>
                <span class="info-value">{{ book.isbn || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">出版社:</span>
                <span class="info-value">{{ book.publisher || '未知' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">价格:</span>
                <span class="info-value price">¥{{ formatPrice(book.price) }}</span>
              </div>
            </div>
            
            <div class="book-meta">
              <div class="meta-item">
                <el-icon><Star /></el-icon>
                <span>{{ book.avg_rating?.toFixed(1) || '0.0' }}</span>
              </div>
              <div class="meta-item">
                <el-icon><Notebook /></el-icon>
                <span>{{ book.borrowed_count || 0 }}次借阅</span>
              </div>
              <div class="meta-item">
                <el-icon><Files /></el-icon>
                <span>{{ book.stock || 0 }}本可借</span>
              </div>
            </div>
            
            <div class="book-actions">
              <el-button 
                type="primary" 
                size="small" 
                @click.stop="goToBookDetail(book.id)"
                class="detail-btn"
              >
                查看详情
              </el-button>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-books">
        <el-empty description="暂无热门图书数据">
          <el-button type="primary" @click="$router.push('/books')">浏览全部图书</el-button>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getPopularBooks, getBooks } from '@/api/book'
import { getMyBorrowRecords, getOverdueRecords } from '@/api/borrow'
import { getMyReservations } from '@/api/reservation'
import { 
  Collection, 
  Reading, 
  ChatDotRound, 
  Notebook, 
  Clock, 
  Warning, 
  Star, 
  ArrowRight, 
  User,
  Files
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const hotBooks = ref([])
const stats = ref({
  borrowing:0,
  reserved:0,
  overdue:0
})

const loading = ref(true)

// 图书副本总数（所有图书的total字段之和）
const totalCopies = ref(0)
// 图书种类数（不同的图书记录数）
const bookTypes = ref(0)

// 获取分类名称
const getCategoryName = (categoryId) => {
  const categoryMap = {
    1:'文学小说',
    2:'计算机科学',
    3:'历史传记',
    4:'哲学宗教',
    5:'艺术设计'
  }
  return categoryMap[categoryId] || '未分类'
}

// 获取分类样式类
const getCategoryClass = (categoryId) => {
  const classMap = {
    1:'category-literature',
    2:'category-technology',
    3:'category-history',
    4:'category-philosophy',
    5:'category-art'
  }
  return classMap[categoryId] || ''
}

// 格式化价格
const formatPrice = (price) => {
  if (price === undefined || price === null) return '0.00'
  return parseFloat(price).toFixed(2)
}

const goToBookDetail = (bookId) => {
  router.push(`/books/${bookId}`)
}

const fetchData = async () => {
  loading.value = true
  try {
    // 1. 获取热门图书
    const booksRes = await getPopularBooks(8)
    if (booksRes.code === 200) {
      hotBooks.value = booksRes.data
    }
    
    // 2. 获取所有图书以计算副本总数
    // 这里需要获取所有图书数据，可能需要分页获取
    const allBooksRes = await getBooks({ page:1, per_page:1000 }) // 假设不会有超过1000本书
    if (allBooksRes.code === 200 && allBooksRes.data) {
      // 计算副本总数
      totalCopies.value = allBooksRes.data.reduce((sum, book) => sum + (book.total || 0), 0)
      // 获取种类数（记录数）
      bookTypes.value = allBooksRes.data.length
    }
    
    // 3. 获取借阅统计（需要登录）
    if (authStore.isLoggedIn) {
      // 获取正在借阅的图书
      const borrowRes = await getMyBorrowRecords({ status:'borrowed' })
      if (borrowRes.code === 200) {
        stats.value.borrowing = borrowRes.data.length
      }
      
      // 获取预约中的图书
      const reservRes = await getMyReservations({ status:'waiting' })
      if (reservRes.code === 200) {
        stats.value.reserved = reservRes.data.length
      }
      
      // 获取逾期图书
      const overdueRes = await getOverdueRecords()
      if (overdueRes.code === 200) {
        stats.value.overdue = overdueRes.data.length
      }
    } else {
      // 如果未登录，显示提示信息或使用默认值
      stats.value.borrowing = 0
      stats.value.reserved = 0
      stats.value.overdue = 0
    }
  } catch (error) {
    console.error('获取数据失败', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.home {
  padding:20px;
  max-width:1400px;
  margin:0 auto;
}

/* 欢迎卡片 */
.welcome-card {
  border:none;
  background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color:white;
  border-radius:16px;
  margin-bottom:24px;
  overflow:hidden;
}

.welcome-card :deep(.el-card__body) {
  padding:0;
}

.welcome-content {
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:40px;
  min-height:200px;
}

.welcome-text {
  flex:1;
}

.welcome-text h1 {
  margin:0 0 16px 0;
  font-size:32px;
  font-weight:700;
}

.greeting {
  font-size:18px;
  margin:0 0 12px 0;
  color:rgba(255, 255, 255, 0.9);
}

.greeting .username {
  font-weight:600;
  color:#ffd700;
}

.welcome-message {
  font-size:16px;
  color:rgba(255, 255, 255, 0.8);
  margin:0 0 24px 0;
  line-height:1.6;
}

.welcome-stats {
  display:flex;
  gap:24px;
  margin-top:24px;
}

.stat-item {
  display:flex;
  align-items:center;
  gap:8px;
  background:rgba(255, 255, 255, 0.1);
  padding:8px 16px;
  border-radius:20px;
  backdrop-filter:blur(10px);
  border:1px solid rgba(255, 255, 255, 0.2);
}

.stat-item .el-icon {
  font-size:18px;
}

.welcome-illustration {
  width:200px;
  height:150px;
  display:flex;
  align-items:center;
  justify-content:center;
}

.book-stack {
  position:relative;
  width:120px;
  height:120px;
}

.book {
  position:absolute;
  background:white;
  border-radius:4px;
  box-shadow:0 2px 8px rgba(0, 0, 0, 0.2);
}

.book-1 {
  width:60px;
  height:80px;
  background:linear-gradient(135deg, #ff9a9e, #fad0c4);
  transform:rotate(15deg);
  left:0;
  top:0;
}

.book-2 {
  width:70px;
  height:90px;
  background:linear-gradient(135deg, #a1c4fd, #c2e9fb);
  transform:rotate(-5deg);
  left:30px;
  top:10px;
}

.book-3 {
  width:65px;
  height:85px;
  background:linear-gradient(135deg, #f6d365, #fda085);
  transform:rotate(5deg);
  left:50px;
  top:5px;
}

.book-4 {
  width:55px;
  height:75px;
  background:linear-gradient(135deg, #a8edea, #fed6e3);
  transform:rotate(-10deg);
  left:60px;
  top:20px;
}

/* 统计卡片 */
.stats-row {
  margin-bottom:32px;
}

.stat-card {
  border:none;
  border-radius:12px;
  transition:all 0.3s ease;
  height:120px;
  position:relative;
  overflow:hidden;
}

.stat-card:hover {
  transform:translateY(-5px);
}

.stat-card::before {
  content:'';
  position:absolute;
  top:0;
  left:0;
  right:0;
  height:4px;
  border-radius:12px 12px 0 0;
}

.stat-card-1::before {
  background:linear-gradient(90deg, #667eea, #764ba2);
}

.stat-card-2::before {
  background:linear-gradient(90deg, #4caf50, #8bc34a);
}

.stat-card-3::before {
  background:linear-gradient(90deg, #ff9800, #ff5722);
}

.stat-card-4::before {
  background:linear-gradient(90deg, #2196f3, #03a9f4);
}

.stat-icon {
  position:absolute;
  top:20px;
  left:20px;
  width:48px;
  height:48px;
  border-radius:12px;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:24px;
}

.stat-card-1 .stat-icon {
  background:rgba(102, 126, 234, 0.1);
  color:#667eea;
}

.stat-card-2 .stat-icon {
  background:rgba(76, 175, 80, 0.1);
  color:#4caf50;
}

.stat-card-3 .stat-icon {
  background:rgba(255, 152, 0, 0.1);
  color:#ff9800;
}

.stat-card-4 .stat-icon {
  background:rgba(33, 150, 243, 0.1);
  color:#2196f3;
}

.stat-content {
  margin-left:80px;
  padding-top:20px;
}

.stat-number {
  font-size:32px;
  font-weight:700;
  line-height:1;
  margin-bottom:8px;
}

.stat-label {
  font-size:14px;
  color:#909399;
  font-weight:500;
}

.stat-trend {
  position:absolute;
  bottom:16px;
  right:20px;
  font-size:12px;
  color:#909399;
}

/* 热门图书 */
.hot-books-card {
  border:none;
  border-radius:16px;
  box-shadow:0 4px 20px rgba(0, 0, 0, 0.08);
}

.section-header {
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:0 4px;
}

.section-title {
  display:flex;
  align-items:center;
  gap:12px;
}

.section-title h2 {
  margin:0;
  font-size:24px;
  font-weight:600;
  color:#303133;
}

.section-title .el-icon {
  color:#667eea;
  font-size:24px;
}

.view-all {
  display:flex;
  align-items:center;
  gap:6px;
  color:#667eea;
  text-decoration:none;
  font-weight:500;
  font-size:14px;
  transition:all 0.3s;
}

.view-all:hover {
  color:#764ba2;
  gap:8px;
}

/* 图书容器 */
.books-container {
  display:grid;
  grid-template-columns:repeat(auto-fill, minmax(300px, 1fr));
  gap:24px;
  margin-top:16px;
}

.book-item {
  background:white;
  border-radius:12px;
  overflow:hidden;
  cursor:pointer;
  transition:all 0.3s ease;
  border:1px solid #ebeef5;
  display:flex;
  flex-direction:column;
}

.book-item:hover {
  transform:translateY(-5px);
  box-shadow:0 8px 24px rgba(0, 0, 0, 0.12);
  border-color:#667eea;
}

/* 图书封面 - 无图片版本 */
.book-cover-container {
  position:relative;
  height:120px;
  background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow:hidden;
}

.book-cover {
  width:100%;
  height:100%;
  display:flex;
  align-items:center;
  justify-content:center;
  position:relative;
}

.book-icon {
  font-size:48px;
  color:rgba(255, 255, 255, 0.9);
}

/* 图书标签 */
.book-tag {
  position:absolute;
  top:12px;
  right:12px;
  padding:4px 12px;
  border-radius:20px;
  font-size:12px;
  font-weight:600;
  color:white;
  box-shadow:0 2px 8px rgba(0, 0, 0, 0.2);
  background:rgba(255, 255, 255, 0.2);
  backdrop-filter:blur(10px);
  border:1px solid rgba(255, 255, 255, 0.3);
}

.category-literature {
  background:rgba(64, 158, 255, 0.8);
}

.category-technology {
  background:rgba(103, 194, 58, 0.8);
}

.category-history {
  background:rgba(230, 162, 60, 0.8);
}

.category-philosophy {
  background:rgba(144, 147, 153, 0.8);
}

.category-art {
  background:rgba(245, 108, 108, 0.8);
}

/* 图书详情 */
.book-details {
  padding:20px;
  flex:1;
  display:flex;
  flex-direction:column;
}

.book-title {
  margin:0 0 12px 0;
  font-size:18px;
  font-weight:600;
  color:#303133;
  line-height:1.4;
  height:2.5em;
  overflow:hidden;
  display:-webkit-box;
  -webkit-line-clamp:2;
  -webkit-box-orient:vertical;
}

.book-author {
  display:flex;
  align-items:center;
  gap:6px;
  font-size:14px;
  color:#606266;
  margin:0 0 16px 0;
}

.book-author .el-icon {
  font-size:16px;
  color:#909399;
}

/* 图书信息 */
.book-info {
  display:flex;
  flex-direction:column;
  gap:8px;
  margin-bottom:16px;
  padding:12px 0;
  border-top:1px solid #f0f0f0;
  border-bottom:1px solid #f0f0f0;
}

.info-item {
  display:flex;
  justify-content:space-between;
  align-items:center;
  font-size:13px;
}

.info-label {
  color:#909399;
  min-width:60px;
}

.info-value {
  color:#303133;
  font-weight:500;
  text-align:right;
  flex:1;
}

.info-value.price {
  color:#f56c6c;
  font-weight:600;
}

/* 图书元数据 */
.book-meta {
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:16px;
  padding:12px 0;
  border-bottom:1px solid #f0f0f0;
}

.meta-item {
  display:flex;
  align-items:center;
  gap:4px;
  font-size:12px;
  color:#606266;
}

.meta-item .el-icon {
  color:#e6a23c;
}

/* 操作按钮 */
.book-actions {
  margin-top:auto;
  text-align:center;
}

.detail-btn {
  width:100%;
  background:linear-gradient(135deg, #667eea, #764ba2);
  border:none;
  border-radius:8px;
  font-weight:500;
  transition:all 0.3s;
}

.detail-btn:hover {
  transform:translateY(-2px);
  box-shadow:0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 空状态 */
.empty-books {
  padding:60px 0;
}

/* 响应式设计 */
@media (max-width:1200px) {
  .books-container {
    grid-template-columns:repeat(auto-fill, minmax(280px, 1fr));
  }
}

@media (max-width:768px) {
  .home {
    padding:12px;
  }
  
  .welcome-content {
    flex-direction:column;
    padding:24px;
    text-align:center;
  }
  
  .welcome-illustration {
    margin-top:24px;
    width:150px;
    height:120px;
  }
  
  .book-stack {
    width:100px;
    height:100px;
  }
  
  .welcome-text h1 {
    font-size:24px;
  }
  
  .welcome-stats {
    justify-content:center;
    flex-wrap:wrap;
  }
  
  .stats-row {
    gap:16px;
  }
  
  .stat-card {
    height:100px;
  }
  
  .stat-number {
    font-size:28px;
  }
  
  .section-title h2 {
    font-size:20px;
  }
  
  .books-container {
    grid-template-columns:repeat(auto-fill, minmax(250px, 1fr));
    gap:16px;
  }
}

@media (max-width:480px) {
  .books-container {
    grid-template-columns:1fr;
  }
  
  .welcome-stats {
    flex-direction:column;
    align-items:center;
  }
}
</style>