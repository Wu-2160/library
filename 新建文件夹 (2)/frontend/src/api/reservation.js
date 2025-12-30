import request from './request'

export const reserveBook = (bookId) => {
  return request.post(`/reservations/${bookId}`)
}

export const getMyReservations = (params) => {
  return request.get('/reservations/my-reservations', { params })
}

export const cancelReservation = (reservationId) => {
  return request.post(`/reservations/${reservationId}/cancel`)
}

export const getReservationQueue = (bookId) => {
  return request.get(`/reservations/queue/${bookId}`)
}