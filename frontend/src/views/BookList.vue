<template>
  <div class="book-list">
    <!-- 搜索框 -->
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索书名、作者、ISBN..."
        clearable
        @input="searchBooks"
        @keyup.enter="searchBooks"
        size="large"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      
      <!-- 分类筛选 -->
      <el-select
        v-model="selectedCategory"
        placeholder="全部分类"
        clearable
        @change="fetchBooks"
        size="large"
        style="width:180px;"
      >
        <el-option label="全部分类" value="" />
        <el-option label="文学小说" :value="1" />
        <el-option label="计算机科学" :value="2" />
        <el-option label="历史传记" :value="3" />
        <el-option label="哲学宗教" :value="4" />
        <el-option label="艺术设计" :value="5" />
      </el-select>

      <!-- 排序方式（从标准文件整合） -->
      <el-select
        v-model="sortBy"
        placeholder="排序方式"
        @change="fetchBooks"
        size="large"
        style="width:150px;"
      >
        <el-option label="最新添加" value="created_at" />
        <el-option label="借阅次数" value="borrowed_count" />
        <el-option label="评分最高" value="avg_rating" />
      </el-select>
    </div>

    <!-- 图书列表 -->
    <div v-if="loading" class="loading">
      <el-skeleton animated :count="8" />
    </div>

    <div v-else-if="books.length > 0" class="books-grid">
      <div
        v-for="book in books"
        :key="book.id"
        class="book-card"
        @click="goToDetail(book.id)"
      >
        <!-- 书籍类型标签 -->
        <div class="book-type-tag" :class="getBookTypeClass(book.category_id)">
          {{ getCategoryName(book.category_id) }}
        </div>

        <div class="book-header">
          <h3 class="book-title">{{ book.title }}</h3>
          <p class="book-author">
            <el-icon><User /></el-icon>
            {{ book.author || '未知作者' }}
          </p>
        </div>

        <div class="book-info">
          <div class="book-meta">
            <div class="isbn-info">
              <el-icon><Document /></el-icon>
              <span class="isbn">{{ formatISBN(book.isbn) }}</span>
            </div>
            <div class="publisher-info">
              <el-icon><OfficeBuilding /></el-icon>
              <span class="publisher">{{ book.publisher || '未知出版社' }}</span>
            </div>
          </div>

          <div class="book-details">
            <div class="detail-item">
              <span class="label">价格:</span>
              <span class="value price">¥{{ formatPrice(book.price) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">库存:</span>
              <div class="stock-info">
                <el-tag 
                  size="small"
                  :type="getStockType(book.stock)"
                  effect="light"
                  class="stock-tag"
                >
                  {{ getStockText(book.stock) }}
                </el-tag>
                <span class="stock-count" :class="{ 'low-stock':book.stock <= 2 }">
                  {{ book.stock }}/{{ book.total }}本
                </span>
              </div>
            </div>
          </div>

          <!-- 统计信息（包含借阅次数和评分） -->
          <div class="book-stats">
            <div class="stat-item" v-if="book.borrowed_count">
              <el-icon><Notebook /></el-icon>
              <span>{{ book.borrowed_count || 0 }}次借阅</span>
            </div>
            <div class="stat-item" v-if="book.avg_rating">
              <el-icon><Star /></el-icon>
              <span>{{ book.avg_rating?.toFixed(1) || '0.0' }}分</span>
            </div>
            <div class="stat-item" v-if="book.total_comments !== undefined">
              <el-icon><ChatLineSquare /></el-icon>
              <span>{{ book.total_comments || 0 }}条评价</span>
            </div>
          </div>

          <div class="book-actions">
            <el-button
              v-if="book.stock > 0"
              type="primary"
              size="small"
              @click.stop="handleBorrow(book)"
              :loading="borrowLoading === book.id"
              :disabled="!isLoggedIn"
              :icon="ShoppingCart"
              class="action-btn"
            >
              {{ isLoggedIn ? '立即借阅' :'请先登录' }}
            </el-button>
            <el-button
              v-else
              type="warning"
              size="small"
              @click.stop="handleReserve(book)"
              :loading="reserveLoading === book.id"
              :disabled="!isLoggedIn"
              :icon="Clock"
              class="action-btn"
            >
              {{ isLoggedIn ? '预约图书' :'请先登录' }}
            </el-button>
            <el-button
              type="default"
              size="small"
              @click.stop="goToDetail(book.id)"
              :icon="View"
              class="action-btn"
            >
              查看详情
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 无数据 -->
    <div v-else class="empty">
      <el-empty description="暂无图书">
        <el-button type="primary" @click="resetFilters">重置筛选</el-button>
      </el-empty>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 48, 96]"
        :total="totalBooks"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchBooks"
        @current-change="fetchBooks"
        background
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  getBooks
} from '@/api/book'
import { borrowBook as borrowBookApi } from '@/api/borrow'
import { reserveBook as reserveBookApi } from '@/api/reservation'
import { useAuthStore } from '@/stores/auth'
import {
  Search,
  Document,
  OfficeBuilding,
  User,
  ShoppingCart,
  Clock,
  View,
  Star,
  Notebook,
  ChatLineSquare
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 数据
const books = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const selectedCategory = ref('')
const sortBy = ref('created_at') // 排序方式（从标准文件整合）
const borrowLoading = ref(null)
const reserveLoading = ref(null)

// 分页
const currentPage = ref(1)
const pageSize = ref(12)
const totalBooks = ref(0)

// 权限检查
const isLoggedIn = computed(() => authStore.isLoggedIn)

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

// 获取分类颜色类名
const getBookTypeClass = (categoryId) => {
  const classMap = {
    1:'type-literature',
    2:'type-technology',
    3:'type-history',
    4:'type-philosophy',
    5:'type-art'
  }
  return classMap[categoryId] || ''
}

// 库存类型映射
const getStockType = (stock) => {
  if (stock === 0) return 'danger'
  if (stock <= 2) return 'warning'
  return 'success'
}

// 获取库存文本
const getStockText = (stock) => {
  if (stock === 0) return '无库存'
  if (stock <= 2) return '库存紧张'
  return '有库存'
}

// 格式化价格
const formatPrice = (price) => {
  if (price === undefined || price === null) return '0.00'
  return parseFloat(price).toFixed(2)
}

// 格式化ISBN
const formatISBN = (isbn) => {
  if (!isbn) return 'N/A'
  const cleanISBN = isbn.replace(/[-\s]/g, '')
  if (cleanISBN.length === 13) {
    return `${cleanISBN.slice(0, 3)}-${cleanISBN.slice(3, 4)}-${cleanISBN.slice(4, 7)}-${cleanISBN.slice(7, 12)}-${cleanISBN.slice(12)}`
  }
  return isbn
}

// 获取图书列表（整合排序功能）
const fetchBooks = async () => {
  loading.value = true
  try {
    const params = {
      page:currentPage.value,
      per_page:pageSize.value,
      keyword:searchKeyword.value,
      sort_by:sortBy.value // 添加排序参数
    }
    
    if (selectedCategory.value) {
      params.category_id = selectedCategory.value
    }
    
    const res = await getBooks(params)
    
    if (res.code === 200) {
      books.value = res.data
      totalBooks.value = res.pagination?.total || res.data.length
      
      // 为没有描述的书籍添加默认描述
      books.value.forEach(book => {
        if (!book.description) {
          book.description = getDefaultDescription(book)
        }
      })
    } else {
      ElMessage.error(res.msg || '获取图书失败')
      books.value = []
    }
  } catch (error) {
    console.error('获取图书失败:', error)
    ElMessage.error('获取图书失败')
    books.value = []
  } finally {
    loading.value = false
  }
}

// 根据书籍信息生成默认描述
const getDefaultDescription = (book) => {
  const descriptions = {
    '978-7-115-29099-8':'本书系统全面地介绍了Python编程语言的各个方面，从基础语法到高级应用，适合Python初学者和有一定经验的开发者阅读。',
    '978-7-115-52311-7':'《三体》是刘慈欣创作的系列长篇科幻小说，作品讲述了地球人类文明和三体文明的信息交流、生死搏杀及两个文明在宇宙中的兴衰历程。',
    '978-7-201-04607-2':'《人类简史：从动物到上帝》是以色列历史学家尤瓦尔·赫拉利创作的历史类著作，讲述了人类从石器时代至21世纪的演化与发展史。',
    '978-7-010-09127-2':'《道德经》是中国古代先秦诸子分家前的一部著作，是道家哲学思想的重要来源。内容涵盖哲学、伦理学、政治学、军事学等诸多学科。',
    '978-7-218-13563-4':'本书介绍了艺术史上的重要艺术家及其代表作品，涵盖绘画、雕塑、建筑等多个艺术领域，是了解艺术的入门读物。'
  }
  
  return descriptions[book.isbn] || `《${book.title}》是一本优秀的${getCategoryName(book.category_id)}类书籍，值得一读。`
}

// 搜索图书
const searchBooks = () => {
  currentPage.value = 1
  fetchBooks()
}

// 重置筛选
const resetFilters = () => {
  searchKeyword.value = ''
  selectedCategory.value = ''
  sortBy.value = 'created_at'
  currentPage.value = 1
  fetchBooks()
}

// 借阅图书（使用标准文件的API调用）
const handleBorrow = async (book) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  borrowLoading.value = book.id
  try {
    const res = await borrowBookApi(book.id)
    
    if (res.code === 200) {
      ElMessage.success(`成功借阅《${book.title}》`)
      
      // 更新本地库存显示
      book.stock--
      if (book.borrowed_count !== undefined) {
        book.borrowed_count++
      }
    } else {
      ElMessage.error(res.msg || '借阅失败')
    }
  } catch (error) {
    ElMessage.error('借阅失败')
  } finally {
    borrowLoading.value = null
  }
}

