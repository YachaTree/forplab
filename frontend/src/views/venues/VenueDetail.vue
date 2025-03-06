<template>
  <div class="venue-detail-container">
    <!-- 로딩 및 에러 메시지 -->
    <div v-if="loading" class="loading-message">
      <p>구장 정보를 불러오는 중...</p>
    </div>
    
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchVenue">다시 시도</button>
    </div>
    
    <div v-if="!loading && !error && venue" class="venue-content">
      <!-- 상단 헤더 -->
      <div class="venue-header">
        <div class="venue-images">
          <div class="main-image">
            <img :src="venue.image || '/img/default-venue.jpg'" alt="Venue" />
          </div>
          <div v-if="venue.images && venue.images.length > 0" class="image-thumbnails">
            <div 
              v-for="image in venue.images" 
              :key="image.id" 
              class="thumbnail"
              @click="openImageGallery(image.id)"
            >
              <img :src="image.image" alt="Venue" />
            </div>
          </div>
        </div>
        
        <div class="venue-info-header">
          <h1 class="venue-name">{{ venue.name }}</h1>
          
          <div class="venue-rating">
            <div class="rating-stars">
              <i 
                v-for="n in 5" 
                :key="n" 
                :class="['fas', n <= Math.round(venue.average_rating || 0) ? 'fa-star' : 'fa-star-o']"
              ></i>
            </div>
            <span class="rating-value">{{ venue.average_rating ? venue.average_rating.toFixed(1) : 'N/A' }}</span>
            <span class="review-count">({{ venue.reviews ? venue.reviews.length : 0 }}개 리뷰)</span>
          </div>
          
          <div class="venue-address">
            <i class="fas fa-map-marker-alt"></i>
            <span>{{ venue.address }}</span>
          </div>
          
          <div class="venue-contact" v-if="venue.phone">
            <i class="fas fa-phone"></i>
            <span>{{ venue.phone }}</span>
          </div>
        </div>
      </div>
      
      <!-- 구장 정보 -->
      <div class="venue-details-section">
        <h2 class="section-title">구장 정보</h2>
        
        <div class="details-grid">
          <div class="detail-item">
            <div class="detail-label">구장 유형</div>
            <div class="detail-value">{{ getSurfaceTypeText(venue.surface_type) }}</div>
          </div>
          
          <div class="detail-item">
            <div class="detail-label">크기</div>
            <div class="detail-value">{{ venue.size }}</div>
          </div>
          
          <div class="detail-item">
            <div class="detail-label">주차 시설</div>
            <div class="detail-value">{{ venue.has_parking ? '있음' : '없음' }}</div>
          </div>
          
          <div class="detail-item">
            <div class="detail-label">샤워 시설</div>
            <div class="detail-value">{{ venue.has_shower ? '있음' : '없음' }}</div>
          </div>
          
          <div class="detail-item">
            <div class="detail-label">탈의실</div>
            <div class="detail-value">{{ venue.has_locker_room ? '있음' : '없음' }}</div>
          </div>
          
          <div class="detail-item">
            <div class="detail-label">조명</div>
            <div class="detail-value">{{ venue.has_lights ? '있음' : '없음' }}</div>
          </div>
        </div>
      </div>
      
      <!-- 구장 설명 -->
      <div v-if="venue.description" class="venue-description-section">
        <h2 class="section-title">구장 설명</h2>
        <div class="venue-description">
          <p>{{ venue.description }}</p>
        </div>
      </div>
      
      <!-- 구장 위치 -->
      <div class="venue-location-section">
        <h2 class="section-title">위치</h2>
        <div class="venue-map">
          <!-- 지도 컴포넌트 또는 임베드 -->
          <div class="map-placeholder">
            <p>지도 표시 영역</p>
            <p>위도: {{ venue.latitude }}, 경도: {{ venue.longitude }}</p>
          </div>
        </div>
      </div>
      
      <!-- 리뷰 섹션 -->
      <div class="venue-reviews-section">
        <div class="reviews-header">
          <h2 class="section-title">리뷰</h2>
          <button 
            v-if="isAuthenticated" 
            class="write-review-btn"
            @click="showReviewForm = true"
          >
            리뷰 작성
          </button>
        </div>
        
        <!-- 리뷰 작성 폼 -->
        <div v-if="showReviewForm" class="review-form">
          <h3>리뷰 작성</h3>
          <div class="rating-input">
            <span>평점:</span>
            <div class="rating-stars-input">
              <i 
                v-for="n in 5" 
                :key="n" 
                :class="['fas', n <= reviewForm.rating ? 'fa-star' : 'fa-star-o']"
                @click="reviewForm.rating = n"
              ></i>
            </div>
          </div>
          <div class="comment-input">
            <textarea 
              v-model="reviewForm.comment" 
              placeholder="리뷰 내용을 입력하세요"
              rows="4"
            ></textarea>
          </div>
          <div class="form-actions">
            <button class="cancel-btn" @click="cancelReview">취소</button>
            <button 
              class="submit-btn" 
              @click="submitReview"
              :disabled="reviewSubmitting || !reviewForm.rating || !reviewForm.comment"
            >
              {{ reviewSubmitting ? '제출 중...' : '리뷰 등록' }}
            </button>
          </div>
        </div>
        
        <!-- 리뷰 목록 -->
        <div v-if="venue.reviews && venue.reviews.length > 0" class="reviews-list">
          <div v-for="review in venue.reviews" :key="review.id" class="review-card">
            <div class="review-header">
              <div class="reviewer-info">
                <img :src="review.user.profile_image || '/img/default-avatar.png'" alt="User" class="reviewer-avatar" />
                <span class="reviewer-name">{{ review.user.username }}</span>
              </div>
              <div class="review-rating">
                <div class="rating-stars">
                  <i 
                    v-for="n in 5" 
                    :key="n" 
                    :class="['fas', n <= review.rating ? 'fa-star' : 'fa-star-o']"
                  ></i>
                </div>
                <span class="review-date">{{ formatDate(review.created_at) }}</span>
              </div>
            </div>
            <div class="review-content">
              <p>{{ review.comment }}</p>
            </div>
          </div>
        </div>
        
        <div v-else class="no-reviews">
          <p>아직 리뷰가 없습니다. 첫 리뷰를 작성해보세요!</p>
        </div>
      </div>
      
      <!-- 관련 매치 -->
      <div v-if="relatedMatches && relatedMatches.length > 0" class="related-matches-section">
        <h2 class="section-title">이 구장의 예정된 매치</h2>
        <div class="related-matches">
          <div v-for="match in relatedMatches" :key="match.id" class="match-card" @click="goToMatchDetail(match.id)">
            <div class="match-header">
              <span class="match-date">{{ formatDate(match.date) }} {{ match.start_time }}</span>
              <span :class="['match-status', `status-${match.status}`]">{{ getStatusText(match.status) }}</span>
            </div>
            
            <h3 class="match-title">{{ match.title }}</h3>
            
            <div class="match-info">
              <div class="info-item">
                <i class="fas fa-users"></i>
                <span>{{ match.current_players_count }}/{{ match.max_players }}</span>
              </div>
              
              <div class="info-item">
                <i class="fas fa-trophy"></i>
                <span>{{ getSkillLevelText(match.skill_level) }}</span>
              </div>
              
              <div class="info-item">
                <i class="fas fa-venus-mars"></i>
                <span>{{ getGenderText(match.gender) }}</span>
              </div>
            </div>
            
            <div class="match-price">
              <span>{{ formatPrice(match.price) }}원</span>
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
  name: 'VenueDetail',
  
  data() {
    return {
      relatedMatches: [],
      showReviewForm: false,
      reviewForm: {
        rating: 0,
        comment: ''
      },
      reviewSubmitting: false
    };
  },
  
  computed: {
    ...mapState({
      venue: state => state.currentVenue,
      loading: state => state.venueLoading,
      error: state => state.venueError
    }),
    
    ...mapGetters(['isAuthenticated'])
  },
  
  created() {
    this.fetchVenue();
    this.fetchRelatedMatches();
  },
  
  methods: {
    ...mapActions(['fetchVenue']),
    
    async fetchVenue() {
      try {
        await this.$store.dispatch('fetchVenue', this.$route.params.id);
      } catch (error) {
        console.error('구장 상세 조회 실패:', error);
      }
    },
    
    async fetchRelatedMatches() {
      try {
        // 이 구장에서 열리는 매치 조회
        const response = await this.$store.dispatch('fetchMatches', {
          venue: this.$route.params.id,
          status: 'open'
        });
        
        if (response && response.data && response.data.results) {
          this.relatedMatches = response.data.results.slice(0, 3); // 최대 3개만 표시
        }
      } catch (error) {
        console.error('관련 매치 조회 실패:', error);
      }
    },
    
    async submitReview() {
      if (!this.reviewForm.rating || !this.reviewForm.comment) return;
      
      this.reviewSubmitting = true;
      
      try {
        await this.$store.dispatch('createVenueReview', {
          venueId: this.$route.params.id,
          reviewData: {
            rating: this.reviewForm.rating,
            comment: this.reviewForm.comment
          }
        });
        
        // 리뷰 등록 성공 후 구장 정보 다시 조회
        await this.fetchVenue();
        
        this.showReviewForm = false;
        this.reviewForm = {
          rating: 0,
          comment: ''
        };
        
        this.$toast.success('리뷰가 성공적으로 등록되었습니다.');
      } catch (error) {
        console.error('리뷰 등록 실패:', error);
        this.$toast.error('리뷰 등록에 실패했습니다. 다시 시도해주세요.');
      } finally {
        this.reviewSubmitting = false;
      }
    },
    
    cancelReview() {
      this.showReviewForm = false;
      this.reviewForm = {
        rating: 0,
        comment: ''
      };
    },
    
    openImageGallery(imageId) {
      // 이미지 갤러리 열기 로직
      console.log('Open image gallery with image ID:', imageId);
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
    
    formatPrice(price) {
      return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },
    
    getSurfaceTypeText(surfaceType) {
      const surfaceTypeMap = {
        'grass': '천연잔디',
        'artificial': '인조잔디',
        'futsal': '풋살장'
      };
      
      return surfaceTypeMap[surfaceType] || surfaceType;
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
    }
  }
};
</script>

