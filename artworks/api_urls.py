from django.urls import path
from .api_views import (
    ArtworkListView,
    ArtworkDetailView
)

urlpatterns = [
    # 작품 리소스 관리 
    path('', ArtworkListView.as_view(), name='api_artwork_list'),  
    path('<int:pk>/', ArtworkDetailView.as_view(), name='api_artwork_detail'),  
] 