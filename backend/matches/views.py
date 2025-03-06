from django.shortcuts import render
from rest_framework import generics, permissions

# Create your views here.

# 임시 뷰 클래스 (나중에 구현 예정)
class MatchListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return []  # 임시로 빈 리스트 반환

class MatchCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

class MatchDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

class MatchUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

class MatchDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

class MatchJoinView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

class MatchLeaveView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

class MatchParticipantsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

class MatchResultView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

class MatchResultCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
