<template>
  <div class="user-search-container">
    <h1 class="page-title">사용자 검색</h1>
    
    <!-- 검색 폼 -->
    <div class="search-form">
      <div class="search-input-container">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="사용자명 또는 이메일로 검색" 
          class="search-input"
          @keyup.enter="searchUsers"
        >
        <button class="search-button" @click="searchUsers" :disabled="searchLoading">
          <i class="fas fa-search"></i>
          {{ searchLoading ? '검색 중...' : '검색' }}
        </button>
      </div>
      
      <div class="filter-container">
        <div class="filter-item">
          <label for="skill-level">실력 수준:</label>
          <select id="skill-level" v-model="skillLevel">
            <option value="">전체</option>
            <option value="BEG">입문</option>
            <option value="INT">중급</option>
            <option value="ADV">고급</option>
            <option value="PRO">프로</option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- 검색 결과 -->
    <div class="search-results" v-if="!searchLoading && searchResults.length > 0">
      <h2 class="results-title">검색 결과 ({{ searchResults.length }}명)</h2>
      
      <div class="user-cards">
        <div v-for="user in searchResults" :key="user.id" class="user-card" @click="goToUserProfile(user.id)">
          <div class="user-avatar">
            <img :src="getProfileImageUrl(user.profile_image)" alt="프로필 이미지">
          </div>
          <div class="user-info">
            <h3 class="user-name">{{ user.username }}</h3>
            <p class="user-email">{{ user.email }}</p>
            <div class="user-level">
              <span class="level-value">{{ getSkillLevelText(user.skill_level) }}</span>
            </div>
            <div class="user-stats">
              <div class="stat-item">
                <span class="stat-value">{{ user.matches_played }}</span>
                <span class="stat-label">경기</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ user.wins }}</span>
                <span class="stat-label">승</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ user.draws }}</span>
                <span class="stat-label">무</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ user.losses }}</span>
                <span class="stat-label">패</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 로딩 상태 -->
    <div v-if="searchLoading" class="loading-message">
      <p>사용자를 검색하는 중...</p>
    </div>
    
    <!-- 검색 결과 없음 -->
    <div v-if="!searchLoading && searchResults.length === 0 && hasSearched" class="empty-message">
      <p>검색 결과가 없습니다.</p>
      <p>다른 검색어로 다시 시도해보세요.</p>
    </div>
    
    <!-- 에러 메시지 -->
    <div v-if="searchError" class="error-message">
      <p>{{ searchError }}</p>
      <button @click="searchUsers">다시 시도</button>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'UserSearch',
  
  data() {
    return {
      searchQuery: '',
      skillLevel: '',
      hasSearched: false,
      debounceTimeout: null,
      searchCache: {}, // 검색 결과 캐싱
      lastSearchParams: null // 마지막 검색 파라미터
    };
  },
  
  computed: {
    ...mapState({
      searchResults: state => state.auth.searchResults,
      searchLoading: state => state.auth.searchLoading,
      searchError: state => state.auth.searchError
    }),
    
    // 검색 파라미터 생성
    searchParams() {
      const params = {};
      
      if (this.searchQuery) {
        params.search = this.searchQuery;
      }
      
      if (this.skillLevel) {
        params.skill_level = this.skillLevel;
      }
      
      return params;
    },
    
    // 캐시 키 생성
    cacheKey() {
      return `${this.searchQuery || ''}_${this.skillLevel || ''}`;
    }
  },
  
  watch: {
    // 검색어나 필터가 변경되면 디바운스 검색 실행
    searchQuery() {
      this.debouncedSearch();
    },
    
    skillLevel() {
      this.debouncedSearch();
    }
  },
  
  methods: {
    ...mapActions({
      searchUsersAction: 'auth/searchUsers'
    }),
    
    // 디바운스 검색 (입력이 끝난 후 일정 시간이 지나면 검색 실행)
    debouncedSearch() {
      // 이전 타이머 취소
      if (this.debounceTimeout) {
        clearTimeout(this.debounceTimeout);
      }
      
      // 검색어가 비어있으면 검색하지 않음
      if (!this.searchQuery && !this.skillLevel) {
        return;
      }
      
      // 새 타이머 설정 (500ms 후 검색 실행)
      this.debounceTimeout = setTimeout(() => {
        this.searchUsers();
      }, 500);
    },
    
    async searchUsers() {
      // 검색어와 필터가 모두 비어있으면 검색하지 않음
      if (!this.searchQuery && !this.skillLevel) {
        alert('검색어 또는 필터를 입력해주세요.');
        return;
      }
      
      try {
        // 캐시 키 생성
        const key = this.cacheKey;
        
        // 캐시에 결과가 있으면 캐시된 결과 사용
        if (this.searchCache[key]) {
          console.log('캐시된 검색 결과 사용:', key);
          this.$store.commit('auth/SET_SEARCH_RESULTS', this.searchCache[key]);
          this.hasSearched = true;
          return;
        }
        
        // 캐시에 없으면 API 호출
        const params = this.searchParams;
        this.lastSearchParams = params;
        
        const response = await this.searchUsersAction(params);
        this.hasSearched = true;
        
        // 검색 결과 캐싱
        this.searchCache[key] = response.data;
        console.log('검색 결과 캐싱:', key);
      } catch (error) {
        console.error('사용자 검색 실패:', error);
      }
    },
    
    goToUserProfile(userId) {
      this.$router.push(`/users/${userId}`);
    },
    
    getSkillLevelText(level) {
      const levelMap = {
        'BEG': '입문',
        'INT': '중급',
        'ADV': '고급',
        'PRO': '프로'
      };
      
      return levelMap[level] || level;
    },
    
    getProfileImageUrl(imageUrl) {
      if (!imageUrl) {
        return '/img/default-avatar.png';
      }
      return imageUrl;
    }
  }
};
</script>

