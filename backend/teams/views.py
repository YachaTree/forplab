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
    serializer_class = TeamCreateSerializer
    queryset = Team.objects.all()
    
    def update(self, request, *args, **kwargs):
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
            if isinstance(data['is_recruiting'], str):
                if data['is_recruiting'].lower() == 'true':
                    data['is_recruiting'] = True
                elif data['is_recruiting'].lower() == 'false':
                    data['is_recruiting'] = False
        
        # 수정된 데이터로 요청 객체 업데이트
        request._full_data = data
        
        return super().update(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        # 팀 소유자만 업데이트할 수 있도록 권한 확인
        instance = self.get_object()
        if instance.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("팀 소유자만 팀 정보를 수정할 수 있습니다.")
        
        serializer.save()

class TeamDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Team.objects.all()
    
    def perform_destroy(self, instance):
        # 팀 소유자만 삭제할 수 있도록 권한 확인
        if instance.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("팀 소유자만 팀을 삭제할 수 있습니다.")
        
        # 팀 삭제 수행
        instance.delete()

class TeamMemberListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeamMemberSerializer
    
    def get_queryset(self):
        team_id = self.kwargs.get('team_id')
        return TeamMember.objects.filter(team_id=team_id)

class TeamMemberDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeamMemberSerializer
    
    def get_object(self):
        team_id = self.kwargs.get('team_id')
        user_id = self.kwargs.get('user_id')
        return TeamMember.objects.get(team_id=team_id, user_id=user_id)

class TeamMemberUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeamMemberSerializer
    
    def get_object(self):
        team_id = self.kwargs.get('team_id')
        user_id = self.kwargs.get('user_id')
        return TeamMember.objects.get(team_id=team_id, user_id=user_id)
    
    def perform_update(self, serializer):
        # 팀 소유자만 팀원 역할을 변경할 수 있도록 권한 확인
        team_id = self.kwargs.get('team_id')
        team = Team.objects.get(id=team_id)
        
        if team.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("팀 소유자만 팀원 역할을 변경할 수 있습니다.")
        
        serializer.save()

class TeamMemberRemoveView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        team_id = self.kwargs.get('team_id')
        user_id = self.kwargs.get('user_id')
        return TeamMember.objects.get(team_id=team_id, user_id=user_id)
    
    def perform_destroy(self, instance):
        # 팀 소유자만 팀원을 제외할 수 있도록 권한 확인
        team = instance.team
        
        # 팀 소유자이거나 자기 자신을 제외하는 경우에만 허용
        if team.owner != self.request.user and instance.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("팀 소유자만 다른 팀원을 제외할 수 있습니다.")
        
        # 팀 소유자는 제외할 수 없음
        if instance.user == team.owner:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("팀 소유자는 제외할 수 없습니다.")
        
        instance.delete()

class TeamJoinRequestListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeamJoinRequestSerializer
    
    def get_queryset(self):
        team_id = self.kwargs.get('team_id')
        team = Team.objects.get(id=team_id)
        
        # 팀 소유자만 가입 신청 목록을 볼 수 있음
        if team.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("팀 소유자만 가입 신청 목록을 볼 수 있습니다.")
        
        return TeamJoinRequest.objects.filter(team_id=team_id)

class TeamJoinRequestCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeamJoinRequestSerializer
    
    def perform_create(self, serializer):
        team_id = self.kwargs.get('team_id')
        team = Team.objects.get(id=team_id)
        
        # 이미 팀원인 경우 가입 신청 불가
        if TeamMember.objects.filter(team=team, user=self.request.user).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("이미 팀원입니다.")
        
        # 이미 가입 신청한 경우 중복 신청 불가
        if TeamJoinRequest.objects.filter(team=team, user=self.request.user).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("이미 가입 신청을 했습니다.")
        
        serializer.save(team=team, user=self.request.user)

class TeamJoinRequestAcceptView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        from rest_framework.response import Response
        from rest_framework import status
        
        team_id = self.kwargs.get('team_id')
        request_id = self.kwargs.get('request_id')
        
        try:
            team = Team.objects.get(id=team_id)
            join_request = TeamJoinRequest.objects.get(id=request_id, team=team)
            
            # 팀 소유자만 가입 신청을 수락할 수 있음
            if team.owner != self.request.user:
                return Response(
                    {"detail": "팀 소유자만 가입 신청을 수락할 수 있습니다."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 팀원 생성
            TeamMember.objects.create(
                team=team,
                user=join_request.user,
                role='MEMBER',
                position=join_request.position
            )
            
            # 가입 신청 삭제
            join_request.delete()
            
            return Response(
                {"detail": "가입 신청이 수락되었습니다."},
                status=status.HTTP_200_OK
            )
        except Team.DoesNotExist:
            return Response(
                {"detail": "팀을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )
        except TeamJoinRequest.DoesNotExist:
            return Response(
                {"detail": "가입 신청을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

class TeamJoinRequestRejectView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        from rest_framework.response import Response
        from rest_framework import status
        
        team_id = self.kwargs.get('team_id')
        request_id = self.kwargs.get('request_id')
        
        try:
            team = Team.objects.get(id=team_id)
            join_request = TeamJoinRequest.objects.get(id=request_id, team=team)
            
            # 팀 소유자만 가입 신청을 거절할 수 있음
            if team.owner != self.request.user:
                return Response(
                    {"detail": "팀 소유자만 가입 신청을 거절할 수 있습니다."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 가입 신청 삭제
            join_request.delete()
            
            return Response(
                {"detail": "가입 신청이 거절되었습니다."},
                status=status.HTTP_200_OK
            )
        except Team.DoesNotExist:
            return Response(
                {"detail": "팀을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )
        except TeamJoinRequest.DoesNotExist:
            return Response(
                {"detail": "가입 신청을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )
