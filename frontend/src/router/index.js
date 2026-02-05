import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Input',
    component: () => import('../pages/InputPage.vue')
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../pages/ChatPage.vue'),
    props: (route) => ({ initialMessage: route.query.message })
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
