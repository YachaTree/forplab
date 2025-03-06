<template>
  <div class="home-container">
    <div class="hero-section">
      <div class="hero-content">
        <h1>플랩풋볼</h1>
        <p class="hero-subtitle">축구를 일상에 가까이</p>
        <p class="hero-description">
          혼자서도 함께 축구를 즐길 수 있는 세상을 만들고 있습니다.
          <br>
          지금 바로 플랩풋볼과 함께 축구를 시작해보세요!
        </p>
        <div class="hero-buttons">
          <router-link to="/matches" class="btn btn-primary">매치 찾기</router-link>
          <router-link to="/venues" class="btn btn-secondary">구장 보기</router-link>
        </div>
      </div>
    </div>

    <div class="features-section">
      <h2>플랩풋볼 특징</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">🏆</div>
          <h3>소셜 매치</h3>
          <p>혼자와도 함께 즐기는 축구! 새로운 친구들과 함께 축구를 즐겨보세요.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">👥</div>
          <h3>팀 매치</h3>
          <p>나만의 팀을 만들고 다른 팀과 경기를 펼쳐보세요.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🏟️</div>
          <h3>구장 예약</h3>
          <p>전국 각지의 축구장을 쉽고 빠르게 예약할 수 있습니다.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3>레이팅 시스템</h3>
          <p>나의 실력을 객관적으로 평가하고 성장해보세요.</p>
        </div>
      </div>
    </div>

    <div class="cta-section">
      <h2>지금 바로 시작하세요!</h2>
      <p>플랩풋볼과 함께 축구의 즐거움을 경험해보세요.</p>
      <div class="cta-buttons">
        <router-link v-if="!isAuthenticated" to="/register" class="btn btn-primary">회원가입</router-link>
        <router-link v-if="!isAuthenticated" to="/login" class="btn btn-secondary">로그인</router-link>
        <router-link v-if="isAuthenticated" to="/matches" class="btn btn-primary">매치 참가하기</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'HomeView',
  
  setup() {
    const store = useStore();
    
    const isAuthenticated = computed(() => store.getters.isAuthenticated);
    
    return {
      isAuthenticated,
    };
  },
};
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero-section {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 500px;
  background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('https://images.unsplash.com/photo-1556056504-5c7696c4c28d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2076&q=80');
  background-size: cover;
  background-position: center;
  color: white;
  text-align: center;
  padding: 40px;
  border-radius: 8px;
  margin-bottom: 40px;
}

.hero-content {
  max-width: 800px;
}

h1 {
  font-size: 3rem;
  margin-bottom: 10px;
}

.hero-subtitle {
  font-size: 1.5rem;
  margin-bottom: 20px;
}

.hero-description {
  font-size: 1.1rem;
  margin-bottom: 30px;
  line-height: 1.6;
}

.hero-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.btn {
  display: inline-block;
  padding: 12px 24px;
  border-radius: 4px;
  font-weight: bold;
  text-decoration: none;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background-color: #45a049;
}

.btn-secondary {
  background-color: transparent;
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.features-section {
  padding: 60px 0;
  text-align: center;
}

.features-section h2 {
  font-size: 2rem;
  margin-bottom: 40px;
  color: #333;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.feature-card {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

.cta-section {
  background-color: #f9f9f9;
  padding: 60px;
  text-align: center;
  border-radius: 8px;
  margin-bottom: 60px;
}

.cta-section h2 {
  font-size: 2rem;
  margin-bottom: 15px;
  color: #333;
}

.cta-section p {
  font-size: 1.1rem;
  margin-bottom: 30px;
  color: #666;
}

.cta-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.cta-buttons .btn-secondary {
  border-color: #4CAF50;
  color: #4CAF50;
}

.cta-buttons .btn-secondary:hover {
  background-color: rgba(76, 175, 80, 0.1);
}

@media (max-width: 768px) {
  .hero-section {
    min-height: 400px;
  }
  
  h1 {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.2rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .cta-section {
    padding: 40px 20px;
  }
}
</style> 