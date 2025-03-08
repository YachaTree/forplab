<template>
  <div class="team-detail-container">
    <!-- 로딩 및 에러 메시지 -->
    <div v-if="loading" class="loading-message">
      <p>팀 정보를 불러오는 중...</p>
    </div>
    
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchTeam">다시 시도</button>
    </div>
    
    <div v-if="!loading && !error && team" class="team-content">
      <!-- 상단 헤더 -->
      <div class="team-header">
        <div class="team-logo">
          <img :src="team.logo || '/img/default-team.jpg'" alt="Team Logo" />
        </div>
        
        <div class="team-info-header">
          <h1 class="team-name">{{ team.name }}</h1>
          
          <div class="team-level" :class="'level-' + team.level">
            {{ getLevelText(team.level) }}
          </div>
          
          <div class="team-region">
            <i class="fas fa-map-marker-alt"></i>
            <span>{{ getRegionText(team.region) }}</span>
          </div>
          
          <div class="team-stats">
            <div class="stat-item">
              <div class="stat-label">팀원</div>
              <div class="stat-value">{{ team.member_count }}명</div>
            </div>
            
            <div class="stat-item">
              <div class="stat-label">경기</div>
              <div class="stat-value">{{ team.match_count }}경기</div>
            </div>
            
            <div class="stat-item">
              <div class="stat-label">승/무/패</div>
              <div class="stat-value">{{ team.win_count }}/{{ team.draw_count }}/{{ team.lose_count }}</div>
            </div>
          </div>
          
          <!-- 팀 가입 버튼 -->
          <div class="team-actions" v-if="isAuthenticated && !isTeamMember && !isTeamLeader && !hasJoinRequest">
            <button 
              class="join-team-btn" 
              @click="showJoinRequestForm = true"
              :disabled="!team.is_recruiting"
            >
              {{ team.is_recruiting ? '팀 가입 신청' : '모집 마감' }}
            </button>
          </div>
          
          <!-- 팀 관리 버튼 (팀장인 경우) -->
          <div class="team-actions" v-if="isTeamLeader">
            <button class="manage-team-btn" @click="goToTeamManage">팀 관리</button>
          </div>
          
          <!-- 팀 탈퇴 버튼 (팀원인 경우) -->
          <div class="team-actions" v-if="isTeamMember && !isTeamLeader">
            <button class="leave-team-btn" @click="confirmLeaveTeam">팀 탈퇴</button>
          </div>
          
          <!-- 가입 신청 상태 (신청 중인 경우) -->
          <div class="team-actions" v-if="!isTeamMember && !isTeamLeader && hasJoinRequest">
            <div class="join-request-status">
              <i class="fas fa-hourglass-half"></i>
              <span>가입 신청 중</span>
            </div>
            <button class="cancel-request-btn" @click="confirmCancelRequest">신청 취소</button>
          </div>
        </div>
      </div>
      
      <!-- 팀 소개 -->
      <div v-if="team.description" class="team-description-section">
        <h2 class="section-title">팀 소개</h2>
        <div class="team-description">
          <p>{{ team.description }}</p>
        </div>
      </div>
      
      <!-- 팀 가입 신청 폼 -->
      <div v-if="showJoinRequestForm" class="join-request-form-section">
        <h2 class="section-title">팀 가입 신청</h2>
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
              {{ joinRequestSubmitting ? '제출 중...' : '가입 신청' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 팀원 목록 -->
      <div class="team-members-section">
        <h2 class="section-title">팀원 목록</h2>
        
        <div v-if="team.members && team.members.length > 0" class="members-list">
          <div v-for="member in team.members" :key="member.id" class="member-card">
            <div class="member-avatar">
              <img :src="member.user.profile_image || '/img/default-avatar.png'" alt="User" />
            </div>
            
            <div class="member-info">
              <div class="member-name">
                {{ member.username }}
                <span v-if="member.is_leader" class="leader-badge">팀장</span>
              </div>
              
              <div class="member-position">
                {{ getPositionText(member.position) }}
              </div>
              
              <div class="member-join-date">
                가입일: {{ formatDate(member.joined_at) }}
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-members">
          <p>아직 팀원이 없습니다.</p>
        </div>
      </div>
      
      <!-- 팀 경기 기록 -->
      <div class="team-matches-section">
        <h2 class="section-title">최근 경기</h2>
        
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
          <p>아직 경기 기록이 없습니다.</p>
        </div>
      </div>
      
      <!-- 팀 가입 신청 목록 (팀장인 경우) -->
      <div v-if="isTeamLeader && team.join_requests && team.join_requests.length > 0" class="join-requests-section">
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
              <button class="reject-btn" @click="rejectJoinRequest(request.id)">거절</button>
              <button class="approve-btn" @click="approveJoinRequest(request.id)">수락</button>
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
      joinRequestSubmitting: false
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
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.loading-message,
.error-message {
  text-align: center;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin: 20px 0;
}

.error-message {
  color: #e74c3c;
}

.team-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.team-header {
  display: flex;
  padding: 30px;
  background-color: #f9f9f9;
  border-bottom: 1px solid #eee;
}

.team-logo {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 30px;
  border: 3px solid white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.team-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.team-info-header {
  flex: 1;
}

.team-name {
  font-size: 28px;
  margin: 0 0 10px;
  color: #333;
}

.team-level {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 15px;
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

.team-region {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  color: #555;
  font-size: 16px;
}

.team-region i {
  margin-right: 8px;
  color: #777;
}

.team-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  background-color: white;
  padding: 10px 15px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.team-actions {
  margin-top: 15px;
}

.join-team-btn,
.manage-team-btn,
.leave-team-btn,
.cancel-request-btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  border: none;
}

.join-team-btn {
  background-color: #4caf50;
  color: white;
}

.join-team-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.manage-team-btn {
  background-color: #2196f3;
  color: white;
}

.leave-team-btn {
  background-color: #f44336;
  color: white;
}

.cancel-request-btn {
  background-color: #f44336;
  color: white;
  margin-left: 10px;
}

.join-request-status {
  display: inline-flex;
  align-items: center;
  background-color: #fff8e1;
  color: #ffa000;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  margin-right: 10px;
}

.join-request-status i {
  margin-right: 5px;
}

.section-title {
  font-size: 20px;
  margin: 0 0 15px;
  color: #333;
}

.team-description-section,
.join-request-form-section,
.team-members-section,
.team-matches-section,
.join-requests-section {
  padding: 30px;
  border-bottom: 1px solid #eee;
}

.team-description {
  line-height: 1.6;
  color: #555;
}

.join-request-form {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 15px;
}

.cancel-btn,
.submit-btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.cancel-btn {
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  color: #333;
}

.submit-btn {
  background-color: #4caf50;
  border: none;
  color: white;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.members-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.member-card {
  display: flex;
  align-items: center;
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.member-avatar {
  width: 50px;
  height: 50px;
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
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
}

.leader-badge {
  background-color: #ffc107;
  color: #333;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 8px;
}

.member-position,
.member-join-date {
  font-size: 14px;
  color: #666;
}

.empty-members,
.empty-matches {
  text-align: center;
  padding: 20px;
  color: #666;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.matches-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.match-card {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.match-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.match-date {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.match-teams {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.home-team,
.away-team {
  font-weight: 500;
  color: #333;
  flex: 1;
}

.home-team {
  text-align: right;
  padding-right: 10px;
}

.away-team {
  text-align: left;
  padding-left: 10px;
}

.current-team {
  color: #2196f3;
  font-weight: 600;
}

.match-score {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  padding: 5px 10px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.match-venue {
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
}

.match-venue i {
  margin-right: 5px;
}

.join-requests-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.request-card {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.request-user {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
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
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
}

.request-date {
  font-size: 14px;
  color: #666;
}

.request-details {
  margin-bottom: 15px;
}

.request-position {
  margin-bottom: 10px;
}

.request-message {
  margin-bottom: 10px;
}

.detail-label {
  font-weight: 500;
  color: #333;
  margin-right: 5px;
}

.detail-value {
  color: #555;
}

.request-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.reject-btn,
.approve-btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  border: none;
}

.reject-btn {
  background-color: #f44336;
  color: white;
}

.approve-btn {
  background-color: #4caf50;
  color: white;
}

@media (max-width: 768px) {
  .team-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .team-logo {
    margin-right: 0;
    margin-bottom: 20px;
  }
  
  .team-region {
    justify-content: center;
  }
  
  .team-stats {
    justify-content: center;
  }
  
  .members-list {
    grid-template-columns: 1fr;
  }
  
  .match-teams {
    flex-direction: column;
    gap: 10px;
  }
  
  .home-team,
  .away-team {
    text-align: center;
    padding: 0;
  }
}
</style> 