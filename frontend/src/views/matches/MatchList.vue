<template>
  <div class="match-list-container">
    <h1 class="page-title">매치 목록</h1>
    
    <!-- 필터 섹션 -->
    <div class="filters-container">
      <div class="filter-group">
        <label>날짜</label>
        <input type="date" v-model="filters.date" @change="applyFilters" />
      </div>
      
      <div class="filter-group">
        <label>실력 수준</label>
        <select v-model="filters.skill_level" @change="applyFilters">
          <option value="">전체</option>
          <option value="beginner">입문</option>
          <option value="intermediate">중급</option>
          <option value="advanced">고급</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>성별</label>
        <select v-model="filters.gender" @change="applyFilters">
          <option value="">전체</option>
          <option value="male">남성</option>
          <option value="female">여성</option>
          <option value="mixed">혼성</option>
        </select>
      </div>
      
      <button class="reset-button" @click="resetFilters">필터 초기화</button>
    </div>
    
    <!-- 로딩 및 에러 메시지 -->
    <div v-if="loading" class="loading-message">
      <p>매치 목록을 불러오는 중...</p>
    </div>
    
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchMatches">다시 시도</button>
    </div>
    
    <!-- 매치 목록 -->
    <div v-if="!loading && !error && matches.length === 0" class="empty-message">
      <p>조건에 맞는 매치가 없습니다.</p>
    </div>
    
    <div v-if="!loading && !error && matches.length > 0" class="matches-grid">
      <div v-for="match in matches" :key="match.id" class="match-card" @click="goToMatchDetail(match.id)">
        <div class="match-header">
          <span class="match-date">{{ formatDate(match.date) }} {{ match.start_time }}</span>
          <span :class="['match-status', `status-${match.status}`]">{{ getStatusText(match.status) }}</span>
        </div>
        
        <h3 class="match-title">{{ match.title }}</h3>
        
        <div class="match-venue">
          <i class="fas fa-map-marker-alt"></i>
          <span>{{ match.venue_name }}</span>
        </div>
        
        <div class="match-info">
          <div class="info-item">
            <i class="fas fa-users"></i>
            <span>{{ match.current_players_count }}/{{ match.max_players }}</span>
          </div>
          
          <div class="info-item">
            <i class="fas fa-trophy"></i>
            <span>{{ getSkillLevelText(match.skill_level) }}</span>
          </div>
          
          <div class="info-item">
            <i class="fas fa-venus-mars"></i>
            <span>{{ getGenderText(match.gender) }}</span>
          </div>
        </div>
        
        <div class="match-price">
          <span>{{ formatPrice(match.price) }}원</span>
        </div>
      </div>
    </div>
    
    <!-- 페이지네이션 -->
    <div v-if="!loading && !error && matches.length > 0" class="pagination">
      <button :disabled="page === 1" @click="prevPage">이전</button>
      <span>{{ page }} / {{ totalPages }}</span>
      <button :disabled="page === totalPages" @click="nextPage">다음</button>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'MatchList',
  
  data() {
    return {
      filters: {
        date: '',
        skill_level: '',
        gender: '',
        page: 1
      },
      page: 1,
      pageSize: 10,
      totalPages: 1
    };
  },
  
  computed: {
    ...mapState({
      matches: state => state.matches,
      loading: state => state.matchesLoading,
      error: state => state.matchesError
    })
  },
  
  created() {
    this.fetchMatches();
  },
  
  methods: {
    ...mapActions(['fetchMatches']),
    
    async fetchMatches() {
      try {
        const params = {
          ...this.filters,
          page: this.page,
          page_size: this.pageSize
        };
        
        const response = await this.$store.dispatch('fetchMatches', params);
        
        // 페이지네이션 정보 업데이트 (백엔드에서 제공하는 경우)
        if (response && response.data && response.data.count) {
          this.totalPages = Math.ceil(response.data.count / this.pageSize);
        }
      } catch (error) {
        console.error('매치 목록 조회 실패:', error);
      }
    },
    
    applyFilters() {
      this.page = 1; // 필터 적용 시 첫 페이지로 이동
      this.fetchMatches();
    },
    
    resetFilters() {
      this.filters = {
        date: '',
        skill_level: '',
        gender: '',
        page: 1
      };
      this.page = 1;
      this.fetchMatches();
    },
    
    prevPage() {
      if (this.page > 1) {
        this.page--;
        this.fetchMatches();
      }
    },
    
    nextPage() {
      if (this.page < this.totalPages) {
        this.page++;
        this.fetchMatches();
      }
    },
    
    goToMatchDetail(matchId) {
      this.$router.push({ name: 'MatchDetail', params: { id: matchId } });
    },
    
    formatDate(dateString) {
      const date = new Date(dateString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      
      return `${year}.${month}.${day}`;
    },
    
    formatPrice(price) {
      return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },
    
    getStatusText(status) {
      const statusMap = {
        'open': '모집중',
        'full': '모집완료',
        'in_progress': '진행중',
        'completed': '종료',
        'canceled': '취소'
      };
      
      return statusMap[status] || status;
    },
    
    getSkillLevelText(skillLevel) {
      const skillLevelMap = {
        'beginner': '입문',
        'intermediate': '중급',
        'advanced': '고급'
      };
      
      return skillLevelMap[skillLevel] || skillLevel;
    },
    
    getGenderText(gender) {
      const genderMap = {
        'male': '남성',
        'female': '여성',
        'mixed': '혼성'
      };
      
      return genderMap[gender] || gender;
    }
  }
};
</script>

<style scoped>
.match-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  font-size: 28px;
  margin-bottom: 20px;
  color: #333;
}

.filters-container {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-size: 14px;
  margin-bottom: 5px;
  color: #555;
}

.filter-group select,
.filter-group input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 150px;
}

.reset-button {
  align-self: flex-end;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 15px;
  cursor: pointer;
  margin-left: auto;
}

.loading-message,
.error-message,
.empty-message {
  text-align: center;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin: 20px 0;
}

.error-message {
  color: #e74c3c;
}

.matches-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.match-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 15px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.match-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.match-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.match-date {
  font-size: 14px;
  color: #666;
}

.match-status {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.status-open {
  background-color: #e3f2fd;
  color: #1976d2;
}

.status-full {
  background-color: #fff8e1;
  color: #ffa000;
}

.status-in_progress {
  background-color: #e8f5e9;
  color: #388e3c;
}

.status-completed {
  background-color: #eeeeee;
  color: #616161;
}

.status-canceled {
  background-color: #ffebee;
  color: #d32f2f;
}

.match-title {
  font-size: 18px;
  margin: 10px 0;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.match-venue {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  color: #555;
  font-size: 14px;
}

.match-venue i {
  margin-right: 5px;
  color: #777;
}

.match-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #666;
}

.info-item i {
  margin-right: 5px;
  width: 16px;
  text-align: center;
}

.match-price {
  font-weight: 600;
  color: #2c3e50;
  font-size: 16px;
  text-align: right;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}

.pagination button {
  padding: 8px 15px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .matches-grid {
    grid-template-columns: 1fr;
  }
  
  .filters-container {
    flex-direction: column;
  }
  
  .filter-group {
    width: 100%;
  }
}
</style> 