import request from './request'

export const getAllUsers = (params) => {
  return request.get('/admin/users', { params })
}

export const freezeUser = (userId) => {
  return request.post(`/admin/users/${userId}/freeze`)
}

export const unfreezeUser = (userId) => {
  return request.post(`/admin/users/${userId}/unfreeze`)
}

export const getOverviewStatistics = () => {
  return request.get('/admin/statistics/overview')
}

export const getTopBooksStatistics = (params) => {
  return request.get('/admin/statistics/top-books', { params })
}

export const getUserActivityStatistics = (params) => {
  return request.get('/admin/statistics/user-activity', { params })
}

export const getCategoryDistribution = () => {
  return request.get('/admin/statistics/category-distribution')
}

export const getBorrowReturnRate = () => {
  return request.get('/admin/statistics/borrow-return-rate')
}

export const getOverdueReport = () => {
  return request.get('/admin/statistics/overdue-report')
}

export const getOperationLogs = (params) => {
  return request.get('/admin/logs', { params })
}

export const exportUsers = () => {
  return request.get('/admin/export/users')
}

export const exportBorrowRecords = () => {
  return request.get('/admin/export/borrow-records')
}