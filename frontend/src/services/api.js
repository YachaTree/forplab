import axios from 'axios';

// API 기본 URL 설정
const API_URL = 'http://localhost:8000/api/v1';

// 캐시 설정
const CACHE_DURATION = 5 * 60 * 1000; // 5분 (밀리초)
const apiCache = {
  data: {},
  
  // 캐시에 데이터 저장
  set(key, data) {
    this.data[key] = {
      data,
      timestamp: Date.now()
    };
  },
  
  // 캐시에서 데이터 가져오기
  get(key) {
    const cached = this.data[key];
    if (!cached) return null;
    
    // 캐시 만료 확인
    const now = Date.now();
    if (now - cached.timestamp > CACHE_DURATION) {
      delete this.data[key];
      return null;
    }
    
    return cached.data;
  },
  
  // 캐시 키 생성
  createKey(method, url, params) {
    return `${method}:${url}:${JSON.stringify(params || {})}`;
  },
  
  // 특정 패턴의 캐시 무효화
  invalidate(pattern) {
    for (const key in this.data) {
      if (key.includes(pattern)) {
        delete this.data[key];
      }
    }
  }
};

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
    
    // 캐싱 설정
    if (config.method === 'get' && config.cache !== false) {
      const cacheKey = apiCache.createKey(config.method, config.url, config.params);
      const cachedData = apiCache.get(cacheKey);
      
      if (cachedData) {
        console.log('캐시된 데이터 사용:', cacheKey);
        
        // 캐시된 데이터가 있으면 요청 취소하고 캐시된 데이터 반환
        config.adapter = () => {
          return Promise.resolve({
            data: cachedData,
            status: 200,
            statusText: 'OK',
            headers: {},
            config,
            request: {}
          });
        };
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 토큰 만료 처리 및 캐싱
apiClient.interceptors.response.use(
  (response) => {
    // GET 요청 결과 캐싱
    if (response.config.method === 'get' && response.config.cache !== false) {
      const cacheKey = apiCache.createKey(
        response.config.method,
        response.config.url,
        response.config.params
      );
      
      apiCache.set(cacheKey, response.data);
      console.log('응답 데이터 캐싱:', cacheKey);
    }
    
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
    console.log('프로필 업데이트 요청:', profileData);
    
    // FormData 내용 디버깅
    if (profileData instanceof FormData) {
      console.log('FormData 내용 (API 서비스):');
      for (let [key, value] of profileData.entries()) {
        console.log(`${key}: ${value instanceof File ? `${value.name} (${value.type}, ${value.size} bytes)` : value}`);
      }
    }
    
    // multipart/form-data는 axios가 자동으로 설정하므로 Content-Type 헤더를 명시적으로 설정하지 않음
    // 하지만 일부 브라우저에서는 명시적으로 설정해야 할 수 있음
    const headers = {
      'Content-Type': 'multipart/form-data'
    };
    
    // 프로필 업데이트 후 관련 캐시 무효화
    return apiClient.put('/users/profile/update/', profileData, { headers })
      .then(response => {
        // 사용자 관련 캐시 무효화
        apiCache.invalidate('/users/profile');
        apiCache.invalidate(`/users/${response.data.user.id}`);
        return response;
      });
  },
  searchUsers(params) {
    console.log('사용자 검색 요청:', params);
    return apiClient.get('/users/search/', { params })
      .then(response => {
        console.log('사용자 검색 응답:', response.data);
        return response;
      })
      .catch(error => {
        console.error('사용자 검색 실패:', error.response ? error.response.data : error.message);
        throw error;
      });
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