<style scoped>
.user-search-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 20px;
  color: var(--text-color);
}

/* 검색 폼 */
.search-form {
  background-color: var(--white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  padding: 20px;
  margin-bottom: 30px;
}

.search-input-container {
  display: flex;
  margin-bottom: 15px;
}

.search-input {
  flex-grow: 1;
  padding: 12px 15px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius) 0 0 var(--border-radius);
  font-size: 16px;
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.search-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 0 20px;
  border-radius: 0 var(--border-radius) var(--border-radius) 0;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
}

.search-button:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.search-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.search-button i {
  margin-right: 8px;
}

.filter-container {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.filter-item {
  display: flex;
  align-items: center;
}

.filter-item label {
  margin-right: 10px;
  font-size: 14px;
  color: var(--text-light);
}

.filter-item select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 14px;
  transition: border-color 0.3s;
}

.filter-item select:focus {
  outline: none;
  border-color: var(--primary-color);
}

/* 검색 결과 */
.search-results {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.results-title {
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 20px;
  color: var(--text-color);
}

.user-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.user-card {
  display: flex;
  background-color: var(--white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  padding: 20px;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.user-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.user-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 20px;
  flex-shrink: 0;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info {
  flex-grow: 1;
}

.user-name {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 5px;
  color: var(--text-color);
}

.user-email {
  font-size: 14px;
  color: var(--text-light);
  margin-bottom: 10px;
}

.user-level {
  display: inline-block;
  background-color: var(--primary-light);
  color: var(--primary-color);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  margin-bottom: 10px;
}

.user-stats {
  display: flex;
  gap: 15px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-color);
  display: block;
}

.stat-label {
  font-size: 12px;
  color: var(--text-light);
}

/* 로딩 및 에러 메시지 */
.loading-message,
.error-message,
.empty-message {
  text-align: center;
  padding: 40px 0;
  background-color: var(--white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  margin-bottom: 20px;
}

.loading-message {
  position: relative;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-message::after {
  content: '';
  position: absolute;
  width: 40px;
  height: 40px;
  border: 4px solid var(--primary-light);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-top: 40px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #e53935;
}

.error-message button {
  background-color: #e53935;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: var(--border-radius);
  margin-top: 10px;
  transition: background-color 0.3s;
}

.error-message button:hover {
  background-color: #c62828;
}

.empty-message {
  color: var(--text-lighter);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .user-cards {
    grid-template-columns: 1fr;
  }
  
  .search-input-container {
    flex-direction: column;
  }
  
  .search-input {
    border-radius: var(--border-radius);
    margin-bottom: 10px;
  }
  
  .search-button {
    border-radius: var(--border-radius);
    justify-content: center;
    padding: 12px;
  }
  
  .filter-container {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-item {
    width: 100%;
  }
  
  .filter-item select {
    flex-grow: 1;
  }
}
</style> 