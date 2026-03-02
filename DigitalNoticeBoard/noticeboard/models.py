from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



from django.contrib.auth.models import User

class Profile(models.Model):

    DEPARTMENT_CHOICES = [
        ('cse', 'CSE'),
        ('ece', 'ECE'),
        ('mech', 'Mechanical'),
        ('mba', 'MBA'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(
        max_length=20,
        choices=DEPARTMENT_CHOICES
    )

    def __str__(self):
        return self.user.username
    

class Notice(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='notice_files/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)

    department = models.CharField(
        max_length=20,
        choices=Profile.DEPARTMENT_CHOICES,
        default='cse'
    )

    views_count = models.IntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name='liked_notices', blank=True)

    # ✅ MOVE THIS INSIDE
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='low'
    )

    def __str__(self):
        return self.title