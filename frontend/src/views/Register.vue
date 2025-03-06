<template>
  <div class="register-container">
    <div class="register-card">
      <h1>회원가입</h1>
      
      <div v-if="error" class="error-message">
        <div v-if="typeof error === 'string'">{{ error }}</div>
        <ul v-else>
          <li v-for="(errors, field) in error" :key="field">
            <strong>{{ field }}:</strong> {{ errors.join(', ') }}
          </li>
        </ul>
      </div>
      
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">아이디 *</label>
          <input 
            type="text" 
            id="username" 
            v-model="formData.username" 
            required 
            placeholder="아이디를 입력하세요"
          />
        </div>
        
        <div class="form-group">
          <label for="email">이메일 *</label>
          <input 
            type="email" 
            id="email" 
            v-model="formData.email" 
            required 
            placeholder="이메일을 입력하세요"
          />
        </div>
        
        <div class="form-group">
          <label for="password">비밀번호 *</label>
          <input 
            type="password" 
            id="password" 
            v-model="formData.password" 
            required 
            placeholder="비밀번호를 입력하세요"
          />
          <small>8자 이상, 문자와 숫자 조합</small>
        </div>
        
        <div class="form-group">
          <label for="password_confirm">비밀번호 확인 *</label>
          <input 
            type="password" 
            id="password_confirm" 
            v-model="formData.password_confirm" 
            required 
            placeholder="비밀번호를 다시 입력하세요"
          />
        </div>
        
        <div class="form-row">
          <div class="form-group half">
            <label for="first_name">이름</label>
            <input 
              type="text" 
              id="first_name" 
              v-model="formData.first_name" 
              placeholder="이름"
            />
          </div>
          
          <div class="form-group half">
            <label for="last_name">성</label>
            <input 
              type="text" 
              id="last_name" 
              v-model="formData.last_name" 
              placeholder="성"
            />
          </div>
        </div>
        
        <div class="form-group">
          <label for="phone">전화번호</label>
          <input 
            type="tel" 
            id="phone" 
            v-model="formData.phone" 
            placeholder="전화번호를 입력하세요"
          />
        </div>
        
        <div class="form-group">
          <label for="birth_date">생년월일</label>
          <input 
            type="date" 
            id="birth_date" 
            v-model="formData.birth_date"
          />
        </div>
        
        <div class="form-group">
          <label for="skill_level">실력 수준</label>
          <select id="skill_level" v-model="formData.skill_level">
            <option value="BEG">입문</option>
            <option value="INT">중급</option>
            <option value="ADV">고급</option>
            <option value="PRO">프로</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="bio">자기소개</label>
          <textarea 
            id="bio" 
            v-model="formData.bio" 
            rows="3" 
            placeholder="자기소개를 입력하세요"
          ></textarea>
        </div>
        
        <button type="submit" :disabled="loading" class="register-button">
          {{ loading ? '가입 중...' : '회원가입' }}
        </button>
      </form>
      
      <div class="login-link">
        이미 계정이 있으신가요? <router-link to="/login">로그인</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'RegisterView',
  
  setup() {
    const store = useStore();
    const router = useRouter();
    
    // 폼 데이터
    const formData = reactive({
      username: '',
      email: '',
      password: '',
      password_confirm: '',
      first_name: '',
      last_name: '',
      phone: '',
      birth_date: '',
      skill_level: 'BEG',
      bio: '',
    });
    
    // 스토어에서 상태 가져오기
    const loading = computed(() => store.getters.loading);
    const error = computed(() => store.getters.error);
    
    // 회원가입 처리
    const handleRegister = async () => {
      const success = await store.dispatch('register', formData);
      
      if (success) {
        // 회원가입 성공 시 로그인 페이지로 이동
        router.push('/login');
      }
    };
    
    return {
      formData,
      loading,
      error,
      handleRegister,
    };
  },
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 600px;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background-color: white;
  margin-bottom: 40px;
}

h1 {
  text-align: center;
  margin-bottom: 24px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 15px;
}

.half {
  flex: 1;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

input, select, textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

textarea {
  resize: vertical;
}

small {
  display: block;
  margin-top: 5px;
  color: #777;
  font-size: 12px;
}

.register-button {
  width: 100%;
  padding: 12px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 10px;
}

.register-button:hover {
  background-color: #45a049;
}

.register-button:disabled {
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

.login-link {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.login-link a {
  color: #4CAF50;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style> 