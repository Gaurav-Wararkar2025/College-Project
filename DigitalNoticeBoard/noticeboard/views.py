from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import Notice, Category
from .forms import NoticeForm


# ===============================
# HOME VIEW (Dashboard + Filters)
# ===============================
def home(request):
    """
    Displays all notices with:
    - Category filtering
    - Search functionality
    - Sorting
    - Pagination
    - Dashboard analytics
    """

    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    sort_order = request.GET.get('sort', '-created_at')

    notices = Notice.objects.all().order_by(sort_order)

    # Category Filter
    if category_id:
        notices = notices.filter(category_id=category_id)

    # Search Filter
    if search_query:
        notices = notices.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Pagination (6 notices per page)
    paginator = Paginator(notices, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    # Dashboard Analytics
    total_notices = Notice.objects.count()
    total_categories = Category.objects.count()

    context = {
        'notices': page_obj,
        'categories': categories,
        'total_notices': total_notices,
        'total_categories': total_categories,
        'search_query': search_query,
        'selected_category': category_id,
    }

    return render(request, 'noticeboard/home.html', context)


# ===============================
# ADD NOTICE
# ===============================
@login_required
def add_notice(request):
    """
    Allows only staff/admin users to add notice.
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
# EDIT NOTICE
# ===============================
@login_required
def edit_notice(request, pk):
    """
    Allows only staff/admin users to edit notice.
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
# DELETE NOTICE
# ===============================
@login_required
def delete_notice(request, pk):
    """
    Allows only staff/admin users to delete notice.
    """

    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to delete notices.")

    notice = get_object_or_404(Notice, pk=pk)

    if request.method == 'POST':
        notice.delete()
        messages.success(request, "Notice deleted successfully.")
        return redirect('home')

    return render(request, 'noticeboard/confirm_delete.html', {'notice': notice})