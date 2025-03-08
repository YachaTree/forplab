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
              <input type="file" id="profile_image" @change="handleImageUpload" accept="image/jpeg,image/jpg,image/png,image/gif">
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
      imageKey: 0 // 이미지 강제 갱신을 위한 키
    };
  },
  
  computed: {
    ...mapState({
      user: state => state.auth.user,
      loading: state => state.auth.loading,
      error: state => state.auth.error
    }),
    
    isCurrentUser() {
      // /profile 경로인 경우 항상 현재 사용자로 간주
      if (this.$route.path === '/profile') {
        return true;
      }
      
      // 사용자 ID로 비교
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
    console.log('현재 사용자 정보:', this.user);
    
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
      updateProfile: 'auth/updateProfile'
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
    }
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
  padding: 30px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: var(--white);
  position: relative;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  margin-right: 30px;
  flex-shrink: 0;
  transition: transform 0.3s;
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
}

.username {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.user-email {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 20px;
}

.user-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  min-width: 60px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  display: block;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.user-level {
  display: inline-block;
  background-color: rgba(255, 255, 255, 0.2);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  margin-top: 10px;
}

.user-actions {
  position: absolute;
  top: 30px;
  right: 30px;
}

.edit-profile-btn {
  background-color: rgba(255, 255, 255, 0.2);
  color: var(--white);
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  display: flex;
  align-items: center;
  transition: background-color 0.3s;
}

.edit-profile-btn:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.edit-profile-btn i {
  margin-right: 6px;
}

/* 탭 메뉴 */
.tab-menu {
  display: flex;
  border-bottom: 1px solid var(--border-color);
}

.tab-item {
  padding: 15px 20px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  position: relative;
  transition: color 0.3s;
  display: flex;
  align-items: center;
}

.tab-item i {
  margin-right: 8px;
  font-size: 18px;
}

.tab-item:hover {
  color: var(--primary-color);
}

.tab-item.active {
  color: var(--primary-color);
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 100%;
  height: 3px;
  background-color: var(--primary-color);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}

/* 탭 컨텐츠 */
.tab-content {
  padding: 30px;
  min-height: 300px;
}

/* 기본 정보 탭 */
.info-section {
  max-width: 600px;
}

.info-section h3 {
  font-size: 20px;
  margin-bottom: 20px;
  color: var(--text-color);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
}

.info-row {
  display: flex;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color);
}

.info-label {
  width: 120px;
  font-weight: 500;
  color: var(--text-light);
  flex-shrink: 0;
}

.info-value {
  flex-grow: 1;
}

.bio-text {
  white-space: pre-line;
  line-height: 1.6;
}

/* 소속 팀 탭 */
.teams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.team-card {
  background-color: var(--white);
  border-radius: var(--border-radius);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.team-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.team-logo {
  height: 140px;
  overflow: hidden;
  background-color: #f5f5f5;
}

.team-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.team-info {
  padding: 15px;
}

.team-name {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 5px;
}

.team-level, .team-region {
  font-size: 14px;
  color: var(--text-light);
  margin-bottom: 5px;
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
  background-color: var(--white);
  border-radius: var(--border-radius);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.match-item:hover {
  transform: translateX(5px);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
}

.match-date {
  width: 120px;
  font-size: 14px;
  color: var(--text-light);
  flex-shrink: 0;
}

.match-title {
  flex-grow: 1;
  font-weight: 500;
  margin: 0 15px;
}

.match-venue {
  width: 150px;
  font-size: 14px;
  color: var(--text-light);
  flex-shrink: 0;
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
  color: var(--text-lighter);
}

/* 프로필 수정 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s;
}

.modal-content {
  background-color: var(--white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 30px;
  animation: scaleIn 0.3s;
}

@keyframes scaleIn {
  from { transform: scale(0.9); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.modal-content h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: var(--text-color);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
}

.edit-profile-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 5px;
  color: var(--text-light);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: var(--primary-color);
  outline: none;
}

.readonly-input {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.image-upload-container {
  margin-top: 5px;
}

.image-hint {
  font-size: 12px;
  color: var(--text-lighter);
  margin-top: 5px;
}

.selected-image {
  margin-top: 10px;
  padding: 10px;
  background-color: var(--primary-light);
  border-radius: var(--border-radius);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-btn {
  padding: 10px 20px;
  background-color: #f5f5f5;
  color: var(--text-color);
  border: none;
  border-radius: var(--border-radius);
  font-size: 16px;
  transition: background-color 0.3s;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.save-btn {
  padding: 10px 20px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  font-size: 16px;
  transition: background-color 0.3s;
}

.save-btn:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.save-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 20px;
  }
  
  .profile-avatar {
    margin-right: 0;
    margin-bottom: 20px;
  }
  
  .user-stats {
    justify-content: center;
  }
  
  .user-actions {
    position: static;
    margin-top: 20px;
    display: flex;
    justify-content: center;
  }
  
  .tab-menu {
    overflow-x: auto;
    white-space: nowrap;
    -webkit-overflow-scrolling: touch;
  }
  
  .tab-content {
    padding: 20px;
  }
  
  .info-row {
    flex-direction: column;
  }
  
  .info-label {
    width: 100%;
    margin-bottom: 5px;
  }
  
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
</style> 