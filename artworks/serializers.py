from rest_framework import serializers
from .models import Artwork
from artists.serializers import ArtistListSerializer


class ArtworkSerializer(serializers.ModelSerializer):
    """작품 상세 정보 시리얼라이저"""
    artist = ArtistListSerializer(read_only=True)
    size_display = serializers.CharField(read_only=True)
    has_image = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Artwork
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ArtworkListSerializer(serializers.ModelSerializer):
    """작품 목록용 간단한 시리얼라이저"""
    artist_name = serializers.CharField(source='artist.artist_name', read_only=True)
    size_display = serializers.CharField(read_only=True)
    has_image = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Artwork
        fields = ('id', 'title', 'artist_name', 'image_url', 'price', 
                 'canvas_size', 'creation_year', 'size_display', 'created_at', 'has_image')


class ArtworkCreateSerializer(serializers.ModelSerializer):
    """작품 생성용 시리얼라이저"""
    
    class Meta:
        model = Artwork
        fields = ('title', 'size_width', 'size_height', 
                 'price', 'canvas_size', 'creation_year')

    def validate_title(self, value):
        """제목 유효성 검사 (64자 이하)"""
        if len(value) > 64:
            raise serializers.ValidationError("제목은 64자 이하로 입력해주세요.")
        return value

    def validate_canvas_size(self, value):
        """호수 유효성 검사 (1-500)"""
        if value < 1 or value > 500:
            raise serializers.ValidationError("호수는 1 이상 500 이하의 숫자를 입력해주세요.")
        return value

    def validate_creation_year(self, value):
        """제작년도 유효성 검사"""
        from datetime import datetime
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError("제작년도가 너무 과거입니다.")
        return value

    def validate_price(self, value):
        """가격 유효성 검사"""
        if value is not None and value < 0:
            raise serializers.ValidationError("가격은 0 이상이어야 합니다.")
        return value

    def create(self, validated_data):
        # 현재 로그인한 사용자의 작가 정보를 artist로 설정
        request = self.context['request']
        if hasattr(request.user, 'artist'):
            validated_data['artist'] = request.user.artist
            return super().create(validated_data)
        else:
            raise serializers.ValidationError("작가로 등록된 사용자만 작품을 등록할 수 있습니다.")


class ArtworkUpdateSerializer(serializers.ModelSerializer):
    """작품 수정용 시리얼라이저"""
    
    class Meta:
        model = Artwork
        fields = ('title', 'size_width', 'size_height', 
                 'price', 'canvas_size', 'creation_year')

    def validate_title(self, value):
        """제목 유효성 검사 (64자 이하)"""
        if len(value) > 64:
            raise serializers.ValidationError("제목은 64자 이하로 입력해주세요.")
        return value

    def validate_canvas_size(self, value):
        """호수 유효성 검사 (1-500)"""
        if value < 1 or value > 500:
            raise serializers.ValidationError("호수는 1 이상 500 이하의 숫자를 입력해주세요.")
        return value

    def validate_creation_year(self, value):
        """제작년도 유효성 검사"""
        from datetime import datetime
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError("제작년도가 너무 과거입니다.")
        return value

    def validate_price(self, value):
        """가격 유효성 검사"""
        if value is not None and value < 0:
            raise serializers.ValidationError("가격은 0 이상이어야 합니다.")
        return value 