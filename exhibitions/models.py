from django.db import models
from django.conf import settings
from django.utils import timezone


class Exhibition(models.Model):
    """전시 정보"""
    
    # 기본 정보
    title = models.CharField(max_length=64, verbose_name='전시명')  # 64자로 변경
    
    # 일정 정보
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(verbose_name='종료일')
    
    # 참여 작가 (단일 작가)
    artist = models.ForeignKey(
        'artists.Artist',
        on_delete=models.CASCADE,
        related_name='exhibitions',
        verbose_name='참여 작가'
    )
    
    # 전시 작품들
    artworks = models.ManyToManyField(
        'artworks.Artwork',
        through='ExhibitionArtwork',
        related_name='exhibitions',
        blank=True,
        verbose_name='전시 작품'
    )
    
    # 일반 관리 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exhibitions'
        verbose_name = '전시'
        verbose_name_plural = '전시들'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        """현재 진행 중인 전시인지 확인"""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date
    
    @property
    def days_until_start(self):
        """시작까지 남은 일수"""
        return 0
    
    @property
    def days_until_end(self):
        """종료까지 남은 일수"""
        return 0


# ExhibitionArtist 모델 제거됨 (artist가 단일 ForeignKey로 변경됨)


class ExhibitionArtwork(models.Model):
    """전시 작품 중간 테이블"""
    
    exhibition = models.ForeignKey(Exhibition, on_delete=models.CASCADE)
    artwork = models.ForeignKey('artworks.Artwork', on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exhibition_artworks'
        verbose_name = '전시 작품'
        verbose_name_plural = '전시 작품들'
        unique_together = ['exhibition', 'artwork']
    
    def __str__(self):
        return "전시 작품"
