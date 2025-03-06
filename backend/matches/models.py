from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Match(models.Model):
    """
    축구 매치 모델
    """
    TYPE_CHOICES = [
        ('SOCIAL', '소셜 매치'),
        ('TEAM', '팀 매치'),
        ('TOURNAMENT', '토너먼트'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', '모집중'),
        ('CLOSED', '모집완료'),
        ('CANCELED', '취소됨'),
        ('COMPLETED', '경기완료'),
    ]
    
    GENDER_CHOICES = [
        ('MALE', '남성'),
        ('FEMALE', '여성'),
        ('MIXED', '혼성'),
    ]
    
    title = models.CharField(_('제목'), max_length=100)
    match_type = models.CharField(_('매치 유형'), max_length=10, choices=TYPE_CHOICES)
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, related_name='matches')
    date = models.DateField(_('경기 날짜'))
    start_time = models.TimeField(_('시작 시간'))
    end_time = models.TimeField(_('종료 시간'))
    status = models.CharField(_('상태'), max_length=10, choices=STATUS_CHOICES, default='OPEN')
    max_players = models.IntegerField(_('최대 인원'))
    current_players = models.ManyToManyField('users.User', through='MatchParticipant', related_name='matches')
    skill_level = models.CharField(_('실력 수준'), max_length=3, choices=[
        ('BEG', '입문'),
        ('INT', '중급'),
        ('ADV', '고급'),
        ('ALL', '모든 수준')
    ], default='ALL')
    gender = models.CharField(_('성별'), max_length=6, choices=GENDER_CHOICES, default='MIXED')
    price = models.DecimalField(_('참가비'), max_digits=10, decimal_places=2)
    description = models.TextField(_('설명'), blank=True)
    host = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='hosted_matches')
    team_match = models.BooleanField(_('팀 매치 여부'), default=False)
    home_team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='home_matches')
    away_team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='away_matches')
    created_at = models.DateTimeField(_('생성일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)
    
    # 경기 결과
    home_score = models.IntegerField(_('홈팀 점수'), null=True, blank=True)
    away_score = models.IntegerField(_('원정팀 점수'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('매치')
        verbose_name_plural = _('매치들')
        ordering = ['-date', '-start_time']
        
    def __str__(self):
        return f"{self.title} ({self.date} {self.start_time})"
    
    @property
    def is_full(self):
        """매치가 가득 찼는지 확인"""
        return self.current_players.count() >= self.max_players
    
    @property
    def available_spots(self):
        """남은 자리 수 계산"""
        return max(0, self.max_players - self.current_players.count())
    
    @property
    def is_past(self):
        """지난 매치인지 확인"""
        now = timezone.now()
        match_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.end_time)
        )
        return now > match_datetime

class MatchParticipant(models.Model):
    """
    매치 참가자 모델
    """
    STATUS_CHOICES = [
        ('REGISTERED', '등록됨'),
        ('CANCELED', '취소됨'),
        ('ATTENDED', '참석함'),
        ('NOSHOW', '불참'),
    ]
    
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    status = models.CharField(_('상태'), max_length=10, choices=STATUS_CHOICES, default='REGISTERED')
    team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.BooleanField(_('결제 상태'), default=False)
    registered_at = models.DateTimeField(_('등록일'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('매치 참가자')
        verbose_name_plural = _('매치 참가자들')
        unique_together = ('match', 'user')  # 한 사용자는 한 매치에 한 번만 등록 가능
        
    def __str__(self):
        return f"{self.match.title} - {self.user.username} ({self.get_status_display()})"

class MatchResult(models.Model):
    """
    매치 결과 모델
    """
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='result')
    home_score = models.IntegerField(_('홈팀 점수'))
    away_score = models.IntegerField(_('원정팀 점수'))
    mvp = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='mvp_matches')
    summary = models.TextField(_('경기 요약'), blank=True)
    created_at = models.DateTimeField(_('생성일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)
    
    class Meta:
        verbose_name = _('매치 결과')
        verbose_name_plural = _('매치 결과들')
        
    def __str__(self):
        return f"{self.match.title} - {self.home_score}:{self.away_score}"
