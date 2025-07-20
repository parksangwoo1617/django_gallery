from django.shortcuts import render
from accounts.decorators import artist_required


def artist_list_view(request):
    """작가 목록 페이지"""
    return render(request, 'artist_list.html')


def artist_detail_view(request, pk):
    """작가 상세 페이지"""
    return render(request, 'artist_list.html', {'artist_id': pk})


def artist_apply_view(request):
    """작가 등록 신청 페이지"""
    return render(request, 'artist_apply.html')


@artist_required
def artist_dashboard_view(request):
    """작가 대시보드 페이지 - 작가 권한 필요"""
    return render(request, 'artist_dashboard.html')


@artist_required
def artwork_create_view(request):
    """작품 등록 페이지 - 작가 권한 필요"""
    return render(request, 'artwork_create.html')


@artist_required
def exhibition_create_view(request):
    """전시 등록 페이지 - 작가 권한 필요"""
    return render(request, 'exhibition_create.html')
