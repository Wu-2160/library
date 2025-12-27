<template>
  <div class="book-detail" v-if="book">
    <el-row :gutter="30">
      <!-- 图书封面和基本信息 -->
      <el-col :xs="24" :sm="24" :md="8">
        <div class="book-cover-container">
          <img
            :src="book.cover_url || 'https://via.placeholder.com/150x200? text=Book'"
            :alt="book.title"
            class="book-cover"
          >
          
          <div class="book-basic">
            <el-tag class="category-tag">{{ book.category }}</el-tag>
            <p class="price">¥ {{ book.price }}</p>
            <p class="stock" :class="{ 'no-stock': book.stock === 0 }">
              库存:  {{ book.stock }}
            </p>
            
            <el-button
              v-if="book.stock > 0"
              type="success"
              size="large"
              @click="handleBorrow"
              :loading="borrowing"
              class="action-button"
            >
              借阅此书
            </el-button>
            <el-button
              v-else
              type="warning"
              size="large"
              @click="handleReserve"
              :loading="reserving"
              class="action-button"
            >
              预约此书
            </el-button>
          </div>
        </div>
      </el-col>
      
      <!-- 详细信息 -->
      <el-col :xs="24" :sm="24" :md="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <h1>{{ book.title }}</h1>
            </div>
</template>
          
          <el-descriptions :column="1" border>
            <el-descriptions-item label="作者">{{ book.author }}</el-descriptions-item>
            <el-descriptions-item label="出版社">{{ book.publisher }}</el-descriptions-item>
            <el-descriptions-item label="ISBN">{{ book.isbn }}</el-descriptions-item>
            <el-descriptions-item label="总库存">{{ book.total }}</el-descriptions-item>
            <el-descriptions-item label="借阅次数">{{ book.borrowed_count }}</el-descriptions-item>
            <el-descriptions-item label="平均评分">
              <el-rate v-model="book.avg_rating" disabled />
              ({{ book.avg_rating }})
            </el-descriptions-item>
            <el-descriptions-item label="馆藏位置">{{ book.location || '未标记' }}</el-descriptions-item>
            <el-descriptions-item label="添加时间">
              {{ formatDate(book.created_at) }}
            </el-descriptions-item>
          </el-descriptions>
          
          <!-- 图书描述 -->
          <el-divider />
          <h3>图书描述</h3>
          <p class="description">
            {{ book.description || '暂无描述' }}
          </p>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 评论区 -->
    <el-card class="comments-card">
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
          >
            提交评价
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
              v-if="authStore.user.id === comment.user_id || authStore.userRole === 'admin'"
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
        style="text-align: center; margin-top: 20px"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getBookDetail } from '@/api/book'
import { borrowBook as borrowBookApi } from '@/api/borrow'
import { reserveBook as reserveBookApi } from '@/api/reservation'
import { addComment, deleteComment as deleteCommentApi, getBookComments } from '@/api/comment'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const authStore = useAuthStore()

const book = ref(null)
const comments = ref([])
const commentPage = ref(1)
const totalComments = ref(0)
const borrowing = ref(false)
const reserving = ref(false)
const commentSubmitting = ref(false)

const commentForm = reactive({
  rating: 5,
  comment: ''
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const fetchBook = async () => {
  try {
    const bookId = route.params.id
    const res = await getBookDetail(bookId)
    
    if (res.code === 200) {
      book.value = res.data
    } else {
      ElMessage.error('获取图书失败')
    }
  } catch (error) {
    ElMessage.error('获取图书失败')
  }
}

const fetchComments = async () => {
  try {
    const bookId = route.params.id
    const res = await getBookComments(bookId, {
      page: commentPage.value,
      per_page: 5
    })
    
    if (res.code === 200) {
      comments.value = res.data
      totalComments.value = res.pagination.total
    }
  } catch (error) {
    console.error('获取评论失败', error)
  }
}

const handleBorrow = async () => {
  try {
    borrowing.value = true
    const bookId = route.params.id
    const res = await borrowBookApi(bookId)
    
    if (res.code === 200) {
      ElMessage.success('借阅成功')
      fetchBook()
    } else {
      ElMessage.error(res.msg || '借阅失败')
    }
  } catch (error) {
    ElMessage.error('借阅失败')
  } finally {
    borrowing.value = false
  }
}

const handleReserve = async () => {
  try {
    reserving.value = true
    const bookId = route.params.id
    const res = await reserveBookApi(bookId)
    
    if (res.code === 200) {
      ElMessage.success('预约成功')
      fetchBook()
    } else {
      ElMessage.error(res.msg || '预约失败')
    }
  } catch (error) {
    ElMessage.error('预约失败')
  } finally {
    reserving.value = false
  }
}

const submitComment = async () => {
  if (!commentForm.rating) {
    ElMessage.warning('请选择评分')
    return
  }
  
  try {
    commentSubmitting.value = true
    const bookId = route.params.id
    const res = await addComment(bookId, {
      rating: commentForm.rating,
      comment: commentForm.comment
    })
    
    if (res.code === 200) {
      ElMessage.success('评价成功')
      commentForm.rating = 5
      commentForm.comment = ''
      fetchComments()
      fetchBook()
    } else {
      ElMessage.error(res.msg || '评价失败')
    }
  } catch (error) {
    ElMessage.error('评价失败')
  } finally {
    commentSubmitting.value = false
  }
}

const deleteComment = async (commentId) => {
  try {
    await ElMessageBox.confirm('确定删除此评论吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText:  '取消',
      type:  'warning'
    })
    
    const res = await deleteCommentApi(commentId)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      fetchComments()
      fetchBook()
    } else {
      ElMessage.error('删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchBook()
  fetchComments()
})
</script>

<style scoped>
.book-detail {
  padding-bottom: 30px;
}

.book-cover-container {
  position: sticky;
  top: 20px;
}

.book-cover {
  width: 100%;
  border-radius: 4px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.book-basic {
  background: white;
  padding: 20px;
  border-radius: 4px;
  box-shadow:  0 2px 10px rgba(0, 0, 0, 0.05);
}

.category-tag {
  display: block;
  margin-bottom: 10px;
}

.price {
  font-size: 24px;
  color: #f56c6c;
  font-weight: bold;
  margin:  10px 0;
}

.stock {
  font-size: 14px;
  color: #606266;
  margin:  10px 0;
}

.stock.no-stock {
  color: #f56c6c;
  font-weight: bold;
}

.action-button {
  width: 100%;
  height: 40px;
  margin-top: 20px;
}

.card-header h1 {
  margin: 0;
  font-size: 28px;
}

.description {
  line-height: 1.8;
  color: #606266;
  margin:  0;
}

.comments-card {
  margin-top: 30px;
}

.comment-form {
  margin-bottom: 20px;
}

.comments-list {
  max-height: 600px;
  overflow-y:  auto;
}

.comment-item {
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 10px;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.username {
  font-weight: bold;
  color: #303133;
}

.time {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
}

.comment-content {
  margin:  10px 0 0;
  color: #606266;
  line-height: 1.6;
}

.no-comments {
  text-align: center;
  color: #909399;
  padding: 30px 0;
}

:deep(.el-rate) {
  display: inline-flex;
}

:deep(.el-descriptions__body) {
  font-size: 14px;
}
</style>