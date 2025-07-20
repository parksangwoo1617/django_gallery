from rest_framework import permissions


class IsArtistUser(permissions.BasePermission):
    """작가 사용자 권한"""  
    message = "작가 권한이 필요합니다."
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.is_artist
        )


class CanApplyForArtist(permissions.BasePermission):
    """작가 신청 가능 여부 (일반 사용자 + 아직 신청하지 않은)"""
    message = "이미 작가이거나 신청 중입니다."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # 이미 작가인 경우
        if request.user.is_artist:
            return False
            
        return True 