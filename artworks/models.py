from django.db import models

class Artwork(models.Model):
    title = models.CharField(max_length=64, verbose_name='작품명') 
    artist = models.ForeignKey(
        'artists.Artist',
        on_delete=models.CASCADE,
        related_name='artworks',
        verbose_name='작가'
    )
    
    size_width = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='가로(cm)')
    size_height = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='세로(cm)')
    
    image_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='이미지 URL'
    )
    
    
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        null=True, 
        blank=True,
        verbose_name='가격'
    )
    canvas_size = models.IntegerField(default=10, verbose_name='호수') 
    creation_year = models.IntegerField(verbose_name='제작년도')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'artworks'
        verbose_name = '작품'
        verbose_name_plural = '작품들'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def size_display(self):
        return f"{self.size_width}cm × {self.size_height}cm"

    @property 
    def has_image(self):
        """이미지가 있는지 확인"""
        return bool(self.image_url)
