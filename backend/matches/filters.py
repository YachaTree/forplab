import django_filters
from django.db.models import Q
from .models import Match

class MatchFilter(django_filters.FilterSet):
    """
    매치 필터링을 위한 필터 클래스
    """
    date = django_filters.DateFilter(field_name='date')
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    
    skill_level = django_filters.CharFilter(field_name='skill_level')
    gender = django_filters.CharFilter(field_name='gender')
    status = django_filters.CharFilter(field_name='status')
    match_type = django_filters.CharFilter(field_name='match_type')
    
    venue = django_filters.NumberFilter(field_name='venue__id')
    venue_name = django_filters.CharFilter(field_name='venue__name', lookup_expr='icontains')
    
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Match
        fields = ['date', 'date_from', 'date_to', 'skill_level', 'gender', 
                  'status', 'match_type', 'venue', 'venue_name', 'price_min', 
                  'price_max', 'search']
    
    def filter_search(self, queryset, name, value):
        """
        제목, 설명, 구장 이름으로 검색
        """
        return queryset.filter(
            Q(title__icontains=value) | 
            Q(description__icontains=value) | 
            Q(venue__name__icontains=value)
        ) 