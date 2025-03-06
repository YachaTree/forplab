from django.db import models
from django.utils.translation import gettext_lazy as _

class Venue(models.Model):
    """
    축구 구장 모델
    """
    SURFACE_CHOICES = [
        ('GRASS', '천연잔디'),
        ('ARTIFICIAL', '인조잔디'),
        ('FUTSAL', '풋살장'),
    ]
    
    SIZE_CHOICES = [
        ('5', '5인용'),
        ('6', '6인용'),
        ('7', '7인용'),
        ('11', '11인용'),
    ]
    
    name = models.CharField(_('구장명'), max_length=100)
    address = models.CharField(_('주소'), max_length=255)
    latitude = models.FloatField(_('위도'), null=True, blank=True)
    longitude = models.FloatField(_('경도'), null=True, blank=True)
    description = models.TextField(_('설명'), blank=True)
    surface_type = models.CharField(_('구장 표면'), max_length=20, choices=SURFACE_CHOICES)
    size = models.CharField(_('구장 크기'), max_length=2, choices=SIZE_CHOICES)
    image = models.ImageField(_('구장 이미지'), upload_to='venue_images/', null=True, blank=True)
    hourly_rate = models.DecimalField(_('시간당 가격'), max_digits=10, decimal_places=2, null=True, blank=True)
    opening_time = models.TimeField(_('개장 시간'))
    closing_time = models.TimeField(_('폐장 시간'))
    has_parking = models.BooleanField(_('주차 가능 여부'), default=False)
    has_shower = models.BooleanField(_('샤워 시설 여부'), default=False)
    has_locker = models.BooleanField(_('락커 여부'), default=False)
    created_at = models.DateTimeField(_('생성일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)
    
    class Meta:
        verbose_name = _('구장')
        verbose_name_plural = _('구장들')
        
    def __str__(self):
        return self.name

class VenueImage(models.Model):
    """
    구장 이미지 모델 (여러 이미지 저장 가능)
    """
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(_('이미지'), upload_to='venue_images/')
    description = models.CharField(_('설명'), max_length=255, blank=True)
    created_at = models.DateTimeField(_('생성일'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('구장 이미지')
        verbose_name_plural = _('구장 이미지들')
        
    def __str__(self):
        return f"{self.venue.name} - {self.id}"

class VenueReview(models.Model):
    """
    구장 리뷰 모델
    """
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    rating = models.IntegerField(_('평점'), choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(_('리뷰 내용'))
    created_at = models.DateTimeField(_('작성일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)
    
    class Meta:
        verbose_name = _('구장 리뷰')
        verbose_name_plural = _('구장 리뷰들')
        unique_together = ('venue', 'user')  # 한 사용자는 한 구장에 하나의 리뷰만 작성 가능
        
    def __str__(self):
        return f"{self.venue.name} - {self.user.username} - {self.rating}점"
