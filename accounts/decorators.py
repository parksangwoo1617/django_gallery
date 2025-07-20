from functools import wraps
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages


def artist_required(view_func):
    """작가 권한 필요 데코레이터"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_artist:
            # 이미 신청했는지 확인
            from artists.models import ArtistApplication
            
            existing_application = ArtistApplication.objects.filter(user=request.user).first()
            
            if request.content_type == 'application/json':
                return JsonResponse({
                    'error': '작가 권한이 필요합니다.'
                }, status=403)
            else:
                if existing_application:
                    if existing_application.status == 'pending':
                        messages.info(request, '작가 등록 신청이 심사 중입니다. 심사 완료까지 기다려주세요.')
                        return redirect('core:home')
                    elif existing_application.status == 'rejected':
                        messages.error(request, '이전 작가 등록 신청이 반려되었습니다. 다시 신청해주세요.')
                        return redirect('artists:apply')
                    else:
                        messages.error(request, '작가 권한이 필요합니다.')
                        return redirect('artists:apply')
                else:
                    messages.error(request, '작가 권한이 필요합니다. 먼저 작가 등록 신청을 해주세요.')
                    return redirect('artists:apply')
        
        return view_func(request, *args, **kwargs)
    return wrapper

 