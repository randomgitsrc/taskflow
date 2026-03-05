import { createRouter, createWebHistory } from 'vue-router'
import TaskList from './views/TaskList.vue'
import TaskDetail from './views/TaskDetail.vue'
import Stats from './views/Stats.vue'
import Projects from './views/Projects.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'tasks',
      component: TaskList,
    },
    {
      path: '/task/:id',
      name: 'detail',
      component: TaskDetail,
    },
    {
      path: '/stats',
      name: 'stats',
      component: Stats,
    },
    {
      path: '/projects',
      name: 'projects',
      component: Projects,
    },
  ],
})

export default router
