from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    # 관리자 인증
    path('login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.admin_logout_view, name='admin_logout'),
    
    # 어드민 홈 (대시보드)
    path('', views.dashboard_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # 작가 신청 관리
    path('applications/', views.applications_view, name='applications'),
    
    # 작가 통계
    path('statistics/', views.statistics_view, name='statistics'),
    
    # API 엔드포인트
    path('api/dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('api/export/applications/', views.export_applications_csv, name='export_applications_csv'),
    
    # 관리자용 작가 신청 API (세션 기반 인증)
    path('api/applications/', views.api_applications_list, name='api_applications_list'),
    path('api/applications/<int:pk>/', views.api_application_detail, name='api_application_detail'),
    path('api/applications/<int:pk>/review/', views.api_application_review, name='api_application_review'),
    path('api/check-session/', views.api_check_admin_session, name='api_check_admin_session'),
] 