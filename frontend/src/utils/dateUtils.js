/**
 * 날짜를 포맷팅하는 유틸리티 함수
 * @param {string} dateString - ISO 형식의 날짜 문자열
 * @param {object} options - Intl.DateTimeFormat 옵션
 * @returns {string} 포맷팅된 날짜 문자열
 */
export function formatDate(dateString, options = {}) {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  
  // 기본 옵션
  const defaultOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    ...options
  };
  
  // 시간 정보가 필요 없는 경우 옵션에서 제외
  if (options.dateOnly) {
    delete defaultOptions.hour;
    delete defaultOptions.minute;
    delete options.dateOnly;
  }
  
  return new Intl.DateTimeFormat('ko-KR', defaultOptions).format(date);
}

/**
 * 상대적 시간을 표시하는 함수 (예: '3일 전', '방금 전')
 * @param {string} dateString - ISO 형식의 날짜 문자열
 * @returns {string} 상대적 시간 문자열
 */
export function timeAgo(dateString) {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now - date) / 1000);
  
  // 시간 간격 계산
  const intervals = {
    년: 31536000,
    개월: 2592000,
    주: 604800,
    일: 86400,
    시간: 3600,
    분: 60,
    초: 1
  };
  
  // 가장 적합한 시간 단위 찾기
  for (const [unit, secondsInUnit] of Object.entries(intervals)) {
    const interval = Math.floor(seconds / secondsInUnit);
    
    if (interval >= 1) {
      return `${interval}${unit} 전`;
    }
  }
  
  return '방금 전';
} 