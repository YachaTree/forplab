from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Team, TeamMember, TeamJoinRequest

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    """
    간단한 사용자 정보 시리얼라이저
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'profile_image', 'skill_level')

class TeamMemberSerializer(serializers.ModelSerializer):
    """
    팀 멤버 시리얼라이저
    """
    user = UserSimpleSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    
    class Meta:
        model = TeamMember
        fields = ('id', 'user', 'role', 'role_display', 'position', 'position_display', 'joined_at')

class TeamJoinRequestSerializer(serializers.ModelSerializer):
    """
    팀 가입 요청 시리얼라이저
    """
    user = UserSimpleSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    
    class Meta:
        model = TeamJoinRequest
        fields = ('id', 'user', 'message', 'position', 'position_display', 'status', 'status_display', 'created_at')
        read_only_fields = ('user', 'status')

class TeamSerializer(serializers.ModelSerializer):
    """
    팀 시리얼라이저
    """
    owner = UserSimpleSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    region_display = serializers.CharField(source='get_region_display', read_only=True)
    
    class Meta:
        model = Team
        fields = ('id', 'name', 'logo', 'description', 'level', 'level_display',
                  'region', 'region_display', 'is_recruiting',
                  'rating', 'owner', 'members_count', 'matches_played', 'wins',
                  'draws', 'losses', 'goals_scored', 'goals_conceded',
                  'created_at')
    
    def get_members_count(self, obj):
        return obj.members.count()

class TeamDetailSerializer(serializers.ModelSerializer):
    """
    팀 상세 시리얼라이저
    """
    owner = UserSimpleSerializer(read_only=True)
    members = serializers.SerializerMethodField()
    join_requests = serializers.SerializerMethodField()
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    region_display = serializers.CharField(source='get_region_display', read_only=True)
    win_rate = serializers.FloatField(read_only=True)
    goal_difference = serializers.IntegerField(read_only=True)
    is_member = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    has_join_request = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ('id', 'name', 'logo', 'description', 'level', 'level_display',
                  'region', 'region_display', 'is_recruiting',
                  'rating', 'owner', 'members', 'join_requests', 'matches_played',
                  'wins', 'draws', 'losses', 'goals_scored', 'goals_conceded',
                  'win_rate', 'goal_difference', 'is_member', 'is_owner', 'has_join_request',
                  'created_at', 'updated_at')
    
    def get_members(self, obj):
        members = TeamMember.objects.filter(team=obj)
        return TeamMemberSerializer(members, many=True).data
    
    def get_join_requests(self, obj):
        user = self.context['request'].user
        # 팀 소유자만 가입 요청을 볼 수 있음
        if user == obj.owner:
            requests = TeamJoinRequest.objects.filter(team=obj, status='PENDING')
            return TeamJoinRequestSerializer(requests, many=True).data
        return []
    
    def get_is_member(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            is_member = TeamMember.objects.filter(team=obj, user=user).exists()
            print(f"사용자 {user.id}({user.username})의 팀 {obj.id}({obj.name}) 멤버십 확인: {is_member}")
            return is_member
        return False
    
    def get_is_owner(self, obj):
        user = self.context['request'].user
        return user == obj.owner
    
    def get_has_join_request(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            has_request = TeamJoinRequest.objects.filter(team=obj, user=user, status='PENDING').exists()
            print(f"사용자 {user.id}({user.username})의 팀 {obj.id}({obj.name}) 가입 신청 확인: {has_request}")
            return has_request
        return False

class TeamCreateSerializer(serializers.ModelSerializer):
    """
    팀 생성 시리얼라이저
    """
    class Meta:
        model = Team
        fields = ('id', 'name', 'logo', 'description', 'level', 'region', 'is_recruiting')
        read_only_fields = ('id',)
    
    def validate_region(self, value):
        # 유효한 지역인지 확인
        valid_regions = ['seoul', 'gyeonggi', 'incheon', 'other']
        if value not in valid_regions:
            raise serializers.ValidationError(f"유효하지 않은 지역입니다. 유효한 값: {', '.join(valid_regions)}")
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        team = Team.objects.create(owner=user, **validated_data)
        
        # 팀 생성자를 팀의 주장으로 추가
        TeamMember.objects.create(team=team, user=user, role='CAPTAIN')
        
        return team 