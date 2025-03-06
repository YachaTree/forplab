import { createRouter, createWebHistory } from 'vue-router';
import store from '@/store';

// 페이지 컴포넌트 (나중에 구현 예정)
const Home = () => import('@/views/Home.vue');
const Login = () => import('@/views/Login.vue');
const Register = () => import('@/views/Register.vue');
const Profile = () => import('@/views/Profile.vue');
const MatchList = () => import('@/views/matches/MatchList.vue');
const MatchDetail = () => import('@/views/matches/MatchDetail.vue');
const MatchCreate = () => import('@/views/matches/MatchCreate.vue');
const VenueList = () => import('@/views/venues/VenueList.vue');
const VenueDetail = () => import('@/views/venues/VenueDetail.vue');
const TeamList = () => import('@/views/teams/TeamList.vue');
const TeamDetail = () => import('@/views/teams/TeamDetail.vue');
const TeamCreate = () => import('@/views/teams/TeamCreate.vue');

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true },
  },
  {
    path: '/matches',
    name: 'MatchList',
    component: MatchList,
  },
  {
    path: '/matches/:id',
    name: 'MatchDetail',
    component: MatchDetail,
    props: true,
  },
  {
    path: '/matches/create',
    name: 'MatchCreate',
    component: MatchCreate,
    meta: { requiresAuth: true },
  },
  {
    path: '/venues',
    name: 'VenueList',
    component: VenueList,
  },
  {
    path: '/venues/:id',
    name: 'VenueDetail',
    component: VenueDetail,
    props: true,
  },
  {
    path: '/teams',
    name: 'TeamList',
    component: TeamList,
  },
  {
    path: '/teams/:id',
    name: 'TeamDetail',
    component: TeamDetail,
    props: true,
  },
  {
    path: '/teams/create',
    name: 'TeamCreate',
    component: TeamCreate,
    meta: { requiresAuth: true },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// 네비게이션 가드
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters.isAuthenticated;
  
  // 인증이 필요한 페이지
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } });
    return;
  }
  
  // 게스트만 접근 가능한 페이지 (로그인, 회원가입)
  if (to.meta.requiresGuest && isAuthenticated) {
    next({ name: 'Home' });
    return;
  }
  
  next();
});

export default router; 