import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name:  'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home.vue')
      },
      {
        path: 'books',
        name: 'BookList',
        component: () => import('@/views/BookList.vue')
      },
      {
        path: 'books/:id',
        name: 'BookDetail',
        component:  () => import('@/views/BookDetail.vue')
      },
      {
        path: 'my-borrow',
        name: 'MyBorrow',
        component: () => import('@/views/MyBorrow.vue')
      },
      {
        path: 'my-reservation',
        name: 'MyReservation',
        component: () => import('@/views/MyReservation.vue')
      },
      {
        path: 'profile',
        name: 'UserProfile',
        component: () => import('@/views/UserProfile.vue')
      },
      {
        path: 'admin/dashboard',
        name: 'AdminDashboard',
        component:  () => import('@/views/AdminDashboard.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'admin/users',
        name: 'AdminUsers',
        component:  () => import('@/views/AdminUsers.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'admin/books',
        name: 'AdminBooks',
        component: () => import('@/views/AdminBooks.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'admin/statistics',
        name: 'AdminStatistics',
        component: () => import('@/views/AdminStatistics.vue'),
        meta: { requiresAdmin: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 导航守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.requiresAdmin && authStore.userRole !== 'admin') {
    next('/')
  } else {
    next()
  }
})

export default router