"""
관리자 전용 인증 백엔드
AdminAccount 테이블에서 관리자 로그인 처리
"""
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import AdminAccount


class AdminAuthenticationBackend(BaseBackend):
    """관리자 전용 인증 백엔드"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """AdminAccount 테이블에서 관리자 인증"""
        if username is None or password is None:
            return None
            
        try:
            admin = AdminAccount.objects.get(username=username)
            
            # 비밀번호 확인
            if check_password(password, admin.password):
                return admin
                    
        except Exception:
            # 존재하지 않는 사용자 -> None 반환
            return None
            
        return None
    
    def get_user(self, user_id):
        """사용자 ID로 AdminAccount 조회"""
        try:
            return AdminAccount.objects.get(pk=user_id)
        except Exception:
            return None


def admin_authenticate(username, password):
    """관리자 인증 헬퍼 함수"""
    try:
        admin = AdminAccount.objects.get(username=username)
        
        if check_password(password, admin.password):
            return admin
            
    except Exception:
        pass
        
    return None 