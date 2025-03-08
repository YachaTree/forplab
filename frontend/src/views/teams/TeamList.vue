<template>
  <div class="team-list-container">
    <h1 class="page-title">팀 목록</h1>
    
    <!-- 필터 토글 버튼 -->
    <div class="filter-toggle">
      <button @click="showFilters = !showFilters" class="toggle-button">
        <i :class="showFilters ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
        필터 {{ showFilters ? '접기' : '펼치기' }}
      </button>
    </div>
    
    <!-- 필터 섹션 -->
    <div class="filters-container" v-show="showFilters">
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
        <label>정렬</label>
        <select v-model="sortOption" @change="applyFilters">
          <option value="name">이름순</option>
          <option value="-created_at">최신순</option>
          <option value="created_at">오래된순</option>
          <option value="-members_count">팀원 많은순</option>
          <option value="members_count">팀원 적은순</option>
          <option value="-win_rate">승률 높은순</option>
          <option value="win_rate">승률 낮은순</option>
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
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>팀 목록을 불러오는 중...</p>
    </div>
    
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchTeams">다시 시도</button>
    </div>
    
    <!-- 팀 목록 -->
    <transition name="fade">
      <div v-if="!loading && !error && teams.length === 0" class="empty-message">
        <i class="fas fa-search"></i>
        <p>조건에 맞는 팀이 없습니다.</p>
        <button @click="resetFilters" class="reset-search-btn">필터 초기화</button>
      </div>
    </transition>
    
    <transition-group name="fade" tag="div" class="teams-grid" v-if="!loading && !error && teams.length > 0">
      <div v-for="team in teams" :key="team.id" class="team-card" @click="goToTeamDetail(team.id)">
        <div class="team-logo">
          <img :src="team.logo || '/img/default-team.jpg'" alt="Team Logo" />
          <div class="team-level-badge" :class="'level-' + team.level">
            {{ getLevelText(team.level) }}
          </div>
        </div>
        
        <div class="team-content">
          <h3 class="team-name">{{ team.name }}</h3>
          
          <div class="team-region">
            <i class="fas fa-map-marker-alt"></i>
            <span>{{ getRegionText(team.region) }}</span>
          </div>
          
          <div class="team-info">
            <div class="info-item">
              <i class="fas fa-users"></i>
              <span>{{ team.members_count }}명</span>
            </div>
            
            <div class="info-item">
              <i class="fas fa-calendar-alt"></i>
              <span>{{ team.matches_played }}경기</span>
            </div>
            
            <div class="info-item">
              <i class="fas fa-trophy"></i>
              <span>{{ team.wins }}승 {{ team.draws }}무 {{ team.losses }}패</span>
            </div>
            
            <div class="info-item win-rate">
              <i class="fas fa-percentage"></i>
              <span>승률 {{ Math.round(team.win_rate || 0) }}%</span>
            </div>
          </div>
          
          <div class="team-footer">
            <div class="team-created">
              <i class="fas fa-clock"></i>
              <span>{{ formatDate(team.created_at) }}</span>
            </div>
            
            <div class="team-recruiting" v-if="team.is_recruiting">
              <span class="recruiting-badge">모집중</span>
            </div>
            <div class="team-recruiting" v-else>
              <span class="closed-badge">모집마감</span>
            </div>
          </div>
        </div>
      </div>
    </transition-group>
    
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
      sortOption: '-created_at',
      showFilters: true,
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
    // URL 쿼리 파라미터에서 필터 상태 복원
    this.restoreFiltersFromQuery();
    this.fetchTeams();
  },
  
  methods: {
    ...mapActions({
      fetchTeamsAction: 'teams/fetchTeams'
    }),
    
    // URL 쿼리 파라미터에서 필터 상태 복원
    restoreFiltersFromQuery() {
      const query = this.$route.query;
      
      // 필터 복원
      if (query.region) this.filters.region = query.region;
      if (query.level) this.filters.level = query.level;
      if (query.is_recruiting) this.filters.is_recruiting = query.is_recruiting;
      if (query.search) this.filters.search = query.search;
      
      // 정렬 옵션 복원
      if (query.ordering) this.sortOption = query.ordering;
      
      // 페이지 복원
      if (query.page) this.page = parseInt(query.page) || 1;
    },
    
    // URL 쿼리 파라미터 업데이트
    updateQueryParams() {
      // 현재 필터 상태로 쿼리 파라미터 구성
      const query = {};
      
      if (this.filters.region) query.region = this.filters.region;
      if (this.filters.level) query.level = this.filters.level;
      if (this.filters.is_recruiting) query.is_recruiting = this.filters.is_recruiting;
      if (this.filters.search) query.search = this.filters.search;
      if (this.sortOption !== '-created_at') query.ordering = this.sortOption;
      if (this.page > 1) query.page = this.page;
      
      // 현재 경로에 쿼리 파라미터 업데이트 (히스토리 변경 없이)
      this.$router.replace({ 
        query: Object.keys(query).length > 0 ? query : undefined 
      }).catch(err => {
        if (err.name !== 'NavigationDuplicated') {
          throw err;
        }
      });
    },
    
    async fetchTeams() {
      try {
        const params = {
          ...this.filters,
          ordering: this.sortOption,
          page: this.page,
          page_size: this.pageSize
        };
        
        const response = await this.fetchTeamsAction(params);
        
        // 페이지네이션 정보 업데이트 (백엔드에서 제공하는 경우)
        if (response && response.data && response.data.count) {
          this.totalPages = Math.ceil(response.data.count / this.pageSize);
        }
        
        // URL 쿼리 파라미터 업데이트
        this.updateQueryParams();
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
      this.sortOption = '-created_at';
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
    },
    
    getRegionText(region) {
      const regionMap = {
        'seoul': '서울',
        'gyeonggi': '경기',
        'incheon': '인천',
        'other': '기타'
      };
      
      return regionMap[region] || region;
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}.${month}.${day}`;
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

.filter-toggle {
  margin-bottom: 15px;
}

.toggle-button {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #555;
  transition: all 0.2s ease;
}

.toggle-button:hover {
  background-color: #e9e9e9;
}

.filters-container {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #eee;
  transition: all 0.3s ease;
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

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 0;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #4caf50;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  color: #e74c3c;
}

.teams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.team-card {
  background-color: #fff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.team-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.team-logo {
  position: relative;
  height: 160px;
  overflow: hidden;
}

.team-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.team-card:hover .team-logo img {
  transform: scale(1.05);
}

.team-level-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.level-beginner {
  background-color: #4caf50;
}

.level-intermediate {
  background-color: #2196f3;
}

.level-advanced {
  background-color: #f44336;
}

.team-content {
  padding: 15px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.team-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.team-region {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  color: #666;
  font-size: 14px;
}

.team-region i {
  margin-right: 5px;
  color: #ff5722;
}

.team-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #555;
}

.info-item i {
  margin-right: 5px;
  width: 16px;
  text-align: center;
  color: #666;
}

.win-rate {
  color: #e91e63;
  font-weight: bold;
}

.team-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.team-created {
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
}

.team-created i {
  margin-right: 5px;
}

.recruiting-badge {
  background-color: #4caf50;
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.closed-badge {
  background-color: #9e9e9e;
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
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

.empty-message {
  text-align: center;
  padding: 50px 0;
  color: #666;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-message i {
  font-size: 48px;
  color: #ddd;
  margin-bottom: 15px;
}

.reset-search-btn {
  margin-top: 15px;
  padding: 8px 16px;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-search-btn:hover {
  background-color: #e0e0e0;
}

/* 애니메이션 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.fade-move {
  transition: transform 0.5s;
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