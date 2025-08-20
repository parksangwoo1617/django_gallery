"""
관리자 전용 인증 백엔드
AdminAccount 테이블에서 관리자 로그인 처리
"""
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import AdminAccount


def admin_authenticate(username, password):
    """관리자 인증 헬퍼 함수"""
    try:
        admin = AdminAccount.objects.get(username=username)
        
        if check_password(password, admin.password):
            return admin
            
    except Exception:
        pass
        
    return None 