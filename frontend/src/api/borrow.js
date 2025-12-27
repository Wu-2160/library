import request from './request'

export const borrowBook = (bookId) => {
  return request.post(`/borrows/${bookId}`)
}

export const returnBook = (recordId) => {
  return request.post(`/borrows/${recordId}/return`)
}

export const getMyBorrowRecords = (params) => {
  return request.get('/borrows/my-records', { params })
}

export const renewBook = (recordId) => {
  return request.post(`/borrows/${recordId}/renew`)
}

export const getOverdueRecords = () => {
  return request.get('/borrows/overdue')
}