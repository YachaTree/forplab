<template>
  <div class="team-create-container">
    <h1 class="page-title">새 팀 만들기</h1>
    
    <div class="form-container">
      <form @submit.prevent="submitForm">
        <!-- 팀 기본 정보 -->
        <div class="form-section">
          <h2 class="section-title">기본 정보</h2>
          
          <div class="form-group">
            <label for="name">팀 이름 <span class="required">*</span></label>
            <input 
              type="text" 
              id="name" 
              v-model="form.name" 
              placeholder="팀 이름을 입력하세요"
              required
            >
            <div v-if="errors.name" class="error-message">{{ errors.name }}</div>
          </div>
          
          <div class="form-group">
            <label for="region">활동 지역 <span class="required">*</span></label>
            <select 
              id="region" 
              v-model="form.region" 
              required
            >
              <option value="">지역 선택</option>
              <option value="seoul">서울</option>
              <option value="gyeonggi">경기</option>
              <option value="incheon">인천</option>
              <option value="other">기타</option>
            </select>
            <div v-if="errors.region" class="error-message">{{ errors.region }}</div>
          </div>
          
          <div class="form-group">
            <label for="level">팀 레벨 <span class="required">*</span></label>
            <select 
              id="level" 
              v-model="form.level" 
              required
            >
              <option value="">레벨 선택</option>
              <option value="beginner">입문</option>
              <option value="intermediate">중급</option>
              <option value="advanced">고급</option>
            </select>
            <div v-if="errors.level" class="error-message">{{ errors.level }}</div>
          </div>
          
          <div class="form-group">
            <label for="description">팀 소개</label>
            <textarea 
              id="description" 
              v-model="form.description" 
              placeholder="팀 소개를 입력하세요"
              rows="4"
            ></textarea>
            <div v-if="errors.description" class="error-message">{{ errors.description }}</div>
          </div>
        </div>
        
        <!-- 팀 로고 -->
        <div class="form-section">
          <h2 class="section-title">팀 로고</h2>
          
          <div class="logo-upload">
            <div class="logo-preview" v-if="logoPreview">
              <img :src="logoPreview" alt="Team Logo Preview" />
            </div>
            <div class="logo-placeholder" v-else>
              <i class="fas fa-image"></i>
              <span>로고 이미지 없음</span>
            </div>
            
            <div class="upload-actions">
              <label for="logo" class="upload-btn">
                <i class="fas fa-upload"></i>
                로고 업로드
              </label>
              <input 
                type="file" 
                id="logo" 
                @change="handleLogoUpload" 
                accept="image/*"
                style="display: none;"
              >
              
              <button 
                type="button" 
                class="remove-btn" 
                @click="removeLogo" 
                v-if="logoPreview"
              >
                <i class="fas fa-trash"></i>
                삭제
              </button>
            </div>
            
            <div v-if="errors.logo" class="error-message">{{ errors.logo }}</div>
          </div>
        </div>
        
        <!-- 팀 설정 -->
        <div class="form-section">
          <h2 class="section-title">팀 설정</h2>
          
          <div class="form-group checkbox-group">
            <input 
              type="checkbox" 
              id="is_recruiting" 
              v-model="form.is_recruiting"
            >
            <label for="is_recruiting">팀원 모집 활성화</label>
          </div>
          
          <div class="form-group checkbox-group">
            <input 
              type="checkbox" 
              id="is_private" 
              v-model="form.is_private"
            >
            <label for="is_private">비공개 팀 (초대로만 가입 가능)</label>
          </div>
        </div>
        
        <!-- 제출 버튼 -->
        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="goBack">취소</button>
          <button 
            type="submit" 
            class="submit-btn" 
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? '생성 중...' : '팀 생성하기' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'TeamCreate',
  
  data() {
    return {
      form: {
        name: '',
        region: '',
        level: '',
        description: '',
        logo: null,
        is_recruiting: true,
        is_private: false
      },
      logoPreview: null,
      errors: {},
      isSubmitting: false
    };
  },
  
  computed: {
    ...mapGetters(['isAuthenticated'])
  },
  
  created() {
    // 로그인 상태 확인
    if (!this.isAuthenticated) {
      this.$router.push({ name: 'Login', query: { redirect: this.$route.fullPath } });
    }
  },
  
  methods: {
    handleLogoUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // 파일 크기 제한 (5MB)
      if (file.size > 5 * 1024 * 1024) {
        this.errors.logo = '로고 이미지는 5MB 이하여야 합니다.';
        return;
      }
      
      // 이미지 파일 타입 확인
      if (!file.type.match('image.*')) {
        this.errors.logo = '이미지 파일만 업로드 가능합니다.';
        return;
      }
      
      this.form.logo = file;
      this.errors.logo = null;
      
      // 이미지 미리보기 생성
      const reader = new FileReader();
      reader.onload = e => {
        this.logoPreview = e.target.result;
      };
      reader.readAsDataURL(file);
    },
    
    removeLogo() {
      this.form.logo = null;
      this.logoPreview = null;
    },
    
    validateForm() {
      this.errors = {};
      let isValid = true;
      
      if (!this.form.name.trim()) {
        this.errors.name = '팀 이름을 입력해주세요.';
        isValid = false;
      }
      
      if (!this.form.region) {
        this.errors.region = '활동 지역을 선택해주세요.';
        isValid = false;
      }
      
      if (!this.form.level) {
        this.errors.level = '팀 레벨을 선택해주세요.';
        isValid = false;
      }
      
      return isValid;
    },
    
    async submitForm() {
      if (!this.validateForm()) return;
      
      this.isSubmitting = true;
      
      try {
        // FormData 객체 생성 (파일 업로드를 위해)
        const formData = new FormData();
        formData.append('name', this.form.name);
        formData.append('level', this.form.level);
        formData.append('region', this.form.region);
        formData.append('is_recruiting', this.form.is_recruiting);
        
        if (this.form.description) {
          formData.append('description', this.form.description);
        }
        
        if (this.form.logo) {
          formData.append('logo', this.form.logo);
        }
        
        // 팀 생성 API 호출
        const response = await this.$store.dispatch('createTeam', formData);
        
        // 성공 메시지 표시
        alert('팀이 성공적으로 생성되었습니다.');
        
        // 응답 데이터 확인
        console.log('팀 생성 응답:', response);
        
        // 생성된 팀 ID 확인
        if (response && response.data && response.data.id) {
          // 생성된 팀 상세 페이지로 이동
          this.$router.push({ name: 'TeamDetail', params: { id: response.data.id } });
        } else {
          // ID가 없으면 팀 목록 페이지로 이동
          this.$router.push({ name: 'TeamList' });
        }
      } catch (error) {
        console.error('팀 생성 실패:', error);
        
        // 서버 응답 에러 처리
        if (error && error.response && error.response.data) {
          const serverErrors = error.response.data;
          console.log('서버 오류 응답:', serverErrors);
          
          // 필드별 에러 메시지 설정
          for (const field in serverErrors) {
            if (Object.prototype.hasOwnProperty.call(serverErrors, field)) {
              this.errors[field] = Array.isArray(serverErrors[field])
                ? serverErrors[field][0]
                : serverErrors[field];
            }
          }
        } else {
          // 일반 에러 메시지
          alert('팀 생성에 실패했습니다. 다시 시도해주세요.');
        }
      } finally {
        this.isSubmitting = false;
      }
    },
    
    goBack() {
      this.$router.go(-1);
    }
  }
};
</script>

