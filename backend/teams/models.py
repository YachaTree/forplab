from django.db import models
from django.utils.translation import gettext_lazy as _

class Team(models.Model):
    """
    축구 팀 모델
    """
    LEVEL_CHOICES = [
        ('BEG', '입문'),
        ('INT', '중급'),
        ('ADV', '고급'),
        ('PRO', '프로'),
    ]
    
    name = models.CharField(_('팀명'), max_length=100)
    logo = models.ImageField(_('로고'), upload_to='team_logos/', null=True, blank=True)
    description = models.TextField(_('팀 소개'), blank=True)
    level = models.CharField(_('팀 수준'), max_length=3, choices=LEVEL_CHOICES, default='BEG')
    rating = models.FloatField(_('팀 레이팅'), default=1000.0)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='owned_teams')
    members = models.ManyToManyField('users.User', through='TeamMember', related_name='teams')
    created_at = models.DateTimeField(_('생성일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)
    
    # 팀 통계
    matches_played = models.IntegerField(_('경기 수'), default=0)
    wins = models.IntegerField(_('승리 수'), default=0)
    draws = models.IntegerField(_('무승부 수'), default=0)
    losses = models.IntegerField(_('패배 수'), default=0)
    goals_scored = models.IntegerField(_('득점'), default=0)
    goals_conceded = models.IntegerField(_('실점'), default=0)
    
    class Meta:
        verbose_name = _('팀')
        verbose_name_plural = _('팀들')
        
    def __str__(self):
        return self.name
    
    @property
    def win_rate(self):
        """승률 계산"""
        if self.matches_played == 0:
            return 0
        return (self.wins / self.matches_played) * 100
    
    @property
    def goal_difference(self):
        """득실차 계산"""
        return self.goals_scored - self.goals_conceded
    
    @property
    def member_count(self):
        """팀원 수 계산"""
        return self.members.count()

class TeamMember(models.Model):
    """
    팀 멤버십 모델
    """
    ROLE_CHOICES = [
        ('CAPTAIN', '주장'),
        ('MANAGER', '매니저'),
        ('PLAYER', '선수'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    role = models.CharField(_('역할'), max_length=10, choices=ROLE_CHOICES, default='PLAYER')
    joined_at = models.DateTimeField(_('가입일'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('팀 멤버')
        verbose_name_plural = _('팀 멤버들')
        unique_together = ('team', 'user')  # 한 사용자는 한 팀에 한 번만 가입 가능
        
    def __str__(self):
        return f"{self.team.name} - {self.user.username} ({self.get_role_display()})"

class TeamJoinRequest(models.Model):
    """
    팀 가입 요청 모델
    """
    STATUS_CHOICES = [
        ('PENDING', '대기중'),
        ('ACCEPTED', '수락됨'),
        ('REJECTED', '거절됨'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='join_requests')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='team_requests')
    message = models.TextField(_('가입 메시지'), blank=True)
    status = models.CharField(_('상태'), max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(_('요청일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('처리일'), auto_now=True)
    
    class Meta:
        verbose_name = _('팀 가입 요청')
        verbose_name_plural = _('팀 가입 요청들')
        unique_together = ('team', 'user', 'status')  # 동일한 상태의 중복 요청 방지
        
    def __str__(self):
        return f"{self.user.username} -> {self.team.name} ({self.get_status_display()})"
