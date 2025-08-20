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
