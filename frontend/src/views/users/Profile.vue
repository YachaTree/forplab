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
          <img :src="getProfileImageUrl(user.profile_image)" :key="imageKey" alt="프로필 이미지">
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
          
          <!-- 친구 관련 버튼 (다른 사용자의 프로필을 볼 때) -->
          <div class="user-actions" v-else>
            <!-- 친구 요청 버튼 -->
            <button 
              v-if="!isFriend && !hasSentRequest && !hasReceivedRequest" 
              @click="sendFriendRequest" 
              class="friend-request-btn"
              :disabled="requestLoading"
            >
              <i class="fas fa-user-plus"></i>
              친구 요청 보내기
            </button>
            
            <!-- 요청 전송됨 상태 -->
            <button 
              v-else-if="hasSentRequest" 
              class="request-sent-btn"
              disabled
            >
              <i class="fas fa-clock"></i>
              요청 전송됨
            </button>
            
            <!-- 요청 수락 버튼 -->
            <div v-else-if="hasReceivedRequest" class="friend-request-actions">
              <button 
                @click="acceptFriendRequest" 
                class="accept-request-btn"
                :disabled="requestLoading"
              >
                <i class="fas fa-check"></i>
                요청 수락
              </button>
              <button 
                @click="rejectFriendRequest" 
                class="reject-request-btn"
                :disabled="requestLoading"
              >
                <i class="fas fa-times"></i>
                요청 거절
              </button>
            </div>
            
            <!-- 이미 친구인 경우 -->
            <button 
              v-else-if="isFriend" 
              @click="confirmDeleteFriend" 
              class="remove-friend-btn"
            >
              <i class="fas fa-user-minus"></i>
              친구 삭제
            </button>
          </div>
        </div>
      </div>
      
      <!-- 탭 메뉴 -->
      <div class="tab-menu">
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'info' }"
          @click="changeTab('info')"
        >
          <i class="fas fa-info-circle"></i>
          기본 정보
        </div>
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'teams' }"
          @click="changeTab('teams')"
        >
          <i class="fas fa-users"></i>
          소속 팀
        </div>
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'matches' }"
          @click="changeTab('matches')"
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
                <img :src="getTeamLogoUrl(team.logo)" alt="팀 로고">
              </div>
              <div class="team-info">
                <h3 class="team-name">{{ team.name }}</h3>
                <p class="team-level">{{ team.level_display }}</p>
                <p class="team-region">{{ team.region_display }}</p>
              </div>
              <div class="view-details">
                자세히 보기
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
            <label for="username">사용자명 (변경 불가)</label>
            <input type="text" id="username" v-model="editForm.username" readonly class="readonly-input">
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
            <div class="image-upload-container">
              <label for="profile_image_input" class="upload-label">
                <i class="fas fa-upload"></i> 이미지 선택하기
              </label>
              <input type="file" id="profile_image_input" @change="handleImageUpload" accept="image/jpeg,image/jpg,image/png,image/gif">
              <p class="image-hint">JPEG, JPG, PNG, GIF 형식만 허용됩니다. (최대 5MB)</p>
              <div v-if="editForm.profile_image" class="selected-image">
                <p>선택된 이미지: {{ editForm.profile_image.name }}</p>
              </div>
            </div>
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
      userMatches: [],
      imageKey: 0, // 이미지 강제 갱신을 위한 키
      isFriend: false,
      hasSentRequest: false,
      hasReceivedRequest: false,
      requestLoading: false
    };
  },
  
  computed: {
    ...mapState({
      user: state => state.auth.user,
      loading: state => state.auth.loading,
      error: state => state.auth.error,
      currentUser: state => state.auth.user,
      friends: state => state.friends.friends,
      friendRequests: state => state.friends.friendRequests,
      sentRequests: state => state.friends.sentRequests
    }),
    
    isCurrentUser() {
      return this.currentUser && this.user && this.currentUser.id === this.user.id;
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
    console.log('현재 사용자 정보:', this.user);
    
    // URL에서 탭 정보 읽어오기
    const tab = this.$route.query.tab;
    if (tab && ['info', 'teams', 'matches'].includes(tab)) {
      this.activeTab = tab;
    }
    
    // 사용자 정보가 없는 경우 먼저 프로필 정보를 가져옴
    if (!this.user) {
      console.log('사용자 정보가 없음, 프로필 정보 조회 시도');
      this.fetchProfile().then(() => {
        console.log('프로필 정보 조회 성공, 사용자:', this.user);
        this.loadUserTeams();
        this.loadUserMatches();
        // 프로필 수정 폼 초기화
        this.initEditForm();
      }).catch(error => {
        console.error('프로필 정보 조회 실패:', error);
      });
    } else {
      this.fetchUserProfile();
      this.loadUserTeams();
      this.loadUserMatches();
      // 프로필 수정 폼 초기화
      this.initEditForm();
    }
  },
  
  methods: {
    ...mapActions({
      fetchProfile: 'auth/fetchProfile',
      updateProfile: 'auth/updateProfile',
      fetchUserProfileAction: 'auth/fetchUserProfile',
      fetchFriends: 'friends/fetchFriends',
      fetchFriendRequests: 'friends/fetchFriendRequests',
      fetchSentRequests: 'friends/fetchSentRequests',
      sendFriendRequestAction: 'friends/sendFriendRequest',
      acceptFriendRequestAction: 'friends/acceptFriendRequest',
      rejectFriendRequestAction: 'friends/rejectFriendRequest',
      deleteFriendshipAction: 'friends/deleteFriendship'
    }),
    
    async fetchUserProfile() {
      console.log('프로필 정보 조회 시작, 경로:', this.$route.path);
      console.log('현재 사용자 정보 (조회 전):', this.user);
      
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
          console.log('현재 사용자 프로필 (fetchProfile 후):', this.user);
          
          // 프로필 수정 폼 초기화
          if (this.user) {
            this.initEditForm();
          }
        }
        
        console.log('프로필 정보 조회 완료, 사용자 정보:', this.user);
        
        // 친구 관련 데이터 로드
        if (!this.isCurrentUser) {
          await Promise.all([
            this.fetchFriends(),
            this.fetchFriendRequests(),
            this.fetchSentRequests()
          ]);
          this.checkFriendshipStatus();
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
        
        // 기본 정보 추가
        formData.append('email', this.editForm.email);
        
        if (this.editForm.phone) {
          formData.append('phone', this.editForm.phone);
        }
        
        if (this.editForm.birth_date) {
          formData.append('birth_date', this.editForm.birth_date);
        }
        
        formData.append('skill_level', this.editForm.skill_level);
        formData.append('bio', this.editForm.bio);
        
        // 이미지가 있는 경우 추가
        let hasImageUpdate = false;
        if (this.editForm.profile_image) {
          hasImageUpdate = true;
          // 파일 타입에 따라 확장자 결정
          let extension = '';
          const fileType = this.editForm.profile_image.type;
          
          if (fileType === 'image/jpeg' || fileType === 'image/jpg') extension = '.jpg';
          else if (fileType === 'image/png') extension = '.png';
          else if (fileType === 'image/gif') extension = '.gif';
          
          // 파일 이름 생성 (타임스탬프 추가하여 고유성 보장)
          const timestamp = new Date().getTime();
          const fileName = `profile_${timestamp}${extension}`;
          
          // 새 파일 객체 생성
          const newFile = new File([this.editForm.profile_image], fileName, { type: fileType });
          
          // FormData에 추가
          formData.append('profile_image', newFile);
          console.log('이미지 파일 추가:', fileName, fileType);
        }
        
        // FormData 내용 디버깅
        console.log('FormData 내용:');
        for (let [key, value] of formData.entries()) {
          console.log(`${key}: ${value instanceof File ? `${value.name} (${value.type}, ${value.size} bytes)` : value}`);
        }
        
        // 프로필 업데이트 요청
        const response = await this.updateProfile(formData);
        console.log('프로필 업데이트 응답:', response);
        
        this.showEditForm = false;
        alert('프로필이 성공적으로 업데이트되었습니다.');
        
        // 프로필 정보 다시 불러오기
        await this.fetchProfile();
        
        // 이미지 업데이트가 있었다면 이미지 키 증가시켜 강제 갱신
        if (hasImageUpdate) {
          console.log('이미지 업데이트 감지, 이미지 키 갱신');
          this.imageKey++; // 이미지 키 증가
          
          // 브라우저 캐시 강제 갱신을 위해 이미지 URL 직접 조작
          if (this.user && this.user.profile_image) {
            const timestamp = new Date().getTime();
            const imageUrl = this.user.profile_image.includes('?') 
              ? this.user.profile_image.split('?')[0] + `?t=${timestamp}`
              : this.user.profile_image + `?t=${timestamp}`;
            
            // 사용자 객체 복사 후 이미지 URL 업데이트
            const updatedUser = { ...this.user, profile_image: imageUrl };
            this.$store.commit('auth/SET_USER', updatedUser);
            
            // 이미지 프리로드
            const img = new Image();
            img.src = imageUrl;
          }
        }
      } catch (error) {
        console.error('프로필 업데이트 실패:', error);
        
        // 에러 메시지 상세 출력
        if (error.response) {
          console.error('에러 응답:', error.response.status, error.response.data);
          
          // 백엔드에서 반환한 에러 메시지가 있으면 표시
          if (error.response.data) {
            let errorMessage = '프로필 업데이트에 실패했습니다: ';
            
            // 에러 메시지 형식에 따라 처리
            if (error.response.data.detail) {
              errorMessage += error.response.data.detail;
            } else if (error.response.data.profile_image) {
              // 이미지 관련 에러 메시지
              errorMessage += `이미지 오류: ${error.response.data.profile_image.join(', ')}`;
            } else {
              // 기타 필드 에러
              const errors = [];
              for (const field in error.response.data) {
                if (Array.isArray(error.response.data[field])) {
                  errors.push(`${field}: ${error.response.data[field].join(', ')}`);
                }
              }
              errorMessage += errors.join('; ');
            }
            
            alert(errorMessage);
          } else {
            alert('프로필 업데이트에 실패했습니다. 다시 시도해주세요.');
          }
        } else if (error.message) {
          // 클라이언트 측 유효성 검사 에러
          alert(error.message);
        } else {
          alert('프로필 업데이트에 실패했습니다. 다시 시도해주세요.');
        }
      } finally {
        this.updating = false;
      }
    },
    
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // 이미지 파일 크기 및 형식 검사
      const maxSize = 5 * 1024 * 1024; // 5MB
      if (file.size > maxSize) {
        alert('이미지 크기는 5MB를 초과할 수 없습니다.');
        event.target.value = ''; // 파일 선택 초기화
        return;
      }
      
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
      if (!allowedTypes.includes(file.type)) {
        alert('이미지는 JPEG, JPG, PNG, GIF 형식만 허용됩니다.');
        event.target.value = ''; // 파일 선택 초기화
        return;
      }
      
      // 이미지 최적화 (크기 조정 및 압축)
      this.optimizeImage(file).then(optimizedFile => {
        // 파일 객체 저장
        this.editForm.profile_image = optimizedFile;
        console.log('이미지 파일 최적화 완료:', optimizedFile.name, optimizedFile.type, optimizedFile.size);
      }).catch(error => {
        console.error('이미지 최적화 실패:', error);
        // 최적화 실패 시 원본 파일 사용
        this.editForm.profile_image = file;
        console.log('원본 이미지 파일 사용:', file.name, file.type, file.size);
      });
    },
    
    optimizeImage(file) {
      return new Promise((resolve, reject) => {
        // 이미지 로드
        const img = new Image();
        img.onload = () => {
          // 최대 크기 설정 (가로/세로 최대 1200px)
          const maxWidth = 1200;
          const maxHeight = 1200;
          
          let width = img.width;
          let height = img.height;
          
          // 이미지 크기 조정
          if (width > maxWidth || height > maxHeight) {
            if (width > height) {
              height = Math.round(height * (maxWidth / width));
              width = maxWidth;
            } else {
              width = Math.round(width * (maxHeight / height));
              height = maxHeight;
            }
          }
          
          // 캔버스 생성
          const canvas = document.createElement('canvas');
          canvas.width = width;
          canvas.height = height;
          
          // 이미지 그리기
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, width, height);
          
          // 이미지 압축 및 변환
          const quality = 0.8; // 80% 품질
          
          // 파일 형식에 따라 압축 방식 결정
          let mimeType = file.type;
          if (file.type === 'image/png') {
            mimeType = 'image/jpeg'; // PNG는 JPEG로 변환하여 더 작은 파일 크기로 압축
          }
          
          // 캔버스를 Blob으로 변환
          canvas.toBlob(blob => {
            if (!blob) {
              reject(new Error('이미지 변환 실패'));
              return;
            }
            
            // 파일명 생성
            const timestamp = new Date().getTime();
            const extension = mimeType === 'image/jpeg' ? '.jpg' : 
                             mimeType === 'image/png' ? '.png' : 
                             mimeType === 'image/gif' ? '.gif' : '.jpg';
            const fileName = `profile_${timestamp}${extension}`;
            
            // Blob을 File 객체로 변환
            const optimizedFile = new File([blob], fileName, { type: mimeType });
            
            resolve(optimizedFile);
          }, mimeType, quality);
        };
        
        img.onerror = () => {
          reject(new Error('이미지 로드 실패'));
        };
        
        // 파일을 Data URL로 변환하여 이미지 로드
        const reader = new FileReader();
        reader.onload = e => {
          img.src = e.target.result;
        };
        reader.onerror = () => {
          reject(new Error('파일 읽기 실패'));
        };
        reader.readAsDataURL(file);
      });
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
    },
    
    getProfileImageUrl(imageUrl) {
      if (!imageUrl) {
        return '/img/default-avatar.png';
      }
      
      // 이미 타임스탬프가 있는 경우 그대로 반환
      if (imageUrl.includes('?t=')) {
        return imageUrl;
      }
      
      // 캐시 방지를 위해 타임스탬프 추가
      const timestamp = new Date().getTime();
      return `${imageUrl}?t=${timestamp}`;
    },
    
    getTeamLogoUrl(logoUrl) {
      if (!logoUrl) {
        return '/img/default-team.png';
      }
      
      // 상대 경로인 경우 절대 경로로 변환
      if (!logoUrl.startsWith('http') && !logoUrl.startsWith('/')) {
        // 이미 /media로 시작하는 경우
        if (logoUrl.startsWith('/media')) {
          logoUrl = `http://localhost:8000${logoUrl}`;
        } else {
          logoUrl = `http://localhost:8000/media/${logoUrl}`;
        }
      }
      
      console.log('팀 로고 URL:', logoUrl);
      
      // 이미 타임스탬프가 있는 경우 그대로 반환
      if (logoUrl.includes('?t=')) {
        return logoUrl;
      }
      
      // 캐시 방지를 위해 타임스탬프 추가
      const timestamp = new Date().getTime();
      return `${logoUrl}?t=${timestamp}`;
    },
    
    // 컴포넌트가 마운트된 후 이미지 로딩 확인
    mounted() {
      // 이미지 로딩 완료 후 처리
      if (this.user && this.user.profile_image) {
        const img = new Image();
        img.onload = () => {
          console.log('프로필 이미지 로딩 완료:', this.user.profile_image);
        };
        img.onerror = () => {
          console.error('프로필 이미지 로딩 실패:', this.user.profile_image);
        };
        img.src = this.getProfileImageUrl(this.user.profile_image);
      }
    },
    
    // 탭 변경 메서드
    changeTab(tab) {
      this.activeTab = tab;
      
      // URL 업데이트
      this.$router.push({
        query: { ...this.$route.query, tab }
      });
    },
    
    // 친구 상태 확인 메소드
    checkFriendshipStatus() {
      if (!this.user || !this.currentUser || this.isCurrentUser) return;
      
      // 이미 친구인지 확인
      this.isFriend = this.friends.some(friendship => 
        (friendship.from_user.id === this.user.id || friendship.to_user.id === this.user.id) && 
        friendship.status === 'ACCEPTED'
      );
      
      // 친구 요청을 보냈는지 확인
      this.hasSentRequest = this.sentRequests.some(request => 
        request.to_user.id === this.user.id && 
        request.status === 'PENDING'
      );
      
      // 친구 요청을 받았는지 확인
      this.hasReceivedRequest = this.friendRequests.some(request => 
        request.from_user.id === this.user.id && 
        request.status === 'PENDING'
      );
    },
    
    // 친구 요청 ID 가져오기
    getFriendRequestId() {
      if (this.hasReceivedRequest) {
        const request = this.friendRequests.find(req => 
          req.from_user.id === this.user.id && 
          req.status === 'PENDING'
        );
        return request ? request.id : null;
      }
      return null;
    },
    
    // 친구 관계 ID 가져오기
    getFriendshipId() {
      if (this.isFriend) {
        const friendship = this.friends.find(f => 
          f.from_user.id === this.user.id || 
          f.to_user.id === this.user.id
        );
        return friendship ? friendship.id : null;
      }
      return null;
    },
    
    // 친구 요청 보내기
    async sendFriendRequest() {
      if (!this.user || this.requestLoading) return;
      
      this.requestLoading = true;
      
      try {
        await this.sendFriendRequestAction(this.user.id);
        this.$toast.success('친구 요청을 보냈습니다.');
        await this.fetchSentRequests();
        this.checkFriendshipStatus();
      } catch (error) {
        console.error('친구 요청 전송 실패:', error);
        this.$toast.error('친구 요청 전송에 실패했습니다.');
      } finally {
        this.requestLoading = false;
      }
    },
    
    // 친구 요청 수락
    async acceptFriendRequest() {
      const requestId = this.getFriendRequestId();
      if (!requestId || this.requestLoading) return;
      
      this.requestLoading = true;
      
      try {
        await this.acceptFriendRequestAction(requestId);
        this.$toast.success('친구 요청을 수락했습니다.');
        await Promise.all([
          this.fetchFriends(),
          this.fetchFriendRequests()
        ]);
        this.checkFriendshipStatus();
      } catch (error) {
        console.error('친구 요청 수락 실패:', error);
        this.$toast.error('친구 요청 수락에 실패했습니다.');
      } finally {
        this.requestLoading = false;
      }
    },
    
    // 친구 요청 거절
    async rejectFriendRequest() {
      const requestId = this.getFriendRequestId();
      if (!requestId || this.requestLoading) return;
      
      this.requestLoading = true;
      
      try {
        await this.rejectFriendRequestAction(requestId);
        this.$toast.success('친구 요청을 거절했습니다.');
        await this.fetchFriendRequests();
        this.checkFriendshipStatus();
      } catch (error) {
        console.error('친구 요청 거절 실패:', error);
        this.$toast.error('친구 요청 거절에 실패했습니다.');
      } finally {
        this.requestLoading = false;
      }
    },
    
    // 친구 삭제 확인
    confirmDeleteFriend() {
      if (confirm('정말로 이 친구를 삭제하시겠습니까?')) {
        this.deleteFriend();
      }
    },
    
    // 친구 삭제
    async deleteFriend() {
      const friendshipId = this.getFriendshipId();
      if (!friendshipId) return;
      
      this.requestLoading = true;
      
      try {
        await this.deleteFriendshipAction(friendshipId);
        this.$toast.success('친구가 삭제되었습니다.');
        await this.fetchFriends();
        this.checkFriendshipStatus();
      } catch (error) {
        console.error('친구 삭제 실패:', error);
        this.$toast.error('친구 삭제에 실패했습니다.');
      } finally {
        this.requestLoading = false;
      }
    },
  },
  
  watch: {
    showEditForm(newVal) {
      if (newVal && this.user) {
        // 모달이 열릴 때 프로필 수정 폼 초기화
        this.initEditForm();
      }
    },
    // 사용자 정보가 변경될 때 프로필 수정 폼 초기화
    user(newVal) {
      if (newVal) {
        this.initEditForm();
      }
    },
    // 친구 상태 변경 감지
    friends() {
      this.checkFriendshipStatus();
    },
    friendRequests() {
      this.checkFriendshipStatus();
    },
    sentRequests() {
      this.checkFriendshipStatus();
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

/* 로딩 및 에러 메시지 */
.loading-message,
.error-message {
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

/* 프로필 컨텐츠 */
.profile-content {
  background-color: var(--white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  overflow: hidden;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 프로필 헤더 */
.profile-header {
  display: flex;
  padding: 40px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: var(--white);
  position: relative;
  border-radius: var(--border-radius) var(--border-radius) 0 0;
  overflow: hidden;
}

.profile-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, 0.1) 50%, rgba(255, 255, 255, 0.1) 75%, transparent 75%, transparent);
  background-size: 10px 10px;
  opacity: 0.2;
  z-index: 0;
}

.profile-avatar {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  overflow: hidden;
  border: 5px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
  margin-right: 40px;
  flex-shrink: 0;
  transition: transform 0.3s;
  position: relative;
  z-index: 1;
}

.profile-avatar:hover {
  transform: scale(1.05);
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-info {
  flex-grow: 1;
  position: relative;
  z-index: 1;
}

.username {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.user-email {
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 25px;
}

.user-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 25px;
  margin-bottom: 25px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.stat-item {
  text-align: center;
  min-width: 70px;
  position: relative;
}

.stat-item:not(:last-child)::after {
  content: '';
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  height: 70%;
  width: 1px;
  background: rgba(255, 255, 255, 0.3);
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  display: block;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.stat-label {
  font-size: 16px;
  opacity: 0.9;
  margin-top: 5px;
}

.user-level {
  display: inline-block;
  background-color: rgba(255, 255, 255, 0.25);
  padding: 8px 16px;
  border-radius: 25px;
  font-size: 16px;
  margin-top: 15px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  font-weight: 500;
}

.user-actions {
  position: absolute;
  top: 40px;
  right: 40px;
  z-index: 1;
}

.edit-profile-btn {
  background-color: rgba(255, 255, 255, 0.25);
  color: var(--white);
  border: none;
  padding: 10px 20px;
  border-radius: 25px;
  font-size: 16px;
  display: flex;
  align-items: center;
  transition: all 0.3s;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  font-weight: 500;
}

.edit-profile-btn:hover {
  background-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
}

.edit-profile-btn i {
  margin-right: 8px;
  font-size: 18px;
}

/* 탭 메뉴 */
.tab-menu {
  display: flex;
  border-bottom: 1px solid #e2e8f0;
  background-color: #fff;
  position: sticky;
  top: 70px; /* 네비게이션 바 높이에 맞춤 */
  z-index: 10;
  margin-bottom: 0;
  padding: 0;
  width: 100%;
}

.tab-item {
  padding: 15px 0;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4a5568;
  border: none;
  background: none;
  flex: 1;
  text-align: center;
}

.tab-item i {
  margin-right: 8px;
  font-size: 16px;
}

.tab-item:hover {
  color: #4299e1;
}

.tab-item.active {
  color: white;
  background-color: #4299e1;
  font-weight: 600;
}

.tab-item.active::after {
  display: none;
}

/* 탭 컨텐츠 */
.tab-content {
  padding: 40px;
  min-height: 300px;
  animation: fadeIn 0.5s ease-out;
  background-color: #fff;
}

/* 기본 정보 탭 */
.info-section {
  max-width: 700px;
}

.info-section h3 {
  font-size: 24px;
  margin-bottom: 25px;
  color: #333;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 15px;
  font-weight: 700;
}

.info-row {
  display: flex;
  margin-bottom: 20px;
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
  transition: all 0.3s;
  border-radius: 8px;
}

.info-label {
  width: 140px;
  font-weight: 600;
  color: #555;
  flex-shrink: 0;
}

.info-value {
  flex-grow: 1;
  color: #333;
}

.bio-text {
  white-space: pre-line;
  line-height: 1.7;
}

/* 프로필 수정 폼 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px var(--primary-light);
  outline: none;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 30px;
}

.cancel-btn {
  padding: 12px 24px;
  background-color: #f5f5f5;
  color: #333;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.save-btn {
  padding: 12px 24px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.save-btn:hover:not(:disabled) {
  background-color: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 이미지 업로드 */
.image-upload-container {
  margin-top: 10px;
}

.image-upload-container .upload-label {
  display: inline-block;
  padding: 12px 20px;
  background-color: var(--primary-color);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
}

.image-upload-container .upload-label:hover {
  background-color: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.image-hint {
  margin-top: 8px;
  color: #666;
  font-size: 14px;
}

.selected-image {
  margin-top: 15px;
  padding: 12px;
  background-color: var(--primary-light);
  border-radius: 8px;
  display: flex;
  align-items: center;
}

.selected-image p {
  margin: 0;
  color: #333;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 30px 20px;
  }
  
  .profile-avatar {
    margin-right: 0;
    margin-bottom: 25px;
  }
  
  .user-stats {
    justify-content: center;
  }
  
  .user-actions {
    position: static;
    margin-top: 25px;
    display: flex;
    justify-content: center;
  }
  
  .tab-menu {
    overflow-x: auto;
  }
  
  .tab-content {
    padding: 25px 15px;
  }
  
  .info-row {
    flex-direction: column;
  }
  
  .info-label {
    width: 100%;
    margin-bottom: 8px;
  }
  
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .cancel-btn, .save-btn {
    width: 100%;
  }
}

/* 프로필 수정 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s;
  backdrop-filter: blur(5px);
}

.modal-content {
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 30px;
  animation: scaleIn 0.3s;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

@keyframes scaleIn {
  from { transform: scale(0.9); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@keyframes slideIn {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}

.modal-content h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 15px;
  font-weight: 700;
  text-align: center;
}

.edit-profile-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 소속 팀 탭 */
.teams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
  margin-top: 20px;
}

.team-card {
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #eee;
}

.team-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-light);
}

.team-logo {
  height: 180px;
  overflow: hidden;
  background-color: #f8f8f8;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #eee;
}

.team-logo img {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
  transition: transform 0.3s;
}

.team-card:hover .team-logo img {
  transform: scale(1.05);
}

.team-info {
  padding: 20px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

.team-name {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 12px;
  color: #333;
  line-height: 1.3;
}

.team-level, .team-region {
  font-size: 15px;
  color: #666;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.team-level::before {
  content: '\f005';
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
  margin-right: 10px;
  font-size: 14px;
  color: #ffc107;
}

.team-region::before {
  content: '\f3c5';
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
  margin-right: 10px;
  font-size: 14px;
  color: #e91e63;
}

.team-card .view-details {
  margin-top: auto;
  padding: 12px 0;
  text-align: center;
  background-color: var(--primary-light);
  color: var(--primary-color);
  font-weight: 600;
  transition: all 0.3s;
  font-size: 15px;
}

.team-card:hover .view-details {
  background-color: var(--primary-color);
  color: white;
}

/* 참여 경기 탭 */
.matches-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.match-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  position: relative;
  overflow: hidden;
}

.match-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background-color: var(--primary-color);
  opacity: 0;
  transition: opacity 0.3s;
}

.match-item:hover::before {
  opacity: 1;
}

.match-item:hover {
  transform: translateX(5px);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
}

.match-date {
  width: 120px;
  font-size: 14px;
  color: #666;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.match-date::before {
  content: '\f133';
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
  margin-right: 5px;
  color: var(--primary-color);
}

.match-title {
  flex-grow: 1;
  font-weight: 500;
  margin: 0 15px;
}

.match-venue {
  width: 150px;
  font-size: 14px;
  color: #666;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.match-venue::before {
  content: '\f3c5';
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
  margin-right: 5px;
  color: #e91e63;
}

.match-status {
  width: 100px;
  text-align: center;
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  flex-shrink: 0;
}

.status-open {
  background-color: #e3f2fd;
  color: #1976d2;
}

.status-closed {
  background-color: #ffebee;
  color: #d32f2f;
}

.status-completed {
  background-color: #e8f5e9;
  color: #388e3c;
}

.status-canceled {
  background-color: #f5f5f5;
  color: #757575;
}

/* 빈 메시지 */
.empty-message {
  text-align: center;
  padding: 40px 0;
  color: #999;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.empty-message::before {
  content: '\f119';
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
  font-size: 48px;
  display: block;
  margin-bottom: 20px;
  color: #999;
}

@media (max-width: 768px) {
  .match-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .match-date, .match-venue, .match-status {
    width: 100%;
    margin-top: 5px;
  }
  
  .match-title {
    margin: 5px 0;
  }
  
  .modal-content {
    padding: 20px;
    width: 95%;
  }
  
  .stat-item:not(:last-child)::after {
    display: none;
  }
}

@media (max-width: 480px) {
  .profile-avatar {
    width: 100px;
    height: 100px;
  }
  
  .username {
    font-size: 24px;
  }
  
  .user-email {
    font-size: 14px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .stat-label {
    font-size: 12px;
  }
  
  .tab-item {
    padding: 12px 15px;
    font-size: 14px;
  }
  
  .tab-item i {
    font-size: 16px;
  }
}

/* 친구 관련 버튼 스타일 */
.friend-request-btn,
.request-sent-btn,
.accept-request-btn,
.reject-request-btn,
.remove-friend-btn {
  padding: 8px 15px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.3s;
  border: none;
}

.friend-request-btn {
  background-color: #4a90e2;
  color: white;
}

.friend-request-btn:hover {
  background-color: #3a7bc8;
}

.request-sent-btn {
  background-color: #e0e0e0;
  color: #666;
  cursor: not-allowed;
}

.friend-request-actions {
  display: flex;
  gap: 10px;
}

.accept-request-btn {
  background-color: #2ecc71;
  color: white;
}

.accept-request-btn:hover {
  background-color: #27ae60;
}

.reject-request-btn {
  background-color: #e74c3c;
  color: white;
}

.reject-request-btn:hover {
  background-color: #c0392b;
}

.remove-friend-btn {
  background-color: #f5f5f5;
  color: #e74c3c;
  border: 1px solid #e74c3c;
}

.remove-friend-btn:hover {
  background-color: #ffebee;
}
</style> 