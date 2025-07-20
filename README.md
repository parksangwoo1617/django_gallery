# Django Gallery

Django 기반 온라인 갤러리 플랫폼입니다. 작가들이 작품을 등록하고 전시회를 개최할 수 있으며, 관리자가 작가 신청을 심사하고 플랫폼을 관리할 수 있습니다.

**🌐 라이브 사이트**: [http://django-gallery.kro.kr/](http://django-gallery.kro.kr/)

## 🎯 주요 기능

- **작가 관리**: 작가 신청 및 승인 시스템
- **작품 관리**: AWS S3를 통한 이미지 업로드 및 관리
- **전시회 관리**: 작가별 전시회 개최 및 운영
- **관리자 대시보드**: 통계 및 신청 관리

## 🔑 시스템 접근 방법

### 📊 관리자 페이지 접근

**프로덕션**: `http://django-gallery.kro.kr/management/`

**관리자 로그인**

- **로그인 페이지**:
  - 프로덕션: `http://django-gallery.kro.kr/management/login/`
- **기본 계정**:
  - 사용자명: `admin`
  - 비밀번호: `admin123`

### 🎨 작가 대시보드 접근

**프로덕션**: `http://django-gallery.kro.kr/artists/dashboard/`
