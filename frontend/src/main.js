import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// Vue 3 기능 플래그 설정
window.__VUE_PROD_HYDRATION_MISMATCH_DETAILS__ = true;

// 토큰이 있으면 사용자 정보 로드
if (localStorage.getItem('token')) {
  store.dispatch('auth/fetchProfile').catch(error => {
    console.error('사용자 정보 로드 실패:', error);
    // 토큰이 유효하지 않으면 로그아웃 처리
    if (error.response && error.response.status === 401) {
      store.dispatch('auth/logout');
    }
  });
}

// 앱 생성 및 마운트
createApp(App)
  .use(router)
  .use(store)
  .mount('#app')
