from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import Match, MatchParticipant, MatchResult
from .serializers import (
    MatchListSerializer,
    MatchDetailSerializer,
    MatchCreateSerializer,
    MatchUpdateSerializer,
    MatchParticipantSerializer,
    MatchResultCreateSerializer
)
from .filters import MatchFilter

# Create your views here.

# 임시 뷰 클래스 (나중에 구현 예정)
class MatchListView(generics.ListAPIView):
    """
    매치 목록 조회 뷰
    """
    serializer_class = MatchListSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = MatchFilter
    ordering_fields = ['date', 'start_time', 'price']
    ordering = ['date', 'start_time']
    
    def get_queryset(self):
        return Match.objects.all().select_related('venue', 'host')

class MatchCreateView(generics.CreateAPIView):
    """
    매치 생성 뷰
    """
    serializer_class = MatchCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

class MatchDetailView(generics.RetrieveAPIView):
    """
    매치 상세 조회 뷰
    """
    queryset = Match.objects.all()
    serializer_class = MatchDetailSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

class MatchUpdateView(generics.UpdateAPIView):
    """
    매치 수정 뷰
    """
    queryset = Match.objects.all()
    serializer_class = MatchUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context
    
    def perform_update(self, serializer):
        match = self.get_object()
        
        # 매치 호스트만 수정 가능
        if match.host != self.request.user:
            self.permission_denied(self.request, message="매치 호스트만 수정할 수 있습니다.")
        
        serializer.save()

class MatchDeleteView(generics.DestroyAPIView):
    """
    매치 삭제 뷰
    """
    queryset = Match.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_destroy(self, instance):
        # 매치 호스트만 삭제 가능
        if instance.host != self.request.user:
            self.permission_denied(self.request, message="매치 호스트만 삭제할 수 있습니다.")
        
        # 이미 시작된 매치는 삭제 불가
        if instance.is_past:
            self.permission_denied(self.request, message="이미 종료된 매치는 삭제할 수 없습니다.")
        
        instance.delete()

class MatchJoinView(APIView):
    """
    매치 참가 신청 뷰
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, match_id):
        match = get_object_or_404(Match, id=match_id)
        user = request.user
        
        # 이미 참가 신청한 경우
        if MatchParticipant.objects.filter(match=match, user=user).exists():
            return Response({"detail": "이미 참가 신청한 매치입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 매치가 모집 중이 아닌 경우
        if match.status != 'OPEN':
            return Response({"detail": "모집 중인 매치가 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 매치가 가득 찬 경우
        if match.current_players.count() >= match.max_players:
            return Response({"detail": "매치 인원이 가득 찼습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 참가 신청
        participant = MatchParticipant.objects.create(
            match=match,
            user=user,
            status='REGISTERED'
        )
        
        # 매치가 가득 찼는지 확인하고 상태 업데이트
        if match.current_players.count() >= match.max_players:
            match.status = 'CLOSED'
            match.save()
        
        serializer = MatchParticipantSerializer(participant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MatchLeaveView(APIView):
    """
    매치 참가 취소 뷰
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, match_id):
        match = get_object_or_404(Match, id=match_id)
        user = request.user
        
        # 참가 신청한 적이 없는 경우
        participant = MatchParticipant.objects.filter(match=match, user=user).first()
        if not participant:
            return Response({"detail": "참가 신청한 적이 없는 매치입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 매치가 이미 시작된 경우
        if match.is_past:
            return Response({"detail": "이미 종료된 매치는 취소할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 참가 취소
        participant.status = 'CANCELED'
        participant.save()
        
        # 매치 상태 업데이트
        if match.status == 'CLOSED':
            match.status = 'OPEN'
            match.save()
        
        return Response({"detail": "매치 참가가 취소되었습니다."}, status=status.HTTP_200_OK)

class MatchParticipantsView(generics.ListAPIView):
    """
    매치 참가자 목록 조회 뷰
    """
    serializer_class = MatchParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        match_id = self.kwargs['match_id']
        return MatchParticipant.objects.filter(match_id=match_id)

class MatchResultView(generics.RetrieveAPIView):
    """
    매치 결과 조회 뷰
    """
    serializer_class = MatchResultCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        match_id = self.kwargs['match_id']
        return get_object_or_404(MatchResult, match_id=match_id)

class MatchResultCreateView(generics.CreateAPIView):
    """
    매치 결과 등록 뷰
    """
    serializer_class = MatchResultCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['match_id'] = self.kwargs['match_id']
        return context
    
    def perform_create(self, serializer):
        match_id = self.kwargs['match_id']
        match = get_object_or_404(Match, id=match_id)
        
        # 매치 호스트만 결과 등록 가능
        if match.host != self.request.user:
            self.permission_denied(self.request, message="매치 호스트만 결과를 등록할 수 있습니다.")
        
        # 이미 결과가 등록된 경우
        if hasattr(match, 'result'):
            self.permission_denied(self.request, message="이미 결과가 등록된 매치입니다.")
        
        # 아직 종료되지 않은 매치인 경우
        if not match.is_past:
            self.permission_denied(self.request, message="아직 종료되지 않은 매치입니다.")
        
        serializer.save()
