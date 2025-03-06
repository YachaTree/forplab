<template>
  <div class="venue-list-container">
    <h1 class="page-title">구장 목록</h1>
    
    <!-- 필터 섹션 -->
    <div class="filters-container">
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
        <label>구장 유형</label>
        <select v-model="filters.surface_type" @change="applyFilters">
          <option value="">전체</option>
          <option value="grass">천연잔디</option>
          <option value="artificial">인조잔디</option>
          <option value="futsal">풋살장</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>검색</label>
        <input 
          type="text" 
          v-model="filters.search" 
          @input="debounceSearch"
          placeholder="구장 이름 검색"
        >
      </div>
      
      <button class="reset-button" @click="resetFilters">필터 초기화</button>
    </div>
    
    <!-- 로딩 및 에러 메시지 -->
    <div v-if="loading" class="loading-message">
      <p>구장 목록을 불러오는 중...</p>
    </div>
    
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchVenues">다시 시도</button>
    </div>
    
    <!-- 구장 목록 -->
    <div v-if="!loading && !error && venues.length === 0" class="empty-message">
      <p>조건에 맞는 구장이 없습니다.</p>
    </div>
    
    <div v-if="!loading && !error && venues.length > 0" class="venues-grid">
      <div v-for="venue in venues" :key="venue.id" class="venue-card" @click="goToVenueDetail(venue.id)">
        <div class="venue-image">
          <img :src="venue.image || '/img/default-venue.jpg'" alt="Venue" />
          <div class="venue-rating">
            <i class="fas fa-star"></i>
            <span>{{ venue.average_rating ? venue.average_rating.toFixed(1) : 'N/A' }}</span>
          </div>
        </div>
        
        <div class="venue-content">
          <h3 class="venue-name">{{ venue.name }}</h3>
          
          <div class="venue-address">
            <i class="fas fa-map-marker-alt"></i>
            <span>{{ venue.address }}</span>
          </div>
          
          <div class="venue-info">
            <div class="info-item">
              <i class="fas fa-futbol"></i>
              <span>{{ getSurfaceTypeText(venue.surface_type) }}</span>
            </div>
            
            <div class="info-item">
              <i class="fas fa-ruler-combined"></i>
              <span>{{ venue.size }}</span>
            </div>
            
            <div class="info-item">
              <i class="fas fa-comment"></i>
              <span>리뷰 {{ venue.review_count }}개</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 페이지네이션 -->
    <div v-if="!loading && !error && venues.length > 0" class="pagination">
      <button :disabled="page === 1" @click="prevPage">이전</button>
      <span>{{ page }} / {{ totalPages }}</span>
      <button :disabled="page === totalPages" @click="nextPage">다음</button>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import _ from 'lodash';

export default {
  name: 'VenueList',
  
  data() {
    return {
      filters: {
        region: '',
        surface_type: '',
        search: '',
        page: 1
      },
      page: 1,
      pageSize: 10,
      totalPages: 1
    };
  },
  
  computed: {
    ...mapState({
      venues: state => state.venues,
      loading: state => state.venuesLoading,
      error: state => state.venuesError
    })
  },
  
  created() {
    this.fetchVenues();
    this.debounceSearch = _.debounce(this.applyFilters, 500);
  },
  
  methods: {
    ...mapActions(['fetchVenues']),
    
    async fetchVenues() {
      try {
        const params = {
          ...this.filters,
          page: this.page,
          page_size: this.pageSize
        };
        
        const response = await this.$store.dispatch('fetchVenues', params);
        
        // 페이지네이션 정보 업데이트 (백엔드에서 제공하는 경우)
        if (response && response.data && response.data.count) {
          this.totalPages = Math.ceil(response.data.count / this.pageSize);
        }
      } catch (error) {
        console.error('구장 목록 조회 실패:', error);
      }
    },
    
    applyFilters() {
      this.page = 1; // 필터 적용 시 첫 페이지로 이동
      this.fetchVenues();
    },
    
    resetFilters() {
      this.filters = {
        region: '',
        surface_type: '',
        search: '',
        page: 1
      };
      this.page = 1;
      this.fetchVenues();
    },
    
    prevPage() {
      if (this.page > 1) {
        this.page--;
        this.fetchVenues();
      }
    },
    
    nextPage() {
      if (this.page < this.totalPages) {
        this.page++;
        this.fetchVenues();
      }
    },
    
    goToVenueDetail(venueId) {
      this.$router.push({ name: 'VenueDetail', params: { id: venueId } });
    },
    
    getSurfaceTypeText(surfaceType) {
      const surfaceTypeMap = {
        'grass': '천연잔디',
        'artificial': '인조잔디',
        'futsal': '풋살장'
      };
      
      return surfaceTypeMap[surfaceType] || surfaceType;
    }
  }
};
</script>

<style scoped>
.venue-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  font-size: 28px;
  margin-bottom: 20px;
  color: #333;
}

.filters-container {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
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

.loading-message,
.error-message,
.empty-message {
  text-align: center;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin: 20px 0;
}

.error-message {
  color: #e74c3c;
}

.venues-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.venue-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.venue-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.venue-image {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.venue-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.venue-rating {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.venue-rating i {
  color: #ffc107;
}

.venue-content {
  padding: 15px;
}

.venue-name {
  font-size: 18px;
  margin: 0 0 10px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.venue-address {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
  color: #555;
  font-size: 14px;
}

.venue-address i {
  margin-right: 5px;
  margin-top: 3px;
  color: #777;
}

.venue-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
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

@media (max-width: 768px) {
  .venues-grid {
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