// 预约图书（使用标准文件的API调用）
const handleReserve = async (book) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  reserveLoading.value = book.id
  try {
    const res = await reserveBookApi(book.id)
    
    if (res.code === 200) {
      ElMessage.success(`已预约《${book.title}》，图书上架后会通知您`)
    } else {
      ElMessage.error(res.msg || '预约失败')
    }
  } catch (error) {
    ElMessage.error('预约失败')
  } finally {
    reserveLoading.value = null
  }
}

// 跳转到详情页
const goToDetail = (bookId) => {
  router.push(`/books/${bookId}`)
}

onMounted(() => {
  fetchBooks()
})
</script>

<style scoped>
.book-list {
  padding:20px;
  max-width:1400px;
  margin:0 auto;
}

/* 搜索栏 */
.search-bar {
  display:flex;
  gap:16px;
  margin-bottom:30px;
  align-items:center;
  flex-wrap:wrap;
}

.search-bar .el-input {
  flex:1;
  min-width:300px;
  max-width:500px;
}

/* 加载状态 */
.loading {
  padding:40px 0;
}

/* 图书网格 */
.books-grid {
  display:grid;
  grid-template-columns:repeat(auto-fill, minmax(320px, 1fr));
  gap:24px;
  margin-bottom:40px;
}

