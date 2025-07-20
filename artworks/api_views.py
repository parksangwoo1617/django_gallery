from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from django.db.models import Q
from .models import Artwork
from .serializers import (
    ArtworkSerializer,
    ArtworkListSerializer,
    ArtworkCreateSerializer,
    ArtworkUpdateSerializer
)


class ArtworkListView(generics.ListCreateAPIView):
    """작품 목록 조회 및 작품 생성 API"""
    queryset = Artwork.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'price', 'creation_year', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArtworkCreateSerializer  
        return ArtworkListSerializer  

    def get_permissions(self):
        if self.request.method == 'POST':
            from core.permissions import IsArtistUser
            return [IsArtistUser()]
        else:
            return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 검색 필터
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(artist__artist_name__icontains=search)
            )
        
        # 작가 필터
        artist = self.request.query_params.get('artist', None)
        if artist:
            queryset = queryset.filter(artist_id=artist)
        
        # 가격 범위 필터
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # 제작년도 필터
        year = self.request.query_params.get('year', None)
        if year:
            queryset = queryset.filter(creation_year=year)
            
        return queryset


class ArtworkDetailView(generics.RetrieveUpdateDestroyAPIView):
    """작품 상세 조회, 수정, 삭제 API"""
    queryset = Artwork.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ArtworkUpdateSerializer  
        return ArtworkSerializer  

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.method == 'GET':
            return Artwork.objects.all()
        else:
            if hasattr(self.request.user, 'artist'):
                return Artwork.objects.filter(artist=self.request.user.artist)
            return Artwork.objects.none()

    def destroy(self, request, *args, **kwargs):
        """작품 삭제"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'message': '작품이 성공적으로 삭제되었습니다.'
        }, status=status.HTTP_200_OK) 