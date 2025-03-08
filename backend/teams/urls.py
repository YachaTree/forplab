from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    # 팀 관련 URL
    path('', views.TeamListView.as_view(), name='team_list'),
    path('create/', views.TeamCreateView.as_view(), name='team_create'),
    path('<int:pk>/', views.TeamDetailView.as_view(), name='team_detail'),
    path('<int:pk>/update/', views.TeamUpdateView.as_view(), name='team_update'),
    path('<int:pk>/delete/', views.TeamDeleteView.as_view(), name='team_delete'),
    
    # 팀 멤버 관련 URL
    path('<int:team_id>/members/', views.TeamMemberListView.as_view(), name='team_member_list'),
    path('<int:team_id>/members/<int:user_id>/', views.TeamMemberDetailView.as_view(), name='team_member_detail'),
    path('<int:team_id>/members/<int:user_id>/update/', views.TeamMemberUpdateView.as_view(), name='team_member_update'),
    path('<int:team_id>/members/<int:user_id>/remove/', views.TeamMemberRemoveView.as_view(), name='team_member_remove'),
    
    # 팀 가입 요청 관련 URL
    path('<int:team_id>/join-requests/', views.TeamJoinRequestListView.as_view(), name='team_join_request_list'),
    path('<int:team_id>/join-requests/create/', views.TeamJoinRequestCreateView.as_view(), name='team_join_request_create'),
    path('<int:team_id>/join-requests/<int:request_id>/accept/', views.TeamJoinRequestAcceptView.as_view(), name='team_join_request_accept'),
    path('<int:team_id>/join-requests/<int:request_id>/reject/', views.TeamJoinRequestRejectView.as_view(), name='team_join_request_reject'),
    
    # 팀 탈퇴 및 가입 신청 취소 URL
    path('<int:team_id>/leave/', views.TeamLeaveView.as_view(), name='team_leave'),
    path('<int:team_id>/cancel-request/', views.TeamCancelJoinRequestView.as_view(), name='team_cancel_join_request'),
] 