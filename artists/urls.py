from django.urls import path
from . import views

app_name = 'artists'

urlpatterns = [
    # 작가 관련 페이지
    path('', views.artist_list_view, name='list'),
    path('<int:pk>/', views.artist_detail_view, name='detail'),
    path('apply/', views.artist_apply_view, name='apply'),
    path('dashboard/', views.artist_dashboard_view, name='dashboard'),
    
    # 작품 관련 페이지
    path('artworks/create/', views.artwork_create_view, name='artwork_create'),
    
    # 전시 관련 페이지  
    path('exhibitions/create/', views.exhibition_create_view, name='exhibition_create'),
]
