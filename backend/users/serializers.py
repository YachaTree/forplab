from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Friendship

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    사용자 정보 시리얼라이저
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 
                  'birth_date', 'profile_image', 'skill_level', 'rating', 
                  'matches_played', 'wins', 'draws', 'losses', 'bio')
        read_only_fields = ('rating', 'matches_played', 'wins', 'draws', 'losses')

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    사용자 등록 시리얼라이저
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 
                  'last_name', 'phone', 'birth_date', 'skill_level', 'bio')
    
    def validate(self, data):
        # 비밀번호 일치 확인
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "비밀번호가 일치하지 않습니다."})
        
        # 비밀번호 유효성 검사
        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        
        return data
    
    def create(self, validated_data):
        # password_confirm 필드 제거
        validated_data.pop('password_confirm')
        
        # 사용자 생성
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            birth_date=validated_data.get('birth_date'),
            skill_level=validated_data.get('skill_level', 'BEG'),
            bio=validated_data.get('bio', '')
        )
        
        return user

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    사용자 프로필 업데이트 시리얼라이저
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'birth_date', 
                  'profile_image', 'skill_level', 'bio')
    
    def update(self, instance, validated_data):
        # 기본 필드 업데이트
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.skill_level = validated_data.get('skill_level', instance.skill_level)
        instance.bio = validated_data.get('bio', instance.bio)
        
        instance.save()
        return instance

class PasswordChangeSerializer(serializers.Serializer):
    """
    비밀번호 변경 시리얼라이저
    """
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("현재 비밀번호가 일치하지 않습니다.")
        return value
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "새 비밀번호가 일치하지 않습니다."})
        
        try:
            validate_password(data['new_password'], self.context['request'].user)
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})
        
        return data 

class FriendshipSerializer(serializers.ModelSerializer):
    """
    친구 관계 시리얼라이저
    """
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)
    
    class Meta:
        model = Friendship
        fields = ('id', 'from_user', 'to_user', 'status', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class FriendshipCreateSerializer(serializers.ModelSerializer):
    """
    친구 요청 생성 시리얼라이저
    """
    to_user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Friendship
        fields = ('id', 'to_user_id', 'status')
        read_only_fields = ('status',)
    
    def validate_to_user_id(self, value):
        # 자기 자신에게 친구 요청을 보낼 수 없음
        if self.context['request'].user.id == value:
            raise serializers.ValidationError("자기 자신에게 친구 요청을 보낼 수 없습니다.")
        
        # 존재하는 사용자인지 확인
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 사용자입니다.")
        
        # 이미 친구 요청을 보냈는지 확인
        if Friendship.objects.filter(
            from_user=self.context['request'].user,
            to_user_id=value
        ).exists():
            raise serializers.ValidationError("이미 친구 요청을 보냈습니다.")
        
        # 상대방이 이미 친구 요청을 보냈는지 확인
        if Friendship.objects.filter(
            from_user_id=value,
            to_user=self.context['request'].user
        ).exists():
            raise serializers.ValidationError("상대방이 이미 친구 요청을 보냈습니다.")
        
        return value
    
    def create(self, validated_data):
        from_user = self.context['request'].user
        to_user_id = validated_data.pop('to_user_id')
        to_user = User.objects.get(id=to_user_id)
        
        friendship = Friendship.objects.create(
            from_user=from_user,
            to_user=to_user,
            status='PENDING'
        )
        
        return friendship 