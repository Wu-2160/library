<template>
  <div class="book-list">
    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索书名/作者/ISBN"
            clearable
            @input="fetchBooks"
          >
            <template #prefix>
              <i class="el-icon-search"></i>
</template>
          </el-input>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-select
            v-model="searchForm.category_id"
            placeholder="选择分类"
            clearable
            @change="fetchBooks"
          >
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-select
            v-model="searchForm.sort_by"
            placeholder="排序方式"
            @change="fetchBooks"
          >
            <el-option label="最新添加" value="created_at" />
            <el-option label="借阅次数" value="borrowed_count" />
            <el-option label="评分最高" value="avg_rating" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 图书列表 -->
    <el-row :gutter="20" class="books-container">
      <el-col v-for="book in books" :key="book.id" :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="book-card" shadow="hover">
          <div class="book-cover">
            <img
              :src="book.cover_url || 'https://via.placeholder.com/150x200? text=Book'"
              :alt="book.title"
            >
            <div class="book-action" v-if="book.stock > 0">
              <el-button type="primary" size="small" @click="goToDetail(book.id)">
                查看详情
              </el-button>
            </div>
            <div v-else class="book-no-stock">无库存</div>
          </div>
          
          <div class="book-info">
            <h3>{{ truncate(book.title, 20) }}</h3>
            <p class="author">作者：{{ book.author || '未知' }}</p>
            <p class="isbn">ISBN：{{ book.isbn }}</p>
            <p class="price">¥ {{ book.price }}</p>
            
            <div class="stats">
              <span>⭐ {{ book.avg_rating }}</span>
              <span>📖 {{ book.borrowed_count }}次</span>
              <span class="stock" :class="{ 'no-stock': book.stock === 0 }">
                库存 {{ book.stock }}
              </span>
            </div>
            
            <div class="actions">
              <el-button
                v-if="book.stock > 0"
                type="success"
                size="small"
                @click="borrowBook(book.id)"
                :loading="borrowLoading === book.id"
              >
                借阅
              </el-button>
              <el-button
                v-else
                type="warning"
                size="small"
                @click="reserveBook(book.id)"
                :loading="reserveLoading === book.id"
              >
                预约
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 分页 -->
    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.per_page"
      :page-sizes="[10, 20, 50]"
      :total="pagination.total"
      layout="total, sizes, prev, pager, next, jumper"
      @change="fetchBooks"
      style="text-align: center; margin-top: 20px"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getBooks, getCategories } from '@/api/book'
import { borrowBook as borrowBookApi } from '@/api/borrow'
import { reserveBook as reserveBookApi } from '@/api/reservation'
import { ElMessage } from 'element-plus'

const router = useRouter()

const books = ref([])
const categories = ref([])
const borrowLoading = ref(null)
const reserveLoading = ref(null)

const searchForm = reactive({
  keyword: '',
  category_id: '',
  sort_by:  'created_at'
})

const pagination = reactive({
  page: 1,
  per_page: 12,
  total: 0
})

const truncate = (str, length) => {
  return str.length > length ? str.substring(0, length) + '...' : str
}

const fetchBooks = async () => {
  try {
    const res = await getBooks({
      page: pagination.page,
      per_page: pagination.per_page,
      keyword: searchForm.keyword,
      category_id: searchForm.category_id,
      sort_by: searchForm.sort_by
    })
    
    if (res.code === 200) {
      books.value = res.data
      pagination.total = res.pagination.total
    }
  } catch (error) {
    ElMessage.error('获取图书失败')
  }
}

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

const borrowBook = async (bookId) => {
  try {
    borrowLoading.value = bookId
    const res = await borrowBookApi(bookId)
    
    if (res.code === 200) {
      ElMessage.success('借阅成功')
      fetchBooks()
    } else {
      ElMessage.error(res.msg || '借阅失败')
    }
  } catch (error) {
    ElMessage.error('借阅失败')
  } finally {
    borrowLoading.value = null
  }
}

const reserveBook = async (bookId) => {
  try {
    reserveLoading.value = bookId
    const res = await reserveBookApi(bookId)
    
    if (res.code === 200) {
      ElMessage.success('预约成功')
      fetchBooks()
    } else {
      ElMessage.error(res.msg || '预约失败')
    }
  } catch (error) {
    ElMessage.error('预约失败')
  } finally {
    reserveLoading.value = null
  }
}

const goToDetail = (bookId) => {
  router.push(`/books/${bookId}`)
}

onMounted(() => {
  fetchCategories()
  fetchBooks()
})
</script>

<style scoped>
.search-card {
  margin-bottom: 20px;
}

.books-container {
  margin:  20px 0;
}

.book-card {
  height: 100%;
  cursor: pointer;
  transition: all 0.3s;
}

.book-card:hover {
  transform:  translateY(-5px);
}

.book-cover {
  position: relative;
  height: 200px;
  margin:  -20px -20px 10px -20px;
  overflow: hidden;
  border-radius: 4px 4px 0 0;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-action,
.book-no-stock {
  position: absolute;
  top: 0;
  left: 0;
  right:  0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
}

.book-no-stock {
  font-size: 18px;
  font-weight:  bold;
}

.book-info h3 {
  font-size: 16px;
  margin: 10px 0 5px;
  font-weight: bold;
}

.author {
  font-size: 12px;
  color: #909399;
  margin: 5px 0;
}

.isbn {
  font-size: 11px;
  color: #c0c4cc;
  margin: 5px 0;
}

.price {
  font-size:  14px;
  color: #f56c6c;
  font-weight: bold;
  margin: 8px 0;
}

.stats {
  font-size: 12px;
  color: #606266;
  display: flex;
  justify-content: space-between;
  margin: 8px 0;
  flex-wrap: wrap;
  gap: 5px;
}

.stock.no-stock {
  color:  #f56c6c;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top:  10px;
}

.actions :deep(.el-button) {
  flex: 1;
}
</style>