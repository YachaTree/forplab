from django.urls import path
from . import views

app_name = 'venues'

urlpatterns = [
    # 구장 관련 URL
    path('', views.VenueListView.as_view(), name='venue_list'),
    path('<int:pk>/', views.VenueDetailView.as_view(), name='venue_detail'),
    path('search/', views.VenueSearchView.as_view(), name='venue_search'),
    
    # 구장 리뷰 관련 URL
    path('<int:venue_id>/reviews/', views.VenueReviewListView.as_view(), name='venue_review_list'),
    path('<int:venue_id>/reviews/create/', views.VenueReviewCreateView.as_view(), name='venue_review_create'),
    path('<int:venue_id>/reviews/<int:review_id>/', views.VenueReviewDetailView.as_view(), name='venue_review_detail'),
    
    # 구장 이미지 관련 URL
    path('<int:venue_id>/images/', views.VenueImageListView.as_view(), name='venue_image_list'),
] 