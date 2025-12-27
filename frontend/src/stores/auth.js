import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
  
  const isLoggedIn = computed(() => !!token.value)
  const userRole = computed(() => user.value.role || 'reader')
  const userId = computed(() => user.value.id)
  
  const login = (data) => {
    token.value = data.token
    user.value = data.user
    localStorage.setItem('token', token.value)
    localStorage.setItem('user', JSON.stringify(user.value))
  }
  
  const logout = () => {
    token.value = ''
    user.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
  
  const updateUser = (userData) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }
  
  return {
    token,
    user,
    isLoggedIn,
    userRole,
    userId,
    login,
    logout,
    updateUser
  }
})