<template>
  <div class="match-detail-container">
    <!-- 로딩 및 에러 메시지 -->
    <div v-if="loading" class="loading-message">
      <p>매치 정보를 불러오는 중...</p>
    </div>
    
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchMatch">다시 시도</button>
    </div>
    
    <div v-if="!loading && !error && match" class="match-content">
      <!-- 상단 헤더 -->
      <div class="match-header">
        <div class="match-status-bar">
          <span :class="['match-status', `status-${match.status}`]">{{ getStatusText(match.status) }}</span>
          <span class="match-date">{{ formatDate(match.date) }} {{ match.start_time }} ~ {{ match.end_time }}</span>
        </div>
        
        <h1 class="match-title">{{ match.title }}</h1>
        
        <div class="match-host">
          <img :src="match.host.profile_image || '/img/default-avatar.png'" alt="Host" class="host-avatar">
          <span>주최자: {{ match.host.username }}</span>
        </div>
      </div>
      
      <!-- 매치 정보 -->
      <div class="match-info-section">
        <div class="info-card">
          <h3>매치 정보</h3>
          
          <div class="info-row">
            <div class="info-label">매치 유형</div>
            <div class="info-value">{{ getMatchTypeText(match.match_type) }}</div>
          </div>
          
          <div class="info-row">
            <div class="info-label">실력 수준</div>
            <div class="info-value">{{ getSkillLevelText(match.skill_level) }}</div>
          </div>
          
          <div class="info-row">
            <div class="info-label">성별</div>
            <div class="info-value">{{ getGenderText(match.gender) }}</div>
          </div>
          
          <div class="info-row">
            <div class="info-label">참가 인원</div>
            <div class="info-value">{{ match.current_players_count }}/{{ match.max_players }}명</div>
          </div>
          
          <div class="info-row">
            <div class="info-label">참가비</div>
            <div class="info-value">{{ formatPrice(match.price) }}원</div>
          </div>
        </div>
        
        <div class="info-card">
          <h3>구장 정보</h3>
          
          <div class="venue-name">
            <i class="fas fa-map-marker-alt"></i>
            <span>{{ match.venue.name }}</span>
          </div>
          
          <div class="venue-address">{{ match.venue.address }}</div>
          
          <div class="venue-contact">
            <i class="fas fa-phone"></i>
            <span>{{ match.venue.phone }}</span>
          </div>
          
          <button class="venue-detail-btn" @click="goToVenueDetail(match.venue.id)">구장 상세 정보</button>
        </div>
      </div>
      
      <!-- 매치 설명 -->
      <div class="match-description-section">
        <h3>매치 설명</h3>
        <div class="match-description">
          <p>{{ match.description }}</p>
        </div>
      </div>
      
      <!-- 참가자 목록 -->
      <div class="match-participants-section">
        <h3>참가자 ({{ match.participants.length }}/{{ match.max_players }})</h3>
        
        <div class="participants-list">
          <div v-for="participant in match.participants" :key="participant.id" class="participant-card">
            <img :src="participant.user.profile_image || '/img/default-avatar.png'" alt="User" class="participant-avatar">
            <div class="participant-info">
              <div class="participant-name">{{ participant.user.username }}</div>
              <div class="participant-skill">{{ getSkillLevelText(participant.user.skill_level) }}</div>
            </div>
            <div :class="['participant-status', `status-${participant.status}`]">
              {{ getParticipantStatusText(participant.status) }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- 매치 결과 (종료된 경우) -->
      <div v-if="match.status === 'completed' && match.result" class="match-result-section">
        <h3>매치 결과</h3>
        
        <div class="result-card">
          <div class="result-score">
            <div class="team-score">
              <span class="team-name">팀 A</span>
              <span class="score">{{ match.result.team_a_score }}</span>
            </div>
            <span class="score-divider">:</span>
            <div class="team-score">
              <span class="score">{{ match.result.team_b_score }}</span>
              <span class="team-name">팀 B</span>
            </div>
          </div>
          
          <div v-if="match.result.mvp" class="result-mvp">
            <h4>MVP</h4>
            <div class="mvp-info">
              <img :src="match.result.mvp.profile_image || '/img/default-avatar.png'" alt="MVP" class="mvp-avatar">
              <span class="mvp-name">{{ match.result.mvp.username }}</span>
            </div>
          </div>
          
          <div v-if="match.result.comment" class="result-comment">
            <h4>코멘트</h4>
            <p>{{ match.result.comment }}</p>
          </div>
        </div>
      </div>
      
      <!-- 액션 버튼 -->
      <div class="match-actions">
        <button 
          v-if="isAuthenticated && !isParticipant && match.status === 'open'" 
          class="action-btn join-btn"
          @click="joinMatch"
          :disabled="joinLoading"
        >
          {{ joinLoading ? '처리 중...' : '참가 신청' }}
        </button>
        
        <button 
          v-if="isAuthenticated && isParticipant && (match.status === 'open' || match.status === 'full')" 
          class="action-btn leave-btn"
          @click="leaveMatch"
          :disabled="leaveLoading"
        >
          {{ leaveLoading ? '처리 중...' : '참가 취소' }}
        </button>
        
        <button 
          v-if="isAuthenticated && isHost && (match.status === 'open' || match.status === 'full')" 
          class="action-btn edit-btn"
          @click="editMatch"
        >
          매치 수정
        </button>
        
        <button 
          v-if="isAuthenticated && isHost && match.status === 'completed' && !match.result" 
          class="action-btn result-btn"
          @click="createResult"
        >
          결과 등록
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
  name: 'MatchDetail',
  
  data() {
    return {
      joinLoading: false,
      leaveLoading: false
    };
  },
  
  computed: {
    ...mapState({
      match: state => state.currentMatch,
      loading: state => state.matchLoading,
      error: state => state.matchError,
      user: state => state.user
    }),
    
    ...mapGetters(['isAuthenticated']),
    
    isHost() {
      return this.match && this.user && this.match.host.id === this.user.id;
    },
    
    isParticipant() {
      if (!this.match || !this.user) return false;
      return this.match.is_participant;
    }
  },
  
  created() {
    this.fetchMatch();
  },
  
  methods: {
    ...mapActions(['fetchMatch']),
    
    async fetchMatch() {
      try {
        await this.$store.dispatch('fetchMatch', this.$route.params.id);
      } catch (error) {
        console.error('매치 상세 조회 실패:', error);
      }
    },
    
    async joinMatch() {
      this.joinLoading = true;
      try {
        await this.$store.dispatch('joinMatch', this.match.id);
        this.$toast.success('매치 참가 신청이 완료되었습니다.');
      } catch (error) {
        console.error('매치 참가 실패:', error);
        this.$toast.error(error.response?.data?.detail || '매치 참가에 실패했습니다.');
      } finally {
        this.joinLoading = false;
      }
    },
    
    async leaveMatch() {
      this.leaveLoading = true;
      try {
        await this.$store.dispatch('leaveMatch', this.match.id);
        this.$toast.success('매치 참가가 취소되었습니다.');
      } catch (error) {
        console.error('매치 참가 취소 실패:', error);
        this.$toast.error(error.response?.data?.detail || '매치 참가 취소에 실패했습니다.');
      } finally {
        this.leaveLoading = false;
      }
    },
    
    editMatch() {
      this.$router.push({ name: 'MatchEdit', params: { id: this.match.id } });
    },
    
    createResult() {
      this.$router.push({ name: 'MatchResultCreate', params: { id: this.match.id } });
    },
    
    goToVenueDetail(venueId) {
      this.$router.push({ name: 'VenueDetail', params: { id: venueId } });
    },
    
    formatDate(dateString) {
      const date = new Date(dateString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
      const weekday = weekdays[date.getDay()];
      
      return `${year}.${month}.${day} (${weekday})`;
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
    
    getMatchTypeText(matchType) {
      const matchTypeMap = {
        'friendly': '친선전',
        'league': '리그전',
        'tournament': '토너먼트'
      };
      
      return matchTypeMap[matchType] || matchType;
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
    },
    
    getParticipantStatusText(status) {
      const statusMap = {
        'confirmed': '확정',
        'pending': '대기중',
        'canceled': '취소'
      };
      
      return statusMap[status] || status;
    }
  }
};
</script>

<style scoped>
.match-detail-container {
  max-width: 900px;
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

.match-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.match-header {
  padding: 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.match-status-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.match-status {
  font-size: 14px;
  padding: 5px 12px;
  border-radius: 20px;
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

.match-date {
  font-size: 14px;
  color: #666;
}

.match-title {
  font-size: 24px;
  margin: 10px 0 15px;
  color: #333;
}

.match-host {
  display: flex;
  align-items: center;
}

.host-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-right: 10px;
  object-fit: cover;
}

.match-info-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  padding: 20px;
}

.info-card {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
}

.info-card h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
  color: #333;
}

.info-row {
  display: flex;
  margin-bottom: 10px;
}

.info-label {
  width: 100px;
  font-weight: 500;
  color: #666;
}

.info-value {
  flex: 1;
  color: #333;
}

.venue-name {
  display: flex;
  align-items: center;
  font-weight: 500;
  font-size: 16px;
  margin-bottom: 10px;
}

.venue-name i {
  margin-right: 8px;
  color: #1976d2;
}

.venue-address {
  margin-bottom: 10px;
  color: #666;
}

.venue-contact {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  color: #666;
}

.venue-contact i {
  margin-right: 8px;
  color: #1976d2;
}

.venue-detail-btn {
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
}

.venue-detail-btn:hover {
  background-color: #e0e0e0;
}

.match-description-section,
.match-participants-section,
.match-result-section {
  padding: 20px;
  border-top: 1px solid #eee;
}

.match-description-section h3,
.match-participants-section h3,
.match-result-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
  color: #333;
}

.match-description {
  color: #555;
  line-height: 1.6;
}

.participants-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.participant-card {
  display: flex;
  align-items: center;
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 10px;
}

.participant-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
  object-fit: cover;
}

