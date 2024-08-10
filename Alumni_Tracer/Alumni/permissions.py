from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

alumni_group, _ = Group.objects.get_or_create(name='Alumni')

def create_groups():
    # Create groups
    student_group, _ = Group.objects.get_or_create(name='Students')
    alumni_group, _ = Group.objects.get_or_create(name='Alumni')
    employer_group, _ = Group.objects.get_or_create(name='Employers')
    admin_group, _ = Group.objects.get_or_create(name='University Admin')
    leap_admin_group, _ = Group.objects.get_or_create(name='LEAP Admin')

def assign_permissions():
    # Assign permissions
    alumni_content_type = ContentType.objects.get(app_label='your_app_label', model='your_model_name')
    permission_view_profile = Permission.objects.get(content_type=alumni_content_type, codename='view_profile')
    permission_update_profile = Permission.objects.get(content_type=alumni_content_type, codename='change_profile')
    alumni_group.permissions.add(permission_view_profile, permission_update_profile)

def assign_user_to_group(user, group_name):
    # Assign user to group
    group = Group.objects.get(name=group_name)
    user.groups.add(group)
