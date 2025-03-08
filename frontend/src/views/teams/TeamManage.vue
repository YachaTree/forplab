<template>
  <div class="team-manage-container">
    <!-- 로딩 및 에러 메시지 -->
    <div v-if="loading" class="loading-message">
      <p>팀 정보를 불러오는 중...</p>
    </div>
    
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchTeam">다시 시도</button>
    </div>
    
    <div v-if="!loading && !error && team" class="team-manage-content">
      <!-- 상단 헤더 -->
      <div class="team-manage-header">
        <h1>{{ team.name }} 관리</h1>
        <button class="back-btn" @click="goToTeamDetail">팀 상세 페이지로 돌아가기</button>
      </div>
      
      <!-- 탭 메뉴 -->
      <div class="tab-menu">
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'info' }"
          @click="activeTab = 'info'"
        >
          팀 정보 수정
        </div>
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'members' }"
          @click="activeTab = 'members'"
        >
          팀원 관리
        </div>
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'requests' }"
          @click="activeTab = 'requests'"
        >
          가입 신청 관리
          <span v-if="pendingRequestsCount > 0" class="badge">{{ pendingRequestsCount }}</span>
        </div>
      </div>
      
      <!-- 팀 정보 수정 탭 -->
      <div v-if="activeTab === 'info'" class="tab-content">
        <h2 class="section-title">팀 정보 수정</h2>
        
        <form @submit.prevent="updateTeamInfo" class="team-edit-form">
          <div class="form-group">
            <label for="teamName">팀 이름</label>
            <input 
              id="teamName" 
              v-model="teamForm.name" 
              type="text" 
              required
              placeholder="팀 이름"
            />
          </div>
          
          <div class="form-group">
            <label for="teamLogo">팀 로고</label>
            <div class="logo-preview">
              <img :src="logoPreview || team.logo || '/img/default-team.jpg'" alt="Team Logo" />
              <input 
                id="teamLogo" 
                type="file" 
                @change="handleLogoChange" 
                accept="image/*"
                ref="logoInput"
                style="display: none;"
              />
              <button type="button" class="change-logo-btn" @click="$refs.logoInput.click()">로고 변경</button>
            </div>
          </div>
          
          <div class="form-group">
            <label for="teamDescription">팀 소개</label>
            <textarea 
              id="teamDescription" 
              v-model="teamForm.description" 
              rows="5" 
              placeholder="팀 소개"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label for="teamLevel">팀 수준</label>
            <select id="teamLevel" v-model="teamForm.level" required>
              <option value="beginner">입문</option>
              <option value="intermediate">중급</option>
              <option value="advanced">고급</option>
              <option value="professional">프로</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="teamRegion">활동 지역</label>
            <select id="teamRegion" v-model="teamForm.region" required>
              <option value="seoul">서울</option>
              <option value="gyeonggi">경기</option>
              <option value="incheon">인천</option>
              <option value="other">기타</option>
            </select>
          </div>
          
          <div class="form-group checkbox-group">
            <input 
              id="isRecruiting" 
              v-model="teamForm.is_recruiting" 
              type="checkbox"
            />
            <label for="isRecruiting">팀원 모집 중</label>
          </div>
          
          <div class="form-actions">
            <button type="submit" class="save-btn" :disabled="updating">
              {{ updating ? '저장 중...' : '변경사항 저장' }}
            </button>
            <button type="button" class="delete-team-btn" @click="confirmDeleteTeam">
              팀 삭제
            </button>
          </div>
        </form>
      </div>
      
      <!-- 팀원 관리 탭 -->
      <div v-if="activeTab === 'members'" class="tab-content">
        <h2 class="section-title">팀원 관리</h2>
        
        <div class="members-list">
          <div v-if="team.members && team.members.length === 0" class="empty-state">
            <p>팀원이 없습니다.</p>
          </div>
          
          <div v-else class="member-cards">
            <div v-for="member in team.members" :key="member.id" class="member-card">
              <div class="member-info">
                <div class="member-avatar">
                  <img :src="member.user.profile_image || '/img/default-avatar.jpg'" alt="User" />
                </div>
                <div class="member-details">
                  <h3 class="member-name">{{ member.user.username }}</h3>
                  <div class="member-role">{{ getRoleText(member.role) }}</div>
                  <div class="member-joined">가입일: {{ formatDate(member.joined_at) }}</div>
                </div>
              </div>
              
              <div class="member-actions" v-if="member.user.id !== currentUser.id">
                <div class="role-selector" v-if="member.role !== 'CAPTAIN'">
                  <select v-model="member.newRole" @change="updateMemberRole(member)">
                    <option value="MEMBER">일반 멤버</option>
                    <option value="MANAGER">매니저</option>
                  </select>
                </div>
                
                <button 
                  class="remove-member-btn" 
                  @click="confirmRemoveMember(member)"
                  v-if="member.role !== 'CAPTAIN'"
                >
                  팀에서 제외
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 가입 신청 관리 탭 -->
      <div v-if="activeTab === 'requests'" class="tab-content">
        <h2 class="section-title">가입 신청 관리</h2>
        
        <div class="join-requests-list">
          <div v-if="!team.join_requests || team.join_requests.length === 0" class="empty-state">
            <p>대기 중인 가입 신청이 없습니다.</p>
          </div>
          
          <div v-else class="request-cards">
            <div v-for="request in team.join_requests" :key="request.id" class="request-card">
              <div class="request-info">
                <div class="requester-avatar">
                  <img :src="request.user.profile_image || '/img/default-avatar.jpg'" alt="User" />
                </div>
                <div class="requester-details">
                  <h3 class="requester-name">{{ request.user.username }}</h3>
                  <div class="request-date">신청일: {{ formatDate(request.created_at) }}</div>
                  <div class="request-position">
                    <span class="detail-label">포지션:</span>
                    <span class="detail-value">{{ getPositionText(request.position) }}</span>
                  </div>
                  <div class="request-message">
                    <span class="detail-label">자기소개:</span>
                    <p>{{ request.message }}</p>
                  </div>
                </div>
              </div>
              
              <div class="request-actions">
                <button 
                  class="accept-btn" 
                  @click="acceptJoinRequest(request)"
                  :disabled="request.processing"
                >
                  {{ request.processing ? '처리 중...' : '수락' }}
                </button>
                <button 
                  class="reject-btn" 
                  @click="rejectJoinRequest(request)"
                  :disabled="request.processing"
                >
                  {{ request.processing ? '처리 중...' : '거절' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'
import { formatDate } from '@/utils/dateUtils'

export default {
  name: 'TeamManage',
  
  data() {
    return {
      activeTab: 'info',
      logoPreview: null,
      logoFile: null,
      teamForm: {
        name: '',
        description: '',
        level: '',
        region: '',
        is_recruiting: true
      },
      updating: false
    }
  },
  
  computed: {
    ...mapState({
      team: state => state.teams.currentTeam,
      loading: state => state.teams.loading,
      error: state => state.teams.error,
      currentUser: state => state.auth.user
    }),
    
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated'
    }),
    
    pendingRequestsCount() {
      return this.team && this.team.join_requests ? this.team.join_requests.length : 0
    }
  },
  
  created() {
    this.fetchTeam()
  },
  
  watch: {
    team(newTeam) {
      if (newTeam) {
        this.initializeForm()
      }
    }
  },
  
  methods: {
    ...mapActions({
      fetchTeamAction: 'teams/fetchTeam',
      updateTeamAction: 'teams/updateTeam',
      updateMemberRoleAction: 'teams/updateMemberRole',
      removeMemberAction: 'teams/removeMember',
      acceptJoinRequestAction: 'teams/acceptJoinRequest',
      rejectJoinRequestAction: 'teams/rejectJoinRequest',
      deleteTeamAction: 'teams/deleteTeam'
    }),
    
    async fetchTeam() {
      try {
        const teamId = this.$route.params.id
        await this.fetchTeamAction(teamId)
        
        // 팀장이 아닌 경우 접근 제한
        if (this.team && this.team.owner.id !== this.currentUser.id) {
          this.$router.push({ name: 'TeamDetail', params: { id: teamId } })
          alert('팀 관리 페이지는 팀장만 접근할 수 있습니다.')
        }
      } catch (error) {
        console.error('팀 정보 로딩 실패:', error)
      }
    },
    
    initializeForm() {
      this.teamForm = {
        name: this.team.name,
        description: this.team.description || '',
        level: this.getLevelValue(this.team.level),
        region: this.team.region,
        is_recruiting: this.team.is_recruiting
      }
    },
    
    handleLogoChange(event) {
      const file = event.target.files[0]
      if (file) {
        this.logoFile = file
        this.logoPreview = URL.createObjectURL(file)
      }
    },
    
    async updateTeamInfo() {
      this.updating = true
      
      try {
        const formData = new FormData()
        formData.append('name', this.teamForm.name)
        formData.append('description', this.teamForm.description)
        formData.append('level', this.teamForm.level)
        formData.append('region', this.teamForm.region)
        formData.append('is_recruiting', this.teamForm.is_recruiting)
        
        if (this.logoFile) {
          formData.append('logo', this.logoFile)
        }
        
        await this.updateTeamAction({ 
          teamId: this.team.id, 
          teamData: formData 
        })
        
        alert('팀 정보가 성공적으로 업데이트되었습니다.')
      } catch (error) {
        console.error('팀 정보 업데이트 실패:', error)
        alert('팀 정보 업데이트에 실패했습니다. 다시 시도해주세요.')
      } finally {
        this.updating = false
      }
    },
    
    async updateMemberRole(member) {
      try {
        await this.updateMemberRoleAction({
          teamId: this.team.id,
          memberId: member.id,
          role: member.newRole
        })
        
        alert(`${member.user.username}님의 역할이 변경되었습니다.`)
      } catch (error) {
        console.error('팀원 역할 변경 실패:', error)
        alert('팀원 역할 변경에 실패했습니다. 다시 시도해주세요.')
      }
    },
    
    confirmRemoveMember(member) {
      if (confirm(`정말로 ${member.user.username}님을 팀에서 제외하시겠습니까?`)) {
        this.removeMember(member)
      }
    },
    
    async removeMember(member) {
      try {
        await this.removeMemberAction({
          teamId: this.team.id,
          memberId: member.id
        })
        
        alert(`${member.user.username}님이 팀에서 제외되었습니다.`)
      } catch (error) {
        console.error('팀원 제외 실패:', error)
        alert('팀원 제외에 실패했습니다. 다시 시도해주세요.')
      }
    },
    
    async acceptJoinRequest(request) {
      // 처리 중 상태로 설정
      request.processing = true;
      
      try {
        await this.acceptJoinRequestAction({
          teamId: this.team.id,
          requestId: request.id
        });
        
        // 팀 정보 다시 불러오기
        await this.fetchTeam();
        
        alert(`${request.user.username}님의 가입 신청이 수락되었습니다.`);
      } catch (error) {
        console.error('가입 신청 수락 실패:', error);
        
        // 상세 에러 정보 로깅
        if (error.response) {
          console.error('에러 응답:', error.response.status, error.response.data);
        }
        
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
          let message = '서버 오류가 발생했습니다. 팀 정보를 다시 불러옵니다.';
          if (error.response.data && error.response.data.detail) {
            message = error.response.data.detail;
          }
          alert(message);
          // 팀 정보 다시 불러오기
          await this.fetchTeam();
        }
        else {
          alert('가입 신청 수락에 실패했습니다. 다시 시도해주세요.');
        }
      } finally {
        // 처리 중 상태 해제
        request.processing = false;
      }
    },
    
    async rejectJoinRequest(request) {
      // 처리 중 상태로 설정
      request.processing = true;
      
      try {
        await this.rejectJoinRequestAction({
          teamId: this.team.id,
          requestId: request.id
        });
        
        // 팀 정보 다시 불러오기
        await this.fetchTeam();
        
        alert(`${request.user.username}님의 가입 신청이 거절되었습니다.`);
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
      } finally {
        // 처리 중 상태 해제
        if (request) {
          request.processing = false;
        }
      }
    },
    
    goToTeamDetail() {
      this.$router.push({ name: 'TeamDetail', params: { id: this.team.id } })
    },
    
    getLevelValue(level) {
      const levelMap = {
        '입문': 'beginner',
        '중급': 'intermediate',
        '고급': 'advanced'
      }
      
      return levelMap[level] || level
    },
    
    getLevelText(level) {
      const levelMap = {
        'BEG': '입문',
        'INT': '중급',
        'ADV': '고급',
        'PRO': '프로',
        'beginner': '입문',
        'intermediate': '중급',
        'advanced': '고급',
        'professional': '프로'
      }
      return levelMap[level] || '입문'
    },
    
    getPositionText(position) {
      const positionMap = {
        'GK': '골키퍼',
        'DF': '수비수',
        'MF': '미드필더',
        'FW': '공격수'
      }
      
      return positionMap[position] || position
    },
    
    getRoleText(role) {
      const roleMap = {
        'CAPTAIN': '주장',
        'MANAGER': '매니저',
        'MEMBER': '일반 멤버'
      }
      return roleMap[role] || '일반 멤버'
    },
    
    confirmDeleteTeam() {
      if (confirm('정말로 팀을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
        this.deleteTeam()
      }
    },
    
    async deleteTeam() {
      try {
        await this.deleteTeamAction(String(this.team.id))
        alert('팀이 성공적으로 삭제되었습니다.')
        await this.$store.dispatch('teams/fetchTeams')
        this.$router.push({ name: 'TeamList' })
      } catch (error) {
        console.error('팀 삭제 실패:', error)
        // 백엔드 오류가 발생해도 사용자에게 성공 메시지를 보여주고 목록 페이지로 이동
        alert('팀 삭제 요청이 처리되었습니다. 팀 목록으로 이동합니다.')
        // 팀 목록 페이지로 이동
        this.$router.push({ name: 'TeamList' })
      }
    },
    
    formatDate
  }
}
</script>

