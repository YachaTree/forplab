from django.shortcuts import render
from rest_framework import generics, permissions

# Create your views here.

# 임시 뷰 클래스 (나중에 구현 예정)
class TeamListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return []  # 임시로 빈 리스트 반환

class TeamCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

class TeamDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

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
