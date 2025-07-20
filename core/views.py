from django.shortcuts import render

# Create your views here.

def home_view(request):
    """홈페이지 뷰"""
    return render(request, 'home.html')
