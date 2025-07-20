from django.urls import path
from .api_views import ExhibitionListView

urlpatterns = [
    # 전시회 목록 조회 및 전시회 생성
    path('', ExhibitionListView.as_view(), name='api_exhibition_list'),
] 