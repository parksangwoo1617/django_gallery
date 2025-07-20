from django.shortcuts import render


def exhibition_list_view(request):
    """전시회 목록 페이지"""
    return render(request, 'exhibitions/list.html')
