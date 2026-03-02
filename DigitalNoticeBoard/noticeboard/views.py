from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import Notice, Category
from .forms import NoticeForm
from django.utils import timezone


# ======================================================
# HOME VIEW (Dashboard + Filters + Pagination + Search)
# ======================================================
from django.db.models import Q
from .models import Notice, Category


from django.contrib.auth.decorators import user_passes_test

def staff_check(user):
    return user.is_staff

from django.db import models

def home(request):

    notices = Notice.objects.select_related('category').all()
    categories = Category.objects.all()

    # -------------------------------------------------
    # EXPIRY FILTER (Hide expired notices)
    # -------------------------------------------------
    notices = notices.filter(
        models.Q(expiry_date__isnull=True) |
        models.Q(expiry_date__gt=timezone.now())
    )

    # -------------------------------------------------
    # ROLE-BASED DEPARTMENT FILTER
    # -------------------------------------------------
    #if request.user.is_authenticated:
     #   user_dept = request.user.profile.department
      #  notices = notices.filter(department=user_dept)

    # -------------------------------------------------
    # SEARCH
    # -------------------------------------------------
    search_query = request.GET.get('search')
    if search_query:
        notices = notices.filter(
            title__icontains=search_query
        )

    # -------------------------------------------------
    # CATEGORY FILTER
    # -------------------------------------------------
    category_id = request.GET.get('category')
    if category_id and category_id != "all":
        notices = notices.filter(category_id=category_id)

    # -------------------------------------------------
    # PINNING + SORTING
    # -------------------------------------------------
    sort = request.GET.get('sort', '-created_at')
    notices = notices.order_by('-is_pinned', sort)

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

@login_required(login_url='login')
@user_passes_test(staff_check)
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
@user_passes_test(staff_check)
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
@user_passes_test(staff_check)
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
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Notice

def staff_check(user):
    return user.is_staff


@login_required(login_url='login')
@user_passes_test(staff_check)
def delete_notice(request, pk):

    notice = get_object_or_404(Notice, pk=pk)

    if request.method == "POST":
        notice.delete()
        messages.success(request, "Notice deleted successfully.")
        return redirect('home')

    # If GET → show confirmation page
    return render(request, 'noticeboard/confirm_delete.html', {
        'notice': notice
    })




from django.shortcuts import get_object_or_404


def notice_detail(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    notice.views_count += 1
    notice.save()
    notices = notices.order_by('-is_pinned', '-created_at')

    return render(request, 'noticeboard/notice_detail.html', {
        'notice': notice
    })



from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

def login_view(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # ROLE BASED REDIRECT
            if user.is_staff:
                return redirect('dashboard')
            else:
                return redirect('home')

        else:
            return render(request, 'noticeboard/login.html', {
                'error': 'Invalid credentials'
            })

    return render(request, 'noticeboard/login.html')



from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('home')



from django.http import JsonResponse

@login_required(login_url='login')
def like_notice(request, pk):

    notice = get_object_or_404(Notice, pk=pk)

    if request.user in notice.likes.all():
        notice.likes.remove(request.user)
        liked = False
    else:
        notice.likes.add(request.user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'total_likes': notice.likes.count()
    })


@login_required(login_url='login')
@user_passes_test(staff_check)
def analytics_dashboard(request):
    notices = Notice.objects.all()
    return render(request, 'noticeboard/analytics.html', {'notices': notices})