<style scoped>
.team-create-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  font-size: 28px;
  margin-bottom: 20px;
  color: #333;
}

.form-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.form-section {
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.section-title {
  font-size: 20px;
  margin: 0 0 20px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.required {
  color: #f44336;
}

.form-group input[type="text"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.form-group textarea {
  resize: vertical;
}

.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-group input[type="checkbox"] {
  margin-right: 10px;
}

.error-message {
  color: #f44336;
  font-size: 14px;
  margin-top: 5px;
}

.logo-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.logo-preview,
.logo-placeholder {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
  border: 2px dashed #ddd;
}

.logo-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.logo-placeholder {
  flex-direction: column;
  color: #999;
}

.logo-placeholder i {
  font-size: 40px;
  margin-bottom: 10px;
}

.upload-actions {
  display: flex;
  gap: 10px;
}

.upload-btn,
.remove-btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
}

.upload-btn {
  background-color: #2196f3;
  color: white;
  border: none;
}

.remove-btn {
  background-color: #f44336;
  color: white;
  border: none;
}

.form-actions {
  padding: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cancel-btn,
.submit-btn {
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  font-size: 16px;
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

@media (max-width: 768px) {
  .form-section {
    padding: 15px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .cancel-btn,
  .submit-btn {
    width: 100%;
  }
}
</style> 