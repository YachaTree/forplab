FROM node:16-alpine

WORKDIR /app

# 의존성 설치
COPY package*.json ./
RUN npm install

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8080

# 개발 서버 실행
CMD ["npm", "run", "serve"] 