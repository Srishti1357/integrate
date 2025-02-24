from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from .models import Visitor
from django.shortcuts import render
from .models import Visitor
from .filters import VisitorFilter
# def visitor_list(request):
#     visitors = Visitor.objects.all()
#     return render(request, "visitor_list.html", {"visitors": visitors})




# def visitor_list(request):
#     visitors = Visitor.objects.all()
#     visitor_filter = VisitorFilter(request.GET, queryset=visitors)  # Apply filters
#     print(visitor_filter.qs[0].name)
#     return render(request, "visitor_list.html", {"visitors": visitor_filter.qs, "visitor_filter": visitor_filter})

from django.shortcuts import render
from .models import Visitor
from .filters import VisitorFilter

def visitor_list(request):
    visitors = Visitor.objects.all()
    visitor_filter = VisitorFilter(request.GET, queryset=visitors)  # Apply filters
    
    # ✅ Sorting filtered visitors by datetime (newest first)
    sorted_visitors = sorted(visitor_filter.qs, key=lambda v: v.datetime, reverse=True)

    return render(request, "visitor_list.html", {"visitors": sorted_visitors, "visitor_filter": visitor_filter})


def update_approval(request, visitor_id, status):
    visitor = Visitor.objects.get(id=visitor_id)
    visitor.approval = status
    visitor.save()
    return JsonResponse({"status": "success", "approval": visitor.approval_status()})
