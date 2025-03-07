from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import TeamSerializer, TeamDetailSerializer, TeamCreateSerializer, TeamMemberSerializer, TeamJoinRequestSerializer
from .models import Team, TeamMember, TeamJoinRequest

# Create your views here.

# 임시 뷰 클래스 (나중에 구현 예정)
class TeamListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeamSerializer
    
    def get_queryset(self):
        queryset = Team.objects.all()
        
        # 필터링 적용
        region = self.request.query_params.get('region', None)
        level = self.request.query_params.get('level', None)
        is_recruiting = self.request.query_params.get('is_recruiting', None)
        search = self.request.query_params.get('search', None)
        
        if region:
            queryset = queryset.filter(region=region)
        
        if level:
            # 프론트엔드 값을 백엔드 값으로 변환
            level_map = {
                'beginner': 'BEG',
                'intermediate': 'INT',
                'advanced': 'ADV',
                'professional': 'PRO'
            }
            backend_level = level_map.get(level, level)
            queryset = queryset.filter(level=backend_level)
        
        if is_recruiting:
            is_recruiting_bool = is_recruiting.lower() == 'true'
            queryset = queryset.filter(is_recruiting=is_recruiting_bool)
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset

class TeamCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeamCreateSerializer
    
    def create(self, request, *args, **kwargs):
        # 프론트엔드에서 보내는 level 값을 백엔드 값으로 변환
        data = request.data.copy()
        if 'level' in data:
            level_map = {
                'beginner': 'BEG',
                'intermediate': 'INT',
                'advanced': 'ADV',
                'professional': 'PRO'
            }
            if data['level'] in level_map:
                data['level'] = level_map[data['level']]
        
        # 불리언 필드 처리
        if 'is_recruiting' in data:
            if data['is_recruiting'].lower() == 'true':
                data['is_recruiting'] = True
            elif data['is_recruiting'].lower() == 'false':
                data['is_recruiting'] = False
        
        # 수정된 데이터로 요청 객체 업데이트
        request._full_data = data
        
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save()

class TeamDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeamDetailSerializer
    queryset = Team.objects.all()

class TeamUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

class TeamDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

class TeamMemberListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

class TeamMemberDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

class TeamMemberUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

class TeamMemberRemoveView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

class TeamJoinRequestListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

class TeamJoinRequestCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

class TeamJoinRequestAcceptView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

class TeamJoinRequestRejectView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
