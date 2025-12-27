import request from './request'

export const getNotifications = (params) => {
  return request.get('/notifications', { params })
}

export const markAsRead = (notifId) => {
  return request.put(`/notifications/${notifId}/read`)
}

export const readAllNotifications = () => {
  return request.put('/notifications/read-all')
}