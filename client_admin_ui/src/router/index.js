import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('../layouts/ClientLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue')
      },
      {
        path: 'leads',
        name: 'Leads Pipeline',
        component: () => import('../views/LeadsKanban.vue')
      },
      {
        path: 'interactions',
        name: 'Interaction History',
        component: () => import('../views/InteractionHistory.vue')
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('../views/Analytics.vue')
      },
      {
        path: 'agent',
        name: 'Agent Config',
        component: () => import('../views/AgentConfiguration.vue')
      },
      {
        path: 'billing',
        name: 'Billing',
        component: () => import('../views/Billing.vue')
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to) => {
  const authStore = useAuthStore();
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return '/login';
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    return '/';
  }
});

export default router;
