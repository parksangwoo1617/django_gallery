from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomAuthenticationForm, CustomUserCreationForm


def login_view(request):
    """로그인 뷰"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'{username}님, 환영합니다!')
                return redirect('/')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """로그아웃 뷰"""
    logout(request)
    messages.info(request, '로그아웃되었습니다.')
    return redirect('/')


def signup_view(request):
    """회원가입 뷰"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username}님, 회원가입이 완료되었습니다!')
            login(request, user)  # 회원가입 후 자동 로그인
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})
