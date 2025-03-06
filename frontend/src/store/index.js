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
    currentVenue: null,
    venueLoading: false,
    venueError: null,
    teams: [],
    teamsLoading: false,
    teamsError: null,
    currentTeam: null,
    teamLoading: false,
    teamError: null
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
    currentVenue: state => state.currentVenue,
    venueLoading: state => state.venueLoading,
    venueError: state => state.venueError,
    teams: state => state.teams,
    teamsLoading: state => state.teamsLoading,
    teamsError: state => state.teamsError,
    currentTeam: state => state.currentTeam,
    teamLoading: state => state.teamLoading,
    teamError: state => state.teamError
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
    SET_CURRENT_VENUE(state, venue) {
      state.currentVenue = venue
    },
    SET_VENUE_LOADING(state, isLoading) {
      state.venueLoading = isLoading
    },
    SET_VENUE_ERROR(state, error) {
      state.venueError = error
    },
    SET_TEAMS(state, teams) {
      state.teams = teams
    },
    SET_TEAMS_LOADING(state, isLoading) {
      state.teamsLoading = isLoading
    },
    SET_TEAMS_ERROR(state, error) {
      state.teamsError = error
    },
    SET_CURRENT_TEAM(state, team) {
      state.currentTeam = team
    },
    SET_TEAM_LOADING(state, isLoading) {
      state.teamLoading = isLoading
    },
    SET_TEAM_ERROR(state, error) {
      state.teamError = error
    }
  },
  actions: {
    // 인증 관련 액션
    async login({ commit, dispatch }, credentials) {
      try {
        const response = await authAPI.login(credentials)
        const { access } = response.data
        commit('SET_TOKEN', access)
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
        commit('SET_VENUES', response.data.results || response.data)
        return response
      } catch (error) {
        console.error('구장 목록 조회 실패:', error)
        commit('SET_VENUES_ERROR', error.message || '구장 목록을 불러오는데 실패했습니다.')
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
        console.error('구장 상세 조회 실패:', error)
        commit('SET_VENUE_ERROR', error.message || '구장 정보를 불러오는데 실패했습니다.')
        throw error
      } finally {
        commit('SET_VENUE_LOADING', false)
      }
    },
    
    async createVenueReview({ dispatch }, { venueId, reviewData }) {
      try {
        const response = await venueAPI.createVenueReview(venueId, reviewData)
        // 리뷰 등록 후 구장 정보 다시 조회
        dispatch('fetchVenue', venueId)
        return response
      } catch (error) {
        console.error('구장 리뷰 등록 실패:', error)
        throw error
      }
    },

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
    
    async updateTeam({ dispatch }, { id, teamData }) {
      try {
        const response = await teamAPI.updateTeam(id, teamData)
        // 팀 정보 업데이트 후 다시 조회
        dispatch('fetchTeam', id)
        return response
      } catch (error) {
        console.error('팀 정보 업데이트 실패:', error)
        throw error
      }
    },
    
    async deleteTeam({ dispatch }, id) {
      try {
        const response = await teamAPI.deleteTeam(id)
        // 팀 삭제 후 팀 목록 페이지로 이동하기 위해 목록 다시 조회
        dispatch('fetchTeams')
        return response
      } catch (error) {
        console.error('팀 삭제 실패:', error)
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
    
    async leaveTeam(_, id) {
      try {
        const response = await teamAPI.leaveTeam(id)
        return response
      } catch (error) {
        console.error('팀 탈퇴 실패:', error)
        throw error
      }
    },
    
    async cancelJoinRequest(_, id) {
      try {
        // 가입 신청 취소는 팀 탈퇴와 동일한 API 사용
        const response = await teamAPI.leaveTeam(id)
        return response
      } catch (error) {
        console.error('가입 신청 취소 실패:', error)
        throw error
      }
    },
    
    async getTeamMembers(_, id) {
      try {
        const response = await teamAPI.getMembers(id)
        return response
      } catch (error) {
        console.error('팀원 목록 조회 실패:', error)
        throw error
      }
    },
    
    async getJoinRequests(_, id) {
      try {
        const response = await teamAPI.getJoinRequests(id)
        return response
      } catch (error) {
        console.error('가입 신청 목록 조회 실패:', error)
        throw error
      }
    },
    
    async approveJoinRequest(_, { teamId, requestId }) {
      try {
        const response = await teamAPI.approveJoinRequest(teamId, requestId)
        return response
      } catch (error) {
        console.error('가입 신청 승인 실패:', error)
        throw error
      }
    },
    
    async rejectJoinRequest(_, { teamId, requestId }) {
      try {
        const response = await teamAPI.rejectJoinRequest(teamId, requestId)
        return response
      } catch (error) {
        console.error('가입 신청 거절 실패:', error)
        throw error
      }
    },
  },
  modules: {
  }
}) 