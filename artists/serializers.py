from rest_framework import serializers
from .models import Artist, ArtistApplication
from accounts.serializers import UserProfileSerializer


class ArtistSerializer(serializers.ModelSerializer):
    """작가 정보 시리얼라이저"""
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Artist
        fields = '__all__'
        read_only_fields = ('user', 'approved_at', 'created_at')


class ArtistListSerializer(serializers.ModelSerializer):
    """작가 목록용 간단한 시리얼라이저"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    
    class Meta:
        model = Artist
        fields = ('id', 'artist_name', 'user_name', 'gender', 'gender_display', 
                 'contact_email', 'approved_at', 'created_at')


class ArtistApplicationSerializer(serializers.ModelSerializer):
    """작가 신청 시리얼라이저"""
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = ArtistApplication
        fields = '__all__'
        read_only_fields = ('user', 'status', 'reviewed_at', 
                          'applied_at', 'updated_at')

    def create(self, validated_data):
        # 현재 로그인한 사용자를 신청자로 설정
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ArtistApplicationCreateSerializer(serializers.ModelSerializer):
    """작가 신청 생성용 시리얼라이저"""
    email = serializers.EmailField(source='contact_email')  # 프론트엔드에서 email로 전송
    
    class Meta:
        model = ArtistApplication
        fields = ('artist_name', 'gender', 'birth_date', 'email', 'phone')

    def validate_artist_name(self, value):
        """이름 유효성 검사 (16자 이하)"""
        if not value or not value.strip():
            raise serializers.ValidationError("이름을 입력해주세요.")
        if len(value.strip()) > 16:
            raise serializers.ValidationError("이름은 16자 이하로 입력해주세요.")
        return value.strip()

    def validate_gender(self, value):
        """성별 유효성 검사"""
        if not value:
            raise serializers.ValidationError("성별을 선택해주세요.")
        if value not in ['male', 'female']:
            raise serializers.ValidationError("올바른 성별을 선택해주세요.")
        return value

    def validate_birth_date(self, value):
        """생년월일 유효성 검사"""
        if not value:
            raise serializers.ValidationError("생년월일을 입력해주세요.")
        
        from datetime import date
        today = date.today()
        
        # 미래 날짜 체크
        if value >= today:
            raise serializers.ValidationError("생년월일은 오늘 이전 날짜여야 합니다.")
        
        # 만 18세 이상 체크
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise serializers.ValidationError("작가 등록은 만 18세 이상만 가능합니다.")
        if age > 100:
            raise serializers.ValidationError("올바른 생년월일을 입력해주세요.")
        
        return value

    def validate_email(self, value):
        """이메일 유효성 검사"""
        if not value or not value.strip():
            raise serializers.ValidationError("이메일을 입력해주세요.")
        
        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, value.strip()):
            raise serializers.ValidationError("올바른 이메일 형식을 입력해주세요. (예: example@domain.com)")
        
        return value.strip()

    def validate_phone(self, value):
        """연락처 유효성 검사"""
        if not value or not value.strip():
            raise serializers.ValidationError("연락처를 입력해주세요.")
        
        import re
        phone_regex = r'^[0-9]{3}-[0-9]{4}-[0-9]{4}$'
        if not re.match(phone_regex, value.strip()):
            raise serializers.ValidationError("연락처는 000-0000-0000 형식으로 입력해주세요.")
        
        return value.strip()

    def create(self, validated_data):
        # 현재 로그인한 사용자를 신청자로 설정
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ArtistApplicationListSerializer(serializers.ModelSerializer):
    """작가 신청 목록용 시리얼라이저"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ArtistApplication
        fields = ('id', 'artist_name', 'user_name', 'status', 'status_display', 
                 'applied_at')
