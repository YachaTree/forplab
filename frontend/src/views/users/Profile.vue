<template>
  <div class="profile-container">
    <!-- 로딩 및 에러 메시지 -->
    <div v-if="loading" class="loading-message">
      <p>프로필 정보를 불러오는 중...</p>
    </div>
    
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchUserProfile">다시 시도</button>
    </div>
    
    <div v-if="!loading && !error && user" class="profile-content">
      <!-- 프로필 헤더 -->
      <div class="profile-header">
        <div class="profile-avatar">
          <img :src="user.profile_image || '/img/default-avatar.png'" alt="프로필 이미지">
        </div>
        
        <div class="profile-info">
          <h1 class="username">{{ user.username }}</h1>
          <p class="user-email">{{ user.email }}</p>
          
          <div class="user-stats">
            <div class="stat-item">
              <span class="stat-value">{{ user.matches_played }}</span>
              <span class="stat-label">경기 수</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ user.wins }}</span>
              <span class="stat-label">승리</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ user.draws }}</span>
              <span class="stat-label">무승부</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ user.losses }}</span>
              <span class="stat-label">패배</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ winRate }}%</span>
              <span class="stat-label">승률</span>
            </div>
          </div>
          
          <div class="user-level">
            <span class="level-label">실력 수준:</span>
            <span class="level-value">{{ getSkillLevelText(user.skill_level) }}</span>
          </div>
          
          <div class="user-actions" v-if="isCurrentUser">
            <button class="edit-profile-btn" @click="showEditForm = true">
              <i class="fas fa-edit"></i>
              프로필 수정
            </button>
          </div>
        </div>
      </div>
      
      <!-- 탭 메뉴 -->
      <div class="tab-menu">
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'info' }"
          @click="activeTab = 'info'"
        >
          <i class="fas fa-info-circle"></i>
          기본 정보
        </div>
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'teams' }"
          @click="activeTab = 'teams'"
        >
          <i class="fas fa-users"></i>
          소속 팀
        </div>
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'matches' }"
          @click="activeTab = 'matches'"
        >
          <i class="fas fa-futbol"></i>
          참여 경기
        </div>
      </div>
      
      <!-- 탭 컨텐츠 -->
      <div class="tab-content">
        <!-- 기본 정보 탭 -->
        <div v-if="activeTab === 'info'" class="info-tab">
          <div class="info-section">
            <h3>기본 정보</h3>
            
            <div class="info-row" v-if="user.birth_date">
              <div class="info-label">생년월일</div>
              <div class="info-value">{{ formatDate(user.birth_date) }}</div>
            </div>
            
            <div class="info-row" v-if="user.phone">
              <div class="info-label">연락처</div>
              <div class="info-value">{{ user.phone }}</div>
            </div>
            
            <div class="info-row">
              <div class="info-label">가입일</div>
              <div class="info-value">{{ formatDate(user.date_joined) }}</div>
            </div>
            
            <div class="info-row" v-if="user.bio">
              <div class="info-label">자기소개</div>
              <div class="info-value bio-text">{{ user.bio }}</div>
            </div>
          </div>
        </div>
        
        <!-- 소속 팀 탭 -->
        <div v-if="activeTab === 'teams'" class="teams-tab">
          <div v-if="loading" class="loading-message">
            <p>팀 정보를 불러오는 중...</p>
          </div>
          
          <div v-if="!loading && userTeams.length === 0" class="empty-message">
            <p>소속된 팀이 없습니다.</p>
          </div>
          
          <div v-if="!loading && userTeams.length > 0" class="teams-grid">
            <div v-for="team in userTeams" :key="team.id" class="team-card" @click="goToTeamDetail(team.id)">
              <div class="team-logo">
                <img :src="team.logo || '/img/default-team.png'" alt="팀 로고">
              </div>
              <div class="team-info">
                <h3 class="team-name">{{ team.name }}</h3>
                <p class="team-level">{{ team.level_display }}</p>
                <p class="team-region">{{ team.region_display }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 참여 경기 탭 -->
        <div v-if="activeTab === 'matches'" class="matches-tab">
          <div v-if="loading" class="loading-message">
            <p>경기 정보를 불러오는 중...</p>
          </div>
          
          <div v-if="!loading && userMatches.length === 0" class="empty-message">
            <p>참여한 경기가 없습니다.</p>
          </div>
          
          <div v-if="!loading && userMatches.length > 0" class="matches-list">
            <div v-for="match in userMatches" :key="match.id" class="match-item" @click="goToMatchDetail(match.id)">
              <div class="match-date">{{ formatDate(match.date) }}</div>
              <div class="match-title">{{ match.title }}</div>
              <div class="match-venue">{{ match.venue.name }}</div>
              <div class="match-status" :class="'status-' + match.status.toLowerCase()">
                {{ getStatusText(match.status) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 프로필 수정 모달 -->
    <div v-if="showEditForm" class="modal-overlay" @click.self="showEditForm = false">
      <div class="modal-content">
        <h2>프로필 수정</h2>
        
        <form @submit.prevent="updateUserProfile" class="edit-profile-form">
          <div class="form-group">
            <label for="username">사용자명</label>
            <input type="text" id="username" v-model="editForm.username" required>
          </div>
          
          <div class="form-group">
            <label for="email">이메일</label>
            <input type="email" id="email" v-model="editForm.email" required>
          </div>
          
          <div class="form-group">
            <label for="phone">연락처</label>
            <input type="tel" id="phone" v-model="editForm.phone">
          </div>
          
          <div class="form-group">
            <label for="birth_date">생년월일</label>
            <input type="date" id="birth_date" v-model="editForm.birth_date">
          </div>
          
          <div class="form-group">
            <label for="skill_level">실력 수준</label>
            <select id="skill_level" v-model="editForm.skill_level">
              <option value="BEG">입문</option>
              <option value="INT">중급</option>
              <option value="ADV">고급</option>
              <option value="PRO">프로</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="bio">자기소개</label>
            <textarea id="bio" v-model="editForm.bio" rows="4"></textarea>
          </div>
          
          <div class="form-group">
            <label for="profile_image">프로필 이미지</label>
            <input type="file" id="profile_image" @change="handleImageUpload">
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showEditForm = false">취소</button>
            <button type="submit" class="save-btn" :disabled="updating">
              {{ updating ? '저장 중...' : '저장' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'UserProfile',
  
  data() {
    return {
      activeTab: 'info',
      showEditForm: false,
      updating: false,
      editForm: {
        username: '',
        email: '',
        phone: '',
        birth_date: '',
        skill_level: '',
        bio: '',
        profile_image: null
      },
      userTeams: [],
      userMatches: []
    };
  },
  
  computed: {
    ...mapState({
      user: state => state.auth.user,
      loading: state => state.auth.loading,
      error: state => state.auth.error
    }),
    
    isCurrentUser() {
      return this.user && this.user.id === parseInt(this.$route.params.id);
    },
    
    winRate() {
      if (!this.user || this.user.matches_played === 0) {
        return 0;
      }
      return ((this.user.wins / this.user.matches_played) * 100).toFixed(1);
    }
  },
  
  created() {
    console.log('Profile 컴포넌트 생성됨, 경로:', this.$route.path);
    this.fetchUserProfile();
    this.loadUserTeams();
    this.loadUserMatches();
  },
  
  methods: {
    ...mapActions({
      fetchProfile: 'auth/fetchProfile',
      updateProfile: 'auth/updateProfile'
    }),
    
    async fetchUserProfile() {
      console.log('프로필 정보 조회 시작, 경로:', this.$route.path);
      try {
        // 현재 로그인한 사용자의 프로필 정보 가져오기
        if (this.$route.params.id) {
          console.log('특정 사용자 프로필 조회:', this.$route.params.id);
          // 특정 사용자의 프로필 조회
          const response = await this.$store.dispatch('auth/getUserProfile', this.$route.params.id);
          console.log('사용자 프로필 응답:', response);
          
          // 프로필 수정 폼 초기화 (자신의 프로필인 경우에만)
          if (this.isCurrentUser && this.user) {
            this.initEditForm();
          }
        } else {
          console.log('현재 로그인한 사용자 프로필 조회');
          // 로그인한 사용자 자신의 프로필 조회
          await this.fetchProfile();
          console.log('현재 사용자 프로필:', this.user);
          
          // 프로필 수정 폼 초기화
          if (this.user) {
            this.initEditForm();
          }
        }
      } catch (error) {
        console.error('프로필 정보 조회 실패:', error);
      }
    },
    
    initEditForm() {
      this.editForm = {
        username: this.user.username,
        email: this.user.email,
        phone: this.user.phone || '',
        birth_date: this.user.birth_date || '',
        skill_level: this.user.skill_level || 'BEG',
        bio: this.user.bio || '',
        profile_image: null
      };
    },
    
    async updateUserProfile() {
      this.updating = true;
      
      try {
        const formData = new FormData();
        formData.append('username', this.editForm.username);
        formData.append('email', this.editForm.email);
        
        if (this.editForm.phone) {
          formData.append('phone', this.editForm.phone);
        }
        
        if (this.editForm.birth_date) {
          formData.append('birth_date', this.editForm.birth_date);
        }
        
        formData.append('skill_level', this.editForm.skill_level);
        formData.append('bio', this.editForm.bio);
        
        if (this.editForm.profile_image) {
          formData.append('profile_image', this.editForm.profile_image);
        }
        
        await this.updateProfile(formData);
        
        this.showEditForm = false;
        alert('프로필이 성공적으로 업데이트되었습니다.');
      } catch (error) {
        console.error('프로필 업데이트 실패:', error);
        alert('프로필 업데이트에 실패했습니다. 다시 시도해주세요.');
      } finally {
        this.updating = false;
      }
    },
    
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.editForm.profile_image = file;
      }
    },
    
    async loadUserTeams() {
      console.log('팀 정보 조회 시작');
      try {
        // 사용자가 속한 팀 목록 가져오기
        if (this.$route.params.id) {
          console.log('특정 사용자의 팀 목록 조회:', this.$route.params.id);
          const response = await this.$store.dispatch('auth/getUserTeams', this.$route.params.id);
          console.log('팀 목록 응답:', response);
          this.userTeams = response.data || [];
        } else if (this.user) {
          console.log('현재 로그인한 사용자의 팀 목록 조회:', this.user.id);
          const response = await this.$store.dispatch('auth/getUserTeams', this.user.id);
          console.log('팀 목록 응답:', response);
          this.userTeams = response.data || [];
        }
      } catch (error) {
        console.error('팀 정보 조회 실패:', error);
      }
    },
    
    async loadUserMatches() {
      console.log('경기 정보 조회 시작');
      try {
        // 사용자가 참여한 경기 목록 가져오기
        if (this.$route.params.id) {
          console.log('특정 사용자의 경기 목록 조회:', this.$route.params.id);
          const response = await this.$store.dispatch('auth/getUserMatches', this.$route.params.id);
          console.log('경기 목록 응답:', response);
          this.userMatches = response.data || [];
        } else if (this.user) {
          console.log('현재 로그인한 사용자의 경기 목록 조회:', this.user.id);
          const response = await this.$store.dispatch('auth/getUserMatches', this.user.id);
          console.log('경기 목록 응답:', response);
          this.userMatches = response.data || [];
        }
      } catch (error) {
        console.error('경기 정보 조회 실패:', error);
      }
    },
    
    goToTeamDetail(teamId) {
      this.$router.push(`/teams/${teamId}`);
    },
    
    goToMatchDetail(matchId) {
      this.$router.push(`/matches/${matchId}`);
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      
      const date = new Date(dateString);
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
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
    
    getStatusText(status) {
      const statusMap = {
        'OPEN': '모집중',
        'CLOSED': '모집완료',
        'CANCELED': '취소됨',
        'COMPLETED': '경기완료'
      };
      
      return statusMap[status] || status;
    }
  }
};
</script>

<style scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading-message, .error-message, .empty-message {
  text-align: center;
  padding: 20px;
  margin: 20px 0;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
}

.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.profile-avatar {
  margin-right: 30px;
}

.profile-avatar img {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #4CAF50;
}

.profile-info {
  flex: 1;
}

.username {
  font-size: 2rem;
  margin: 0 0 5px 0;
  color: #333;
}

.user-email {
  color: #666;
  margin: 0 0 15px 0;
}

.user-stats {
  display: flex;
  margin-bottom: 15px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 20px;
  padding: 10px 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #4CAF50;
}

.stat-label {
  font-size: 0.8rem;
  color: #666;
}

.user-level {
  margin-bottom: 15px;
}

.level-label {
  font-weight: bold;
  margin-right: 5px;
}

.level-value {
  color: #4CAF50;
}

.user-actions {
  margin-top: 15px;
}

.edit-profile-btn {
  padding: 8px 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.edit-profile-btn:hover {
  background-color: #45a049;
}

.tab-menu {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #ddd;
}

.tab-item {
  padding: 10px 20px;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}

.tab-item:hover {
  background-color: #f8f9fa;
}

.tab-item.active {
  border-bottom-color: #4CAF50;
  color: #4CAF50;
}

.tab-content {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.info-section h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.info-row {
  display: flex;
  margin-bottom: 15px;
}

.info-label {
  width: 120px;
  font-weight: bold;
  color: #666;
}

.info-value {
  flex: 1;
}

.bio-text {
  white-space: pre-line;
}

.teams-grid, .matches-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.team-card {
  display: flex;
  align-items: center;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.team-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.team-logo {
  margin-right: 15px;
}

.team-logo img {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
}

.team-info {
  flex: 1;
}

.team-name {
  margin: 0 0 5px 0;
  color: #333;
}

.team-level, .team-region {
  margin: 0;
  font-size: 0.9rem;
  color: #666;
}

.match-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.match-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.match-date {
  width: 120px;
  font-weight: bold;
}

.match-title {
  flex: 1;
  font-weight: bold;
}

.match-venue {
  width: 150px;
  color: #666;
}

.match-status {
  width: 80px;
  text-align: center;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.status-open {
  background-color: #d4edda;
  color: #155724;
}

.status-closed {
  background-color: #cce5ff;
  color: #004085;
}

.status-canceled {
  background-color: #f8d7da;
  color: #721c24;
}

.status-completed {
  background-color: #e2e3e5;
  color: #383d41;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.edit-profile-form .form-group {
  margin-bottom: 15px;
}

.edit-profile-form label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.edit-profile-form input,
.edit-profile-form select,
.edit-profile-form textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.cancel-btn {
  padding: 8px 15px;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 10px;
  cursor: pointer;
}

.save-btn {
  padding: 8px 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn:hover {
  background-color: #45a049;
}

.save-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .profile-avatar {
    margin-right: 0;
    margin-bottom: 20px;
  }
  
  .user-stats {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .info-row {
    flex-direction: column;
  }
  
  .info-label {
    width: 100%;
    margin-bottom: 5px;
  }
  
  .teams-grid, .matches-list {
    grid-template-columns: 1fr;
  }
  
  .match-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .match-date, .match-venue, .match-status {
    width: 100%;
    margin-bottom: 5px;
  }
}
</style> 