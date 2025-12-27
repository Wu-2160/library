<template>
  <div class="admin-books">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索书名/作者/ISBN"
            style="width:300px"
            clearable
            @input="searchBooks"
          >
            <template #prefix>
              <i class="el-icon-search"></i>
</template>
          </el-input>
          <el-button type="primary" @click="showAddDialog = true">
            添加新书
          </el-button>
        </div>
</template>
      
      <el-table :data="books" stripe style="width:100%" v-loading="loading">
        <el-table-column prop="title" label="书名" width="180" />
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column prop="isbn" label="ISBN" width="140" />
        <el-table-column prop="price" label="价格" width="80" />
        <el-table-column prop="stock" label="库存" width="80" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column label="封面" width="80">
          <template #default="{ row }">
            <el-image
              v-if="row.cover_url"
              :src="getCoverUrl(row)"
              fit="cover"
              style="width:50px; height:70px; cursor:pointer"
              preview-teleported
              :preview-src-list="[getCoverUrl(row)]"
            />
            <span v-else style="color:#909399">无封面</span>
</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editBook(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="deleteBook(row.id)">
              删除
            </el-button>
</template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :page-sizes="[10, 20, 50]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @change="fetchBooks"
        style="text-align:center; margin-top:20px"
      />
    </el-card>
    
    <el-dialog v-model="showAddDialog" :title="editingBook ? '编辑图书' :'添加新书'" width="600px">
      <el-form :model="bookForm" label-width="100px">
        <el-form-item label="书名" required>
          <el-input v-model="bookForm.title" placeholder="请输入书名" />
        </el-form-item>
        
        <el-form-item label="作者">
          <el-input v-model="bookForm.author" placeholder="请输入作者" />
        </el-form-item>
        
        <el-form-item label="ISBN" required>
          <el-input
            v-model="bookForm.isbn"
            placeholder="请输入ISBN"
            :disabled="!! editingBook"
          />
        </el-form-item>
        
        <el-form-item label="出版社">
          <el-input v-model="bookForm.publisher" placeholder="请输入出版社" />
        </el-form-item>
        
        <el-form-item label="价格">
          <el-input-number v-model="bookForm.price" :min="0" />
        </el-form-item>
        
        <el-form-item label="库存">
          <el-input-number v-model="bookForm.stock" :min="0" />
        </el-form-item>
        
        <el-form-item label="分类">
          <el-select v-model="bookForm.category_id" placeholder="选择分类">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="位置">
          <el-input v-model="bookForm.location" placeholder="请输入馆藏位置" />
        </el-form-item>
        
        
        <el-form-item label="描述">
          <el-input
            v-model="bookForm.description"
            type="textarea"
            rows="4"
            placeholder="请输入图书描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitBook" :loading="submitting">
          {{ editingBook ? '更新' :'添加' }}
        </el-button>
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

const books = ref([])
const categories = ref([])
const loading = ref(false)
const submitting = ref(false)
const searchKeyword = ref('')
const showAddDialog = ref(false)
const editingBook = ref(null)
const fileList = ref([])
const previewUrl = ref('')

const getCoverUrl = (book) => {
  return getImageUrl(book.cover_url)
}

const pagination = reactive({
  page:1,
  per_page: 10,
  total:0
})

const bookForm = reactive({
  title:'',
  author:'',
  isbn: '',
  publisher:'',
  price:0,
  stock:1,
  category_id:null,
  location:'',
  description:''
})

const handleFileSelect = (file) => {
  if (file.size > 16 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 16MB')
    fileList.value = []
    previewUrl.value = ''
    return
  }
  
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value = e.target.result
  }
  reader.readAsDataURL(file.raw)
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
  previewUrl.value = book.cover_url || ''
  fileList.value = []
  showAddDialog.value = true
}

const submitBook = async () => {
  if (!bookForm.title || !bookForm.isbn) {
    ElMessage.warning('书名和ISBN必填')
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
    
    if (fileList.value.length > 0) {
      formData.append('cover', fileList.value[0].raw)
    }
    
    let res
    if (editingBook.value) {
      res = await updateBook(editingBook.value.id, formData)
    } else {
      res = await addBook(formData)
    }
    
    if (res.code === 200 || res.code === 201) {
      ElMessage.success(editingBook.value ? '更新成功' :'添加成功')
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
    await ElMessageBox.confirm('确定删除此图书吗？', '提示', {
      confirmButtonText:'确定',
      cancelButtonText:'取消',
      type:'warning'
    })
    
    const res = await deleteBookApi(bookId)
    if (res.code === 200) {
      ElMessage.success('删除成功')
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
  fileList.value = []
  previewUrl.value = ''
}

onMounted(() => {
  fetchBooks()
  fetchCategories()
})
</script>

<style scoped>
.admin-books {
  padding-bottom:20px;
}

.card-header {
  display:flex;
  justify-content:space-between;
  align-items:center;
  width:100%;
  gap:20px;
}

.upload-container {
  display:flex;
  flex-direction:column;
}
</style>