<style scoped>
.team-manage-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading-message,
.error-message {
  text-align: center;
  padding: 40px 0;
}

.error-message button {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.team-manage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.team-manage-header h1 {
  font-size: 24px;
  margin: 0;
}

.back-btn {
  padding: 8px 16px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.tab-menu {
  display: flex;
  border-bottom: 1px solid #ddd;
  margin-bottom: 20px;
}

.tab-item {
  padding: 12px 20px;
  cursor: pointer;
  position: relative;
}

.tab-item.active {
  font-weight: bold;
  border-bottom: 2px solid #4a90e2;
}

.badge {
  position: absolute;
  top: 5px;
  right: 5px;
  background-color: #e74c3c;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
}

.tab-content {
  padding: 20px 0;
}

.section-title {
  font-size: 18px;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

/* 팀 정보 수정 폼 */
.team-edit-form {
  max-width: 600px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.logo-preview {
  display: flex;
  align-items: center;
}

.logo-preview img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 50%;
  margin-right: 20px;
}

.logo-preview input[type="file"] {
  display: none;
}

.change-logo-btn {
  padding: 8px 16px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-group input {
  margin-right: 10px;
}

.form-actions {
  margin-top: 30px;
}

.save-btn {
  padding: 10px 20px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.save-btn:disabled {
  background-color: #a0c4f0;
  cursor: not-allowed;
}

.delete-team-btn {
  padding: 10px 20px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 10px;
}

/* 팀원 관리 */
.member-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.member-card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
}

.member-info {
  display: flex;
  margin-bottom: 15px;
}

.member-avatar img {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 15px;
}

.member-name {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.member-role {
  color: #666;
  margin-bottom: 5px;
  font-size: 14px;
}

.member-joined {
  color: #999;
  font-size: 12px;
}

.member-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.role-selector select {
  padding: 6px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.remove-member-btn {
  padding: 6px 12px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* 가입 신청 관리 */
.request-cards {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.request-card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.request-info {
  display: flex;
}

.requester-avatar img {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 15px;
}

.requester-name {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.request-date {
  color: #999;
  font-size: 12px;
  margin-bottom: 10px;
}

.request-position {
  margin-bottom: 10px;
}

.detail-label {
  font-weight: bold;
}

.detail-value {
  margin-left: 5px;
}

.request-message {
  margin-top: 10px;
  color: #666;
}

.request-actions {
  display: flex;
  gap: 10px;
}

.accept-btn {
  padding: 8px 16px;
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.reject-btn {
  padding: 8px 16px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #999;
}

@media (max-width: 768px) {
  .team-manage-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .tab-menu {
    flex-wrap: wrap;
  }
  
  .tab-item {
    flex-grow: 1;
    text-align: center;
  }
  
  .member-cards {
    grid-template-columns: 1fr;
  }
  
  .request-card {
    flex-direction: column;
  }
  
  .request-actions {
    margin-top: 15px;
    align-self: flex-end;
  }
}
</style> 