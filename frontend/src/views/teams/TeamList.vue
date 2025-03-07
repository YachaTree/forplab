<template>
  <div class="team-list-container">
    <h1 class="page-title">팀 목록</h1>
    
    <!-- 필터 섹션 -->
    <div class="filters-container">
      <div class="filter-group">
        <label>지역</label>
        <select v-model="filters.region" @change="applyFilters">
          <option value="">전체</option>
          <option value="seoul">서울</option>
          <option value="gyeonggi">경기</option>
          <option value="incheon">인천</option>
          <option value="other">기타</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>팀 레벨</label>
        <select v-model="filters.level" @change="applyFilters">
          <option value="">전체</option>
          <option value="beginner">입문</option>
          <option value="intermediate">중급</option>
          <option value="advanced">고급</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>모집 상태</label>
        <select v-model="filters.is_recruiting" @change="applyFilters">
          <option value="">전체</option>
          <option value="true">모집중</option>
          <option value="false">모집 마감</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>검색</label>
        <input 
          type="text" 
          v-model="filters.search" 
          @input="debounceSearch"
          placeholder="팀 이름 검색"
        >
      </div>
      
      <button class="reset-button" @click="resetFilters">필터 초기화</button>
    </div>
    
    <!-- 팀 생성 버튼 -->
    <div class="action-buttons" v-if="isAuthenticated">
      <button class="create-team-btn" @click="goToTeamCreate">
        <i class="fas fa-plus"></i> 새 팀 만들기
      </button>
    </div>
    
    <!-- 로딩 및 에러 메시지 -->
    <div v-if="loading" class="loading-message">
      <p>팀 목록을 불러오는 중...</p>
    </div>
    
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchTeams">다시 시도</button>
    </div>
    
    <!-- 팀 목록 -->
    <div v-if="!loading && !error && teams.length === 0" class="empty-message">
      <p>조건에 맞는 팀이 없습니다.</p>
    </div>
    
    <div v-if="!loading && !error && teams.length > 0" class="teams-grid">
      <div v-for="team in teams" :key="team.id" class="team-card" @click="goToTeamDetail(team.id)">
        <div class="team-image">
          <img :src="team.logo || '/img/default-team.jpg'" alt="Team" />
          <div class="team-level" :class="'level-' + team.level">
            {{ getLevelText(team.level) }}
          </div>
        </div>
        
        <div class="team-content">
          <h3 class="team-name">{{ team.name }}</h3>
          
          <div class="team-region">
            <i class="fas fa-map-marker-alt"></i>
            <span>{{ team.region }}</span>
          </div>
          
          <div class="team-info">
            <div class="info-item">
              <i class="fas fa-users"></i>
              <span>{{ team.member_count }}명</span>
            </div>
            
            <div class="info-item">
              <i class="fas fa-calendar-alt"></i>
              <span>{{ team.match_count }}경기</span>
            </div>
            
            <div class="info-item">
              <i class="fas fa-trophy"></i>
              <span>{{ team.win_count }}승 {{ team.draw_count }}무 {{ team.lose_count }}패</span>
            </div>
          </div>
          
          <div class="team-recruiting" v-if="team.is_recruiting">
            <span class="recruiting-badge">모집중</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 페이지네이션 -->
    <div v-if="!loading && !error && teams.length > 0" class="pagination">
      <button :disabled="page === 1" @click="prevPage">이전</button>
      <span>{{ page }} / {{ totalPages }}</span>
      <button :disabled="page === totalPages" @click="nextPage">다음</button>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
  name: 'TeamList',
  
  data() {
    return {
      filters: {
        region: '',
        level: '',
        is_recruiting: '',
        search: ''
      },
      page: 1,
      pageSize: 10,
      totalPages: 1,
      searchTimeout: null
    };
  },
  
  computed: {
    ...mapState({
      teams: state => state.teams.teams,
      loading: state => state.teams.teamsLoading,
      error: state => state.teams.teamsError
    }),
    
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated'
    })
  },
  
  created() {
    this.fetchTeams();
  },
  
  methods: {
    ...mapActions({
      fetchTeamsAction: 'teams/fetchTeams'
    }),
    
    async fetchTeams() {
      try {
        const params = {
          ...this.filters,
          page: this.page,
          page_size: this.pageSize
        };
        
        const response = await this.fetchTeamsAction(params);
        
        // 페이지네이션 정보 업데이트 (백엔드에서 제공하는 경우)
        if (response && response.data && response.data.count) {
          this.totalPages = Math.ceil(response.data.count / this.pageSize);
        }
      } catch (error) {
        console.error('팀 목록 조회 실패:', error);
      }
    },
    
    applyFilters() {
      this.page = 1; // 필터 변경 시 첫 페이지로 이동
      this.fetchTeams();
    },
    
    resetFilters() {
      this.filters = {
        region: '',
        level: '',
        is_recruiting: '',
        search: ''
      };
      this.page = 1;
      this.fetchTeams();
    },
    
    debounceSearch() {
      clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => {
        this.applyFilters();
      }, 500);
    },
    
    changePage(newPage) {
      this.page = newPage;
      this.fetchTeams();
    },
    
    prevPage() {
      if (this.page > 1) {
        this.page--;
        this.fetchTeams();
      }
    },
    
    nextPage() {
      if (this.page < this.totalPages) {
        this.page++;
        this.fetchTeams();
      }
    },
    
    goToTeamDetail(teamId) {
      this.$router.push({ name: 'TeamDetail', params: { id: teamId } });
    },
    
    goToTeamCreate() {
      this.$router.push({ name: 'TeamCreate' });
    },
    
    getLevelText(level) {
      const levelMap = {
        'beginner': '입문',
        'intermediate': '중급',
        'advanced': '고급'
      };
      
      return levelMap[level] || level;
    }
  }
};
</script>

<style scoped>
.team-list-container {
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

.action-buttons {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.create-team-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 20px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.create-team-btn:hover {
  background-color: #388e3c;
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

.teams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.team-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.team-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.team-image {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.team-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.team-level {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.level-beginner {
  background-color: #e3f2fd;
  color: #1976d2;
}

.level-intermediate {
  background-color: #fff8e1;
  color: #ffa000;
}

.level-advanced {
  background-color: #fbe9e7;
  color: #d84315;
}

.team-content {
  padding: 15px;
  position: relative;
}

.team-name {
  font-size: 18px;
  margin: 0 0 10px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.team-region {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
  color: #555;
  font-size: 14px;
}

.team-region i {
  margin-right: 5px;
  margin-top: 3px;
  color: #777;
}

.team-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #666;
}

.info-item i {
  margin-right: 8px;
  width: 16px;
  text-align: center;
}

.team-recruiting {
  position: absolute;
  top: 15px;
  right: 15px;
}

.recruiting-badge {
  background-color: #4caf50;
  color: white;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
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
  .teams-grid {
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