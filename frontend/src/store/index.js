import { createStore } from 'vuex'
import { authAPI, matchAPI, venueAPI, teamAPI } from '@/services/api'

export default createStore({
  state: {
    user: null,
    token: localStorage.getItem('token') || null,
    isAuthenticated: !!localStorage.getItem('token'),
    matches: [],
    matchesLoading: false,
    matchesError: null,
    currentMatch: null,
    matchLoading: false,
    matchError: null,
    venues: [],
    venuesLoading: false,
    venuesError: null,
    teams: [],
    teamsLoading: false,
    teamsError: null
  },
  getters: {
    isAuthenticated: state => state.isAuthenticated,
    user: state => state.user,
    matches: state => state.matches,
    matchesLoading: state => state.matchesLoading,
    matchesError: state => state.matchesError,
    currentMatch: state => state.currentMatch,
    matchLoading: state => state.matchLoading,
    matchError: state => state.matchError,
    venues: state => state.venues,
    venuesLoading: state => state.venuesLoading,
    venuesError: state => state.venuesError,
    teams: state => state.teams,
    teamsLoading: state => state.teamsLoading,
    teamsError: state => state.teamsError
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
    SET_MATCHES(state, matches) {
      state.matches = matches
    },
    SET_MATCHES_LOADING(state, isLoading) {
      state.matchesLoading = isLoading
    },
    SET_MATCHES_ERROR(state, error) {
      state.matchesError = error
    },
    SET_CURRENT_MATCH(state, match) {
      state.currentMatch = match
    },
    SET_MATCH_LOADING(state, isLoading) {
      state.matchLoading = isLoading
    },
    SET_MATCH_ERROR(state, error) {
      state.matchError = error
    },
    SET_VENUES(state, venues) {
      state.venues = venues
    },
    SET_VENUES_LOADING(state, isLoading) {
      state.venuesLoading = isLoading
    },
    SET_VENUES_ERROR(state, error) {
      state.venuesError = error
    },
    SET_TEAMS(state, teams) {
      state.teams = teams
    },
    SET_TEAMS_LOADING(state, isLoading) {
      state.teamsLoading = isLoading
    },
    SET_TEAMS_ERROR(state, error) {
      state.teamsError = error
    }
  },
  actions: {
    // 인증 관련 액션
    async login({ commit, dispatch }, credentials) {
      try {
        const response = await authAPI.login(credentials)
        const { token } = response.data
        commit('SET_TOKEN', token)
        dispatch('fetchUserProfile')
        return response
      } catch (error) {
        console.error('로그인 실패:', error)
        throw error
      }
    },
    async register(_, userData) {
      try {
        const response = await authAPI.register(userData)
        return response
      } catch (error) {
        console.error('회원가입 실패:', error)
        throw error
      }
    },
    async logout({ commit }) {
      try {
        await authAPI.logout()
        commit('SET_TOKEN', null)
        commit('SET_USER', null)
      } catch (error) {
        console.error('로그아웃 실패:', error)
        // 로그아웃은 실패해도 클라이언트에서 토큰 제거
        commit('SET_TOKEN', null)
        commit('SET_USER', null)
      }
    },
    async fetchUserProfile({ commit }) {
      try {
        const response = await authAPI.getProfile()
        commit('SET_USER', response.data)
        return response
      } catch (error) {
        console.error('프로필 조회 실패:', error)
        throw error
      }
    },
    async updateProfile({ commit }, profileData) {
      try {
        const response = await authAPI.updateProfile(profileData)
        commit('SET_USER', response.data)
        return response
      } catch (error) {
        console.error('프로필 업데이트 실패:', error)
        throw error
      }
    },

    // 매치 관련 액션
    async fetchMatches({ commit }, params) {
      commit('SET_MATCHES_LOADING', true)
      commit('SET_MATCHES_ERROR', null)
      try {
        const response = await matchAPI.getMatches(params)
        commit('SET_MATCHES', response.data)
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
    async createMatch({ dispatch }, matchData) {
      try {
        const response = await matchAPI.createMatch(matchData)
        dispatch('fetchMatches')
        return response
      } catch (error) {
        console.error('매치 생성 실패:', error)
        throw error
      }
    },
    async updateMatch({ dispatch }, { id, matchData }) {
      try {
        const response = await matchAPI.updateMatch(id, matchData)
        dispatch('fetchMatch', id)
        return response
      } catch (error) {
        console.error('매치 업데이트 실패:', error)
        throw error
      }
    },
    async deleteMatch({ dispatch }, id) {
      try {
        const response = await matchAPI.deleteMatch(id)
        dispatch('fetchMatches')
        return response
      } catch (error) {
        console.error('매치 삭제 실패:', error)
        throw error
      }
    },
    async joinMatch({ dispatch }, id) {
      try {
        const response = await matchAPI.joinMatch(id)
        dispatch('fetchMatch', id)
        return response
      } catch (error) {
        console.error('매치 참가 실패:', error)
        throw error
      }
    },
    async leaveMatch({ dispatch }, id) {
      try {
        const response = await matchAPI.leaveMatch(id)
        dispatch('fetchMatch', id)
        return response
      } catch (error) {
        console.error('매치 참가 취소 실패:', error)
        throw error
      }
    },

    // 구장 관련 액션
    async fetchVenues({ commit }, params) {
      commit('SET_VENUES_LOADING', true)
      commit('SET_VENUES_ERROR', null)
      try {
        const response = await venueAPI.getVenues(params)
        commit('SET_VENUES', response.data)
        return response
      } catch (error) {
        console.error('구장 목록 조회 실패:', error)
        commit('SET_VENUES_ERROR', error.message || '구장 목록을 불러오는데 실패했습니다.')
        throw error
      } finally {
        commit('SET_VENUES_LOADING', false)
      }
    },

    // 팀 관련 액션
    async fetchTeams({ commit }, params) {
      commit('SET_TEAMS_LOADING', true)
      commit('SET_TEAMS_ERROR', null)
      try {
        const response = await teamAPI.getTeams(params)
        commit('SET_TEAMS', response.data)
        return response
      } catch (error) {
        console.error('팀 목록 조회 실패:', error)
        commit('SET_TEAMS_ERROR', error.message || '팀 목록을 불러오는데 실패했습니다.')
        throw error
      } finally {
        commit('SET_TEAMS_LOADING', false)
      }
    }
  },
  modules: {
  }
}) 