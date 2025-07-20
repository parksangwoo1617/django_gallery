from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(APIView):
    """사용자 세션 관리 API (로그인/로그아웃)"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """로그인"""
        try:
            serializer = UserLoginSerializer(data=request.data)
            
            serializer.is_valid(raise_exception=True)
            
            user = serializer.validated_data['user'] 
            
            login(request, user)
            
            response_data = {
                'message': '로그인이 완료되었습니다.',
                'user': UserProfileSerializer(user).data,
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': '로그인 중 오류가 발생했습니다.',
                'detail': str(e) if settings.DEBUG else '내부 서버 오류'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        """로그아웃"""
        try:
            if not request.user.is_authenticated:
                return Response({
                    'message': '이미 로그아웃된 상태입니다.'
                }, status=status.HTTP_200_OK)
            
            username = request.user.username
            logout(request)
            
            return Response({
                'message': '로그아웃되었습니다.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': '로그아웃 중 오류가 발생했습니다.',
                'detail': str(e) if settings.DEBUG else '내부 서버 오류'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """사용자 프로필 조회/수정 API"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = UserUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': '프로필이 업데이트되었습니다.',
            'user': UserProfileSerializer(instance).data
        })


class ChangePasswordView(APIView):
    """비밀번호 변경 API"""
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password']) 
        user.save()
        
        return Response({
            'message': '비밀번호가 성공적으로 변경되었습니다.'
        }, status=status.HTTP_200_OK)



class UserListView(generics.ListCreateAPIView):
    """사용자 목록 조회 및 회원가입 API"""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny] 

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserRegistrationSerializer  # 회원가입
        return UserProfileSerializer  # 목록 조회

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.method == 'GET':
            return User.objects.none()
        return User.objects.all()

    def create(self, request, *args, **kwargs):
        """회원가입 처리"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            login(request, user)
            
            response_data = {
                'message': '회원가입이 완료되었습니다.',
                'user': UserProfileSerializer(user).data,
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': '회원가입 중 오류가 발생했습니다.',
                'detail': str(e) if settings.DEBUG else '내부 서버 오류'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def check_username_availability(request):
    """아이디 사용 가능 여부 검증 API"""
    if request.method == 'GET':
        username = request.GET.get('username')
    else:
        username = request.data.get('username')
    
    if not username:
        return Response({
            'available': False,
            'message': '아이디를 입력해주세요.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 아이디 길이 검증 (Django 기본 최대 150자)
    if len(username) > 150:
        return Response({
            'available': False,
            'message': '아이디는 150자 이하로 입력해주세요.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 아이디 형식 검증 (영문, 숫자, @/./+/-/_ 만 허용)
    import re
    if not re.match(r'^[\w.@+-]+$', username):
        return Response({
            'available': False,
            'message': '아이디는 영문, 숫자, @/./+/-/_ 만 사용 가능합니다.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 중복 검사
    if User.objects.filter(username=username).exists():
        return Response({
            'available': False,
            'message': '이미 사용 중인 아이디입니다.'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'available': True,
        'message': '사용 가능한 아이디입니다.'
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # 인증 불필요
def auth_status(request):
    """사용자 인증 상태 확인 API (로그인 여부만 확인)"""
    if request.user.is_authenticated:
        return Response({
            'is_authenticated': True,
            'user': UserProfileSerializer(request.user).data
        })
    else:
        return Response({
            'is_authenticated': False,
            'user': None
        }) 