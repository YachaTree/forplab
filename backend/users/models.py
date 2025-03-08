from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    커스텀 사용자 모델
    """
    SKILL_CHOICES = [
        ('BEG', '입문'),
        ('INT', '중급'),
        ('ADV', '고급'),
        ('PRO', '프로'),
    ]
    
    phone = models.CharField(_('전화번호'), max_length=15, blank=True)
    birth_date = models.DateField(_('생년월일'), null=True, blank=True)
    profile_image = models.ImageField(_('프로필 이미지'), upload_to='profile_images/', null=True, blank=True)
    skill_level = models.CharField(_('실력 수준'), max_length=3, choices=SKILL_CHOICES, default='BEG')
    rating = models.FloatField(_('레이팅'), default=1000.0)
    matches_played = models.IntegerField(_('참여 경기 수'), default=0)
    wins = models.IntegerField(_('승리 수'), default=0)
    draws = models.IntegerField(_('무승부 수'), default=0)
    losses = models.IntegerField(_('패배 수'), default=0)
    bio = models.TextField(_('자기소개'), blank=True)
    
    class Meta:
        verbose_name = _('사용자')
        verbose_name_plural = _('사용자들')
    
    def __str__(self):
        return self.username
    
    @property
    def win_rate(self):
        """승률 계산"""
        if self.matches_played == 0:
            return 0
        return (self.wins / self.matches_played) * 100

class Friendship(models.Model):
    """
    사용자 간의 친구 관계를 저장하는 모델
    """
    STATUS_CHOICES = [
        ('PENDING', '대기중'),
        ('ACCEPTED', '수락됨'),
        ('REJECTED', '거절됨'),
    ]
    
    from_user = models.ForeignKey(User, related_name='friendships_sent', on_delete=models.CASCADE, verbose_name=_('요청자'))
    to_user = models.ForeignKey(User, related_name='friendships_received', on_delete=models.CASCADE, verbose_name=_('수신자'))
    status = models.CharField(_('상태'), max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(_('생성일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)
    
    class Meta:
        verbose_name = _('친구 관계')
        verbose_name_plural = _('친구 관계들')
        unique_together = ('from_user', 'to_user')
    
    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.get_status_display()})"
