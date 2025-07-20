from django.urls import path
from .api_views import (
    UserListView,
    UserLoginView,
    UserProfileView,
    ChangePasswordView,
    check_username_availability,
    auth_status
)

urlpatterns = [
    # 사용자 리소스 관리
    path('users/', UserListView.as_view(), name='api_user_list'),  
    path('users/me/', UserProfileView.as_view(), name='api_user_profile'), 
    path('users/me/password/', ChangePasswordView.as_view(), name='api_change_password'),
    path('users/check-username/', check_username_availability, name='api_check_username'),  
    
    # 세션 관리 (인증)
    path('sessions/', UserLoginView.as_view(), name='api_session'),  
    
    # 인증 상태 확인
    path('auth/status/', auth_status, name='api_auth_status'),
] 