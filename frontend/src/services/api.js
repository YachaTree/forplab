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
  // 로그인
  login: (username, password) => {
    return apiClient.post('/users/token/', { username, password });
  },
  
  // 회원가입
  register: (userData) => {
    return apiClient.post('/users/register/', userData);
  },
  
  // 사용자 프로필 조회
  getProfile: () => {
    return apiClient.get('/users/profile/');
  },
  
  // 사용자 프로필 업데이트
  updateProfile: (profileData) => {
    return apiClient.put('/users/profile/update/', profileData);
  },
  
  // 비밀번호 변경
  changePassword: (passwordData) => {
    return apiClient.post('/users/password/change/', passwordData);
  },
};

// 매치 관련 API
export const matchAPI = {
  // 매치 목록 조회
  getMatches: (params) => {
    return apiClient.get('/matches/', { params });
  },
  
  // 매치 상세 조회
  getMatch: (id) => {
    return apiClient.get(`/matches/${id}/`);
  },
  
  // 매치 생성
  createMatch: (matchData) => {
    return apiClient.post('/matches/create/', matchData);
  },
  
  // 매치 참가
  joinMatch: (matchId) => {
    return apiClient.post(`/matches/${matchId}/join/`);
  },
  
  // 매치 참가 취소
  leaveMatch: (matchId) => {
    return apiClient.post(`/matches/${matchId}/leave/`);
  },
};

// 구장 관련 API
export const venueAPI = {
  // 구장 목록 조회
  getVenues: (params) => {
    return apiClient.get('/venues/', { params });
  },
  
  // 구장 상세 조회
  getVenue: (id) => {
    return apiClient.get(`/venues/${id}/`);
  },
  
  // 구장 검색
  searchVenues: (query) => {
    return apiClient.get('/venues/search/', { params: { query } });
  },
};

// 팀 관련 API
export const teamAPI = {
  // 팀 목록 조회
  getTeams: (params) => {
    return apiClient.get('/teams/', { params });
  },
  
  // 팀 상세 조회
  getTeam: (id) => {
    return apiClient.get(`/teams/${id}/`);
  },
  
  // 팀 생성
  createTeam: (teamData) => {
    return apiClient.post('/teams/create/', teamData);
  },
  
  // 팀 가입 요청
  requestJoin: (teamId, message) => {
    return apiClient.post(`/teams/${teamId}/join-requests/create/`, { message });
  },
};

export default apiClient; 