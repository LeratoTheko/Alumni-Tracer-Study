from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, User
from .models import AlumniProfile


@receiver(post_save, sender=AlumniProfile)
def add_user_to_alumni_group(sender, instance, created, **kwargs):
    if created:
        alumni_group, created = Group.objects.get_or_create(name='Alumni')
        instance.user.groups.add(alumni_group)
