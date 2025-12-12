import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    #created_at = django_filters.DateFromToRangeFilter()
    #group = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Product
        #fields = ['created_at', 'group', 'name']
        fields = ['name']
