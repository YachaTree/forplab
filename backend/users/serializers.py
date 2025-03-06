from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

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