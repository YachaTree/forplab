import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// Vue 3 기능 플래그 설정
window.__VUE_PROD_HYDRATION_MISMATCH_DETAILS__ = true;

// 앱 생성 및 마운트
createApp(App)
  .use(router)
  .use(store)
  .mount('#app')
