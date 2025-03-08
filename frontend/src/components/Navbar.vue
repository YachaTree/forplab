<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-logo">
        <router-link to="/">ForPlab</router-link>
      </div>
      
      <div class="navbar-links">
        <router-link to="/matches" class="nav-link">매치</router-link>
        <router-link to="/venues" class="nav-link">구장</router-link>
        <router-link to="/teams" class="nav-link">팀</router-link>
        <router-link to="/users/search" class="nav-link" v-if="isAuthenticated">
          <i class="fas fa-search"></i> 사용자 검색
        </router-link>
      </div>
      
      <div class="navbar-actions">
        <template v-if="isAuthenticated">
          <router-link to="/matches/create" class="create-match-btn">
            <i class="fas fa-plus"></i> 매치 생성
          </router-link>
          
          <div class="user-menu" @click="toggleUserMenu" ref="userMenu">
            <img :src="user?.profile_image || '/img/default-avatar.png'" alt="User" class="user-avatar">
            <span class="user-name">{{ user?.username || '사용자' }}</span>
            <i class="fas fa-chevron-down"></i>
            
            <div class="dropdown-menu" v-show="showUserMenu">
              <router-link to="/profile" class="dropdown-item">
                <i class="fas fa-user"></i> 프로필
              </router-link>
              <router-link to="/my-matches" class="dropdown-item">
                <i class="fas fa-futbol"></i> 내 매치
              </router-link>
              <router-link to="/my-teams" class="dropdown-item">
                <i class="fas fa-users"></i> 내 팀
              </router-link>
              <router-link to="/users/search" class="dropdown-item">
                <i class="fas fa-search"></i> 사용자 검색
              </router-link>
              <div class="dropdown-divider"></div>
              <a href="#" class="dropdown-item" @click.prevent="logout">
                <i class="fas fa-sign-out-alt"></i> 로그아웃
              </a>
            </div>
          </div>
        </template>
        
        <template v-else>
          <router-link to="/login" class="login-btn">로그인</router-link>
          <router-link to="/register" class="register-btn">회원가입</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
  name: 'MainNavbar',
  
  data() {
    return {
      showUserMenu: false
    };
  },
  
  computed: {
    ...mapState({
      user: state => state.auth.user
    }),
    
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated'
    })
  },
  
  mounted() {
    document.addEventListener('click', this.handleClickOutside);
  },
  
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  },
  
  methods: {
    ...mapActions({
      logout: 'auth/logout'
    }),
    
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu;
    },
    
    handleClickOutside(event) {
      if (this.$refs.userMenu && !this.$refs.userMenu.contains(event.target)) {
        this.showUserMenu = false;
      }
    }
  }
};
</script>

<style scoped>
.navbar {
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar-logo a {
  font-size: 24px;
  font-weight: 700;
  color: #1976d2;
  text-decoration: none;
}

.navbar-links {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: #333;
  text-decoration: none;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: #f5f5f5;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.login-btn,
.register-btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 500;
  text-decoration: none;
  transition: background-color 0.2s;
}

.login-btn {
  color: #1976d2;
  background-color: transparent;
  border: 1px solid #1976d2;
}

.login-btn:hover {
  background-color: rgba(25, 118, 210, 0.1);
}

.register-btn {
  color: white;
  background-color: #1976d2;
  border: 1px solid #1976d2;
}

.register-btn:hover {
  background-color: #1565c0;
}

.create-match-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 500;
  text-decoration: none;
  color: white;
  background-color: #4caf50;
  transition: background-color 0.2s;
}

.create-match-btn:hover {
  background-color: #388e3c;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  position: relative;
}

.user-menu:hover {
  background-color: #f5f5f5;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.user-name {
  font-weight: 500;
  color: #333;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  width: 200px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 8px 0;
  margin-top: 5px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  color: #333;
  text-decoration: none;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}

.dropdown-divider {
  height: 1px;
  background-color: #eee;
  margin: 8px 0;
}

@media (max-width: 768px) {
  .navbar-links {
    display: none;
  }
  
  .create-match-btn span {
    display: none;
  }
  
  .user-name {
    display: none;
  }
}
</style> 