# 플랩풋볼 클론 프로젝트 개발 계획

## 프로젝트 개요
마이플레이컴퍼니의 플랩풋볼 서비스를 모티브로 한 축구 매칭 플랫폼 클론 프로젝트입니다. 이 프로젝트는 백엔드 개발자 포트폴리오 목적으로 개발됩니다.

## 기술 스택
- **백엔드**: Python, Django REST Framework
- **프론트엔드**: Vue.js 3, Vuex, Vue Router
- **데이터베이스**: PostgreSQL
- **인프라**: Docker, AWS (EC2, RDS, ECR)
- **CI/CD**: GitHub Actions

## 개발 일정 (총 7주)

### 1. 프로젝트 계획 (1주차)

#### 1-1. 요구사항 정의 (1-2일)
- 축구 매칭 서비스의 핵심 기능 정의
- 사용자 스토리 작성
- MVP 범위 설정

#### 1-2. 기술 스택 확정 (1일)
- 백엔드, 프론트엔드, 인프라 기술 스택 결정
- 개발 환경 설계

#### 1-3. 데이터베이스 설계 (1-2일)
- ERD 작성
- 테이블 관계 정의
- 인덱스 설계

### 2. Docker 기반 개발 환경 구성 (2-3일)

#### 2-1. 프로젝트 구조 설정
```
forplab/
├── backend/             # Django 프로젝트
├── frontend/            # Vue.js 프로젝트
├── docker-compose.yml   # 개발 환경 설정
├── .github/             # GitHub Actions
└── README.md
```

#### 2-2. Docker 설정 파일 작성
- 백엔드 Dockerfile
- 프론트엔드 Dockerfile
- docker-compose.yml

#### 2-3. 프로젝트 초기화
- Django 프로젝트 생성
- Vue.js 프로젝트 생성
- 버전 관리 설정

### 3. 백엔드 개발 (2-3주차)

#### 3-1. Django 앱 생성 및 설정
- users 앱: 사용자 관리
- matches 앱: 매치 관리
- venues 앱: 구장 관리
- teams 앱: 팀 관리

#### 3-2. 데이터 모델 설계 및 구현
- 사용자 모델 (User)
- 매치 모델 (Match)
- 구장 모델 (Venue)
- 팀 모델 (Team)
- 참가 모델 (Participation)

#### 3-3. API 엔드포인트 개발
- 사용자 인증 API (JWT 기반)
- 매치 CRUD API
- 구장 정보 API
- 매치 참가 API
- 팀 관리 API

#### 3-4. 비즈니스 로직 구현
- 매칭 알고리즘
- 레이팅 시스템
- 예약 시스템

### 4. 프론트엔드 개발 (3-4주차)

#### 4-1. Vue.js 프로젝트 구조화
- 컴포넌트 설계
- Vuex 스토어 설정
- 라우팅 설정

#### 4-2. 주요 페이지 구현
- 로그인/회원가입
- 매치 목록/상세
- 구장 목록/상세
- 프로필 관리
- 매치 참가 신청

#### 4-3. API 연동
- Axios를 사용한 백엔드 API 연동
- 인증 토큰 관리

### 5. AWS 배포 준비 (5주차)

#### 5-1. 프로덕션 Docker 설정
- 멀티스테이지 빌드 설정
- 보안 강화

#### 5-2. AWS 인프라 구성
- ECR 레포지토리 생성
- ECS/Fargate 설정
- RDS 데이터베이스 설정

#### 5-3. CI/CD 파이프라인 구성
- GitHub Actions 워크플로우 설정
- 자동 테스트 및 배포

### 6. 테스트 및 문서화 (6주차)

#### 6-1. 테스트 작성
- 단위 테스트
- 통합 테스트

#### 6-2. 문서화
- API 문서 (Swagger)
- README 작성
- 아키텍처 다이어그램

### 7. 포트폴리오 정리 (7주차)

#### 7-1. 프로젝트 요약 작성
- 기술적 도전과 해결책
- 배운 점과 개선할 점

#### 7-2. 시연 영상 제작
- 주요 기능 시연
- 기술적 특징 설명

## 주요 기능

### 사용자 관리
- 회원가입/로그인
- 프로필 관리
- 레이팅 시스템

### 매치 관리
- 매치 생성/조회/수정/삭제
- 매치 참가 신청
- 매치 결과 등록

### 구장 관리
- 구장 정보 조회
- 구장 예약 시스템

### 팀 관리
- 팀 생성/조회/수정/삭제
- 팀원 관리
- 팀 매치 관리

## 개발 환경 설정 가이드

### 필수 설치 항목
- Docker & Docker Compose
- Git

### 개발 환경 실행 방법
```bash
# 레포지토리 클론
git clone <repository-url>
cd forplab

# Docker 컨테이너 실행
docker-compose up -d

# 백엔드 마이그레이션
docker-compose exec backend python manage.py migrate

# 개발 서버 접속
# 백엔드: http://localhost:8000
# 프론트엔드: http://localhost:8080
```

## 배포 가이드

### AWS 배포 준비
1. AWS IAM 사용자 생성 (ECR, ECS 권한)
2. GitHub Secrets 설정
3. ECR 레포지토리 생성
4. ECS 클러스터 및 서비스 설정

### 배포 실행
```bash
# main 브랜치에 푸시하면 자동 배포
git push origin main
```

## 프로젝트 관리

### 브랜치 전략
- main: 배포 브랜치
- develop: 개발 브랜치
- feature/*: 기능 개발 브랜치

### 이슈 관리
- GitHub Issues 활용
- 작업 단위로 이슈 생성
- PR과 이슈 연결

## 참고 자료
- [Django 공식 문서](https://docs.djangoproject.com/)
- [Vue.js 공식 문서](https://vuejs.org/guide/introduction.html)
- [Docker 공식 문서](https://docs.docker.com/)
- [AWS 공식 문서](https://docs.aws.amazon.com/) 