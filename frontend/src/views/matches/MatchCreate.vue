<template>
  <div class="match-create-container">
    <h1 class="page-title">새 매치 생성</h1>
    
    <div v-if="loading" class="loading-message">
      <p>처리 중...</p>
    </div>
    
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>
    
    <form @submit.prevent="submitForm" class="match-form">
      <div class="form-group">
        <label for="title">매치 제목 *</label>
        <input 
          type="text" 
          id="title" 
          v-model="form.title" 
          required
          placeholder="매치 제목을 입력하세요"
        >
      </div>
      
      <div class="form-group">
        <label for="description">매치 설명</label>
        <textarea 
          id="description" 
          v-model="form.description" 
          rows="4"
          placeholder="매치에 대한 설명을 입력하세요"
        ></textarea>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label for="date">날짜 *</label>
          <input 
            type="date" 
            id="date" 
            v-model="form.date" 
            required
          >
        </div>
        
        <div class="form-group">
          <label for="start_time">시작 시간 *</label>
          <input 
            type="time" 
            id="start_time" 
            v-model="form.start_time" 
            required
          >
        </div>
        
        <div class="form-group">
          <label for="end_time">종료 시간 *</label>
          <input 
            type="time" 
            id="end_time" 
            v-model="form.end_time" 
            required
          >
        </div>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label for="match_type">매치 유형 *</label>
          <select id="match_type" v-model="form.match_type" required>
            <option value="">선택하세요</option>
            <option value="friendly">친선전</option>
            <option value="league">리그전</option>
            <option value="tournament">토너먼트</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="skill_level">실력 수준 *</label>
          <select id="skill_level" v-model="form.skill_level" required>
            <option value="">선택하세요</option>
            <option value="beginner">입문</option>
            <option value="intermediate">중급</option>
            <option value="advanced">고급</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="gender">성별 *</label>
          <select id="gender" v-model="form.gender" required>
            <option value="">선택하세요</option>
            <option value="male">남성</option>
            <option value="female">여성</option>
            <option value="mixed">혼성</option>
          </select>
        </div>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label for="max_players">최대 인원 *</label>
          <input 
            type="number" 
            id="max_players" 
            v-model.number="form.max_players" 
            min="2" 
            required
          >
        </div>
        
        <div class="form-group">
          <label for="price">참가비 (원) *</label>
          <input 
            type="number" 
            id="price" 
            v-model.number="form.price" 
            min="0" 
            required
          >
        </div>
      </div>
      
      <div class="form-group">
        <label for="venue">구장 *</label>
        <select id="venue" v-model="form.venue" required>
          <option value="">구장을 선택하세요</option>
          <option v-for="venue in venues" :key="venue.id" :value="venue.id">
            {{ venue.name }}
          </option>
        </select>
      </div>
      
      <div class="form-actions">
        <button type="button" class="cancel-btn" @click="goBack">취소</button>
        <button type="submit" class="submit-btn" :disabled="loading">매치 생성</button>
      </div>
    </form>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'MatchCreate',
  
  data() {
    return {
      form: {
        title: '',
        description: '',
        date: '',
        start_time: '',
        end_time: '',
        match_type: '',
        skill_level: '',
        gender: '',
        max_players: 10,
        price: 0,
        venue: ''
      },
      loading: false,
      error: null
    };
  },
  
  computed: {
    ...mapState({
      venues: state => state.venues
    })
  },
  
  created() {
    this.fetchVenues();
  },
  
  methods: {
    ...mapActions(['fetchVenues']),
    
    async submitForm() {
      this.loading = true;
      this.error = null;
      
      try {
        // 날짜 형식 검증
        if (new Date(this.form.date) < new Date().setHours(0, 0, 0, 0)) {
          throw new Error('과거 날짜로 매치를 생성할 수 없습니다.');
        }
        
        // 시간 형식 검증
        if (this.form.start_time >= this.form.end_time) {
          throw new Error('종료 시간은 시작 시간보다 나중이어야 합니다.');
        }
        
        const response = await this.$store.dispatch('createMatch', this.form);
        this.$toast.success('매치가 성공적으로 생성되었습니다.');
        this.$router.push({ name: 'MatchDetail', params: { id: response.data.id } });
      } catch (error) {
        console.error('매치 생성 실패:', error);
        this.error = error.message || error.response?.data?.detail || '매치 생성에 실패했습니다.';
      } finally {
        this.loading = false;
      }
    },
    
    goBack() {
      this.$router.go(-1);
    }
  }
};
</script>

<style scoped>
.match-create-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  font-size: 28px;
  margin-bottom: 20px;
  color: #333;
}

.loading-message,
.error-message {
  text-align: center;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.loading-message {
  background-color: #f0f8ff;
  color: #0066cc;
}

.error-message {
  background-color: #ffebee;
  color: #d32f2f;
}

.match-form {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 25px;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

input,
select,
textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

textarea {
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 30px;
}

.cancel-btn,
.submit-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cancel-btn {
  background-color: #f0f0f0;
  color: #333;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.submit-btn {
  background-color: #1976d2;
  color: white;
}

.submit-btn:hover {
  background-color: #1565c0;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
}
</style> 