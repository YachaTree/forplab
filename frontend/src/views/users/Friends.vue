<template>
  <div class="friends-page">
    <h1 class="page-title">친구 관리</h1>
    
    <div class="tabs">
      <button 
        :class="['tab-button', { active: activeTab === 'friends' }]" 
        @click="activeTab = 'friends'"
      >
        내 친구
      </button>
      <button 
        :class="['tab-button', { active: activeTab === 'requests' }]" 
        @click="activeTab = 'requests'"
      >
        받은 요청
        <span v-if="friendRequests.length" class="badge">{{ friendRequests.length }}</span>
      </button>
      <button 
        :class="['tab-button', { active: activeTab === 'sent' }]" 
        @click="activeTab = 'sent'"
      >
        보낸 요청
        <span v-if="sentRequests.length" class="badge">{{ sentRequests.length }}</span>
      </button>
    </div>
    
    <!-- 친구 목록 탭 -->
    <div v-if="activeTab === 'friends'" class="tab-content">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>친구 목록을 불러오는 중...</p>
      </div>
      
      <div v-else-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div v-else-if="friends.length === 0" class="empty-state">
        <p>아직 친구가 없습니다.</p>
        <p>사용자 검색을 통해 친구를 추가해보세요!</p>
        <router-link to="/users/search" class="btn btn-primary">
          사용자 검색하기
        </router-link>
      </div>
      
      <div v-else class="friends-list">
        <div v-for="friendship in friends" :key="friendship.id" class="friend-card">
          <div class="friend-info">
            <img 
              :src="getProfileImageUrl(friendship.to_user.id === currentUserId ? friendship.from_user : friendship.to_user)" 
              alt="프로필 이미지" 
              class="profile-image"
            >
            <div class="friend-details">
              <h3>{{ getFriendName(friendship) }}</h3>
              <p>{{ getFriendSkillLevel(friendship) }}</p>
            </div>
          </div>
          
          <div class="friend-actions">
            <router-link 
              :to="{ name: 'Profile', params: { id: getFriendId(friendship) }}" 
              class="btn btn-outline"
            >
              프로필 보기
            </router-link>
            <button 
              @click="confirmDeleteFriend(friendship.id)" 
              class="btn btn-danger"
            >
              친구 삭제
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 받은 요청 탭 -->
    <div v-if="activeTab === 'requests'" class="tab-content">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>친구 요청을 불러오는 중...</p>
      </div>
      
      <div v-else-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div v-else-if="friendRequests.length === 0" class="empty-state">
        <p>받은 친구 요청이 없습니다.</p>
      </div>
      
      <div v-else class="request-list">
        <div v-for="request in friendRequests" :key="request.id" class="request-card">
          <div class="friend-info">
            <img 
              :src="getProfileImageUrl(request.from_user)" 
              alt="프로필 이미지" 
              class="profile-image"
            >
            <div class="friend-details">
              <h3>{{ request.from_user.username }}</h3>
              <p>{{ request.from_user.skill_level }}</p>
            </div>
          </div>
          
          <div class="request-actions">
            <button 
              @click="acceptRequest(request.id)" 
              class="btn btn-success"
            >
              수락
            </button>
            <button 
              @click="rejectRequest(request.id)" 
              class="btn btn-danger"
            >
              거절
            </button>
            <router-link 
              :to="{ name: 'Profile', params: { id: request.from_user.id }}" 
              class="btn btn-outline"
            >
              프로필 보기
            </router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 보낸 요청 탭 -->
    <div v-if="activeTab === 'sent'" class="tab-content">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>보낸 요청을 불러오는 중...</p>
      </div>
      
      <div v-else-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div v-else-if="sentRequests.length === 0" class="empty-state">
        <p>보낸 친구 요청이 없습니다.</p>
        <p>사용자 검색을 통해 친구를 추가해보세요!</p>
        <router-link to="/users/search" class="btn btn-primary">
          사용자 검색하기
        </router-link>
      </div>
      
      <div v-else class="request-list">
        <div v-for="request in sentRequests" :key="request.id" class="request-card">
          <div class="friend-info">
            <img 
              :src="getProfileImageUrl(request.to_user)" 
              alt="프로필 이미지" 
              class="profile-image"
            >
            <div class="friend-details">
              <h3>{{ request.to_user.username }}</h3>
              <p>{{ request.to_user.skill_level }}</p>
            </div>
          </div>
          
          <div class="request-actions">
            <router-link 
              :to="{ name: 'Profile', params: { id: request.to_user.id }}" 
              class="btn btn-outline"
            >
              프로필 보기
            </router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 확인 모달 -->
    <div v-if="showConfirmModal" class="modal">
      <div class="modal-content">
        <h3>친구 삭제</h3>
        <p>정말로 이 친구를 삭제하시겠습니까?</p>
        <div class="modal-actions">
          <button @click="deleteFriend" class="btn btn-danger">삭제</button>
          <button @click="showConfirmModal = false" class="btn btn-outline">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'FriendsPage',
  data() {
    return {
      activeTab: 'friends',
      showConfirmModal: false,
      selectedFriendshipId: null
    };
  },
  computed: {
    ...mapState('friends', ['friends', 'friendRequests', 'sentRequests', 'loading', 'error']),
    ...mapState('auth', ['user']),
    currentUserId() {
      return this.user ? this.user.id : null;
    }
  },
  methods: {
    ...mapActions('friends', [
      'fetchFriends', 
      'fetchFriendRequests', 
      'fetchSentRequests',
      'acceptFriendRequest',
      'rejectFriendRequest',
      'deleteFriendship'
    ]),
    
    // 친구 정보 관련 헬퍼 메소드
    getFriendId(friendship) {
      return friendship.to_user.id === this.currentUserId 
        ? friendship.from_user.id 
        : friendship.to_user.id;
    },
    
    getFriendName(friendship) {
      return friendship.to_user.id === this.currentUserId 
        ? friendship.from_user.username 
        : friendship.to_user.username;
    },
    
    getFriendSkillLevel(friendship) {
      return friendship.to_user.id === this.currentUserId 
        ? friendship.from_user.skill_level 
        : friendship.to_user.skill_level;
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
    
    // 친구 요청 관련 메소드
    async acceptRequest(requestId) {
      try {
        await this.acceptFriendRequest(requestId);
        this.$toast.success('친구 요청을 수락했습니다.');
      } catch (error) {
        this.$toast.error('친구 요청 수락에 실패했습니다.');
      }
    },
    
    async rejectRequest(requestId) {
      try {
        await this.rejectFriendRequest(requestId);
        this.$toast.success('친구 요청을 거절했습니다.');
      } catch (error) {
        this.$toast.error('친구 요청 거절에 실패했습니다.');
      }
    },
    
    // 친구 삭제 관련 메소드
    confirmDeleteFriend(friendshipId) {
      this.selectedFriendshipId = friendshipId;
      this.showConfirmModal = true;
    },
    
    async deleteFriend() {
      try {
        await this.deleteFriendship(this.selectedFriendshipId);
        this.showConfirmModal = false;
        this.selectedFriendshipId = null;
        this.$toast.success('친구가 삭제되었습니다.');
      } catch (error) {
        this.$toast.error('친구 삭제에 실패했습니다.');
      }
    }
  },
  created() {
    // 페이지 로드 시 데이터 불러오기
    this.fetchFriends();
    this.fetchFriendRequests();
    this.fetchSentRequests();
  },
  watch: {
    // 탭 변경 시 해당 데이터 다시 불러오기
    activeTab(newTab) {
      if (newTab === 'friends') {
        this.fetchFriends();
      } else if (newTab === 'requests') {
        this.fetchFriendRequests();
      } else if (newTab === 'sent') {
        this.fetchSentRequests();
      }
    }
  }
};
</script>

<style scoped>
.friends-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

/* 탭 스타일 */
.tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #ddd;
}

.tab-button {
  padding: 10px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  position: relative;
  color: #666;
  transition: all 0.3s;
}

.tab-button.active {
  color: #4a90e2;
  font-weight: bold;
}

.tab-button.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 100%;
  height: 3px;
  background-color: #4a90e2;
}

.badge {
  display: inline-block;
  background-color: #e74c3c;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 12px;
  line-height: 20px;
  text-align: center;
  margin-left: 5px;
}

/* 탭 콘텐츠 스타일 */
.tab-content {
  min-height: 300px;
}

/* 친구 카드 스타일 */
.friend-card, .request-card {
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

.friend-card:hover, .request-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.friend-info {
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

.friend-details h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.friend-details p {
  margin: 0;
  color: #666;
}

.friend-actions, .request-actions {
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

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.btn-outline {
  background-color: transparent;
  border: 1px solid #ddd;
  color: #666;
}

.btn-outline:hover {
  background-color: #f5f5f5;
}

/* 로딩 및 에러 스타일 */
.loading {
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

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.empty-state p {
  margin-bottom: 15px;
}

/* 모달 스타일 */
.modal {
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
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.modal-content h3 {
  margin-top: 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style> 