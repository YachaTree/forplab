/**
 * 프로필 이미지 URL을 가져오는 유틸리티 함수
 * @param {Object|string} user - 사용자 객체 또는 이미지 경로
 * @returns {string} 완전한 이미지 URL
 */
export const getProfileImageUrl = (user) => {
  // 기본 이미지 경로
  const DEFAULT_PROFILE_IMAGE = require('@/assets/default-avatar.png');
  
  // user가 없거나 profile_image가 없는 경우 기본 이미지 반환
  if (!user || (typeof user === 'object' && !user.profile_image)) {
    return DEFAULT_PROFILE_IMAGE;
  }
  
  // user가 문자열인 경우 (직접 이미지 경로가 전달된 경우)
  const imageUrl = typeof user === 'object' ? user.profile_image : user;
  
  // 이미 완전한 URL인 경우
  if (imageUrl.startsWith('http')) {
    return imageUrl;
  } 
  // 미디어 경로인 경우
  else if (imageUrl.startsWith('/media')) {
    return `${process.env.VUE_APP_API_URL}${imageUrl}`;
  } 
  // 그 외의 경우
  else {
    return `${process.env.VUE_APP_API_URL}/media/${imageUrl}`;
  }
};

/**
 * 팀 로고 URL을 가져오는 유틸리티 함수
 * @param {Object|string} team - 팀 객체 또는 로고 경로
 * @returns {string} 완전한 로고 URL
 */
export const getTeamLogoUrl = (team) => {
  // 기본 팀 로고 경로
  const DEFAULT_TEAM_LOGO = require('@/assets/default-team.jpg');
  
  // team이 없거나 logo가 없는 경우 기본 이미지 반환
  if (!team || (typeof team === 'object' && !team.logo)) {
    return DEFAULT_TEAM_LOGO;
  }
  
  // team이 문자열인 경우 (직접 로고 경로가 전달된 경우)
  const logoUrl = typeof team === 'object' ? team.logo : team;
  
  // 이미 완전한 URL인 경우
  if (logoUrl.startsWith('http')) {
    return logoUrl;
  } 
  // 미디어 경로인 경우
  else if (logoUrl.startsWith('/media')) {
    return `${process.env.VUE_APP_API_URL}${logoUrl}`;
  } 
  // 그 외의 경우
  else {
    return `${process.env.VUE_APP_API_URL}/media/${logoUrl}`;
  }
};

/**
 * 캐시 방지를 위해 URL에 타임스탬프 추가
 * @param {string} url - 원본 URL
 * @returns {string} 타임스탬프가 추가된 URL
 */
export const addTimestampToUrl = (url) => {
  if (!url) return url;
  
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}t=${new Date().getTime()}`;
}; 