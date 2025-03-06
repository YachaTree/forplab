from django.shortcuts import render
from rest_framework import generics, permissions

# Create your views here.

# 임시 뷰 클래스 (나중에 구현 예정)
class VenueListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return []  # 임시로 빈 리스트 반환

class VenueDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

class VenueSearchView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

class VenueReviewListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

class VenueReviewCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

class VenueReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

class VenueImageListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
