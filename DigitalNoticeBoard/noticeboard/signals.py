from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from .models import Notice


@receiver(post_save, sender=Notice)
def send_notice_email(sender, instance, created, **kwargs):
    if created:

        subject = f"New Notice: {instance.title}"

        message = f"""
A new notice has been posted.

Title: {instance.title}

Category: {instance.category.name}

Content:
{instance.content}

View it on the Notice Board.
"""

        # Get all users with email
        users = User.objects.exclude(email="").values_list("email", flat=True)

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            list(users),
            fail_silently=False,
        )