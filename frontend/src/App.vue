<template>
  <div id="app">
    <Navbar />
    
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
                <li><router-link to="/users/search">사용자 검색</router-link></li>
                <li><router-link to="/friends">친구</router-link></li>
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
          <p>&copy; 2025 플랩풋볼 클론. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue';

export default {
  name: 'App',
  components: {
    Navbar
  }
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

/* 메인 콘텐츠 */
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

.logo-text {
  font-size: 1.5rem;
  font-weight: bold;
  color: #4CAF50;
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
  .footer-content {
    flex-direction: column;
  }
  
  .footer-links {
    flex-direction: column;
    gap: 20px;
  }
}

@media (max-width: 576px) {
  .footer-links {
    gap: 15px;
  }
  
  .footer-section h3 {
    margin-bottom: 10px;
  }
  
  .footer-section ul li {
    margin-bottom: 8px;
  }
}
</style>
