from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
from django.db import models
from django.core.validators import EmailValidator
from django.contrib.auth.validators import UnicodeUsernameValidator


class User(AbstractUser):
    """사용자 모델 - 일반 사용자, 작가만 (관리자 제외)"""
    ROLES = [
        ('general', '일반 사용자'),
        ('artist', '작가'),
    ]
    
    # Django 인증 시스템에 필요한 기본 필드들 (사용하지 않지만 필수)
    email = models.EmailField(blank=True, null=True, max_length=254)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default='general',
        verbose_name='사용자 역할'
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'
    
    @property
    def is_artist(self):
        return self.role == 'artist'
    

    

# 관리자 계정 전용 테이블 (간소화된 구조)
class AdminAccount(AbstractBaseUser):
    """관리자 계정 전용 테이블 - 기본 로그인 정보만"""
    
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        verbose_name='관리자 아이디'
    )
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='마지막 로그인')
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    objects = BaseUserManager()
    
    class Meta:
        db_table = 'admin_accounts'
        verbose_name = '관리자 계정'
        verbose_name_plural = '관리자 계정들'
    
    def __str__(self):
        return f"{self.username}"