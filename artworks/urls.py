from django.urls import path
from . import views

app_name = 'artworks'

urlpatterns = [
    path('', views.artwork_list_view, name='list'),
    path('<int:pk>/', views.artwork_detail_view, name='detail'),
]
