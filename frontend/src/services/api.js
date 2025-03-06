import axios from 'axios';

// API 기본 URL 설정
const API_URL = 'http://localhost:8000/api/v1';

// axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 - 토큰 추가
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 토큰 만료 처리
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // 토큰 만료 에러 (401) 및 재시도하지 않은 요청인 경우
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // 리프레시 토큰으로 새 액세스 토큰 요청
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          // 리프레시 토큰이 없으면 로그아웃
          localStorage.removeItem('token');
          localStorage.removeItem('refreshToken');
          window.location.href = '/login';
          return Promise.reject(error);
        }
        
        const response = await axios.post(`${API_URL}/users/token/refresh/`, {
          refresh: refreshToken,
        });
        
        // 새 토큰 저장
        const { access } = response.data;
        localStorage.setItem('token', access);
        
        // 원래 요청 재시도
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // 리프레시 토큰도 만료된 경우 로그아웃
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// 인증 관련 API
export const authAPI = {
  login(credentials) {
    return apiClient.post('/users/token/', credentials);
  },
  register(userData) {
    return apiClient.post('/users/register/', userData);
  },
  logout() {
    return apiClient.post('/users/logout/');
  },
  getProfile() {
    return apiClient.get('/users/profile/');
  },
  updateProfile(profileData) {
    return apiClient.put('/users/profile/update/', profileData);
  },
};

// 매치 관련 API
export const matchAPI = {
  getMatches(params) {
    return apiClient.get('/matches/', { params });
  },
  getMatch(id) {
    return apiClient.get(`/matches/${id}/`);
  },
  createMatch(matchData) {
    return apiClient.post('/matches/create/', matchData);
  },
  updateMatch(id, matchData) {
    return apiClient.put(`/matches/${id}/update/`, matchData);
  },
  deleteMatch(id) {
    return apiClient.delete(`/matches/${id}/delete/`);
  },
  joinMatch(id) {
    return apiClient.post(`/matches/${id}/join/`);
  },
  leaveMatch(id) {
    return apiClient.post(`/matches/${id}/leave/`);
  },
  getParticipants(id) {
    return apiClient.get(`/matches/${id}/participants/`);
  },
  getMatchResult(id) {
    return apiClient.get(`/matches/${id}/result/`);
  },
  createMatchResult(id, resultData) {
    return apiClient.post(`/matches/${id}/result/create/`, resultData);
  },
};

// 구장 관련 API
export const venueAPI = {
  getVenues(params) {
    return apiClient.get('/venues/', { params });
  },
  getVenue(id) {
    return apiClient.get(`/venues/${id}/`);
  },
  createVenueReview(id, reviewData) {
    return apiClient.post(`/venues/${id}/reviews/`, reviewData);
  },
};

// 팀 관련 API
export const teamAPI = {
  getTeams(params) {
    return apiClient.get('/teams/', { params });
  },
  getTeam(id) {
    return apiClient.get(`/teams/${id}/`);
  },
  createTeam(teamData) {
    return apiClient.post('/teams/create/', teamData);
  },
  updateTeam(id, teamData) {
    return apiClient.put(`/teams/${id}/update/`, teamData);
  },
  deleteTeam(id) {
    return apiClient.delete(`/teams/${id}/delete/`);
  },
  joinTeam(id, requestData) {
    return apiClient.post(`/teams/${id}/join/`, requestData);
  },
  leaveTeam(id) {
    return apiClient.post(`/teams/${id}/leave/`);
  },
  getMembers(id) {
    return apiClient.get(`/teams/${id}/members/`);
  },
  getJoinRequests(id) {
    return apiClient.get(`/teams/${id}/requests/`);
  },
  approveJoinRequest(teamId, requestId) {
    return apiClient.post(`/teams/${teamId}/requests/${requestId}/approve/`);
  },
  rejectJoinRequest(teamId, requestId) {
    return apiClient.post(`/teams/${teamId}/requests/${requestId}/reject/`);
  },
};

export default apiClient; 