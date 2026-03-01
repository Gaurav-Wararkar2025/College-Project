from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import Notice, Category
from .forms import NoticeForm


# ======================================================
# HOME VIEW (Dashboard + Filters + Pagination + Search)
# ======================================================
def home(request):
    notices = Notice.objects.all().order_by('-created_at')
    categories = Category.objects.all()

    # Search
    search = request.GET.get('search')
    if search:
        notices = notices.filter(title__icontains=search)

    # Category Filter
    category = request.GET.get('category')
    if category and category != "all":
        notices = notices.filter(category_id=category)

    context = {
        'notices': notices,
        'categories': categories,
    }
    return render(request, 'noticeboard/home.html', context)


# ===============================
# ADMIN DASHBOARD (Advanced View)
# ===============================
from django.db.models.functions import TruncMonth
from django.db.models import Count
from datetime import datetime


def dashboard(request):
    """
    Advanced Admin dashboard with:
    - Total analytics
    - Category distribution
    - Monthly growth trend
    """

    notices = Notice.objects.all().order_by('-created_at')
    total_notices = notices.count()
    total_categories = Category.objects.count()
    latest_notices = notices[:5]

    # -------------------------
    # Category Pie Chart Data
    # -------------------------
    categories = Category.objects.all()
    category_labels = []
    category_counts = []

    for category in categories:
        category_labels.append(category.name)
        category_counts.append(
            Notice.objects.filter(category=category).count()
        )

    # -------------------------
    # Monthly Trend Graph Data
    # -------------------------
    monthly_data = (
        Notice.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    trend_labels = []
    trend_counts = []

    for entry in monthly_data:
        trend_labels.append(entry['month'].strftime("%b %Y"))
        trend_counts.append(entry['count'])

    context = {
        'total_notices': total_notices,
        'total_categories': total_categories,
        'latest_notices': latest_notices,
        'category_labels': category_labels,
        'category_counts': category_counts,
        'trend_labels': trend_labels,
        'trend_counts': trend_counts,
    }

    return render(request, 'noticeboard/dashboard.html', context)


# ===============================
# ADD NOTICE (Staff Only)
# ==================
@login_required(login_url='login')
def add_notice(request):
    """
    Only staff users can add notices.
    """

    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to add notices.")

    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES)

        if form.is_valid():
            notice = form.save(commit=False)
            notice.created_by = request.user
            notice.save()

            messages.success(request, "Notice added successfully.")
            return redirect('home')
        else:
            messages.error(request, "Error submitting form.")
    else:
        form = NoticeForm()

    return render(request, 'noticeboard/notice_form.html', {'form': form})


# ===============================
# EDIT NOTICE (Staff Only)
# ===============================
@login_required(login_url='login')
def edit_notice(request, pk):
    """
    Only staff users can edit notices.
    """

    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to edit notices.")

    notice = get_object_or_404(Notice, pk=pk)

    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES, instance=notice)

        if form.is_valid():
            form.save()
            messages.success(request, "Notice updated successfully.")
            return redirect('home')
        else:
            messages.error(request, "Error updating notice.")
    else:
        form = NoticeForm(instance=notice)

    return render(request, 'noticeboard/notice_form.html', {'form': form})


# ===============================
# DELETE NOTICE (Staff Only)
# ===============================
@login_required(login_url='login')
def delete_notice(request, pk):
    """
    Only staff users can delete notices.
    """

    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to delete notices.")

    notice = get_object_or_404(Notice, pk=pk)

    if request.method == 'POST':
        notice.delete()
        messages.success(request, "Notice deleted successfully.")
        return redirect('home')

    return render(request, 'noticeboard/confirm_delete.html', {'notice': notice})