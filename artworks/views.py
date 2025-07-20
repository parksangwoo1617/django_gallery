from django.shortcuts import render

def artwork_list_view(request):
    """작품 목록 페이지"""
    return render(request, 'list.html')


def artwork_detail_view(request, pk):
    """작품 상세 페이지"""
    return render(request, 'list.html', {'artwork_id': pk})
