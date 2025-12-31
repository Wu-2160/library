[file name]:AdminBooks.vue
<template>
  <div class="admin-books">
    <!-- 页面标题和统计 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">
            <span class="title-icon">📚</span>
            图书管理
          </h1>
          <p class="page-subtitle">管理图书馆的所有图书信息与库存</p>
        </div>
        <div class="header-right">
          <div class="stats-cards">
            <div class="stat-card">
              <div class="stat-icon">📖</div>
              <div class="stat-info">
                <div class="stat-number">{{ pagination.total }}</div>
                <div class="stat-label">总图书数</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <el-card class="action-bar" shadow="never">
      <div class="action-bar-content">
        <div class="search-container">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索书名、作者、ISBN..."
            class="search-input"
            clearable
            size="large"
            @input="searchBooks"
          >
            <template #prefix>
              <el-icon class="search-icon"><Search /></el-icon>
            </template>
          </el-input>
        </div>
        <div class="action-buttons">
          <el-button 
            type="primary" 
            class="add-button"
            @click="showAddDialog = true"
            size="large"
          >
            <el-icon><Plus /></el-icon>
            添加新书
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 图书表格 -->
    <el-card class="books-table-card" shadow="never">
      <div v-loading="loading" element-loading-text="加载中..." element-loading-spinner="el-icon-loading">
        <el-table 
          :data="books" 
          :header-cell-style="{ background:'#f8fafc', color:'#475569', fontWeight:'600' }"
          :cell-style="{ verticalAlign:'middle' }"
          style="width:100%"
          stripe
        >
          <el-table-column prop="title" label="书名" width="220">
            <template #default="{ row }">
              <div class="book-title-cell">
                <div class="book-cover-small">
                  <el-image
                    v-if="row.cover_url"
                    :src="getCoverUrl(row)"
                    fit="cover"
                    :preview-src-list="[getCoverUrl(row)]"
                    preview-teleported
                    class="cover-image"
                  >
                    <template #error>
                      <div class="image-error">
                        <el-icon><Picture /></el-icon>
                      </div>
                    </template>
                  </el-image>
                  <div v-else class="no-cover">
                    <el-icon><Document /></el-icon>
                  </div>
                </div>
                <div class="book-info">
                  <span class="title-text">{{ row.title }}</span>
                  <span class="author-text">{{ row.author }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="isbn" label="ISBN" width="160">
            <template #default="{ row }">
              <div class="isbn-cell">
                <el-tag size="small" effect="plain" class="isbn-tag">
                  {{ row.isbn }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="category" label="分类" width="120">
            <template #default="{ row }">
              <el-tag 
                size="small" 
                :type="getCategoryType(row.category)"
                effect="light"
                class="category-tag"
              >
                {{ row.category }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="price" label="价格" width="100" align="center">
            <template #default="{ row }">
              <div class="price-cell">
                <span class="price-symbol">¥</span>
                <span class="price-number">{{ row.price.toFixed(2) }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="stock" label="库存" width="100" align="center">
            <template #default="{ row }">
              <div class="stock-cell" :class="{ 'low-stock':row.stock <= 5 && row.stock > 0, 'no-stock':row.stock === 0 }">
                <el-tag 
                  :type="getStockType(row.stock)"
                  size="small"
                  effect="light"
                  class="stock-tag"
                >
                  {{ row.stock === 0 ? '无库存' :`${row.stock}本` }}
                </el-tag>
                <div v-if="row.stock <= 5 && row.stock > 0" class="stock-warning">
                  <el-icon><Warning /></el-icon>
                  库存紧张
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <div class="status-cell">
                <div class="status-indicator" :class="getStatusClass(row.stock)"></div>
                <span>{{ getStatusText(row.stock) }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="180" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons-cell">
                <el-tooltip content="编辑图书" placement="top">
                  <el-button 
                    type="primary" 
                    size="small" 
                    circle
                    @click="editBook(row)"
                    class="action-button edit-btn"
                  >
                    <el-icon><Edit /></el-icon>
                  </el-button>
                </el-tooltip>
                
                <el-tooltip content="查看详情" placement="top">
                  <el-button 
                    type="info" 
                    size="small" 
                    circle
                    @click="viewBook(row)"
                    class="action-button view-btn"
                  >
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                
                <el-tooltip content="删除图书" placement="top">
                  <el-button 
                    type="danger" 
                    size="small" 
                    circle
                    @click="deleteBook(row.id)"
                    class="action-button delete-btn"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchBooks"
          @current-change="fetchBooks"
          background
        />
      </div>
    </el-card>

    <!-- 添加/编辑图书对话框 -->
    <el-dialog 
      v-model="showAddDialog" 
      :title="editingBook ? '编辑图书信息' :'添加新书'"
      width="800px"
      :close-on-click-modal="false"
      class="book-dialog"
    >
      <div class="dialog-content">
        <el-form 
          :model="bookForm" 
          label-width="100px" 
          label-position="top"
          class="book-form"
          @submit.prevent
        >
          <el-row :gutter="30">
            <!-- 左侧基本信息 -->
            <el-col :span="12">
              <div class="form-section">
                <h3 class="section-title">基本信息</h3>
                
                <el-form-item label="书名" required>
                  <el-input 
                    v-model="bookForm.title" 
                    placeholder="请输入书名" 
                    size="large"
                    :maxlength="100"
                    show-word-limit
                  />
                </el-form-item>
                
                <el-form-item label="作者">
                  <el-input 
                    v-model="bookForm.author" 
                    placeholder="请输入作者" 
                    size="large"
                  />
                </el-form-item>
                
                <el-form-item label="ISBN" required>
                  <el-input 
                    v-model="bookForm.isbn" 
                    placeholder="请输入ISBN" 
                    size="large"
                    :disabled="!!editingBook"
                    :maxlength="13"
                  />
                </el-form-item>
                
                <el-form-item label="出版社">
                  <el-input 
                    v-model="bookForm.publisher" 
                    placeholder="请输入出版社" 
                    size="large"
                  />
                </el-form-item>
                
                <el-form-item label="分类">
                  <el-select 
                    v-model="bookForm.category_id" 
                    placeholder="选择分类"
                    size="large"
                    style="width:100%"
                  >
                    <el-option
                      v-for="cat in categories"
                      :key="cat.id"
                      :label="cat.name"
                      :value="cat.id"
                    />
                  </el-select>
                </el-form-item>
              </div>
            </el-col>
            
            <!-- 右侧详细信息 -->
            <el-col :span="12">
              <div class="form-section">
                <h3 class="section-title">详细信息</h3>
                
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="价格">
                      <el-input-number 
                        v-model="bookForm.price" 
                        :min="0" 
                        :precision="2"
                        controls-position="right"
                        size="large"
                        style="width:100%"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="库存">
                      <el-input-number 
                        v-model="bookForm.stock" 
                        :min="0"
                        controls-position="right"
                        size="large"
                        style="width:100%"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-form-item label="馆藏位置">
                  <el-input 
                    v-model="bookForm.location" 
                    placeholder="请输入馆藏位置，如：A-1-001" 
                    size="large"
                  />
                </el-form-item>
                
                <el-form-item label="图书描述">
                  <el-input
                    v-model="bookForm.description"
                    type="textarea"
                    :rows="5"
                    placeholder="请输入图书描述"
                    :maxlength="500"
                    show-word-limit
                    resize="none"
                  />
                </el-form-item>
              </div>
            </el-col>
          </el-row>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showAddDialog = false" size="large">
            取消
          </el-button>
          <el-button 
            type="primary" 
            @click="submitBook" 
            :loading="submitting"
            size="large"
            class="submit-btn"
          >
            {{ editingBook ? '更新图书信息' :'添加新书' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { 
  getBooks,
  getCategories,
  addBook,
  updateBook,
  deleteBook as deleteBookApi
} from '@/api/book'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, 
  Plus, 
  Edit, 
  Delete, 
  View,
  Picture,
  Document,
  Warning
} from '@element-plus/icons-vue'

const books = ref([])
const categories = ref([])
const loading = ref(false)
const submitting = ref(false)
const searchKeyword = ref('')
const showAddDialog = ref(false)
const editingBook = ref(null)

const getCoverUrl = (book) => {
  return getImageUrl(book.cover_url)
}

const pagination = reactive({
  page:1,
  per_page:10,
  total:0
})

const bookForm = reactive({
  title:'',
  author:'',
  isbn:'',
  publisher:'',
  price:0,
  stock:1,
  category_id:null,
  location:'',
  description:''
})

// 分类类型映射
const getCategoryType = (category) => {
  const typeMap = {
    '文学':'primary',
    '科技':'success',
    '历史':'warning',
    '艺术':'danger',
    '教育':'info'
  }
  return typeMap[category] || 'info'
}

// 库存类型映射
const getStockType = (stock) => {
  if (stock === 0) return 'danger'
  if (stock <= 5) return 'warning'
  return 'success'
}

// 状态样式
const getStatusClass = (stock) => {
  if (stock === 0) return 'status-out'
  if (stock <= 5) return 'status-warning'
  return 'status-available'
}

// 状态文本
const getStatusText = (stock) => {
  if (stock === 0) return '已借完'
  if (stock <= 5) return '库存紧张'
  return '可借阅'
}

const fetchBooks = async () => {
  try {
    loading.value = true
    const res = await getBooks({
      page:pagination.page,
      per_page:pagination.per_page,
      keyword:searchKeyword.value
    })
    
    if (res.code === 200) {
      books.value = res.data
      pagination.total = res.pagination.total
    }
  } catch (error) {
    ElMessage.error('获取图书列表失败')
  } finally {
    loading.value = false
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

const searchBooks = () => {
  pagination.page = 1
  fetchBooks()
}

const editBook = (book) => {
  editingBook.value = book
  bookForm.title = book.title
  bookForm.author = book.author
  bookForm.isbn = book.isbn
  bookForm.publisher = book.publisher
  bookForm.price = book.price
  bookForm.stock = book.stock
  bookForm.category_id = book.category_id
  bookForm.location = book.location
  bookForm.description = book.description
  showAddDialog.value = true
}

const viewBook = (book) => {
  // 跳转到图书详情页
  window.open(`/books/${book.id}`, '_blank')
}

const submitBook = async () => {
  if (!bookForm.title || !bookForm.isbn) {
    ElMessage.warning('书名和ISBN为必填项')
    return
  }
  
  try {
    submitting.value = true
    
    const formData = new FormData()
    formData.append('title', bookForm.title)
    formData.append('author', bookForm.author)
    formData.append('isbn', bookForm.isbn)
    formData.append('publisher', bookForm.publisher)
    formData.append('price', bookForm.price)
    formData.append('stock', bookForm.stock)
    if (bookForm.category_id) {
      formData.append('category_id', bookForm.category_id)
    }
    formData.append('location', bookForm.location)
    formData.append('description', bookForm.description)
    
    let res
    if (editingBook.value) {
      res = await updateBook(editingBook.value.id, formData)
    } else {
      res = await addBook(formData)
    }
    
    if (res.code === 200 || res.code === 201) {
      ElMessage.success(editingBook.value ? '图书信息更新成功' :'新书添加成功')
      showAddDialog.value = false
      editingBook.value = null
      resetForm()
      fetchBooks()
    } else {
      ElMessage.error(res.msg || '操作失败')
    }
  } catch (error) {
    console.error('操作错误:', error)
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const deleteBook = async (bookId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这本图书吗？此操作不可恢复。',
      '删除确认',
      {
        confirmButtonText:'确认删除',
        cancelButtonText:'取消',
        type:'warning',
        confirmButtonClass:'delete-confirm-btn',
        cancelButtonClass:'delete-cancel-btn'
      }
    )
    
    const res = await deleteBookApi(bookId)
    if (res.code === 200) {
      ElMessage.success('图书删除成功')
      fetchBooks()
    } else {
      ElMessage.error(res.msg || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const resetForm = () => {
  bookForm.title = ''
  bookForm.author = ''
  bookForm.isbn = ''
  bookForm.publisher = ''
  bookForm.price = 0
  bookForm.stock = 1
  bookForm.category_id = null
  bookForm.location = ''
  bookForm.description = ''
}

onMounted(() => {
  fetchBooks()
  fetchCategories()
})
</script>

<style scoped>
.admin-books {
  padding:24px;
  background:#f8fafc;
  min-height:calc(100vh - 64px);
}

/* 页面标题 */
.page-header {
  margin-bottom:24px;
}

.header-content {
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap:24px;
}

.header-left .page-title {
  margin:0;
  font-size:28px;
  font-weight:700;
  color:#1e293b;
  display:flex;
  align-items:center;
  gap:12px;
}

.title-icon {
  font-size:32px;
}

.page-subtitle {
  margin:8px 0 0;
  color:#64748b;
  font-size:14px;
}

.stats-cards {
  display:flex;
  gap:16px;
}

.stat-card {
  background:white;
  border-radius:12px;
  padding:20px;
  min-width:140px;
  box-shadow:0 1px 3px rgba(0,0,0,0.1);
  display:flex;
  align-items:center;
  gap:16px;
}

.stat-icon {
  font-size:32px;
}

.stat-info {
  display:flex;
  flex-direction:column;
}

.stat-number {
  font-size:24px;
  font-weight:700;
  color:#1e293b;
  line-height:1.2;
}

.stat-label {
  font-size:14px;
  color:#64748b;
}

/* 操作栏 */
.action-bar {
  margin-bottom:24px;
  border-radius:12px;
  border:1px solid #e2e8f0;
}

.action-bar-content {
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap:16px;
}

.search-container {
  flex:1;
  max-width:400px;
}

.search-input {
  --el-input-border-radius:10px;
  --el-input-bg-color:#f8fafc;
  --el-input-border-color:#e2e8f0;
}

.search-input:hover {
  --el-input-border-color:#cbd5e1;
}

.search-input:focus-within {
  --el-input-border-color:#3b82f6;
}

.search-icon {
  color:#94a3b8;
}

.add-button {
  --el-button-border-radius:10px;
  background:linear-gradient(135deg, #3b82f6, #1d4ed8);
  border:none;
  padding:12px 24px;
  font-weight:600;
  display:flex;
  align-items:center;
  gap:8px;
  transition:all 0.3s ease;
}

.add-button:hover {
  transform:translateY(-2px);
  box-shadow:0 4px 12px rgba(59, 130, 246, 0.3);
}

/* 图书表格 */
.books-table-card {
  border-radius:12px;
  border:1px solid #e2e8f0;
  overflow:hidden;
}

/* 表格单元格样式 */
.book-title-cell {
  display:flex;
  align-items:center;
  gap:12px;
}

.book-cover-small {
  width:48px;
  height:64px;
  border-radius:6px;
  overflow:hidden;
  background:#f1f5f9;
  display:flex;
  align-items:center;
  justify-content:center;
  flex-shrink:0;
}

.cover-image {
  width:100%;
  height:100%;
  object-fit:cover;
}

.image-error {
  display:flex;
  align-items:center;
  justify-content:center;
  width:100%;
  height:100%;
  color:#94a3b8;
}

.no-cover {
  display:flex;
  align-items:center;
  justify-content:center;
  width:100%;
  height:100%;
  color:#cbd5e1;
}

.book-info {
  display:flex;
  flex-direction:column;
  min-width:0;
}

.title-text {
  font-weight:600;
  color:#1e293b;
  margin-bottom:4px;
  overflow:hidden;
  text-overflow:ellipsis;
  display:-webkit-box;
  -webkit-line-clamp:2;
  -webkit-box-orient:vertical;
}

.author-text {
  font-size:12px;
  color:#64748b;
}

.isbn-cell {
  display:flex;
  align-items:center;
}

.isbn-tag {
  --el-tag-bg-color:#f1f5f9;
  --el-tag-text-color:#475569;
  border:1px dashed #cbd5e1;
  font-family:'Monaco', 'Menlo', monospace;
  font-size:12px;
}

.category-tag {
  font-weight:500;
}

.price-cell {
  display:flex;
  align-items:baseline;
  justify-content:center;
  gap:2px;
}

.price-symbol {
  font-size:12px;
  color:#64748b;
}

.price-number {
  font-size:16px;
  font-weight:600;
  color:#1e293b;
}

.stock-cell {
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:4px;
}

.stock-tag {
  font-weight:500;
}

.stock-warning {
  font-size:11px;
  color:#f59e0b;
  display:flex;
  align-items:center;
  gap:2px;
}

.low-stock .stock-tag {
  animation:pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity:1;
  }
  50% {
    opacity:0.7;
  }
}

.status-cell {
  display:flex;
  align-items:center;
  gap:8px;
  justify-content:center;
}

.status-indicator {
  width:8px;
  height:8px;
  border-radius:50%;
}

.status-available {
  background-color:#10b981;
  box-shadow:0 0 0 2px rgba(16, 185, 129, 0.2);
}

.status-warning {
  background-color:#f59e0b;
  box-shadow:0 0 0 2px rgba(245, 158, 11, 0.2);
  animation:pulse 2s infinite;
}

.status-out {
  background-color:#ef4444;
  box-shadow:0 0 0 2px rgba(239, 68, 68, 0.2);
}

.action-buttons-cell {
  display:flex;
  justify-content:center;
  gap:8px;
}

.action-button {
  --el-button-border-radius:50%;
  --el-button-hover-bg-color:transparent;
  transition:all 0.2s ease;
}

.edit-btn {
  --el-button-bg-color:#dbeafe;
  --el-button-text-color:#3b82f6;
  --el-button-hover-border-color:#3b82f6;
}

.view-btn {
  --el-button-bg-color:#f0f9ff;
  --el-button-text-color:#0ea5e9;
  --el-button-hover-border-color:#0ea5e9;
}

.delete-btn {
  --el-button-bg-color:#fee2e2;
  --el-button-text-color:#ef4444;
  --el-button-hover-border-color:#ef4444;
}

/* 分页 */
.pagination-container {
  padding:24px 0 8px;
  display:flex;
  justify-content:center;
}

:deep(.el-pagination.is-background .el-pager li) {
  border-radius:8px;
  margin:0 4px;
}

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background:linear-gradient(135deg, #3b82f6, #1d4ed8);
}

/* 对话框 */
.book-dialog :deep(.el-dialog) {
  border-radius:16px;
  overflow:hidden;
}

.book-dialog :deep(.el-dialog__header) {
  padding:24px 24px 0;
  margin:0;
}

.book-dialog :deep(.el-dialog__title) {
  font-size:20px;
  font-weight:600;
  color:#1e293b;
}

.book-dialog :deep(.el-dialog__body) {
  padding:24px;
}

.dialog-content {
  max-height:60vh;
  overflow-y:auto;
}

.form-section {
  padding:20px;
  background:#f8fafc;
  border-radius:12px;
  border:1px solid #e2e8f0;
}

.section-title {
  margin:0 0 20px 0;
  font-size:16px;
  font-weight:600;
  color:#1e293b;
  padding-bottom:12px;
  border-bottom:2px solid #e2e8f0;
}

:deep(.el-form-item) {
  margin-bottom:20px;
}

:deep(.el-form-item__label) {
  font-weight:500;
  color:#475569;
  margin-bottom:8px;
  padding-bottom:0;
}

:deep(.el-input) {
  --el-input-border-radius:8px;
  --el-input-bg-color:white;
  --el-input-border-color:#e2e8f0;
}

:deep(.el-input__inner) {
  height:44px;
}

:deep(.el-input-number) {
  --el-input-border-radius:8px;
  --el-input-bg-color:white;
}

:deep(.el-textarea__inner) {
  border-radius:8px;
  border-color:#e2e8f0;
}

.dialog-footer {
  padding:24px;
  border-top:1px solid #e2e8f0;
  display:flex;
  justify-content:flex-end;
  gap:12px;
}

.submit-btn {
  background:linear-gradient(135deg, #3b82f6, #1d4ed8);
  border:none;
  padding:12px 32px;
  font-weight:600;
}

:deep(.delete-confirm-btn) {
  background:linear-gradient(135deg, #ef4444, #dc2626);
  border:none;
  color:white;
  font-weight:600;
}

:deep(.delete-confirm-btn:hover) {
  background:linear-gradient(135deg, #dc2626, #b91c1c);
}

:deep(.delete-cancel-btn) {
  font-weight:500;
}

/* 响应式设计 */
@media (max-width:992px) {
  .header-content {
    flex-direction:column;
    align-items:flex-start;
  }
  
  .stats-cards {
    width:100%;
  }
  
  .stat-card {
    flex:1;
  }
  
  .action-bar-content {
    flex-direction:column;
    align-items:stretch;
  }
  
  .search-container {
    max-width:100%;
  }
}

@media (max-width:768px) {
  .admin-books {
    padding:16px;
  }
  
  .book-dialog :deep(.el-dialog) {
    width:95%;
    margin:20px auto;
  }
  
  .form-section {
    padding:16px;
  }
}
</style>