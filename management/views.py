from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
import csv
import json

# 관리자 인증 함수 import
from management.admin_auth import admin_authenticate
from management.models import AdminAccount

from artists.models import Artist, ArtistApplication
from artworks.models import Artwork
from exhibitions.models import Exhibition
from django.db.models import Count, Q, Avg


def admin_login_view(request):
    """관리자 전용 로그인 페이지"""
    # 이미 관리자로 로그인된 경우 대시보드로 리다이렉트 (실제 관리자 확인)
    if request.session.get('is_admin_logged_in') and get_current_admin(request):
        return redirect('management:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, '아이디와 비밀번호를 모두 입력해주세요.')
            return render(request, 'admin_login.html')

        # 관리자 계정 인증 (AdminAccount 테이블 사용)
        admin_user = admin_authenticate(username, password)

        if admin_user is not None:
            # 세션에 관리자 정보 저장
            request.session['admin_user_id'] = admin_user.id
            request.session['admin_username'] = admin_user.username
            request.session['is_admin_logged_in'] = True

            # 마지막 로그인 시간 업데이트
            admin_user.last_login = timezone.now()
            admin_user.save(update_fields=['last_login'])

            # next 파라미터가 있으면 해당 페이지로, 없으면 대시보드로
            next_url = request.GET.get('next', 'management:home')
            return redirect(next_url)
        else:
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')

    # GET 요청이거나 로그인 실패 시 로그인 페이지 렌더링
    return render(request, 'admin_login.html')


def admin_logout_view(request):
    """관리자 로그아웃"""
    # 세션에서 관리자 정보 제거
    if 'admin_user_id' in request.session:
        del request.session['admin_user_id']
    if 'admin_username' in request.session:
        del request.session['admin_username']
    if 'is_admin_logged_in' in request.session:
        del request.session['is_admin_logged_in']

    return redirect('management:admin_login')


def get_current_admin(request):
    """현재 로그인된 관리자 정보 조회"""
    if not request.session.get('is_admin_logged_in'):
        return None

    admin_id = request.session.get('admin_user_id')
    if not admin_id:
        return None

    try:
        return AdminAccount.objects.get(id=admin_id)
    except Exception:
        return None


def check_admin_permission(request):
    """관리자 권한 체크 헬퍼"""
    admin = get_current_admin(request)
    if not admin:
        return False, None
    return True, admin


def dashboard_view(request):
    """관리자 대시보드 페이지 - 어드민 홈"""
    is_admin, admin_user = check_admin_permission(request)

    if not is_admin:
        return redirect('management:admin_login')

    return render(request, 'dashboard.html', {'admin_user': admin_user})


def applications_view(request):
    """작가 신청 관리 페이지"""
    is_admin, admin_user = check_admin_permission(request)

    if not is_admin:
        return redirect('management:admin_login')

    return render(request, 'applications.html', {'admin_user': admin_user})


def statistics_view(request):
    """작가 통계 페이지"""
    is_admin, admin_user = check_admin_permission(request)

    if not is_admin:
        return redirect('management:admin_login')

    return render(request, 'statistics.html', {'admin_user': admin_user})





@require_http_methods(["GET"])
def dashboard_stats(request):
    """대시보드 통계 API"""
    is_admin, admin_user = check_admin_permission(request)

    if not is_admin:
        return JsonResponse({'error': '권한이 없습니다.'}, status=403)

    try:
        # 기본 통계
        stats = {
            'pending_applications': ArtistApplication.objects.filter(status='pending').count(),
            'total_artists': Artist.objects.count(),
            'total_artworks': Artwork.objects.count(),
            'total_exhibitions': Exhibition.objects.count(),
        }

        # 성별 통계
        gender_stats = Artist.objects.values('gender').annotate(count=Count('id'))

        # 작가 상세 통계 (실제 데이터 기반)
        artist_stats = []
        artists = Artist.objects.all()
        for artist in artists:
            # 100호 이하 작품 개수
            artwork_count_under_100 = artist.artworks.filter(canvas_size__lte=100).count()

            # 평균 가격 계산 (소수점 제거)
            avg_price = artist.artworks.aggregate(avg_price=Avg('price'))['avg_price'] or 0

            artist_stats.append({
                'artist_name': artist.artist_name,
                'gender': artist.gender,
                'artwork_count_under_100': artwork_count_under_100,
                'avg_price': int(avg_price) if avg_price else 0
            })

        return JsonResponse({
            'stats': stats,
            'gender_stats': list(gender_stats),
            'artist_stats': artist_stats[:100]  # 100줄만 반환
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def export_applications_csv(request):
    """작가 신청 내역을 CSV로 내보내기"""
    is_admin, admin_user = check_admin_permission(request)

    if not is_admin:
        return JsonResponse({'error': '권한이 없습니다.'}, status=403)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="artist_applications_{timezone.now().strftime("%Y%m%d")}.csv"'

    # BOM 추가 (엑셀에서 한글 깨짐 방지)
    response.write('\ufeff')

    writer = csv.writer(response)

    # 헤더 작성 (요구사항에 맞는 컬럼)
    writer.writerow([
        '신청일', '작가명', '성별', '생년월일', '이메일', '연락처',
        '상태', '승인일'
    ])

    # 데이터 작성
    applications = ArtistApplication.objects.all().order_by('-applied_at')

    for app in applications:
        writer.writerow([
            app.applied_at.strftime('%Y-%m-%d %H:%M:%S') if app.applied_at else '',
            app.artist_name or '',
            '남자' if app.gender == 'male' else '여자' if app.gender == 'female' else '',
            app.birth_date.strftime('%Y-%m-%d') if app.birth_date else '',
            app.contact_email or '',
            app.phone or '',
            app.get_status_display() or '',
            app.processed_at.strftime('%Y-%m-%d %H:%M:%S') if getattr(app, 'processed_at', None) else ''
        ])

    return response


# ===========================================
# 관리자용 API 엔드포인트들 (세션 기반 인증)
# ===========================================

@require_http_methods(["GET"])
def api_applications_list(request):
    """관리자용 작가 신청 목록 API (세션 기반 인증)"""
    is_admin, admin_user = check_admin_permission(request)

    if not is_admin:
        return JsonResponse({'error': '관리자 권한이 필요합니다.'}, status=403)

    try:
        # 페이지네이션 파라미터
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        # 전체 작가 신청 목록 (최신순)
        applications = ArtistApplication.objects.all().order_by('-applied_at')

        # 페이지네이션
        paginator = Paginator(applications, page_size)
        page_obj = paginator.get_page(page)

        # 데이터 변환
        results = []
        for app in page_obj:
            results.append({
                'id': app.id,
                'artist_name': app.artist_name,
                'gender': app.gender,
                'birth_date': app.birth_date.isoformat() if app.birth_date else None,
                'contact_email': app.contact_email,
                'phone': app.phone,
                'status': app.status,
                'status_display': app.get_status_display(),
                'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                'processed_at': getattr(app, 'processed_at', None),
            })

        return JsonResponse({
            'results': results,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def api_application_detail(request, pk):
    """관리자용 작가 신청 상세 API (세션 기반 인증)"""
    is_admin, admin_user = check_admin_permission(request)

    if not is_admin:
        return JsonResponse({'error': '관리자 권한이 필요합니다.'}, status=403)

    try:
        application = ArtistApplication.objects.get(pk=pk)

        data = {
            'id': application.id,
            'artist_name': application.artist_name,
            'gender': application.gender,
            'birth_date': application.birth_date.isoformat() if application.birth_date else None,
            'contact_email': application.contact_email,
            'phone': application.phone,
            'status': application.status,
            'status_display': application.get_status_display(),
            'applied_at': application.applied_at.isoformat() if application.applied_at else None,
            'processed_at': getattr(application, 'processed_at', None),
        }

        return JsonResponse(data)

    except ArtistApplication.DoesNotExist:
        return JsonResponse({'error': '신청을 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_application_review(request, pk):
    """관리자용 작가 신청 검토 API (세션 기반 인증)"""

    # 디버그 로그 추가


    is_admin, admin_user = check_admin_permission(request)

    if not is_admin:
        return JsonResponse({'error': '관리자 권한이 필요합니다.'}, status=403)

    try:
        application = ArtistApplication.objects.get(pk=pk)

        if application.status != 'pending':
            return JsonResponse({'error': '이미 처리된 신청입니다.'}, status=400)

        # 요청 데이터 파싱
        data = json.loads(request.body)
        status = data.get('status')  # 'approved' or 'rejected'

        if status not in ['approved', 'rejected']:
            return JsonResponse({'error': '유효하지 않은 상태입니다.'}, status=400)

        # 모델의 메서드 사용
        if status == 'approved':
            try:
                application.approve()
            except Exception as e:
                return JsonResponse({'error': f'승인 처리 실패: {str(e)}'}, status=500)
        else:
            try:
                application.reject()
            except Exception as e:
                return JsonResponse({'error': f'반려 처리 실패: {str(e)}'}, status=500)

        return JsonResponse({
            'message': f'신청이 {"승인" if status == "approved" else "반려"}되었습니다.',
            'application': {
                'id': application.id,
                'status': application.status,
                'status_display': application.get_status_display(),
                'reviewed_at': application.reviewed_at.isoformat() if application.reviewed_at else None,
            }
        })

    except ArtistApplication.DoesNotExist:
        return JsonResponse({'error': '신청을 찾을 수 없습니다.'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': '유효하지 않은 JSON 데이터입니다.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_check_admin_session(request):
    """관리자 세션 상태 확인 API"""

    is_admin, admin_user = check_admin_permission(request)

    return JsonResponse({
        'is_admin': is_admin,
        'session_data': {
            'is_admin_logged_in': request.session.get('is_admin_logged_in'),
            'admin_user_id': request.session.get('admin_user_id'),
            'admin_username': request.session.get('admin_username'),
            'session_key': request.session.session_key,
        },
        'admin_user': admin_user.username if admin_user else None
    })
