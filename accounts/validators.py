from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator,
    MinimumLengthValidator,
    NumericPasswordValidator
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re
from difflib import SequenceMatcher


class KoreanUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    """한국어 사용자 속성 유사성 검증자"""
    
    def validate(self, password, user=None):
        if not user:
            return
            
        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or len(value) < 2:  # 최소 길이를 2로 고정
                continue
            value_parts = re.split(r'\W+', value) + [value]
            for value_part in value_parts:
                if SequenceMatcher(a=password.lower(), b=value_part.lower()).quick_ratio() >= self.max_similarity:
                    raise ValidationError(
                        "비밀번호가 개인정보와 너무 유사합니다.",
                        code='password_too_similar',
                    )
    
    def get_help_text(self):
        return "비밀번호는 개인정보와 너무 유사하면 안 됩니다."


class KoreanMinimumLengthValidator(MinimumLengthValidator):
    """한국어 최소 길이 검증자"""
    
    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                f"비밀번호가 너무 짧습니다. 최소 {self.min_length}자 이상이어야 합니다.",
                code='password_too_short',
                params={'min_length': self.min_length},
            )
    
    def get_help_text(self):
        return f"비밀번호는 최소 {self.min_length}자 이상이어야 합니다."


class KoreanNumericPasswordValidator(NumericPasswordValidator):
    """한국어 숫자 전용 비밀번호 검증자"""
    
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                "비밀번호는 숫자로만 구성될 수 없습니다.",
                code='password_entirely_numeric',
            )
    
    def get_help_text(self):
        return "비밀번호는 숫자로만 구성될 수 없습니다." 