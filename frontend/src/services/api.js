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
    // 네트워크 오류 처리
    if (!error.response) {
      console.error('네트워크 오류 발생:', error.message);
      // 네트워크 오류 발생 시 사용자에게 알림
      if (error.message === 'Network Error') {
        console.error('서버에 연결할 수 없습니다. 네트워크 연결을 확인하거나 서버가 실행 중인지 확인하세요.');
      }
      return Promise.reject(error);
    }
    
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
    console.log('API 로그인 요청:', credentials);
    // 백엔드 API가 username 필드를 사용하므로 email이 있으면 username으로 변환
    const data = { ...credentials };
    if (data.email && !data.username) {
      data.username = data.email;
      delete data.email;
    }
    console.log('변환된 로그인 요청:', data);
    
    // 로그인 요청 시 추가 디버깅 정보
    return apiClient.post('/users/token/', data)
      .then(response => {
        console.log('로그인 성공 응답:', response.data);
        return response;
      })
      .catch(error => {
        console.error('로그인 실패 응답:', error.response ? error.response.data : error.message);
        throw error;
      });
  },
  register(userData) {
    return apiClient.post('/users/register/', userData);
  },
  logout() {
    // 백엔드에 로그아웃 API가 없으므로 성공한 것처럼 빈 객체를 반환
    return Promise.resolve({});
  },
  getProfile() {
    return apiClient.get('/users/profile/');
  },
  getUserProfile(userId) {
    console.log('API 호출: getUserProfile, userId:', userId);
    return apiClient.get(`/users/${userId}/`)
      .then(response => {
        console.log('getUserProfile 응답:', response.data);
        return response;
      })
      .catch(error => {
        console.error('getUserProfile 에러:', error.response ? error.response.data : error.message);
        throw error;
      });
  },
  getUserTeams(userId) {
    return apiClient.get(`/users/${userId}/teams/`);
  },
  getUserMatches(userId) {
    return apiClient.get(`/users/${userId}/matches/`);
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
    return apiClient.post('/teams/create/', teamData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  updateTeam(id, teamData) {
    return apiClient.put(`/teams/${id}/update/`, teamData);
  },
  deleteTeam(id) {
    // ID를 문자열로 변환하여 전달
    return apiClient.delete(`/teams/${String(id)}/delete/`, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
  },
  joinTeam(id, requestData) {
    return apiClient.post(`/teams/${id}/join-requests/create/`, requestData);
  },
  leaveTeam(id) {
    return apiClient.post(`/teams/${id}/leave/`);
  },
  cancelJoinRequest(id) {
    return apiClient.post(`/teams/${id}/cancel-request/`);
  },
  getMembers(id) {
    return apiClient.get(`/teams/${id}/members/`);
  },
  getJoinRequests(id) {
    return apiClient.get(`/teams/${id}/requests/`);
  },
  updateMemberRole(teamId, memberId, roleData) {
    return apiClient.put(`/teams/${teamId}/members/${memberId}/update/`, roleData);
  },
  removeMember(teamId, memberId) {
    return apiClient.delete(`/teams/${teamId}/members/${memberId}/remove/`);
  },
  acceptJoinRequest(teamId, requestId) {
    return apiClient.post(`/teams/${teamId}/join-requests/${requestId}/accept/`);
  },
  rejectJoinRequest(teamId, requestId) {
    return apiClient.post(`/teams/${teamId}/join-requests/${requestId}/reject/`);
  },
};

export default apiClient; 