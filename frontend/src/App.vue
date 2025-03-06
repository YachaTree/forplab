<template>
  <div id="app">
    <header class="header">
      <div class="container">
        <div class="logo">
          <router-link to="/">
            <span class="logo-text">플랩풋볼</span>
          </router-link>
        </div>
        
        <nav class="nav">
          <ul class="nav-list">
            <li class="nav-item">
              <router-link to="/matches">매치</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/venues">구장</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/teams">팀</router-link>
            </li>
          </ul>
        </nav>
        
        <div class="auth-buttons">
          <template v-if="isAuthenticated">
            <div class="user-menu">
              <button class="user-button" @click="toggleUserMenu">
                {{ user ? user.username : '사용자' }}
              </button>
              <div v-if="showUserMenu" class="user-dropdown">
                <router-link to="/profile" class="dropdown-item">프로필</router-link>
                <a href="#" class="dropdown-item" @click.prevent="handleLogout">로그아웃</a>
              </div>
            </div>
          </template>
          <template v-else>
            <router-link to="/login" class="login-button">로그인</router-link>
            <router-link to="/register" class="register-button">회원가입</router-link>
          </template>
        </div>
      </div>
    </header>
    
    <main class="main-content">
      <router-view />
    </main>
    
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-logo">
            <span class="logo-text">플랩풋볼</span>
            <p class="footer-tagline">축구를 일상에 가까이</p>
          </div>
          
          <div class="footer-links">
            <div class="footer-section">
              <h3>서비스</h3>
              <ul>
                <li><router-link to="/matches">매치</router-link></li>
                <li><router-link to="/venues">구장</router-link></li>
                <li><router-link to="/teams">팀</router-link></li>
              </ul>
            </div>
            
            <div class="footer-section">
              <h3>정보</h3>
              <ul>
                <li><a href="#">이용약관</a></li>
                <li><a href="#">개인정보처리방침</a></li>
                <li><a href="#">회사소개</a></li>
              </ul>
            </div>
            
            <div class="footer-section">
              <h3>고객센터</h3>
              <ul>
                <li><a href="#">FAQ</a></li>
                <li><a href="#">문의하기</a></li>
                <li><a href="#">공지사항</a></li>
              </ul>
            </div>
          </div>
        </div>
        
        <div class="footer-bottom">
          <p>&copy; 2023 플랩풋볼 클론. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'App',
  
  setup() {
    const store = useStore();
    const router = useRouter();
    
    const showUserMenu = ref(false);
    
    const isAuthenticated = computed(() => store.getters.isAuthenticated);
    const user = computed(() => store.getters.user);
    
    // 사용자 메뉴 토글
    const toggleUserMenu = () => {
      showUserMenu.value = !showUserMenu.value;
    };
    
    // 로그아웃 처리
    const handleLogout = () => {
      store.dispatch('logout');
      router.push('/');
      showUserMenu.value = false;
    };
    
    // 클릭 이벤트 리스너 (사용자 메뉴 외부 클릭 시 닫기)
    const handleClickOutside = (event) => {
      const userMenu = document.querySelector('.user-menu');
      if (userMenu && !userMenu.contains(event.target)) {
        showUserMenu.value = false;
      }
    };
    
    // 사용자 정보 가져오기
    onMounted(() => {
      if (isAuthenticated.value && !user.value) {
        store.dispatch('fetchUserProfile');
      }
      
      // 클릭 이벤트 리스너 등록
      document.addEventListener('click', handleClickOutside);
    });
    
    return {
      isAuthenticated,
      user,
      showUserMenu,
      toggleUserMenu,
      handleLogout,
    };
  },
};
</script>

<style>
/* 전역 스타일 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Noto Sans KR', sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f5f5f5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

a {
  text-decoration: none;
  color: inherit;
}

ul {
  list-style: none;
}

/* 헤더 스타일 */
.header {
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: bold;
  color: #4CAF50;
}

.nav-list {
  display: flex;
  gap: 20px;
}

.nav-item a {
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-item a:hover,
.nav-item a.router-link-active {
  background-color: rgba(76, 175, 80, 0.1);
  color: #4CAF50;
}

.auth-buttons {
  display: flex;
  gap: 10px;
}

.login-button,
.register-button {
  padding: 8px 16px;
  border-radius: 4px;
  transition: all 0.3s;
}

.login-button {
  color: #4CAF50;
}

.register-button {
  background-color: #4CAF50;
  color: white;
}

.login-button:hover {
  background-color: rgba(76, 175, 80, 0.1);
}

.register-button:hover {
  background-color: #45a049;
}

/* 사용자 메뉴 스타일 */
.user-menu {
  position: relative;
}

.user-button {
  padding: 8px 16px;
  border: none;
  background-color: transparent;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-button:hover {
  background-color: rgba(76, 175, 80, 0.1);
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 150px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  z-index: 10;
}

.dropdown-item {
  display: block;
  padding: 10px 15px;
  transition: background-color 0.3s;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}

/* 메인 콘텐츠 스타일 */
.main-content {
  min-height: calc(100vh - 70px - 250px); /* 헤더와 푸터 높이를 제외한 최소 높이 */
  padding: 30px 0;
}

/* 푸터 스타일 */
.footer {
  background-color: #333;
  color: #fff;
  padding: 50px 0 20px;
}

.footer-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 30px;
}

.footer-logo {
  margin-bottom: 20px;
}

.footer-tagline {
  margin-top: 10px;
  color: #aaa;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  gap: 40px;
}

.footer-section h3 {
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.footer-section ul li {
  margin-bottom: 10px;
}

.footer-section a {
  color: #aaa;
  transition: color 0.3s;
}

.footer-section a:hover {
  color: #fff;
}

.footer-bottom {
  border-top: 1px solid #444;
  padding-top: 20px;
  text-align: center;
  color: #aaa;
  font-size: 0.9rem;
}

/* 반응형 스타일 */
@media (max-width: 768px) {
  .header .container {
    flex-direction: column;
    height: auto;
    padding: 15px;
  }
  
  .logo {
    margin-bottom: 15px;
  }
  
  .nav {
    margin-bottom: 15px;
  }
  
  .nav-list {
    justify-content: center;
  }
  
  .auth-buttons {
    justify-content: center;
  }
  
  .footer-content {
    flex-direction: column;
  }
  
  .footer-links {
    flex-direction: column;
    gap: 20px;
  }
}
</style>
