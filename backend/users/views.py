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
    PasswordChangeSerializer,
    FriendshipSerializer,
    FriendshipCreateSerializer
)
from .models import Friendship

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
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        if not query:
            return User.objects.none()
        
        # 사용자 이름으로 검색
        queryset = User.objects.filter(username__icontains=query)
        
        # 현재 사용자는 검색 결과에서 제외
        current_user = self.request.user
        queryset = queryset.exclude(id=current_user.id)
        
        return queryset[:20]  # 최대 20명까지 반환

# 친구 관련 뷰
class FriendshipListView(generics.ListAPIView):
    """
    사용자의 친구 목록 조회 뷰
    """
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # 수락된 친구 관계만 조회
        return Friendship.objects.filter(
            (Q(from_user=user) | Q(to_user=user)) & Q(status='ACCEPTED')
        )

class FriendRequestListView(generics.ListAPIView):
    """
    사용자에게 온 친구 요청 목록 조회 뷰
    """
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # 대기 중인 친구 요청만 조회
        return Friendship.objects.filter(to_user=user, status='PENDING')

class FriendRequestSentListView(generics.ListAPIView):
    """
    사용자가 보낸 친구 요청 목록 조회 뷰
    """
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # 대기 중인 친구 요청만 조회
        return Friendship.objects.filter(from_user=user, status='PENDING')

class FriendRequestCreateView(generics.CreateAPIView):
    """
    친구 요청 보내기 뷰
    """
    serializer_class = FriendshipCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()
        
        # 알림 생성 (나중에 구현)
        # to_user에게 친구 요청 알림 보내기

class FriendRequestAcceptView(generics.UpdateAPIView):
    """
    친구 요청 수락 뷰
    """
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Friendship.objects.filter(to_user=self.request.user, status='PENDING')
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'ACCEPTED'
        instance.save()
        
        # 알림 생성 (나중에 구현)
        # from_user에게 친구 요청 수락 알림 보내기
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class FriendRequestRejectView(generics.UpdateAPIView):
    """
    친구 요청 거절 뷰
    """
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Friendship.objects.filter(to_user=self.request.user, status='PENDING')
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'REJECTED'
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class FriendshipDeleteView(generics.DestroyAPIView):
    """
    친구 관계 삭제 뷰
    """
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Friendship.objects.filter(
            (Q(from_user=user) | Q(to_user=user)) & Q(status='ACCEPTED')
        )
