from django.urls import path
from .api_views import (
    ArtistListView,
    ArtistDetailView,
    ArtistApplicationListView,
    ArtistApplicationDetailView,
    my_artist_profile,
    my_artist_application_status,
    artist_dashboard_data,
    create_exhibition,
    artist_artworks,
    check_artist_status
)

urlpatterns = [
    # 작가 리소스 관리
    path('', ArtistListView.as_view(), name='api_artist_list'),
    path('<int:pk>/', ArtistDetailView.as_view(), name='api_artist_detail'),
    path('me/', my_artist_profile, name='api_my_artist_profile'),
    path('me/status/', check_artist_status, name='api_check_artist_status'),
    path('me/dashboard/', artist_dashboard_data, name='api_artist_dashboard'),
    path('me/artworks/', artist_artworks, name='api_artist_artworks'),  
    path('me/exhibitions/', create_exhibition, name='api_create_exhibition'),
    
    # 작가 신청 리소스 관리
    path('applications/', ArtistApplicationListView.as_view(), name='api_artist_application_list'),
    path('applications/<int:pk>/', ArtistApplicationDetailView.as_view(), name='api_artist_application_detail'),
    path('applications/me/', my_artist_application_status, name='api_my_artist_application_status'),
] 