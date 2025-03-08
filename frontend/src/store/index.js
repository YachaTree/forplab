import { createStore } from 'vuex'
import { authAPI, matchAPI, venueAPI, teamAPI } from '@/services/api'

// Auth 모듈
const auth = {
  namespaced: true,
  state: {
    user: null,
    token: localStorage.getItem('token') || null,
    isAuthenticated: !!localStorage.getItem('token'),
    loading: false,
    error: null
  },
  getters: {
    isAuthenticated: state => state.isAuthenticated,
    user: state => state.user,
    loading: state => state.loading,
    error: state => state.error
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token
      state.isAuthenticated = !!token
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    },
    SET_USER(state, user) {
      state.user = user
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    }
  },
  actions: {
    // 인증 관련 액션
    async login({ commit, dispatch }, credentials) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const response = await authAPI.login(credentials)
        const token = response.data.access
        commit('SET_TOKEN', token)
        await dispatch('fetchProfile')
        commit('SET_LOADING', false)
        return response
      } catch (error) {
        console.error('로그인 실패:', error)
        commit('SET_ERROR', error.message || '로그인에 실패했습니다.')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    async register({ commit }, userData) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const response = await authAPI.register(userData)
        commit('SET_LOADING', false)
        return response
      } catch (error) {
        console.error('회원가입 실패:', error)
        commit('SET_ERROR', error.message || '회원가입에 실패했습니다.')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    async logout({ commit }) {
      commit('SET_LOADING', true)
      try {
        await authAPI.logout()
        commit('SET_TOKEN', null)
        commit('SET_USER', null)
        commit('SET_LOADING', false)
      } catch (error) {
        console.error('로그아웃 실패:', error)
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    async fetchProfile({ commit }) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const response = await authAPI.getProfile()
        commit('SET_USER', response.data)
        commit('SET_LOADING', false)
        return response
      } catch (error) {
        console.error('프로필 조회 실패:', error)
        commit('SET_ERROR', error.message || '프로필 정보를 불러오는데 실패했습니다.')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    async getUserProfile({ commit }, userId) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        console.log('getUserProfile 액션 호출됨, userId:', userId);
        const response = await authAPI.getUserProfile(userId)
        console.log('getUserProfile 응답:', response.data);
        
        // 사용자 정보를 state에 설정
        commit('SET_USER', response.data)
        
        commit('SET_LOADING', false)
        return response
      } catch (error) {
        console.error('사용자 프로필 조회 실패:', error)
        commit('SET_ERROR', error.message || '사용자 프로필 정보를 불러오는데 실패했습니다.')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    async getUserTeams({ commit }, userId) {
      commit('SET_LOADING', true)
      try {
        const response = await authAPI.getUserTeams(userId)
        commit('SET_LOADING', false)
        return response
      } catch (error) {
        console.error('사용자 팀 조회 실패:', error)
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    async getUserMatches({ commit }, userId) {
      commit('SET_LOADING', true)
      try {
        const response = await authAPI.getUserMatches(userId)
        commit('SET_LOADING', false)
        return response
      } catch (error) {
        console.error('사용자 경기 조회 실패:', error)
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    async updateProfile({ commit, dispatch }, profileData) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const response = await authAPI.updateProfile(profileData)
        // 프로필 업데이트 후 다시 조회
        await dispatch('fetchProfile')
        commit('SET_LOADING', false)
        return response
      } catch (error) {
        console.error('프로필 업데이트 실패:', error)
        commit('SET_ERROR', error.message || '프로필 정보 업데이트에 실패했습니다.')
        commit('SET_LOADING', false)
        throw error
      }
    }
  }
}

// Teams 모듈
const teams = {
  namespaced: true,
  state: {
    teams: [],
    teamsLoading: false,
    teamsError: null,
    currentTeam: null,
    teamLoading: false,
    teamError: null
  },
  getters: {
    teams: state => state.teams,
    teamsLoading: state => state.teamsLoading,
    teamsError: state => state.teamsError,
    currentTeam: state => state.currentTeam,
    teamLoading: state => state.teamLoading,
    teamError: state => state.teamError
  },
  mutations: {
    SET_TEAMS(state, teams) {
      state.teams = teams
    },
    SET_TEAMS_LOADING(state, loading) {
      state.teamsLoading = loading
    },
    SET_TEAMS_ERROR(state, error) {
      state.teamsError = error
    },
    SET_CURRENT_TEAM(state, team) {
      state.currentTeam = team
    },
    SET_TEAM_LOADING(state, loading) {
      state.teamLoading = loading
    },
    SET_TEAM_ERROR(state, error) {
      state.teamError = error
    }
  },
  actions: {
    // 팀 관련 액션
    async fetchTeams({ commit }, params) {
      commit('SET_TEAMS_LOADING', true)
      commit('SET_TEAMS_ERROR', null)
      try {
        const response = await teamAPI.getTeams(params)
        commit('SET_TEAMS', response.data.results || response.data)
        return response
      } catch (error) {
        console.error('팀 목록 조회 실패:', error)
        commit('SET_TEAMS_ERROR', error.message || '팀 목록을 불러오는데 실패했습니다.')
        throw error
      } finally {
        commit('SET_TEAMS_LOADING', false)
      }
    },
    
    async fetchTeam({ commit }, id) {
      commit('SET_TEAM_LOADING', true)
      commit('SET_TEAM_ERROR', null)
      try {
        const response = await teamAPI.getTeam(id)
        commit('SET_CURRENT_TEAM', response.data)
        return response
      } catch (error) {
        console.error('팀 상세 조회 실패:', error)
        commit('SET_TEAM_ERROR', error.message || '팀 정보를 불러오는데 실패했습니다.')
        throw error
      } finally {
        commit('SET_TEAM_LOADING', false)
      }
    },
    
    async createTeam(_, teamData) {
      try {
        const response = await teamAPI.createTeam(teamData)
        return response
      } catch (error) {
        console.error('팀 생성 실패:', error)
        throw error
      }
    },
    
    async updateTeam({ dispatch }, { teamId, teamData }) {
      try {
        const response = await teamAPI.updateTeam(teamId, teamData)
        // 팀 정보 업데이트 후 다시 조회
        await dispatch('fetchTeam', teamId)
        return response
      } catch (error) {
        console.error('팀 업데이트 실패:', error)
        throw error
      }
    },
    
    async joinTeam(_, { id, requestData }) {
      try {
        const response = await teamAPI.joinTeam(id, requestData)
        return response
      } catch (error) {
        console.error('팀 가입 신청 실패:', error)
        throw error
      }
    },
    
    async cancelJoinRequest(_, teamId) {
      try {
        const response = await teamAPI.cancelJoinRequest(teamId)
        return response
      } catch (error) {
        console.error('가입 신청 취소 실패:', error)
        throw error
      }
    },
    
    async acceptJoinRequest({ dispatch }, { teamId, requestId }) {
      try {
        const response = await teamAPI.acceptJoinRequest(teamId, requestId)
        // 가입 신청 승인 후 팀 정보 다시 조회
        await dispatch('fetchTeam', teamId)
        return response
      } catch (error) {
        console.error('가입 신청 승인 실패:', error)
        throw error
      }
    },
    
    async rejectJoinRequest({ dispatch }, { teamId, requestId }) {
      try {
        const response = await teamAPI.rejectJoinRequest(teamId, requestId)
        // 가입 신청 거절 후 팀 정보 다시 조회
        await dispatch('fetchTeam', teamId)
        return response
      } catch (error) {
        console.error('가입 신청 거절 실패:', error)
        throw error
      }
    },
    
    async leaveTeam(_, teamId) {
      try {
        const response = await teamAPI.leaveTeam(teamId)
        return response
      } catch (error) {
        console.error('팀 탈퇴 실패:', error)
        throw error
      }
    },
    
    async deleteTeam({ commit }, teamId) {
      try {
        const response = await teamAPI.deleteTeam(teamId)
        // 팀 삭제 후 현재 팀 정보 초기화
        commit('SET_CURRENT_TEAM', null)
        return response
      } catch (error) {
        console.error('팀 삭제 실패:', error)
        // 오류가 발생해도 현재 팀 정보 초기화
        commit('SET_CURRENT_TEAM', null)
        // 오류를 상위로 전파
        throw error
      }
    },
  }
}

// Matches 모듈
const matches = {
  namespaced: true,
  state: {
    matches: [],
    matchesLoading: false,
    matchesError: null,
    currentMatch: null,
    matchLoading: false,
    matchError: null
  },
  getters: {
    matches: state => state.matches,
    matchesLoading: state => state.matchesLoading,
    matchesError: state => state.matchesError,
    currentMatch: state => state.currentMatch,
    matchLoading: state => state.matchLoading,
    matchError: state => state.matchError
  },
  mutations: {
    SET_MATCHES(state, matches) {
      state.matches = matches
    },
    SET_MATCHES_LOADING(state, loading) {
      state.matchesLoading = loading
    },
    SET_MATCHES_ERROR(state, error) {
      state.matchesError = error
    },
    SET_CURRENT_MATCH(state, match) {
      state.currentMatch = match
    },
    SET_MATCH_LOADING(state, loading) {
      state.matchLoading = loading
    },
    SET_MATCH_ERROR(state, error) {
      state.matchError = error
    }
  },
  actions: {
    // 매치 관련 액션
    async fetchMatches({ commit }, params) {
      commit('SET_MATCHES_LOADING', true)
      commit('SET_MATCHES_ERROR', null)
      try {
        const response = await matchAPI.getMatches(params)
        commit('SET_MATCHES', response.data.results || response.data)
        return response
      } catch (error) {
        console.error('매치 목록 조회 실패:', error)
        commit('SET_MATCHES_ERROR', error.message || '매치 목록을 불러오는데 실패했습니다.')
        throw error
      } finally {
        commit('SET_MATCHES_LOADING', false)
      }
    },
    
    async fetchMatch({ commit }, id) {
      commit('SET_MATCH_LOADING', true)
      commit('SET_MATCH_ERROR', null)
      try {
        const response = await matchAPI.getMatch(id)
        commit('SET_CURRENT_MATCH', response.data)
        return response
      } catch (error) {
        console.error('매치 상세 조회 실패:', error)
        commit('SET_MATCH_ERROR', error.message || '매치 정보를 불러오는데 실패했습니다.')
        throw error
      } finally {
        commit('SET_MATCH_LOADING', false)
      }
    },
    
    async createMatch(_, matchData) {
      try {
        const response = await matchAPI.createMatch(matchData)
        return response
      } catch (error) {
        console.error('매치 생성 실패:', error)
        throw error
      }
    },
    
    async updateMatch({ dispatch }, { matchId, matchData }) {
      try {
        const response = await matchAPI.updateMatch(matchId, matchData)
        // 매치 정보 업데이트 후 다시 조회
        await dispatch('fetchMatch', matchId)
        return response
      } catch (error) {
        console.error('매치 업데이트 실패:', error)
        throw error
      }
    }
  }
}

// Venues 모듈
const venues = {
  namespaced: true,
  state: {
    venues: [],
    venuesLoading: false,
    venuesError: null,
    currentVenue: null,
    venueLoading: false,
    venueError: null
  },
  getters: {
    venues: state => state.venues,
    venuesLoading: state => state.venuesLoading,
    venuesError: state => state.venuesError,
    currentVenue: state => state.currentVenue,
    venueLoading: state => state.venueLoading,
    venueError: state => state.venueError
  },
  mutations: {
    SET_VENUES(state, venues) {
      state.venues = venues
    },
    SET_VENUES_LOADING(state, loading) {
      state.venuesLoading = loading
    },
    SET_VENUES_ERROR(state, error) {
      state.venuesError = error
    },
    SET_CURRENT_VENUE(state, venue) {
      state.currentVenue = venue
    },
    SET_VENUE_LOADING(state, loading) {
      state.venueLoading = loading
    },
    SET_VENUE_ERROR(state, error) {
      state.venueError = error
    }
  },
  actions: {
    // 경기장 관련 액션
    async fetchVenues({ commit }, params) {
      commit('SET_VENUES_LOADING', true)
      commit('SET_VENUES_ERROR', null)
      try {
        const response = await venueAPI.getVenues(params)
        commit('SET_VENUES', response.data.results || response.data)
        return response
      } catch (error) {
        console.error('경기장 목록 조회 실패:', error)
        commit('SET_VENUES_ERROR', error.message || '경기장 목록을 불러오는데 실패했습니다.')
        throw error
      } finally {
        commit('SET_VENUES_LOADING', false)
      }
    },
    
    async fetchVenue({ commit }, id) {
      commit('SET_VENUE_LOADING', true)
      commit('SET_VENUE_ERROR', null)
      try {
        const response = await venueAPI.getVenue(id)
        commit('SET_CURRENT_VENUE', response.data)
        return response
      } catch (error) {
        console.error('경기장 상세 조회 실패:', error)
        commit('SET_VENUE_ERROR', error.message || '경기장 정보를 불러오는데 실패했습니다.')
        throw error
      } finally {
        commit('SET_VENUE_LOADING', false)
      }
    }
  }
}

// 루트 스토어 생성
const store = createStore({
  modules: {
    auth,
    teams,
    matches,
    venues
  },
  // 루트 레벨 getters (모듈 네임스페이스 없이 접근 가능)
  getters: {
    isAuthenticated: state => state.auth.isAuthenticated,
    user: state => state.auth.user
  },
  // 루트 레벨 액션 (모듈 네임스페이스 없이 접근 가능)
  actions: {
    register({ dispatch }, userData) {
      return dispatch('auth/register', userData);
    },
    login({ dispatch }, credentials) {
      return dispatch('auth/login', credentials);
    },
    logout({ dispatch }) {
      return dispatch('auth/logout');
    },
    fetchUserProfile({ dispatch }) {
      return dispatch('auth/fetchUserProfile');
    }
  }
})

export default store 