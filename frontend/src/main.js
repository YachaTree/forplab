import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// 전역 스타일 (필요한 경우)
import './assets/styles/main.css'

// 앱 생성 및 마운트
createApp(App)
  .use(router)
  .use(store)
  .mount('#app')
