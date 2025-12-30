import request from './request'

export const getBooks = (params) => {
  return request.get('/books', { params })
}

export const getBookDetail = (bookId) => {
  return request.get(`/books/${bookId}`)
}

export const getImageUrl = (path) => {
  if (! path) return ''
  // 如果已经是完整 URL，直接返回
  if (path.startsWith('http')) return path
  // 如果是相对路径，补全为完整 URL
  return `http://localhost:5000${path}`
}

// ✅ 修改：支持 FormData（文件上传）
export const addBook = (data) => {
  return request.post('/books', data, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const updateBook = (bookId, data) => {
  return request.put(`/books/${bookId}`, data, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const deleteBook = (bookId) => {
  return request.delete(`/books/${bookId}`)
}

export const getCategories = () => {
  return request.get('/books/categories')
}

export const getPopularBooks = (limit = 10) => {
  return request.get('/books/popular', { params: { limit } })
}

export const getTopRatedBooks = (limit = 10) => {
  return request.get('/books/top-rated', { params: { limit } })
}