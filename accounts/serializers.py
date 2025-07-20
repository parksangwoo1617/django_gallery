from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """사용자 회원가입 시리얼라이저 - 최소 정보만 수집"""
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password],
        error_messages={
            'required': '비밀번호를 입력해주세요.',
            'blank': '비밀번호를 입력해주세요.',
        }
    )
    password_confirm = serializers.CharField(
        write_only=True,
        error_messages={
            'required': '비밀번호 확인을 입력해주세요.',
            'blank': '비밀번호 확인을 입력해주세요.',
        }
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'password_confirm')
        extra_kwargs = {
            'username': {
                'error_messages': {
                    'required': '아이디를 입력해주세요.',
                    'blank': '아이디를 입력해주세요.',
                    'unique': '이미 사용 중인 아이디입니다.',
                    'invalid': '올바른 아이디를 입력해주세요.',
                }
            }
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """사용자 로그인 시리얼라이저"""
    username = serializers.CharField(
        error_messages={
            'required': '아이디를 입력해주세요.',
            'blank': '아이디를 입력해주세요.',
        }
    )
    password = serializers.CharField(
        write_only=True,
        error_messages={
            'required': '비밀번호를 입력해주세요.',
            'blank': '비밀번호를 입력해주세요.',
        }
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('아이디 또는 비밀번호가 올바르지 않습니다.')
            if not user.is_active:
                raise serializers.ValidationError('비활성화된 계정입니다.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('아이디와 비밀번호를 모두 입력해주세요.')


class UserProfileSerializer(serializers.ModelSerializer):
    """사용자 프로필 시리얼라이저"""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'role', 'date_joined', 'is_artist')
        read_only_fields = ('id', 'username', 'date_joined', 'is_artist')


class UserUpdateSerializer(serializers.ModelSerializer):
    """사용자 정보 수정 시리얼라이저"""
    
    class Meta:
        model = User
        fields = ('phone',)
        extra_kwargs = {
            'phone': {
                'error_messages': {
                    'invalid': '올바른 전화번호를 입력해주세요.',
                }
            }
        }


class ChangePasswordSerializer(serializers.Serializer):
    """비밀번호 변경 시리얼라이저"""
    old_password = serializers.CharField(
        write_only=True,
        error_messages={
            'required': '현재 비밀번호를 입력해주세요.',
            'blank': '현재 비밀번호를 입력해주세요.',
        }
    )
    new_password = serializers.CharField(
        write_only=True, 
        validators=[validate_password],
        error_messages={
            'required': '새 비밀번호를 입력해주세요.',
            'blank': '새 비밀번호를 입력해주세요.',
        }
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        error_messages={
            'required': '새 비밀번호 확인을 입력해주세요.',
            'blank': '새 비밀번호 확인을 입력해주세요.',
        }
    )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("새 비밀번호가 일치하지 않습니다.")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("현재 비밀번호가 올바르지 않습니다.")
        return value 