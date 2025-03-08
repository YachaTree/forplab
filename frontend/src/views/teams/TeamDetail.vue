<template>
  <div class="team-detail-container">
    <!-- 로딩 및 에러 메시지 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>팀 정보를 불러오는 중...</p>
    </div>
    
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchTeam" class="retry-button">다시 시도</button>
    </div>
    
    <div v-if="!loading && !error && team" class="team-content">
      <!-- 상단 헤더 -->
      <div class="team-header">
        <div class="team-header-content">
          <div class="team-logo">
            <img :src="team.logo || '/img/default-team.jpg'" alt="Team Logo" />
            <div class="team-level-badge" :class="'level-' + team.level">
              {{ getLevelText(team.level) }}
            </div>
          </div>
          
          <div class="team-info-header">
            <h1 class="team-name">{{ team.name }}</h1>
            
            <div class="team-meta">
              <div class="team-region">
                <i class="fas fa-map-marker-alt"></i>
                <span>{{ getRegionText(team.region) }}</span>
              </div>
              
              <div class="team-created">
                <i class="fas fa-calendar-alt"></i>
                <span>창단일: {{ formatDate(team.created_at) }}</span>
              </div>
              
              <div class="team-recruiting" v-if="team.is_recruiting">
                <i class="fas fa-user-plus"></i>
                <span class="recruiting-badge">모집중</span>
              </div>
              <div class="team-recruiting" v-else>
                <i class="fas fa-user-slash"></i>
                <span class="closed-badge">모집마감</span>
              </div>
            </div>
            
            <div class="team-stats">
              <div class="stat-item">
                <div class="stat-value">{{ team.members_count || 0 }}</div>
                <div class="stat-label">팀원</div>
              </div>
              
              <div class="stat-item">
                <div class="stat-value">{{ team.matches_played || 0 }}</div>
                <div class="stat-label">경기</div>
              </div>
              
              <div class="stat-item">
                <div class="stat-value">{{ team.wins || 0 }}/{{ team.draws || 0 }}/{{ team.losses || 0 }}</div>
                <div class="stat-label">승/무/패</div>
              </div>
              
              <div class="stat-item">
                <div class="stat-value">{{ Math.round(team.win_rate || 0) }}%</div>
                <div class="stat-label">승률</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="team-actions-container">
          <!-- 팀 가입 신청 버튼 (로그인 상태이고, 팀원이 아니고, 팀장이 아니고, 가입 신청 중이 아닌 경우) -->
          <div class="team-actions" v-if="isAuthenticated && !isTeamMember && !isTeamLeader && !hasJoinRequest">
            <button 
              class="join-team-btn" 
              @click="showJoinRequestForm = true"
              :disabled="!team.is_recruiting"
            >
              <i class="fas fa-user-plus"></i>
              {{ team.is_recruiting ? '팀 가입 신청' : '모집 마감' }}
            </button>
          </div>
          
          <!-- 팀 관리 버튼 (팀장인 경우) -->
          <div class="team-actions" v-if="isTeamLeader">
            <button class="manage-team-btn" @click="goToTeamManage">
              <i class="fas fa-cog"></i>
              팀 관리
            </button>
          </div>
          
          <!-- 팀 탈퇴 버튼 (팀원이지만 팀장이 아닌 경우) -->
          <div class="team-actions" v-if="isTeamMember && !isTeamLeader">
            <button class="leave-team-btn" @click="confirmLeaveTeam">
              <i class="fas fa-sign-out-alt"></i>
              팀 탈퇴
            </button>
          </div>
          
          <!-- 가입 신청 상태 (신청 중인 경우) -->
          <div class="team-actions" v-if="hasJoinRequest && !isTeamMember">
            <div class="join-request-status">
              <i class="fas fa-hourglass-half"></i>
              <span>가입 신청 중</span>
            </div>
            <button class="cancel-request-btn" @click="confirmCancelRequest">
              <i class="fas fa-times"></i>
              신청 취소
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
          팀 정보
        </div>
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'members' }"
          @click="activeTab = 'members'"
          v-if="isTeamMember || isTeamLeader"
        >
          <i class="fas fa-users"></i>
          팀원 목록
        </div>
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'matches' }"
          @click="activeTab = 'matches'"
        >
          <i class="fas fa-futbol"></i>
          경기 기록
        </div>
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'requests' }"
          @click="activeTab = 'requests'"
          v-if="isTeamLeader && team.join_requests && team.join_requests.length > 0"
        >
          <i class="fas fa-user-plus"></i>
          가입 신청
          <span class="badge">{{ team.join_requests.length }}</span>
        </div>
      </div>
      
      <!-- 탭 컨텐츠 -->
      <div class="tab-content">
        <!-- 팀 정보 탭 -->
        <div v-if="activeTab === 'info'" class="tab-pane">
          <div v-if="team.description" class="team-description-section">
            <h2 class="section-title">팀 소개</h2>
            <div class="team-description">
              <p>{{ team.description }}</p>
            </div>
          </div>
          
          <div class="team-details-section">
            <h2 class="section-title">팀 상세 정보</h2>
            <div class="team-details">
              <div class="detail-item">
                <div class="detail-label">팀 레벨</div>
                <div class="detail-value">{{ getLevelText(team.level) }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">활동 지역</div>
                <div class="detail-value">{{ getRegionText(team.region) }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">창단일</div>
                <div class="detail-value">{{ formatDate(team.created_at) }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">팀원 수</div>
                <div class="detail-value">{{ team.members_count || 0 }}명</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">경기 수</div>
                <div class="detail-value">{{ team.matches_played || 0 }}경기</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">전적</div>
                <div class="detail-value">{{ team.wins || 0 }}승 {{ team.draws || 0 }}무 {{ team.losses || 0 }}패</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">승률</div>
                <div class="detail-value">{{ Math.round(team.win_rate || 0) }}%</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">득점</div>
                <div class="detail-value">{{ team.goals_scored || 0 }}골</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">실점</div>
                <div class="detail-value">{{ team.goals_conceded || 0 }}골</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">득실차</div>
                <div class="detail-value">{{ (team.goals_scored || 0) - (team.goals_conceded || 0) }}골</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 팀원 목록 탭 -->
        <div v-if="activeTab === 'members' && (isTeamMember || isTeamLeader)" class="tab-pane">
          <div class="team-members-section">
            <h2 class="section-title">팀원 목록</h2>
            
            <div v-if="team.members && team.members.length > 0" class="members-list">
              <div v-for="member in team.members" :key="member.id" class="member-card">
                <div class="member-avatar">
                  <img :src="member.user.profile_image || '/img/default-avatar.png'" alt="User" />
                </div>
                
                <div class="member-info">
                  <div class="member-name">
                    {{ member.user.username }}
                    <span v-if="member.role === 'CAPTAIN'" class="leader-badge">팀장</span>
                    <span v-else-if="member.role === 'MANAGER'" class="manager-badge">매니저</span>
                  </div>
                  
                  <div class="member-position" v-if="member.position">
                    {{ getPositionText(member.position) }}
                  </div>
                  
                  <div class="member-join-date">
                    가입일: {{ formatDate(member.joined_at) }}
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="empty-members">
              <i class="fas fa-users"></i>
              <p>아직 팀원이 없습니다.</p>
            </div>
          </div>
        </div>
        
        <!-- 경기 기록 탭 -->
        <div v-if="activeTab === 'matches'" class="tab-pane">
          <div class="team-matches-section">
            <h2 class="section-title">경기 기록</h2>
            
            <div v-if="team.recent_matches && team.recent_matches.length > 0" class="matches-list">
              <div v-for="match in team.recent_matches" :key="match.id" class="match-card" @click="goToMatchDetail(match.id)">
                <div class="match-date">
                  {{ formatDate(match.date) }}
                </div>
                
                <div class="match-teams">
                  <div class="home-team" :class="{ 'current-team': match.home_team.id === team.id }">
                    {{ match.home_team.name }}
                  </div>
                  
                  <div class="match-score">
                    {{ match.home_score }} - {{ match.away_score }}
                  </div>
                  
                  <div class="away-team" :class="{ 'current-team': match.away_team.id === team.id }">
                    {{ match.away_team.name }}
                  </div>
                </div>
                
                <div class="match-venue">
                  <i class="fas fa-map-marker-alt"></i>
                  <span>{{ match.venue.name }}</span>
                </div>
              </div>
            </div>
            
            <div v-else class="empty-matches">
              <i class="fas fa-futbol"></i>
              <p>아직 경기 기록이 없습니다.</p>
            </div>
          </div>
        </div>
        
        <!-- 가입 신청 목록 탭 -->
        <div v-if="activeTab === 'requests' && isTeamLeader" class="tab-pane">
          <div class="join-requests-section">
            <h2 class="section-title">가입 신청 목록</h2>
            
            <div class="join-requests-list">
              <div v-for="request in team.join_requests" :key="request.id" class="request-card">
                <div class="request-user">
                  <div class="user-avatar">
                    <img :src="request.user.profile_image || '/img/default-avatar.png'" alt="User" />
                  </div>
                  
                  <div class="user-info">
                    <div class="user-name">{{ request.user.username }}</div>
                    <div class="request-date">신청일: {{ formatDate(request.created_at) }}</div>
                  </div>
                </div>
                
                <div class="request-details">
                  <div class="request-position">
                    <span class="detail-label">포지션:</span>
                    <span class="detail-value">{{ getPositionText(request.position) }}</span>
                  </div>
                  
                  <div class="request-message">
                    <span class="detail-label">자기소개:</span>
                    <p class="detail-value">{{ request.message }}</p>
                  </div>
                </div>
                
                <div class="request-actions">
                  <button class="reject-btn" @click="rejectJoinRequest(request.id)">
                    <i class="fas fa-times"></i>
                    거절
                  </button>
                  <button class="approve-btn" @click="approveJoinRequest(request.id)">
                    <i class="fas fa-check"></i>
                    수락
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 팀 가입 신청 폼 -->
      <div v-if="showJoinRequestForm" class="join-request-form-overlay">
        <div class="join-request-form-container">
          <div class="join-request-form-header">
            <h2>팀 가입 신청</h2>
            <button class="close-btn" @click="cancelJoinRequest">
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="join-request-form">
            <div class="form-group">
              <label>자기소개</label>
              <textarea 
                v-model="joinRequestForm.message" 
                placeholder="자기소개와 가입 동기를 작성해주세요."
                rows="4"
              ></textarea>
            </div>
            
            <div class="form-group">
              <label>포지션</label>
              <select v-model="joinRequestForm.position">
                <option value="">선택</option>
                <option value="GK">골키퍼</option>
                <option value="DF">수비수</option>
                <option value="MF">미드필더</option>
                <option value="FW">공격수</option>
              </select>
            </div>
            
            <div class="form-actions">
              <button class="cancel-btn" @click="cancelJoinRequest">취소</button>
              <button 
                class="submit-btn" 
                @click="submitJoinRequest"
                :disabled="joinRequestSubmitting || !joinRequestForm.message || !joinRequestForm.position"
              >
                <i class="fas fa-paper-plane"></i>
                {{ joinRequestSubmitting ? '제출 중...' : '가입 신청' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
  name: 'TeamDetail',
  
  data() {
    return {
      showJoinRequestForm: false,
      joinRequestForm: {
        message: '',
        position: ''
      },
      joinRequestSubmitting: false,
      activeTab: 'info' // 기본 활성 탭
    };
  },
  
  computed: {
    ...mapState({
      team: state => state.teams.currentTeam,
      loading: state => state.teams.teamLoading,
      error: state => state.teams.teamError,
      user: state => state.auth.user
    }),
    
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated'
    }),
    
    isTeamMember() {
      if (!this.isAuthenticated || !this.team || !this.user) {
        return false;
      }
      
      // 백엔드에서 제공하는 is_member 필드 사용
      if (this.team.is_member !== undefined) {
        return this.team.is_member;
      }
      
      // 백엔드에서 is_member 필드를 제공하지 않는 경우 직접 확인
      if (this.team.members) {
        return this.team.members.some(member => member.user && member.user.id === this.user.id);
      }
      
      return false;
    },
    
    isTeamLeader() {
      if (!this.isAuthenticated || !this.team || !this.user) {
        return false;
      }
      
      // 팀 소유자(owner) 확인
      if (this.team.owner && this.team.owner.id === this.user.id) {
        return true;
      }
      
      // 팀 소유자 ID가 문자열인 경우 (API 응답 형식에 따라 다를 수 있음)
      if (this.team.owner && String(this.team.owner.id) === String(this.user.id)) {
        return true;
      }
      
      // 팀 소유자 필드가 다른 형식인 경우 (is_owner 필드가 있는 경우)
      if (this.team.is_owner === true) {
        return true;
      }
      
      // 기존 방식으로도 확인 (팀원 중 리더인지)
      if (this.team.members) {
        const currentUser = this.team.members.find(member => member.user && member.user.id === this.user.id);
        if (currentUser && currentUser.role === 'CAPTAIN') {
          return true;
        }
      }
      
      return false;
    },
    
    hasJoinRequest() {
      if (!this.isAuthenticated || !this.team || !this.user) {
        return false;
      }
      
      // 백엔드에서 제공하는 has_join_request 필드 사용
      if (this.team.has_join_request !== undefined) {
        return this.team.has_join_request;
      }
      
      // 백엔드에서 has_join_request 필드를 제공하지 않는 경우 직접 확인
      if (this.team.join_requests) {
        return this.team.join_requests.some(request => request.user.id === this.user.id);
      }
      
      return false;
    }
  },
  
  created() {
    this.fetchTeam();
    if (this.isAuthenticated) {
      this.fetchUserProfile();
    }
  },
  
  watch: {
    team() {
      // 팀 데이터가 변경되었을 때 필요한 작업이 있으면 여기에 추가
    },
    
    isAuthenticated(newValue) {
      if (newValue && !this.user) {
        this.fetchUserProfile();
      }
    },
    
    isTeamMember(newValue) {
      // 팀원이 아닌 경우 팀원 목록 탭이 활성화되어 있다면 팀 정보 탭으로 변경
      if (!newValue && !this.isTeamLeader && this.activeTab === 'members') {
        this.activeTab = 'info';
      }
    }
  },
  
  methods: {
    ...mapActions({
      fetchTeamAction: 'teams/fetchTeam',
      fetchUserProfile: 'auth/fetchProfile'
    }),
    
    async fetchTeam() {
      try {
        await this.fetchTeamAction(this.$route.params.id);
      } catch (error) {
        console.error('팀 상세 조회 실패:', error);
      }
    },
    
    async submitJoinRequest() {
      if (!this.joinRequestForm.message || !this.joinRequestForm.position) return;
      
      this.joinRequestSubmitting = true;
      
      try {
        await this.$store.dispatch('teams/joinTeam', {
          id: this.$route.params.id,
          requestData: {
            message: this.joinRequestForm.message,
            position: this.joinRequestForm.position
          }
        });
        
        // 가입 신청 성공 후 팀 정보 다시 조회
        await this.fetchTeam();
        
        this.showJoinRequestForm = false;
        this.joinRequestForm = {
          message: '',
          position: ''
        };
        
        alert('팀 가입 신청이 완료되었습니다.');
      } catch (error) {
        console.error('팀 가입 신청 실패:', error);
        
        // 이미 가입 신청한 경우 처리
        if (error.response && error.response.status === 400 && 
            error.response.data && error.response.data.detail) {
          alert(error.response.data.detail);
          this.showJoinRequestForm = false;
          // 팀 정보 다시 조회하여 상태 업데이트
          await this.fetchTeam();
        } 
        // 서버 오류인 경우 (500 에러)
        else if (error.response && error.response.status === 500) {
          alert('서버 오류가 발생했습니다. 팀 정보를 다시 불러옵니다.');
          // 팀 정보 다시 불러오기
          await this.fetchTeam();
          this.showJoinRequestForm = false;
        }
        else {
          alert('팀 가입 신청에 실패했습니다. 다시 시도해주세요.');
        }
      } finally {
        this.joinRequestSubmitting = false;
      }
    },
    
    cancelJoinRequest() {
      this.showJoinRequestForm = false;
      this.joinRequestForm = {
        message: '',
        position: ''
      };
    },
    
    async confirmCancelRequest() {
      if (confirm('가입 신청을 취소하시겠습니까?')) {
        try {
          await this.$store.dispatch('teams/cancelJoinRequest', this.$route.params.id);
          await this.fetchTeam();
          alert('가입 신청이 취소되었습니다.');
        } catch (error) {
          console.error('가입 신청 취소 실패:', error);
          alert('가입 신청 취소에 실패했습니다. 다시 시도해주세요.');
        }
      }
    },
    
    async confirmLeaveTeam() {
      if (confirm('정말 팀을 탈퇴하시겠습니까?')) {
        try {
          await this.$store.dispatch('teams/leaveTeam', this.$route.params.id);
          await this.fetchTeam();
          alert('팀에서 탈퇴했습니다.');
        } catch (error) {
          console.error('팀 탈퇴 실패:', error);
          alert('팀 탈퇴에 실패했습니다. 다시 시도해주세요.');
        }
      }
    },
    
    async approveJoinRequest(requestId) {
      try {
        await this.$store.dispatch('teams/acceptJoinRequest', {
          teamId: this.$route.params.id,
          requestId
        });
        await this.fetchTeam();
        alert('가입 신청을 수락했습니다.');
      } catch (error) {
        console.error('가입 신청 수락 실패:', error);
        
        // 이미 처리된 요청인 경우 (400 또는 404 에러)
        if (error.response && (error.response.status === 404 || error.response.status === 400)) {
          let message = '이미 처리된 가입 신청입니다.';
          if (error.response.data && error.response.data.detail) {
            message = error.response.data.detail;
          }
          alert(message);
          // 팀 정보 다시 불러오기
          await this.fetchTeam();
        } 
        // 서버 오류인 경우 (500 에러)
        else if (error.response && error.response.status === 500) {
          alert('서버 오류가 발생했습니다. 팀 정보를 다시 불러옵니다.');
          // 팀 정보 다시 불러오기
          await this.fetchTeam();
        }
        else {
          alert('가입 신청 수락에 실패했습니다. 다시 시도해주세요.');
        }
      }
    },
    
    async rejectJoinRequest(requestId) {
      try {
        await this.$store.dispatch('teams/rejectJoinRequest', {
          teamId: this.$route.params.id,
          requestId
        });
        await this.fetchTeam();
        alert('가입 신청을 거절했습니다.');
      } catch (error) {
        console.error('가입 신청 거절 실패:', error);
        
        // 이미 처리된 요청인 경우 (400 또는 404 에러)
        if (error.response && (error.response.status === 404 || error.response.status === 400)) {
          let message = '이미 처리된 가입 신청입니다.';
          if (error.response.data && error.response.data.detail) {
            message = error.response.data.detail;
          }
          alert(message);
          // 팀 정보 다시 불러오기
          await this.fetchTeam();
        } 
        // 서버 오류인 경우 (500 에러)
        else if (error.response && error.response.status === 500) {
          alert('서버 오류가 발생했습니다. 팀 정보를 다시 불러옵니다.');
          // 팀 정보 다시 불러오기
          await this.fetchTeam();
        }
        else {
          alert('가입 신청 거절에 실패했습니다. 다시 시도해주세요.');
        }
      }
    },
    
    goToTeamManage() {
      this.$router.push({ name: 'TeamManage', params: { id: this.team.id } });
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
    
    getPositionText(position) {
      const positionMap = {
        'GK': '골키퍼',
        'DF': '수비수',
        'MF': '미드필더',
        'FW': '공격수'
      };
      
      return positionMap[position] || position;
    }
  }
};
</script>

<style scoped>
.team-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
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
  text-align: center;
  padding: 30px;
  background-color: #ffebee;
  border-radius: 8px;
  margin: 20px 0;
  color: #e53935;
  border: 1px solid #ffcdd2;
}

.retry-button {
  margin-top: 15px;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  background-color: #e53935;
  color: white;
  transition: background-color 0.3s;
}

.retry-button:hover {
  background-color: #c62828;
}

.team-content {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.team-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 30px;
  border-bottom: 1px solid #eee;
}

.team-header-content {
  display: flex;
  flex: 1;
  gap: 20px;
}

.team-logo {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.team-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.team-logo:hover img {
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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
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

.team-info-header {
  flex: 1;
}

.team-name {
  font-size: 28px;
  font-weight: bold;
  margin: 0 0 15px;
  color: #333;
}

.team-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
}

.team-region, .team-created, .team-recruiting {
  display: flex;
  align-items: center;
  color: #555;
  font-size: 14px;
}

.team-region i, .team-created i, .team-recruiting i {
  margin-right: 8px;
  color: #777;
  width: 16px;
  text-align: center;
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

.team-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 20px;
}

.stat-item {
  text-align: center;
  min-width: 80px;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #777;
}

.team-actions-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 15px;
}

.team-actions {
  display: flex;
  align-items: center;
}

.join-team-btn, .manage-team-btn, .leave-team-btn, .cancel-request-btn {
  padding: 10px 15px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.join-team-btn {
  background-color: #4caf50;
  color: white;
}

.join-team-btn:hover {
  background-color: #388e3c;
}

.manage-team-btn {
  background-color: #2196f3;
  color: white;
}

.manage-team-btn:hover {
  background-color: #1976d2;
}

.leave-team-btn {
  background-color: #f44336;
  color: white;
}

.leave-team-btn:hover {
  background-color: #d32f2f;
}

.cancel-request-btn {
  background-color: #ff9800;
  color: white;
}

.cancel-request-btn:hover {
  background-color: #f57c00;
}

.join-request-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 10px;
  color: #ff9800;
  font-weight: 500;
}

.tab-menu {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.tab-item {
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  position: relative;
}

.tab-item i {
  font-size: 16px;
}

.tab-item:hover {
  background-color: #f5f5f5;
}

.tab-item.active {
  background-color: #2196f3;
  color: white;
}

.badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background-color: #f44336;
  color: white;
  font-size: 12px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-content {
  animation: fadeIn 0.3s ease-out;
}

.tab-pane {
  width: 100%;
}

.section-title {
  font-size: 20px;
  margin-bottom: 20px;
  color: #333;
  border-left: 4px solid #2196f3;
  padding-left: 10px;
}

.team-description-section, .team-details-section, .team-members-section, .team-matches-section, .join-requests-section {
  margin-bottom: 30px;
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.team-description {
  line-height: 1.6;
  color: #555;
}

.team-details {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.detail-item {
  padding: 10px;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.detail-label {
  font-size: 14px;
  color: #777;
  margin-bottom: 5px;
}

.detail-value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.members-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.member-card {
  display: flex;
  align-items: center;
  padding: 15px;
  border-radius: 8px;
  background-color: #f9f9f9;
  transition: transform 0.3s, box-shadow 0.3s;
}

.member-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.member-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 15px;
}

.member-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.member-info {
  flex: 1;
}

.member-name {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
}

.leader-badge {
  background-color: #f44336;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 8px;
}

.manager-badge {
  background-color: #2196f3;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 8px;
}

.member-position, .member-join-date {
  font-size: 14px;
  color: #777;
}

.matches-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.match-card {
  padding: 15px;
  border-radius: 8px;
  background-color: #f9f9f9;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.match-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.match-date {
  font-size: 14px;
  color: #777;
  margin-bottom: 10px;
}

.match-teams {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.home-team, .away-team {
  font-size: 16px;
  font-weight: 500;
  flex: 1;
}

.away-team {
  text-align: right;
}

.match-score {
  font-size: 20px;
  font-weight: bold;
  padding: 0 15px;
}

.current-team {
  color: #2196f3;
}

.match-venue {
  font-size: 14px;
  color: #777;
  display: flex;
  align-items: center;
}

.match-venue i {
  margin-right: 5px;
}

.empty-members, .empty-matches {
  text-align: center;
  padding: 40px 0;
  color: #999;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-members i, .empty-matches i {
  font-size: 48px;
  color: #ddd;
  margin-bottom: 15px;
}

.join-requests-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.request-card {
  padding: 20px;
  border-radius: 8px;
  background-color: #f9f9f9;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.request-user {
  display: flex;
  align-items: center;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 15px;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 5px;
}

.request-date {
  font-size: 14px;
  color: #777;
}

.request-details {
  padding: 15px;
  border-radius: 8px;
  background-color: #f0f0f0;
}

.request-position, .request-message {
  margin-bottom: 10px;
}

.detail-label {
  font-weight: 500;
  margin-right: 5px;
}

.request-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.reject-btn, .approve-btn {
  padding: 8px 15px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.reject-btn {
  background-color: #f44336;
  color: white;
}

.reject-btn:hover {
  background-color: #d32f2f;
}

.approve-btn {
  background-color: #4caf50;
  color: white;
}

.approve-btn:hover {
  background-color: #388e3c;
}

.join-request-form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
}

.join-request-form-container {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from { transform: translateY(-50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.join-request-form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.join-request-form-header h2 {
  font-size: 20px;
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #777;
  transition: color 0.3s;
}

.close-btn:hover {
  color: #333;
}

.join-request-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

.form-group textarea, .form-group select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group textarea:focus, .form-group select:focus {
  border-color: #2196f3;
  outline: none;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.cancel-btn, .submit-btn {
  padding: 10px 15px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #333;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.submit-btn {
  background-color: #4caf50;
  color: white;
}

.submit-btn:hover {
  background-color: #388e3c;
}

.submit-btn:disabled {
  background-color: #9e9e9e;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .team-header-content {
    flex-direction: column;
  }
  
  .team-logo {
    margin: 0 auto 20px;
  }
  
  .team-info-header {
    text-align: center;
  }
  
  .team-meta {
    justify-content: center;
  }
  
  .team-stats {
    justify-content: center;
  }
  
  .team-actions-container {
    margin-top: 20px;
    align-items: center;
  }
  
  .tab-menu {
    justify-content: center;
  }
  
  .tab-item {
    flex: 1;
    justify-content: center;
  }
  
  .team-details {
    grid-template-columns: 1fr;
  }
  
  .members-list {
    grid-template-columns: 1fr;
  }
}
</style> 