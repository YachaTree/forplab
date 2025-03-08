from django.shortcuts import render
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q
from .serializers import (
    UserSerializer, 
    UserRegistrationSerializer, 
    UserProfileUpdateSerializer,
    PasswordChangeSerializer
)

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    """
    사용자 회원가입 뷰
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # 회원가입 성공 응답
        return Response({
            "message": "회원가입이 성공적으로 완료되었습니다.",
            "user": UserSerializer(user, context=self.get_serializer_context()).data
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveAPIView):
    """
    사용자 프로필 조회 뷰
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class UserProfileUpdateView(generics.UpdateAPIView):
    """
    사용자 프로필 업데이트 뷰
    """
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            "message": "프로필이 성공적으로 업데이트되었습니다.",
            "user": UserSerializer(instance, context=self.get_serializer_context()).data
        })

class UserDetailView(generics.RetrieveAPIView):
    """
    다른 사용자 프로필 조회 뷰
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'

class UserDetailByIdView(generics.RetrieveAPIView):
    """
    사용자 ID로 프로필 조회 뷰
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserTeamsView(generics.ListAPIView):
    """
    사용자가 속한 팀 목록 조회 뷰
    """
    serializer_class = UserSerializer  # 실제로는 TeamSerializer를 사용해야 함
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        from teams.models import Team, TeamMember
        from teams.serializers import TeamSerializer
        
        user_id = self.kwargs.get('pk')
        try:
            user = User.objects.get(id=user_id)
            # 사용자가 속한 팀 목록 조회
            team_members = TeamMember.objects.filter(user=user)
            teams = [tm.team for tm in team_members]
            return teams
        except User.DoesNotExist:
            return []
    
    def list(self, request, *args, **kwargs):
        from teams.serializers import TeamSerializer
        
        queryset = self.get_queryset()
        serializer = TeamSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

class UserMatchesView(generics.ListAPIView):
    """
    사용자가 참여한 경기 목록 조회 뷰
    """
    serializer_class = UserSerializer  # 실제로는 MatchSerializer를 사용해야 함
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        from matches.models import Match, MatchParticipant
        from matches.serializers import MatchSerializer
        
        user_id = self.kwargs.get('pk')
        try:
            user = User.objects.get(id=user_id)
            # 사용자가 참여한 경기 목록 조회
            match_participants = MatchParticipant.objects.filter(user=user)
            matches = [mp.match for mp in match_participants]
            return matches
        except User.DoesNotExist:
            return []
    
    def list(self, request, *args, **kwargs):
        from matches.serializers import MatchSerializer
        
        queryset = self.get_queryset()
        serializer = MatchSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

class PasswordChangeView(APIView):
    """
    비밀번호 변경 뷰
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "비밀번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserSearchView(generics.ListAPIView):
    """
    사용자 검색 API
    
    username, email, skill_level 등으로 사용자를 검색할 수 있습니다.
    ?search=검색어 형태로 요청하면 username과 email에서 검색합니다.
    ?skill_level=BEG 형태로 요청하면 특정 실력 수준의 사용자만 검색합니다.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # 실력 수준으로 필터링
        skill_level = self.request.query_params.get('skill_level', None)
        if skill_level:
            queryset = queryset.filter(skill_level=skill_level)
        
        # 추가 검색 조건
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) | 
                Q(email__icontains=search)
            )
        
        return queryset
