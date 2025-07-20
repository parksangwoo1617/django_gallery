import boto3
import uuid
from django.conf import settings
from PIL import Image
import io


def upload_artwork_image(image_file):
    """
    작품 이미지를 S3에 업로드
    
    Args:
        image_file: 업로드할 이미지 파일
        
    Returns:
        dict: {
            'success': bool,
            'image_url': str or None,
            'error': str or None
        }
    """
    try:
        # S3 설정 확인
        if not all([settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_STORAGE_BUCKET_NAME]):
            return {
                'success': False,
                'image_url': None,
                'error': 'AWS S3 설정이 완료되지 않았습니다.'
            }
        
        # 기본 검증
        if not image_file:
            return {'success': False, 'image_url': None, 'error': '이미지 파일이 없습니다.'}
        
        if image_file.size > 5 * 1024 * 1024:  # 5MB 제한
            return {'success': False, 'image_url': None, 'error': '파일 크기는 5MB 이하여야 합니다.'}
        
        if not image_file.content_type.startswith('image/'):
            return {'success': False, 'image_url': None, 'error': '이미지 파일만 업로드 가능합니다.'}
        
        # 이미지 최적화
        img = Image.open(image_file)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # 크기 조정 (최대 1920x1080)
        img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
        
        # JPEG로 압축
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        # S3 업로드
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # 고유한 파일명 생성
        unique_filename = f"{uuid.uuid4().hex}.jpg"
        s3_key = f"artwork-images/{unique_filename}"
        
        # S3에 업로드
        s3_client.upload_fileobj(
            output,
            settings.AWS_STORAGE_BUCKET_NAME,
            s3_key,
            ExtraArgs={
                'ContentType': 'image/jpeg',
                'CacheControl': 'max-age=86400',
                'ACL': 'public-read'
            }
        )
        
        # 업로드된 이미지 URL 생성
        image_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
        
        return {
            'success': True,
            'image_url': image_url,
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'image_url': None,
            'error': f'이미지 업로드 중 오류 발생: {str(e)}'
        } 