<template>
  <div class="user-search-container">
    <h1 class="page-title">사용자 검색</h1>
    
    <div class="search-form">
      <div class="search-input-container">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="사용자 이름으로 검색" 
          class="search-input"
          @keyup.enter="searchUsers"
        >
        <button @click="searchUsers" class="search-button">
          <i class="fas fa-search"></i>
        </button>
      </div>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>검색 중...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>
    
    <div v-else-if="searchPerformed && users.length === 0" class="no-results">
      <p>검색 결과가 없습니다.</p>
    </div>
    
    <div v-else-if="users.length > 0" class="search-results">
      <div v-for="user in users" :key="user.id" class="user-card">
        <div class="user-info">
          <img 
            :src="getProfileImageUrl(user)" 
            alt="프로필 이미지" 
            class="profile-image"
          >
          <div class="user-details">
            <h3>{{ user.username }}</h3>
            <p v-if="user.skill_level">실력: {{ user.skill_level }}</p>
          </div>
        </div>
        
        <div class="user-actions">
          <router-link 
            :to="{ name: 'Profile', params: { id: user.id }}" 
            class="btn btn-outline"
          >
            프로필 보기
          </router-link>
          
          <!-- 친구 요청 버튼 -->
          <button 
            v-if="!isFriend(user) && !hasSentRequest(user) && !hasReceivedRequest(user) && user.id !== currentUserId" 
            @click="sendFriendRequest(user.id)" 
            class="btn btn-primary"
            :disabled="requestLoading"
          >
            친구 요청 보내기
          </button>
          
          <button 
            v-else-if="hasSentRequest(user)" 
            class="btn btn-disabled"
            disabled
          >
            요청 전송됨
          </button>
          
          <button 
            v-else-if="hasReceivedRequest(user)" 
            @click="acceptFriendRequest(getRequestId(user))" 
            class="btn btn-success"
          >
            요청 수락하기
          </button>
          
          <button 
            v-else-if="isFriend(user)" 
            class="btn btn-disabled"
            disabled
          >
            이미 친구입니다
          </button>
        </div>
      </div>
    </div>
    
    <div v-else class="search-prompt">
      <p>사용자 이름으로 검색해보세요.</p>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'UserSearch',
  data() {
    return {
      searchQuery: '',
      users: [],
      loading: false,
      requestLoading: false,
      error: null,
      searchPerformed: false
    };
  },
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('friends', ['friends', 'friendRequests', 'sentRequests']),
    currentUserId() {
      return this.user ? this.user.id : null;
    }
  },
  methods: {
    ...mapActions('friends', [
      'fetchFriends', 
      'fetchFriendRequests', 
      'fetchSentRequests',
      'sendFriendRequest',
      'acceptFriendRequest'
    ]),
    
    async searchUsers() {
      if (!this.searchQuery.trim()) {
        this.error = '검색어를 입력해주세요.';
        return;
      }
      
      this.loading = true;
      this.error = null;
      this.searchPerformed = true;
      
      try {
        const response = await this.$axios.get('/api/users/search/', {
          params: { query: this.searchQuery }
        });
        this.users = response.data;
      } catch (error) {
        console.error('사용자 검색 실패:', error);
        this.error = '사용자 검색 중 오류가 발생했습니다.';
      } finally {
        this.loading = false;
      }
    },
    
    getProfileImageUrl(user) {
      if (!user || !user.profile_image) {
        return require('@/assets/default-profile.png');
      }
      
      const imageUrl = user.profile_image;
      if (imageUrl.startsWith('http')) {
        return imageUrl;
      } else if (imageUrl.startsWith('/media')) {
        return `${process.env.VUE_APP_API_URL}${imageUrl}`;
      } else {
        return `${process.env.VUE_APP_API_URL}/media/${imageUrl}`;
      }
    },
    
    // 친구 관계 확인 메소드
    isFriend(user) {
      return this.friends.some(friendship => 
        (friendship.from_user.id === user.id || friendship.to_user.id === user.id) && 
        friendship.status === 'ACCEPTED'
      );
    },
    
    hasSentRequest(user) {
      return this.sentRequests.some(request => 
        request.to_user.id === user.id && 
        request.status === 'PENDING'
      );
    },
    
    hasReceivedRequest(user) {
      return this.friendRequests.some(request => 
        request.from_user.id === user.id && 
        request.status === 'PENDING'
      );
    },
    
    getRequestId(user) {
      const request = this.friendRequests.find(req => 
        req.from_user.id === user.id && 
        req.status === 'PENDING'
      );
      return request ? request.id : null;
    },
    
    // 친구 요청 관련 메소드
    async sendFriendRequest(userId) {
      this.requestLoading = true;
      
      try {
        await this.$store.dispatch('friends/sendFriendRequest', userId);
        this.$toast.success('친구 요청을 보냈습니다.');
        // 보낸 요청 목록 갱신
        await this.fetchSentRequests();
      } catch (error) {
        console.error('친구 요청 전송 실패:', error);
        this.$toast.error('친구 요청 전송에 실패했습니다.');
      } finally {
        this.requestLoading = false;
      }
    },
    
    async acceptFriendRequest(requestId) {
      if (!requestId) return;
      
      this.requestLoading = true;
      
      try {
        await this.$store.dispatch('friends/acceptFriendRequest', requestId);
        this.$toast.success('친구 요청을 수락했습니다.');
        // 친구 목록과 요청 목록 갱신
        await this.fetchFriends();
        await this.fetchFriendRequests();
      } catch (error) {
        console.error('친구 요청 수락 실패:', error);
        this.$toast.error('친구 요청 수락에 실패했습니다.');
      } finally {
        this.requestLoading = false;
      }
    }
  },
  created() {
    // 친구 관련 데이터 로드
    this.fetchFriends();
    this.fetchFriendRequests();
    this.fetchSentRequests();
  }
};
</script>

<style scoped>
.user-search-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.search-form {
  margin-bottom: 30px;
}

.search-input-container {
  display: flex;
  max-width: 500px;
  margin: 0 auto;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  border-radius: 4px;
  overflow: hidden;
}

.search-input {
  flex: 1;
  padding: 12px 15px;
  border: none;
  font-size: 16px;
  outline: none;
}

.search-button {
  background-color: #4a90e2;
  color: white;
  border: none;
  padding: 0 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-button:hover {
  background-color: #3a7bc8;
}

/* 사용자 카드 스타일 */
.user-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  margin-bottom: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  background-color: white;
  transition: transform 0.2s;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.user-info {
  display: flex;
  align-items: center;
}

.profile-image {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 15px;
}

.user-details h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.user-details p {
  margin: 0;
  color: #666;
}

.user-actions {
  display: flex;
  gap: 10px;
}

/* 버튼 스타일 */
.btn {
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  border: none;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background-color: #4a90e2;
  color: white;
}

.btn-primary:hover {
  background-color: #3a7bc8;
}

.btn-success {
  background-color: #2ecc71;
  color: white;
}

.btn-success:hover {
  background-color: #27ae60;
}

.btn-outline {
  background-color: transparent;
  border: 1px solid #ddd;
  color: #666;
}

.btn-outline:hover {
  background-color: #f5f5f5;
}

.btn-disabled {
  background-color: #e0e0e0;
  color: #888;
  cursor: not-allowed;
}

/* 로딩 및 에러 스타일 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #4a90e2;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #e74c3c;
  text-align: center;
  padding: 20px;
}

.no-results, .search-prompt {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}
</style> 