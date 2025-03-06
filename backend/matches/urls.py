from django.urls import path
from .views import (
    MatchListView, MatchDetailView, MatchCreateView, MatchUpdateView, 
    MatchDeleteView, MatchJoinView, MatchLeaveView, MatchParticipantsView,
    MatchResultView, MatchResultCreateView
)

app_name = 'matches'

urlpatterns = [
    # 매치 관련 URL
    path('', MatchListView.as_view(), name='match-list'),
    path('<int:pk>/', MatchDetailView.as_view(), name='match-detail'),
    path('create/', MatchCreateView.as_view(), name='match-create'),
    path('<int:pk>/update/', MatchUpdateView.as_view(), name='match-update'),
    path('<int:pk>/delete/', MatchDeleteView.as_view(), name='match-delete'),
    
    # 매치 참가 관련 URL
    path('<int:pk>/join/', MatchJoinView.as_view(), name='match-join'),
    path('<int:pk>/leave/', MatchLeaveView.as_view(), name='match-leave'),
    path('<int:pk>/participants/', MatchParticipantsView.as_view(), name='match-participants'),
    
    # 매치 결과 관련 URL
    path('<int:pk>/result/', MatchResultView.as_view(), name='match-result'),
    path('<int:pk>/result/create/', MatchResultCreateView.as_view(), name='match-result-create'),
] 