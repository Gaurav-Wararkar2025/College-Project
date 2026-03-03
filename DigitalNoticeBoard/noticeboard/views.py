from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import Notice, Category
from .forms import NoticeForm
from django.utils import timezone

from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth


from django.db.models import Q
from .models import Notice, Category

from django.contrib.auth.decorators import user_passes_test
# ======================================================
# HOME VIEW (Dashboard + Filters + Pagination + Search)
# ======================================================


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
from django.db.models import Sum, Count


@login_required(login_url='login')
@user_passes_test(staff_check)
def dashboard(request):
    # 1. Base Data Fetching
    # We use select_related('category') to ensure category names show up in the table
    notices = Notice.objects.all().select_related('category').order_by('-created_at')
    
    total_notices = notices.count()
    total_categories = Category.objects.count()
    
    # Show top 10 instead of 5 to fill your UI better
    latest_notices = notices[:10] 

    # 2. CALCULATION: Total Engagement (Likes + Views)
    # This aggregates every single 'like' relationship and 'views_count' integer
    t_likes = Notice.objects.aggregate(total=Count('likes'))['total'] or 0
    t_views = Notice.objects.aggregate(total=Sum('views_count'))['total'] or 0
    total_engagement = t_likes + t_views

    # 3. Category Pie Chart Data
    categories = Category.objects.all()
    category_labels = []
    category_counts = []

    for category in categories:
        category_labels.append(category.name)
        category_counts.append(
            notices.filter(category=category).count()
        )

    # 4. Monthly Trend Graph Data
    monthly_data = (
        notices
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    trend_labels = []
    trend_counts = []

    for entry in monthly_data:
        if entry['month']: 
            trend_labels.append(entry['month'].strftime("%b %Y"))
            trend_counts.append(entry['count'])

    context = {
        'total_notices': total_notices,
        'total_categories': total_categories,
        'total_engagement': total_engagement,
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
from django.utils import timezone

def notice_detail(request, pk):

    notice = get_object_or_404(Notice, pk=pk)

    # Increment views count
    notice.views_count += 1
    notice.save()

    context = {
        'notice': notice
    }

    return render(request, 'noticeboard/notice_detail.html', context)


from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Capture the 'next' destination from the URL (defaults to 'home')
        next_url = request.GET.get('next', 'home')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect to the 'next' page if it exists, otherwise go home
            return redirect(next_url)
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



from django.db.models import Sum, Count
from .models import Notice, Category

@login_required(login_url='login')
@user_passes_test(staff_check)
def analytics_dashboard(request):
    """
    CLEANED MASTER DASHBOARD:
    Calculates engagement, chart data, and fetches the activity log.
    """
    # 1. Fetch all notices with their categories (prevents database lag)
    notices_queryset = Notice.objects.select_related('category').all().order_by('-created_at')
    
    # 2. Key Stats
    total_notices = notices_queryset.count()
    total_categories = Category.objects.count()
    latest_notices = notices_queryset[:10]  # This supplies the 'Activity Log' table

    # 3. ENGAGEMENT CALCULATION (Fixes the "0" issue)
    # Counts every record in the 'likes' many-to-many table
    t_likes = Notice.objects.aggregate(total=Count('likes'))['total'] or 0
    # Adds up the 'views_count' column from every notice
    t_views = Notice.objects.aggregate(total=Sum('views_count'))['total'] or 0
    total_engagement = t_likes + t_views

    # 4. CHART DATA: Categories
    categories = Category.objects.all()
    category_labels = [cat.name for cat in categories]
    category_counts = [notices_queryset.filter(category=cat).count() for cat in categories]

    # 5. CHART DATA: Monthly Trend
    monthly_data = (
        notices_queryset
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    trend_labels = [entry['month'].strftime("%b %Y") for entry in monthly_data if entry['month']]
    trend_counts = [entry['count'] for entry in monthly_data if entry['month']]

    context = {
        'total_notices': total_notices,
        'total_categories': total_categories,
        'total_engagement': total_engagement,
        'latest_notices': latest_notices,
        'category_labels': category_labels,
        'category_counts': category_counts,
        'trend_labels': trend_labels,
        'trend_counts': trend_counts,
    }
    return render(request, 'noticeboard/dashboard.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required


@login_required(login_url='login')
@user_passes_test(staff_check)
def user_list(request):
    users = User.objects.all().exclude(is_superuser=True) # Don't block yourself!
    return render(request, 'noticeboard/user_list.html', {'users': users})

@login_required(login_url='login')
@user_passes_test(staff_check)
def toggle_user_status(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    # is_active controls if they can log in
    target_user.is_active = not target_user.is_active
    target_user.save()
    return redirect('user_list')