<template>
  <div class="login-container">
    <div class="login-card">
      <h1>로그인</h1>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">아이디</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            required 
            placeholder="아이디를 입력하세요"
          />
        </div>
        
        <div class="form-group">
          <label for="password">비밀번호</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            required 
            placeholder="비밀번호를 입력하세요"
          />
        </div>
        
        <button type="submit" :disabled="loading" class="login-button">
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>
      </form>
      
      <div class="register-link">
        계정이 없으신가요? <router-link to="/register">회원가입</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter, useRoute } from 'vue-router';

export default {
  name: 'LoginView',
  
  setup() {
    const store = useStore();
    const router = useRouter();
    const route = useRoute();
    
    // 상태
    const username = ref('');
    const password = ref('');
    
    // 스토어에서 상태 가져오기
    const loading = computed(() => store.getters.loading);
    const error = computed(() => store.getters.error);
    
    // 로그인 처리
    const handleLogin = async () => {
      const success = await store.dispatch('login', {
        username: username.value,
        password: password.value,
      });
      
      if (success) {
        // 리다이렉트 처리
        const redirectPath = route.query.redirect || '/';
        router.push(redirectPath);
      }
    };
    
    return {
      username,
      password,
      loading,
      error,
      handleLogin,
    };
  },
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background-color: white;
}

h1 {
  text-align: center;
  margin-bottom: 24px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.login-button {
  width: 100%;
  padding: 12px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-button:hover {
  background-color: #45a049;
}

.login-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.register-link {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.register-link a {
  color: #4CAF50;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}
</style> 