/* 图书卡片 */
.book-card {
  background:white;
  border-radius:12px;
  overflow:hidden;
  box-shadow:0 4px 12px rgba(0, 0, 0, 0.08);
  transition:all 0.3s ease;
  cursor:pointer;
  padding:20px;
  position:relative;
  border:1px solid #e8e8e8;
  height:100%;
  display:flex;
  flex-direction:column;
}

.book-card:hover {
  transform:translateY(-5px);
  box-shadow:0 8px 24px rgba(0, 0, 0, 0.15);
  border-color:#409eff;
}

/* 书籍类型标签 */
.book-type-tag {
  position:absolute;
  top:12px;
  right:12px;
  padding:4px 12px;
  border-radius:20px;
  font-size:12px;
  font-weight:600;
  color:white;
  z-index:1;
}

.type-literature {
  background:linear-gradient(135deg, #409eff, #66b1ff);
}

.type-technology {
  background:linear-gradient(135deg, #67c23a, #85ce61);
}

.type-history {
  background:linear-gradient(135deg, #e6a23c, #ebb563);
}

.type-philosophy {
  background:linear-gradient(135deg, #909399, #a6a9ad);
}

.type-art {
  background:linear-gradient(135deg, #f56c6c, #f78989);
}

/* 图书头部 */
.book-header {
  margin-bottom:16px;
  padding-right:80px;
}

.book-title {
  margin:0 0 10px 0;
  font-size:18px;
  font-weight:700;
  color:#303133;
  line-height:1.4;
  height:2.5em;
  overflow:hidden;
  display:-webkit-box;
  -webkit-line-clamp:2;
  -webkit-box-orient:vertical;
}

.book-author {
  margin:0;
  color:#606266;
  font-size:14px;
  display:flex;
  align-items:center;
  gap:6px;
}

/* 图书信息 */
.book-info {
  display:flex;
  flex-direction:column;
  gap:16px;
  flex:1;
}

/* 元信息 */
.book-meta {
  display:flex;
  flex-direction:column;
  gap:8px;
  padding:12px 0;
  border-top:1px solid #f0f0f0;
  border-bottom:1px solid #f0f0f0;
}

.isbn-info,
.publisher-info {
  display:flex;
  align-items:center;
  gap:6px;
  font-size:13px;
  color:#606266;
}

.isbn {
  font-family:'Monaco', 'Menlo', 'Consolas', monospace;
  font-size:12px;
}

/* 详细信息 */
.book-details {
  display:flex;
  flex-direction:column;
  gap:10px;
  padding:12px 0;
}

.detail-item {
  display:flex;
  justify-content:space-between;
  align-items:center;
}

.detail-item .label {
  font-size:13px;
  color:#909399;
  min-width:60px;
}

.detail-item .value {
  font-size:14px;
  font-weight:500;
  color:#303133;
}

.price {
  color:#f56c6c;
  font-weight:600;
}

/* 库存信息 */
.stock-info {
  display:flex;
  align-items:center;
  gap:8px;
}

.stock-tag {
  font-weight:500;
  min-width:60px;
  text-align:center;
}

.stock-count {
  font-size:13px;
  color:#606266;
}

.stock-count.low-stock {
  color:#e6a23c;
  font-weight:500;
}

/* 统计信息 */
.book-stats {
  display:flex;
  gap:16px;
  padding:12px 0;
  border-top:1px solid #f0f0f0;
  border-bottom:1px solid #f0f0f0;
}

.stat-item {
  display:flex;
  align-items:center;
  gap:4px;
  font-size:12px;
  color:#909399;
}

/* 操作按钮 */
.book-actions {
  display:flex;
  gap:8px;
  margin-top:auto;
  padding-top:16px;
  border-top:1px solid #f0f0f0;
}

.action-btn {
  flex:1;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:6px;
}

/* 分页 */
.pagination {
  display:flex;
  justify-content:center;
  margin-top:40px;
}

/* 空状态 */
.empty {
  padding:80px 0;
  text-align:center;
}

/* 响应式设计 */
@media (max-width:1200px) {
  .books-grid {
    grid-template-columns:repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width:768px) {
  .book-list {
    padding:12px;
  }
  
  .search-bar {
    flex-direction:column;
    align-items:stretch;
    gap:12px;
  }
  
  .search-bar .el-input,
  .search-bar .el-select {
    max-width:100%;
    min-width:auto;
  }
  
  .books-grid {
    grid-template-columns:repeat(auto-fill, minmax(280px, 1fr));
    gap:16px;
  }
  
  .book-card {
    padding:16px;
  }
  
  .book-actions {
    flex-direction:column;
  }
  
  .action-btn {
    width:100%;
  }
}

@media (max-width:480px) {
  .books-grid {
    grid-template-columns:1fr;
  }
  
  .book-title {
    font-size:16px;
  }
  
  .book-header {
    padding-right:70px;
  }
}
</style>