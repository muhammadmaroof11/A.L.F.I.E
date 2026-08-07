import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false, title: 'login' }
  },
  {
    path: '/',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: 'overview' }
      },
      {
        path: 'tenants',
        name: 'Tenants',
        component: () => import('../views/Tenants.vue'),
        meta: { title: 'tenant management' }
      },
      {
        path: 'tenants/:id',
        name: 'TenantDetail',
        component: () => import('../views/TenantDetail.vue'),
        meta: { title: 'tenant configuration' }
      },
      {
        path: 'personas',
        name: 'Personas',
        component: () => import('../views/Personas.vue'),
        meta: { title: 'niches & agent personas' }
      },
      {
        path: 'calls',
        name: 'CallLogs',
        component: () => import('../views/CallLogs.vue'),
        meta: { title: 'call logs · auto-qa' }
      },
      {
        path: 'tools-registry',
        name: 'ToolRegistry',
        component: () => import('../views/ToolRegistry.vue'),
        meta: { title: 'tool & webhook registry' }
      },
      {
        path: 'phone-numbers',
        name: 'PhoneNumbers',
        component: () => import('../views/PhoneNumbers.vue'),
        meta: { title: 'sip & phone number router' }
      },
      {
        path: 'debug',
        name: 'DebugLogs',
        component: () => import('../views/DebugLogs.vue'),
        meta: { title: 'debug logs · live' }
      },
      {
        path: 'config',
        name: 'AgentConfig',
        component: () => import('../views/AgentConfig.vue'),
        meta: { title: 'agent config editor' }
      },
      {
        path: 'revenue',
        name: 'Revenue',
        component: () => import('../views/Revenue.vue'),
        meta: { title: 'billing · revenue' }
      },
      {
        path: 'credits',
        name: 'Credits',
        component: () => import('../views/Credits.vue'),
        meta: { title: 'billing · credits' }
      },
      {
        path: 'vouchers',
        name: 'Vouchers',
        component: () => import('../views/Vouchers.vue'),
        meta: { title: 'billing · vouchers' }
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
