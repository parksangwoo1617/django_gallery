from rest_framework import generics, permissions, filters
from django.db.models import Q
from .models import Exhibition
from .serializers import ExhibitionListSerializer


class ExhibitionListView(generics.ListAPIView):
    """전시회 목록 조회 API"""
    queryset = Exhibition.objects.all()
    serializer_class = ExhibitionListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
            )
            
        return queryset 