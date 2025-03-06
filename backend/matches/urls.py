from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    # 매치 관련 URL
    path('', views.MatchListView.as_view(), name='match_list'),
    path('create/', views.MatchCreateView.as_view(), name='match_create'),
    path('<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
    path('<int:pk>/update/', views.MatchUpdateView.as_view(), name='match_update'),
    path('<int:pk>/delete/', views.MatchDeleteView.as_view(), name='match_delete'),
    
    # 매치 참가 관련 URL
    path('<int:match_id>/join/', views.MatchJoinView.as_view(), name='match_join'),
    path('<int:match_id>/leave/', views.MatchLeaveView.as_view(), name='match_leave'),
    path('<int:match_id>/participants/', views.MatchParticipantsView.as_view(), name='match_participants'),
    
    # 매치 결과 관련 URL
    path('<int:match_id>/result/', views.MatchResultView.as_view(), name='match_result'),
    path('<int:match_id>/result/create/', views.MatchResultCreateView.as_view(), name='match_result_create'),
] 