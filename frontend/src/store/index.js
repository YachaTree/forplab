import { createStore } from 'vuex';
import { authAPI } from '@/services/api';

export default createStore({
  state: {
    user: null,
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
    isAuthenticated: !!localStorage.getItem('token'),
    loading: false,
    error: null,
  },
  
  getters: {
    isAuthenticated: state => state.isAuthenticated,
    user: state => state.user,
    loading: state => state.loading,
    error: state => state.error,
  },
  
  mutations: {
    SET_USER(state, user) {
      state.user = user;
    },
    SET_TOKENS(state, { token, refreshToken }) {
      state.token = token;
      state.refreshToken = refreshToken;
      state.isAuthenticated = true;
      
      // 로컬 스토리지에 토큰 저장
      localStorage.setItem('token', token);
      localStorage.setItem('refreshToken', refreshToken);
    },
    CLEAR_AUTH(state) {
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      
      // 로컬 스토리지에서 토큰 제거
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
    },
    SET_LOADING(state, loading) {
      state.loading = loading;
    },
    SET_ERROR(state, error) {
      state.error = error;
    },
    CLEAR_ERROR(state) {
      state.error = null;
    },
  },
  
  actions: {
    // 로그인
    async login({ commit }, { username, password }) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      try {
        const response = await authAPI.login(username, password);
        const { access, refresh } = response.data;
        
        commit('SET_TOKENS', { token: access, refreshToken: refresh });
        
        // 사용자 정보 가져오기
        await dispatch('fetchUserProfile');
        
        commit('SET_LOADING', false);
        return true;
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '로그인에 실패했습니다.');
        commit('SET_LOADING', false);
        return false;
      }
    },
    
    // 회원가입
    async register({ commit }, userData) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      try {
        await authAPI.register(userData);
        commit('SET_LOADING', false);
        return true;
      } catch (error) {
        commit('SET_ERROR', error.response?.data || '회원가입에 실패했습니다.');
        commit('SET_LOADING', false);
        return false;
      }
    },
    
    // 로그아웃
    logout({ commit }) {
      commit('CLEAR_AUTH');
    },
    
    // 사용자 프로필 가져오기
    async fetchUserProfile({ commit }) {
      commit('SET_LOADING', true);
      
      try {
        const response = await authAPI.getProfile();
        commit('SET_USER', response.data);
        commit('SET_LOADING', false);
        return true;
      } catch (error) {
        commit('SET_ERROR', '프로필 정보를 가져오는데 실패했습니다.');
        commit('SET_LOADING', false);
        return false;
      }
    },
    
    // 프로필 업데이트
    async updateProfile({ commit }, profileData) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      try {
        const response = await authAPI.updateProfile(profileData);
        commit('SET_USER', response.data.user);
        commit('SET_LOADING', false);
        return true;
      } catch (error) {
        commit('SET_ERROR', error.response?.data || '프로필 업데이트에 실패했습니다.');
        commit('SET_LOADING', false);
        return false;
      }
    },
    
    // 비밀번호 변경
    async changePassword({ commit }, passwordData) {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      try {
        await authAPI.changePassword(passwordData);
        commit('SET_LOADING', false);
        return true;
      } catch (error) {
        commit('SET_ERROR', error.response?.data || '비밀번호 변경에 실패했습니다.');
        commit('SET_LOADING', false);
        return false;
      }
    },
  },
}); 