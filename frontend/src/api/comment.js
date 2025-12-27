import request from './request'

export const addComment = (bookId, data) => {
  return request.post(`/comments/${bookId}`, data)
}

export const deleteComment = (commentId) => {
  return request.delete(`/comments/${commentId}`)
}

export const getBookComments = (bookId, params) => {
  return request.get(`/comments/book/${bookId}`, { params })
}