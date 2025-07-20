from rest_framework import serializers
from .models import Exhibition


class ExhibitionListSerializer(serializers.ModelSerializer):
    """전시회 목록용 간단한 시리얼라이저"""
    artworks_count = serializers.SerializerMethodField()
    is_ongoing = serializers.BooleanField(read_only=True)
    artist_name = serializers.CharField(source='artist.artist_name', read_only=True)
    
    class Meta:
        model = Exhibition
        fields = ('id', 'title', 'start_date', 'end_date', 
                 'artworks_count', 'is_ongoing', 'artist_name')

    def get_artworks_count(self, obj):
        return obj.artworks.count() 