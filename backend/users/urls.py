from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    # 인증 관련 URL
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    
    # 사용자 관련 URL
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile_update'),
    path('profile/<str:username>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # 사용자 검색 API
    path('search/', views.UserSearchView.as_view(), name='user_search'),
    
    # 사용자 ID로 프로필 조회
    path('<int:pk>/', views.UserDetailByIdView.as_view(), name='user_detail_by_id'),
    path('<int:pk>/teams/', views.UserTeamsView.as_view(), name='user_teams'),
    path('<int:pk>/matches/', views.UserMatchesView.as_view(), name='user_matches'),
    
    # 친구 관련 URL
    path('friends/', views.FriendshipListView.as_view(), name='friend_list'),
    path('friends/requests/', views.FriendRequestListView.as_view(), name='friend_request_list'),
    path('friends/requests/sent/', views.FriendRequestSentListView.as_view(), name='friend_request_sent_list'),
    path('friends/requests/create/', views.FriendRequestCreateView.as_view(), name='friend_request_create'),
    path('friends/requests/<int:pk>/accept/', views.FriendRequestAcceptView.as_view(), name='friend_request_accept'),
    path('friends/requests/<int:pk>/reject/', views.FriendRequestRejectView.as_view(), name='friend_request_reject'),
    path('friends/<int:pk>/delete/', views.FriendshipDeleteView.as_view(), name='friendship_delete'),
] 