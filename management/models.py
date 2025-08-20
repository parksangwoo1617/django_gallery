from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import UnicodeUsernameValidator

# Create your models here.


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