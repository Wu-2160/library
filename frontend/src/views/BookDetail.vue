<template>
  <div class="book-detail">
    <!-- 返回按钮 -->
    <div class="back-button">
      <el-button type="text" @click="goBack" :icon="ArrowLeft">
        返回
      </el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <el-skeleton animated :rows="10" />
    </div>

    <!-- 图书详情 -->
    <div v-else-if="book" class="book-content">
      <div class="book-header">
        <h1 class="book-title">{{ book.title }}</h1>
        <div class="book-subtitle">
          <span class="author">{{ book.author || '未知作者' }}</span>
          <el-tag 
            size="small"
            :type="getCategoryType(book.category_id)"
            effect="light"
            class="category-tag"
          >
            {{ getCategoryName(book.category_id) }}
          </el-tag>
        </div>
      </div>

      <div class="book-main">
        <!-- 基本信息卡片 -->
        <el-card class="info-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
            </div>
          </template>
          
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">ISBN</span>
              <span class="info-value isbn">{{ book.isbn || '未提供' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">出版社</span>
              <span class="info-value">{{ book.publisher || '未知' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">价格</span>
              <span class="info-value price">¥{{ formatPrice(book.price) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">库存</span>
              <el-tag 
                :type="getStockType(book.stock)"
                size="small"
                effect="light"
                class="stock-tag"
              >
                {{ book.stock === 0 ? '无库存' :`${book.stock}本（总量${book.total}本）` }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="info-label">分类</span>
              <el-tag 
                :type="getCategoryType(book.category_id)"
                size="small"
                effect="light"
              >
                {{ getCategoryName(book.category_id) }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="info-label">馆藏位置</span>
              <span class="info-value">{{ book.location || '未指定' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">出版时间</span>
              <span class="info-value">{{ book.publish_date || '未知' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">页数</span>
              <span class="info-value">{{ book.pages || '未知' }}页</span>
            </div>
            <!-- 新增：借阅次数和平均评分 -->
            <div class="info-item">
              <span class="info-label">借阅次数</span>
              <span class="info-value">{{ book.borrowed_count || 0 }}次</span>
            </div>
            <div class="info-item">
              <span class="info-label">平均评分</span>
              <div class="info-value rating">
                <el-rate v-model="book.avg_rating" disabled />
                <span class="rating-text">({{ book.avg_rating?.toFixed(1) || '0.0' }})</span>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 图书描述 -->
        <el-card class="description-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>内容简介</span>
            </div>
          </template>
          
          <div class="description-content">
            <p v-if="book.description">{{ book.description }}</p>
            <p v-else class="no-description">暂无内容简介</p>
          </div>
        </el-card>

        <!-- 操作按钮 -->
        <div class="action-section">
          <div class="action-buttons">
            <el-button
              v-if="book.stock > 0"
              type="primary"
              size="large"
              @click="handleBorrow"
              :loading="borrowing"
              :disabled="!isLoggedIn"
              :icon="ShoppingCart"
            >
              {{ isLoggedIn ? '立即借阅' :'请先登录' }}
            </el-button>
            <el-button
              v-else
              type="warning"
              size="large"
              @click="handleReserve"
              :loading="reserving"
              :disabled="!isLoggedIn"
              :icon="Clock"
            >
              {{ isLoggedIn ? '预约图书' :'请先登录' }}
            </el-button>
            <el-button
              type="default"
              size="large"
              @click="toggleFavorite"
              :icon="Star"
              :class="{ 'is-favorite':isFavorite }"
            >
              {{ isFavorite ? '已收藏' :'加入收藏' }}
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 图书不存在 -->
    <div v-else class="not-found">
      <el-empty description="图书不存在或已被删除">
        <el-button type="primary" @click="goToList">返回图书列表</el-button>
      </el-empty>
    </div>

    <!-- 评论区（从标准文件整合而来） -->
    <el-card class="comments-card" v-if="book">
      <template #header>
        <div class="card-header">
          <span>用户评价（{{ totalComments }}）</span>
        </div>
      </template>
      
      <!-- 添加评论表单 -->
      <el-form class="comment-form" @submit.prevent="submitComment">
        <el-form-item label="评分">
          <el-rate
            v-model="commentForm.rating"
            size="large"
            allow-half
          />
        </el-form-item>
        
        <el-form-item label="评论">
          <el-input
            v-model="commentForm.comment"
            type="textarea"
            rows="4"
            placeholder="分享您对这本书的看法..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            @click="submitComment"
            :loading="commentSubmitting"
            :disabled="!isLoggedIn"
          >
            {{ isLoggedIn ? '提交评价' :'请先登录' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-divider />
      
      <!-- 评论列表 -->
      <div v-if="comments.length > 0" class="comments-list">
        <div v-for="comment in comments" :key="comment.id" class="comment-item">
          <div class="comment-header">
            <span class="username">{{ comment.username }}</span>
            <el-rate v-model="comment.rating" disabled size="small" />
            <span class="time">{{ formatDate(comment.created_at) }}</span>
            <el-button
              v-if="authStore.user.id === comment.user_id || authStore.user?.role === 'admin'"
              type="danger"
              size="small"
              text
              @click="deleteComment(comment.id)"
            >
              删除
            </el-button>
          </div>
          <p class="comment-content">{{ comment.comment }}</p>
        </div>
      </div>
      <div v-else class="no-comments">暂无评价</div>
      
      <!-- 评论分页 -->
      <el-pagination
        v-model:current-page="commentPage"
        :page-size="5"
        :total="totalComments"
        layout="prev, pager, next"
        @change="fetchComments"
        style="text-align:center; margin-top:20px"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getBookDetail,
  getCategories
} from '@/api/book'
import { useAuthStore } from '@/stores/auth'
import { borrowBook as borrowBookApi } from '@/api/borrow'
import { reserveBook as reserveBookApi } from '@/api/reservation'
import { addComment, deleteComment as deleteCommentApi, getBookComments } from '@/api/comment'
import {
  ArrowLeft,
  ShoppingCart,
  Clock,
  Star
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 数据
const loading = ref(true)
const book = ref(null)
const categories = ref([])
const borrowing = ref(false)
const reserving = ref(false)
const isFavorite = ref(false)

// 评论相关（从标准文件整合）
const comments = ref([])
const commentPage = ref(1)
const totalComments = ref(0)
const commentSubmitting = ref(false)

const commentForm = ref({
  rating:5,
  comment:''
})

// 权限检查
const isLoggedIn = computed(() => authStore.isLoggedIn)

// 分类类型映射
const getCategoryType = (categoryId) => {
  const typeMap = {
    1:'primary',
    2:'success',
    3:'warning',
    4:'info',
    5:'danger'
  }
  return typeMap[categoryId] || 'info'
}

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

// 库存类型映射
const getStockType = (stock) => {
  if (stock === 0) return 'danger'
  if (stock <= 2) return 'warning'
  return 'success'
}

// 格式化价格
const formatPrice = (price) => {
  if (price === undefined || price === null) return '0.00'
  return parseFloat(price).toFixed(2)
}

// 格式化日期（从标准文件整合）
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 获取图书详情
const fetchBook = async () => {
  try {
    loading.value = true
    const bookId = route.params.id
    
    if (bookId) {
      const res = await getBookDetail(bookId)
      
      if (res.code === 200) {
        book.value = res.data
        // 确保avg_rating有值
        if (!book.value.avg_rating) book.value.avg_rating = 0
        if (!book.value.description) {
          book.value.description = getDefaultDescription(book.value)
        }
      } else {
        ElMessage.error(res.msg || '获取图书详情失败')
        book.value = null
      }
    } else {
      book.value = null
    }
  } catch (error) {
    console.error('获取图书详情失败:', error)
    ElMessage.error('获取图书详情失败')
    book.value = null
  } finally {
    loading.value = false
  }
}

// 获取评论（从标准文件整合）
const fetchComments = async () => {
  try {
    const bookId = route.params.id
    const res = await getBookComments(bookId, {
      page:commentPage.value,
      per_page:5
    })
    
    if (res.code === 200) {
      comments.value = res.data
      totalComments.value = res.pagination?.total || 0
    }
  } catch (error) {
    console.error('获取评论失败', error)
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

// 获取分类列表
const fetchCategories = async () => {
  try {
    const res = await getCategories()
    if (res.code === 200) {
      categories.value = res.data
    }
  } catch (error) {
    console.error('获取分类失败', error)
  }
}

// 借阅图书（整合标准文件的API调用）
const handleBorrow = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  borrowing.value = true
  try {
    const bookId = route.params.id
    const res = await borrowBookApi(bookId)
    
    if (res.code === 200) {
      ElMessage.success('借阅成功！请在30天内归还')
      fetchBook() // 刷新图书信息
    } else {
      ElMessage.error(res.msg || '借阅失败')
    }
  } catch (error) {
    ElMessage.error('借阅失败')
  } finally {
    borrowing.value = false
  }
}

// 预约图书（整合标准文件的API调用）
const handleReserve = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  reserving.value = true
  try {
    const bookId = route.params.id
    const res = await reserveBookApi(bookId)
    
    if (res.code === 200) {
      ElMessage.success('预约成功！图书上架后会通知您')
      fetchBook() // 刷新图书信息
    } else {
      ElMessage.error(res.msg || '预约失败')
    }
  } catch (error) {
    ElMessage.error('预约失败')
  } finally {
    reserving.value = false
  }
}

// 提交评论（从标准文件整合）
const submitComment = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  if (!commentForm.value.rating) {
    ElMessage.warning('请选择评分')
    return
  }
  
  try {
    commentSubmitting.value = true
    const bookId = route.params.id
    const res = await addComment(bookId, {
      rating:commentForm.value.rating,
      comment:commentForm.value.comment
    })
    
    if (res.code === 200) {
      ElMessage.success('评价成功')
      commentForm.value.rating = 5
      commentForm.value.comment = ''
      fetchComments()
      fetchBook() // 刷新图书信息以更新平均评分
    } else {
      ElMessage.error(res.msg || '评价失败')
    }
  } catch (error) {
    ElMessage.error('评价失败')
  } finally {
    commentSubmitting.value = false
  }
}

// 删除评论（从标准文件整合）
const deleteComment = async (commentId) => {
  try {
    await ElMessageBox.confirm('确定删除此评论吗？', '提示', {
      confirmButtonText:'确定',
      cancelButtonText:'取消',
      type:'warning'
    })
    
    const res = await deleteCommentApi(commentId)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      fetchComments()
      fetchBook() // 刷新图书信息以更新平均评分
    } else {
      ElMessage.error('删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 切换收藏
const toggleFavorite = () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  isFavorite.value = !isFavorite.value
  ElMessage.success(isFavorite.value ? '已加入收藏' :'已取消收藏')
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 跳转到图书列表
const goToList = () => {
  router.push('/books')
}

onMounted(() => {
  fetchBook()
  fetchCategories()
  fetchComments()
})
</script>

<style scoped>
.book-detail {
  padding:20px;
  max-width:1200px;
  margin:0 auto;
  min-height:calc(100vh - 120px);
}

.back-button {
  margin-bottom:20px;
}

.back-button .el-button {
  padding:8px 0;
  font-size:14px;
}

.loading {
  padding:40px 0;
}

/* 图书头部 */
.book-header {
  margin-bottom:30px;
  padding:30px;
  background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius:12px;
  color:white;
  position:relative;
  overflow:hidden;
}

.book-header::before {
  content:'';
  position:absolute;
  top:0;
  left:0;
  right:0;
  bottom:0;
  background:url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="rgba(255,255,255,0.1)" d="M0,128L48,122.7C96,117,192,107,288,112C384,117,480,139,576,138.7C672,139,768,117,864,101.3C960,85,1056,75,1152,85.3C1248,96,1344,128,1392,144L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>');
  background-size:cover;
  background-position:center;
}

.book-title {
  margin:0 0 16px 0;
  font-size:32px;
  font-weight:700;
  position:relative;
  z-index:1;
  line-height:1.3;
}

.book-subtitle {
  display:flex;
  align-items:center;
  gap:20px;
  position:relative;
  z-index:1;
}

.book-subtitle .author {
  font-size:18px;
  font-weight:500;
}

.category-tag {
  background:rgba(255, 255, 255, 0.2);
  color:white !important;
  border-color:rgba(255, 255, 255, 0.3);
}

/* 主要内容 */
.book-main {
  display:flex;
  flex-direction:column;
  gap:24px;
}

/* 卡片样式 */
.info-card,
.description-card,
.comments-card {
  border-radius:12px;
  border:1px solid #e4e7ed;
}

:deep(.info-card .el-card__header),
:deep(.description-card .el-card__header),
:deep(.comments-card .el-card__header) {
  padding:20px 24px;
  border-bottom:1px solid #f0f0f0;
  background-color:#fafafa;
}

.card-header {
  font-size:18px;
  font-weight:600;
  color:#303133;
}

:deep(.info-card .el-card__body),
:deep(.description-card .el-card__body),
:deep(.comments-card .el-card__body) {
  padding:24px;
}

/* 信息网格 */
.info-grid {
  display:grid;
  grid-template-columns:repeat(auto-fit, minmax(300px, 1fr));
  gap:16px;
}

.info-item {
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:12px 0;
  border-bottom:1px solid #f5f5f5;
}

.info-item:last-child {
  border-bottom:none;
}

.info-label {
  font-size:14px;
  color:#909399;
  font-weight:500;
  min-width:100px;
}

.info-value {
  font-size:16px;
  color:#303133;
  font-weight:500;
  text-align:right;
  flex:1;
}

.info-value.isbn {
  font-family:'Monaco', 'Menlo', 'Consolas', monospace;
  background:#f5f5f5;
  padding:4px 8px;
  border-radius:4px;
  font-size:14px;
}

.info-value.price {
  color:#f56c6c;
  font-weight:600;
}

.info-value.rating {
  display:flex;
  align-items:center;
  justify-content:flex-end;
  gap:8px;
}

.rating-text {
  font-size:14px;
  color:#606266;
}

.stock-tag {
  font-weight:500;
  text-align:center;
}

/* 描述内容 */
.description-content {
  line-height:1.8;
  color:#606266;
  font-size:16px;
  text-align:justify;
}

.description-content p {
  margin:0 0 16px 0;
}

.description-content p:last-child {
  margin-bottom:0;
}

.no-description {
  color:#909399;
  font-style:italic;
  text-align:center;
  padding:20px;
}

/* 操作区域 */
.action-section {
  padding:24px;
  background:white;
  border-radius:12px;
  border:1px solid #e4e7ed;
}

.action-buttons {
  display:flex;
  gap:16px;
  flex-wrap:wrap;
}

.action-buttons .el-button {
  flex:1;
  min-width:180px;
  height:48px;
  font-size:16px;
  font-weight:500;
}

.action-buttons .el-button.is-favorite {
  background:linear-gradient(135deg, #f56c6c, #f78989);
  border-color:#f56c6c;
  color:white;
}

.action-buttons .el-button.is-favorite:hover {
  background:linear-gradient(135deg, #f78989, #f9a7a7);
  border-color:#f78989;
}

/* 评论区样式（从标准文件整合） */
.comment-form {
  margin-bottom:20px;
}

.comments-list {
  max-height:600px;
  overflow-y:auto;
}

.comment-item {
  padding:15px;
  border-bottom:1px solid #ebeef5;
  border-radius:4px;
  margin-bottom:10px;
}

.comment-item:last-child {
  border-bottom:none;
}

.comment-header {
  display:flex;
  align-items:center;
  gap:10px;
  margin-bottom:10px;
  flex-wrap:wrap;
}

.username {
  font-weight:bold;
  color:#303133;
}

.time {
  font-size:12px;
  color:#909399;
  margin-left:auto;
}

.comment-content {
  margin:10px 0 0;
  color:#606266;
  line-height:1.6;
}

.no-comments {
  text-align:center;
  color:#909399;
  padding:30px 0;
}

/* 响应式设计 */
@media (max-width:992px) {
  .book-detail {
    padding:16px;
  }
  
  .book-header {
    padding:24px 20px;
  }
  
  .book-title {
    font-size:26px;
  }
  
  .info-grid {
    grid-template-columns:1fr;
  }
  
  .action-buttons {
    flex-direction:column;
  }
  
  .action-buttons .el-button {
    min-width:100%;
  }
}

@media (max-width:768px) {
  .book-title {
    font-size:22px;
  }
  
  .book-subtitle {
    flex-direction:column;
    align-items:flex-start;
    gap:12px;
  }
  
  :deep(.info-card .el-card__header),
  :deep(.description-card .el-card__header),
  :deep(.comments-card .el-card__header) {
    padding:16px 20px;
  }
  
  :deep(.info-card .el-card__body),
  :deep(.description-card .el-card__body),
  :deep(.comments-card .el-card__body) {
    padding:20px;
  }
  
  .action-section {
    padding:20px;
  }
  
  .info-item {
    flex-direction:column;
    align-items:flex-start;
    gap:8px;
  }
  
  .info-label {
    min-width:auto;
  }
  
  .info-value {
    text-align:left;
  }
  
  .info-value.rating {
    justify-content:flex-start;
  }
}

@media (max-width:480px) {
  .book-header {
    padding:20px 16px;
  }
  
  .book-title {
    font-size:20px;
  }
}
</style>