<style scoped>
.venue-detail-container {
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

.venue-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.venue-header {
  display: flex;
  flex-direction: column;
}

.venue-images {
  width: 100%;
}

.main-image {
  width: 100%;
  height: 300px;
  overflow: hidden;
}

.main-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-thumbnails {
  display: flex;
  gap: 10px;
  padding: 10px;
  background-color: #f5f5f5;
  overflow-x: auto;
}

.thumbnail {
  width: 80px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.venue-info-header {
  padding: 20px;
}

.venue-name {
  font-size: 24px;
  margin: 0 0 15px;
  color: #333;
}

.venue-rating {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.rating-stars {
  display: flex;
  margin-right: 10px;
}

.rating-stars i {
  color: #ffc107;
  margin-right: 2px;
}

.rating-value {
  font-weight: 600;
  margin-right: 5px;
}

.review-count {
  color: #666;
  font-size: 14px;
}

.venue-address,
.venue-contact {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
  color: #555;
  font-size: 14px;
}

.venue-address i,
.venue-contact i {
  margin-right: 10px;
  margin-top: 3px;
  color: #777;
  width: 16px;
  text-align: center;
}

.section-title {
  font-size: 20px;
  margin: 0 0 15px;
  color: #333;
}

.venue-details-section,
.venue-description-section,
.venue-location-section,
.venue-reviews-section,
.related-matches-section {
  padding: 20px;
  border-top: 1px solid #eee;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.detail-item {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.detail-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.detail-value {
  font-weight: 600;
  color: #333;
}

.venue-description {
  line-height: 1.6;
  color: #555;
}

.venue-map {
  height: 300px;
  background-color: #f5f5f5;
  border-radius: 8px;
  overflow: hidden;
}

.map-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #666;
}

.reviews-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.write-review-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.write-review-btn:hover {
  background-color: #388e3c;
}

.review-form {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.review-form h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
  color: #333;
}

.rating-input {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.rating-input span {
  margin-right: 10px;
}

.rating-stars-input {
  display: flex;
}

.rating-stars-input i {
  font-size: 20px;
  color: #ddd;
  cursor: pointer;
  margin-right: 5px;
}

.rating-stars-input i.fa-star {
  color: #ffc107;
}

.comment-input textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
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

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.review-card {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.review-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.reviewer-info {
  display: flex;
  align-items: center;
}

.reviewer-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-right: 10px;
  object-fit: cover;
}

.reviewer-name {
  font-weight: 500;
  color: #333;
}

.review-rating {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.review-date {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
}

.review-content {
  color: #555;
  line-height: 1.5;
}

.no-reviews {
  text-align: center;
  padding: 30px;
  color: #666;
}

.related-matches {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.match-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 15px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.match-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.match-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.match-date {
  font-size: 14px;
  color: #666;
}

.match-status {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 12px;
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

.match-title {
  font-size: 16px;
  margin: 10px 0;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.match-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #666;
}

.info-item i {
  margin-right: 5px;
  width: 16px;
  text-align: center;
}

.match-price {
  font-weight: 600;
  color: #2c3e50;
  font-size: 16px;
  text-align: right;
}

@media (min-width: 768px) {
  .venue-header {
    flex-direction: row;
  }
  
  .venue-images {
    width: 60%;
  }
  
  .venue-info-header {
    width: 40%;
  }
}

@media (max-width: 768px) {
  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .related-matches {
    grid-template-columns: 1fr;
  }
}
</style> 