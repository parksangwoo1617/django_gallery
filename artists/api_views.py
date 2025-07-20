from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from core.permissions import (
    IsArtistUser, 
    CanApplyForArtist
)
from .models import Artist, ArtistApplication
from artworks.models import Artwork
from exhibitions.models import Exhibition, ExhibitionArtwork
from .serializers import (
    ArtistSerializer,
    ArtistListSerializer,
    ArtistApplicationSerializer,
    ArtistApplicationCreateSerializer,
    ArtistApplicationListSerializer
)
from artworks.serializers import ArtworkSerializer, ArtworkListSerializer
from exhibitions.serializers import ExhibitionListSerializer


class ArtistListView(generics.ListAPIView):
    """작가 목록 조회 API"""
    queryset = Artist.objects.all()
    serializer_class = ArtistListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(artist_name__icontains=search)
        return queryset


class ArtistDetailView(generics.RetrieveAPIView):
    """작가 상세 정보 조회 API"""
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [permissions.AllowAny]


class ArtistApplicationListView(generics.ListCreateAPIView):
    """작가 신청 목록 조회 및 신청 생성 API"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArtistApplicationCreateSerializer  
        return ArtistApplicationListSerializer  

    def get_permissions(self):
        if self.request.method == 'POST':
            # 신청 생성은 특별한 권한 필요
            return [CanApplyForArtist()]
        else:
            # 목록 조회는 인증된 사용자
            return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        # 사용자는 자신의 신청만 볼 수 있음
        return ArtistApplication.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        """작가 신청 생성 (RESTful)"""
        # 이미 작가 신청을 한 사용자인지 확인
        if ArtistApplication.objects.filter(user=request.user, status='pending').exists():
            return Response({
                'error': '이미 작가 신청이 진행 중입니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)


class ArtistApplicationDetailView(generics.RetrieveAPIView):
    """작가 신청 상세 조회 API"""
    serializer_class = ArtistApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ArtistApplication.objects.filter(user=user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_artist_profile(request):
    """내 작가 프로필 조회 API"""
    try:
        artist = request.user.artist
        serializer = ArtistSerializer(artist)
        return Response(serializer.data)
    except Artist.DoesNotExist:
        return Response({
            'error': '작가 프로필이 존재하지 않습니다.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_artist_application_status(request):
    """내 작가 신청 상태 조회 API"""
    try:
        application = ArtistApplication.objects.filter(user=request.user).latest('applied_at')
        serializer = ArtistApplicationSerializer(application)
        return Response(serializer.data)
    except ArtistApplication.DoesNotExist:
        return Response({
            'message': '작가 신청 내역이 없습니다.',
            'has_application': False
        })


@api_view(['GET'])
@permission_classes([IsArtistUser])
def artist_dashboard_data(request):
    """작가 대시보드 데이터 조회 API"""
    try:
        artist = Artist.objects.get(user=request.user)
        
        # 작가 정보
        artist_data = ArtistSerializer(artist).data
        
        # 작가의 작품 목록
        artworks = Artwork.objects.filter(artist=artist).order_by('-created_at')
        artworks_data = ArtworkListSerializer(artworks, many=True).data
        
        # 작가의 전시 목록
        exhibitions = Exhibition.objects.filter(artist=artist).order_by('-start_date')
        exhibitions_data = ExhibitionListSerializer(exhibitions, many=True).data
        
        return Response({
            'artist': artist_data,
            'artworks': artworks_data,
            'exhibitions': exhibitions_data,
            'artworks_count': artworks.count(),
            'exhibitions_count': exhibitions.count()
        })
    except Artist.DoesNotExist:
        return Response({
            'error': '작가 정보를 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)


def create_artwork(request):
    """작품 등록 API (이미지 업로드 포함)"""
    
    CANVAS_SIZES = {
        1: (22, 16), 2: (24, 19), 3: (27, 22), 4: (33, 24), 5: (35, 27),
        6: (41, 32), 8: (46, 38), 10: (53, 46), 12: (61, 50), 15: (65, 54),
        20: (73, 61), 25: (81, 65), 30: (91, 73), 40: (100, 81), 50: (117, 91),
        60: (130, 97), 80: (146, 114), 100: (162, 130), 120: (194, 130), 
        150: (227, 158), 200: (259, 194), 250: (291, 220), 300: (324, 259),
        400: (389, 324), 500: (455, 380)
    }
    
    try:

        try:
            artist = Artist.objects.get(user=request.user)
        except Artist.DoesNotExist:
            return Response({
                'error': '작가 정보를 찾을 수 없습니다. 작가 신청을 먼저 해주세요.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        
        title = request.POST.get('title', '').strip()
        price = request.POST.get('price')
        canvas_size = request.POST.get('canvas_size')
        creation_year = request.POST.get('creation_year')
        image_file = request.FILES.get('image') 
        
        
        if not title:
            return Response({'error': '제목을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(title) > 64:
            return Response({'error': '제목은 64자 이하로 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        try:
            print(f"[DEBUG] 가격 변환 시도: '{price}' -> int")
            price = int(price) if price else 0
            print(f"[DEBUG] 가격 변환 성공: {price}")
            if price < 0:
                return Response({'error': '가격은 0 이상이어야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError) as e:
            return Response({'error': f'올바른 가격을 입력해주세요. 입력값: {price}'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        try:
            canvas_size = int(canvas_size)
            
            if canvas_size < 1 or canvas_size > 500:
                return Response({'error': '호수는 1 이상 500 이하여야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
            
            
            if canvas_size in CANVAS_SIZES:
                size_width, size_height = CANVAS_SIZES[canvas_size]
            else:
                
                base_width = 22 + (canvas_size - 1) * 0.9
                base_height = 16 + (canvas_size - 1) * 0.7
                size_width = round(base_width, 1)
                size_height = round(base_height, 1)
                
        except (ValueError, TypeError) as e:
            return Response({'error': f'올바른 호수를 입력해주세요. 입력값: {canvas_size}'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        try:
            creation_year = int(creation_year) if creation_year else timezone.now().year
            current_year = timezone.now().year
            
            if creation_year > current_year:
                return Response({'error': f'제작년도는 {current_year}년 이하여야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError) as e:
            return Response({'error': f'올바른 제작년도를 입력해주세요. 입력값: {creation_year}'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        image_url = None
        
        if image_file:
            try:
                
                from django.conf import settings
                
                if not all([settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_STORAGE_BUCKET_NAME]):
                    image_url = None
                else:
                    from core.s3_utils import upload_artwork_image
                    
                    upload_result = upload_artwork_image(image_file)
                    
                    if upload_result.get('success'):
                        image_url = upload_result['image_url']
                    else:
                        
                        image_url = None
                        
            except Exception as upload_error:
                
                image_url = None
        else:
            pass
        
        # 5단계: 작품 생성
        
        try:
            artwork = Artwork.objects.create(
                title=title,
                artist=artist,
                price=price,
                canvas_size=canvas_size,
                creation_year=creation_year,
                size_width=size_width,
                size_height=size_height,
                image_url=image_url,
            )
        except Exception as db_error:
            
            # 디버그 정보를 API 응답으로 전달
            return Response({
                'error': '작품 저장 중 오류가 발생했습니다',
                'debug_info': str(db_error),
                'error_type': type(db_error).__name__,
                'data_received': {
                    'title': title,
                    'price': price,
                    'canvas_size': canvas_size,
                    'creation_year': creation_year,
                    'size_width': size_width,
                    'size_height': size_height
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'message': '작품이 성공적으로 등록되었습니다.',
            'artwork': ArtworkListSerializer(artwork).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': '작품 등록 중 예외가 발생했습니다',
            'debug_info': str(e),
            'error_type': type(e).__name__,
            'help': '이 오류 정보를 개발자에게 전달해주세요'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsArtistUser])
def create_exhibition(request):
    """전시 등록 API"""
    try:
        artist = Artist.objects.get(user=request.user)
        
        # 요청 데이터 검증
        title = request.data.get('title', '').strip()
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        artwork_ids = request.data.get('artwork_ids', [])
        
        # 입력 검증
        if not title:
            return Response({'error': '제목을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(title) > 64:
            return Response({'error': '제목은 64자 이하로 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not start_date:
            return Response({'error': '시작일을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not end_date:
            return Response({'error': '종료일을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from datetime import datetime
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start_date_obj >= end_date_obj:
                return Response({'error': '종료일은 시작일보다 늦어야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
                
        except ValueError:
            return Response({'error': '날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not artwork_ids or len(artwork_ids) == 0:
            return Response({'error': '최소 하나의 작품을 선택해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 선택한 작품들이 모두 해당 작가의 것인지 확인
        artworks = Artwork.objects.filter(id__in=artwork_ids, artist=artist)
        if len(artworks) != len(artwork_ids):
            return Response({'error': '선택한 작품 중 일부를 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 트랜잭션으로 전시 생성
        with transaction.atomic():
            exhibition = Exhibition.objects.create(
                title=title,
                start_date=start_date_obj,
                end_date=end_date_obj,
                artist=artist  # 단일 작가 직접 연결
            )
            
            # 전시 작품 추가
            for artwork in artworks:
                ExhibitionArtwork.objects.create(exhibition=exhibition, artwork=artwork)
        
        return Response({
            'message': '전시가 성공적으로 등록되었습니다.',
            'exhibition': ExhibitionListSerializer(exhibition).data
        }, status=status.HTTP_201_CREATED)
        
    except Artist.DoesNotExist:
        return Response({
            'error': '작가 정보를 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsArtistUser])
def artist_artworks(request):
    """작가의 작품 목록 조회 및 작품 생성 API"""
    if request.method == 'GET':
        # 작품 목록 조회
        try:
            artist = Artist.objects.get(user=request.user)
            artworks = Artwork.objects.filter(artist=artist).order_by('-created_at')
            serializer = ArtworkListSerializer(artworks, many=True)
            return Response(serializer.data)
        except Artist.DoesNotExist:
            return Response({
                'error': '작가 정보를 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'POST':
        return create_artwork(request)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_artist_status(request):
    """사용자의 작가 신청 상태 확인 API"""
    user = request.user
    
    # 이미 승인된 작가인지 확인
    try:
        artist = Artist.objects.get(user=user)
        return Response({
            'is_artist': True,
            'artist_id': artist.id,
            'artist_name': artist.artist_name,
            'status': 'approved'
        })
    except Artist.DoesNotExist:
        pass
    
    # 신청 중인 상태인지 확인
    try:
        application = ArtistApplication.objects.filter(user=user).latest('applied_at')
        return Response({
            'is_artist': False,
            'has_application': True,
            'application_status': application.status,
            'application_id': application.id,
            'can_apply': application.status == 'rejected'  # 반려된 경우에만 재신청 가능
        })
    except ArtistApplication.DoesNotExist:
        pass
    
    # 신청 이력이 없는 경우
    return Response({
        'is_artist': False,
        'has_application': False,
        'can_apply': True
    }) 