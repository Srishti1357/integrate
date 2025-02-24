import django_filters
from django_filters import DateFilter, DateTimeFilter
from .models import Visitor

class VisitorFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="datetime", lookup_expr="date__gte", label="Start Date (YYYY-MM-DD)")
    end_date = DateFilter(field_name="datetime", lookup_expr="date__lte", label="End Date (YYYY-MM-DD)")
    start_datetime = DateTimeFilter(field_name="datetime", lookup_expr="gte", label="Start Date & Time")
    end_datetime = DateTimeFilter(field_name="datetime", lookup_expr="lte", label="End Date & Time")

    class Meta:
        model = Visitor
        fields = ["start_date", "end_date", "start_datetime", "end_datetime"]
