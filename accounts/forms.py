from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomAuthenticationForm(AuthenticationForm):
    """커스텀 로그인 폼"""
    username = forms.CharField(
        label='아이디',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '아이디를 입력하세요'
        })
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호를 입력하세요'
        })
    )

class CustomUserCreationForm(UserCreationForm):
    """커스텀 회원가입 폼"""
    username = forms.CharField(
        label='아이디',
        max_length=150,
        help_text='필수. 150자 이하. 문자, 숫자, @/./+/-/_ 만 가능합니다.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '아이디를 입력하세요'
        }),
        error_messages={
            'required': '아이디를 입력해주세요.',
            'unique': '이미 사용 중인 아이디입니다.',
        }
    )
    password1 = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호를 입력하세요'
        }),
        error_messages={
            'required': '비밀번호를 입력해주세요.',
        }
    )
    password2 = forms.CharField(
        label='비밀번호 확인',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호를 다시 입력하세요'
        }),
        error_messages={
            'required': '비밀번호 확인을 입력해주세요.',
        }
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
        
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
        return password2 