.participant-info {
  flex: 1;
}

.participant-name {
  font-weight: 500;
  color: #333;
}

.participant-skill {
  font-size: 12px;
  color: #666;
}

.participant-status {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.status-confirmed {
  background-color: #e8f5e9;
  color: #388e3c;
}

.status-pending {
  background-color: #fff8e1;
  color: #ffa000;
}

.status-canceled {
  background-color: #ffebee;
  color: #d32f2f;
}

.result-card {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
}

.result-score {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
}

.team-score {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.team-name {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.score {
  font-size: 32px;
  font-weight: 700;
  color: #333;
}

.score-divider {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin: 0 20px;
}

.result-mvp {
  text-align: center;
  margin-bottom: 20px;
}

.result-mvp h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
}

.mvp-info {
  display: flex;
  justify-content: center;
  align-items: center;
}

.mvp-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
  object-fit: cover;
}

.mvp-name {
  font-weight: 500;
  color: #333;
}

.result-comment h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
}

.result-comment p {
  color: #555;
  line-height: 1.6;
}

.match-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.action-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.join-btn {
  background-color: #1976d2;
  color: white;
}

.join-btn:hover {
  background-color: #1565c0;
}

.leave-btn {
  background-color: #f44336;
  color: white;
}

.leave-btn:hover {
  background-color: #d32f2f;
}

.edit-btn {
  background-color: #f0f0f0;
  color: #333;
}

.edit-btn:hover {
  background-color: #e0e0e0;
}

.result-btn {
  background-color: #4caf50;
  color: white;
}

.result-btn:hover {
  background-color: #388e3c;
}

.action-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .match-info-section {
    grid-template-columns: 1fr;
  }
  
  .participants-list {
    grid-template-columns: 1fr;
  }
}
</style> 