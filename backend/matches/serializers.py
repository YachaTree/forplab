from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Match, MatchParticipant, MatchResult
from venues.serializers import VenueSerializer
from teams.serializers import TeamSerializer

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    """
    간단한 사용자 정보 시리얼라이저
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'profile_image', 'skill_level')

class MatchParticipantSerializer(serializers.ModelSerializer):
    """
    매치 참가자 시리얼라이저
    """
    user = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = MatchParticipant
        fields = ('id', 'user', 'status', 'team', 'payment_status', 'registered_at')

class MatchResultSerializer(serializers.ModelSerializer):
    """
    매치 결과 시리얼라이저
    """
    mvp = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = MatchResult
        fields = ('id', 'home_score', 'away_score', 'mvp', 'summary')

class MatchListSerializer(serializers.ModelSerializer):
    """
    매치 목록 시리얼라이저 (간략한 정보)
    """
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    host_name = serializers.CharField(source='host.username', read_only=True)
    current_players_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = ('id', 'title', 'match_type', 'venue_name', 'date', 'start_time', 
                  'end_time', 'status', 'max_players', 'current_players_count', 
                  'skill_level', 'gender', 'price', 'host_name')
    
    def get_current_players_count(self, obj):
        return obj.current_players.count()

class MatchDetailSerializer(serializers.ModelSerializer):
    """
    매치 상세 시리얼라이저
    """
    venue = VenueSerializer(read_only=True)
    host = UserSimpleSerializer(read_only=True)
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)
    participants = serializers.SerializerMethodField()
    result = MatchResultSerializer(read_only=True)
    is_joined = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = ('id', 'title', 'match_type', 'venue', 'date', 'start_time', 
                  'end_time', 'status', 'max_players', 'skill_level', 'gender', 
                  'price', 'description', 'host', 'team_match', 'home_team', 
                  'away_team', 'participants', 'result', 'is_joined', 
                  'created_at', 'updated_at')
    
    def get_participants(self, obj):
        participants = MatchParticipant.objects.filter(match=obj)
        return MatchParticipantSerializer(participants, many=True).data
    
    def get_is_joined(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return MatchParticipant.objects.filter(match=obj, user=user).exists()
        return False

class MatchCreateSerializer(serializers.ModelSerializer):
    """
    매치 생성 시리얼라이저
    """
    class Meta:
        model = Match
        fields = ('title', 'match_type', 'venue', 'date', 'start_time', 
                  'end_time', 'max_players', 'skill_level', 'gender', 
                  'price', 'description', 'team_match', 'home_team', 'away_team')
    
    def create(self, validated_data):
        user = self.context['request'].user
        match = Match.objects.create(host=user, **validated_data)
        return match

class MatchUpdateSerializer(serializers.ModelSerializer):
    """
    매치 업데이트 시리얼라이저
    """
    class Meta:
        model = Match
        fields = ('title', 'date', 'start_time', 'end_time', 'max_players', 
                  'skill_level', 'gender', 'price', 'description', 'status')
    
    def validate(self, data):
        # 이미 시작된 매치는 수정 불가
        instance = self.instance
        if instance.is_past:
            raise serializers.ValidationError("이미 종료된 매치는 수정할 수 없습니다.")
        return data

class MatchResultCreateSerializer(serializers.ModelSerializer):
    """
    매치 결과 생성 시리얼라이저
    """
    class Meta:
        model = MatchResult
        fields = ('home_score', 'away_score', 'mvp', 'summary')
    
    def create(self, validated_data):
        match_id = self.context['match_id']
        match = Match.objects.get(id=match_id)
        
        # 매치 상태 업데이트
        match.status = 'COMPLETED'
        match.home_score = validated_data.get('home_score')
        match.away_score = validated_data.get('away_score')
        match.save()
        
        # 결과 생성
        result = MatchResult.objects.create(match=match, **validated_data)
        return result 