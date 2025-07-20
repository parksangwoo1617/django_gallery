from django.db import models
from django.conf import settings


class Artist(models.Model):
    """승인된 작가 정보"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name='사용자'
    )
    
    # 작가 기본 정보
    artist_name = models.CharField(max_length=16, verbose_name='작가명')
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', '남자'),
            ('female', '여자'),
        ],
        default='male',
        verbose_name='성별'
    )
    # 연락 정보
    contact_email = models.EmailField(verbose_name='연락용 이메일')
    
    # 관리 정보
    approved_at = models.DateTimeField(auto_now_add=True, verbose_name='승인일')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'artists'
        verbose_name = '작가'
        verbose_name_plural = '작가들'
        ordering = ['-approved_at']
    
    def __str__(self):
        return self.artist_name


class ArtistApplication(models.Model):
    """작가 등록 신청"""
    
    STATUS_CHOICES = [
        ('pending', '심사 중'),
        ('approved', '승인'),
        ('rejected', '반려'),
    ]
    
    # 신청자 정보
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='신청자'
    )
    
    # 개인 정보 (회원가입 시 받지 않았던 정보)
    phone = models.CharField(max_length=20, verbose_name='연락처')
    birth_date = models.DateField(verbose_name='생년월일')
    
    # 신청 내용 (Artist 모델과 동일한 필드들)
    artist_name = models.CharField(max_length=16, verbose_name='작가명')
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', '남자'),
            ('female', '여자'),
        ],
        default='male',
        verbose_name='성별'
    )
    contact_email = models.EmailField(verbose_name='연락용 이메일')
    
    # 신청 관리
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='심사 상태'
    )
    
    # 관리자 처리 정보
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='심사일')
    
    # 일반 관리 정보
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name='신청일')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'artist_applications'
        verbose_name = '작가 신청'
        verbose_name_plural = '작가 신청들'
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.artist_name} - {self.status}"
    
    def approve(self):
        """신청 승인 처리"""
        from django.utils import timezone
        
        self.status = 'approved'
        self.reviewed_at = timezone.now()
        self.save()
        
        # 사용자 역할을 작가로 변경
        self.user.role = 'artist'
        self.user.save()
        
        # Artist 인스턴스 생성
        Artist.objects.create(
            user=self.user,
            artist_name=self.artist_name,
            gender=self.gender,
            contact_email=self.contact_email,
        )
    
    def reject(self):
        """신청 반려 처리"""
        from django.utils import timezone
        
        self.status = 'rejected'
        self.reviewed_at = timezone.now()
        self.save()
