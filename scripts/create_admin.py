import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

USERNAME = 'admin'
PASSWORD = 'adminpass'
EMAIL = 'admin@example.com'

user, created = User.objects.get_or_create(username=USERNAME, defaults={
    'email': EMAIL,
})

if created:
    user.set_password(PASSWORD)
    user.is_staff = True
    user.is_superuser = True
    user.user_type = 'admin'
    user.save()
    print(f"Created admin user '{USERNAME}' with password '{PASSWORD}'.")
else:
    changed = False
    if not user.is_superuser:
        user.is_superuser = True
        changed = True
    if not user.is_staff:
        user.is_staff = True
        changed = True
    if user.user_type != 'admin':
        user.user_type = 'admin'
        changed = True
    if changed:
        user.set_password(PASSWORD)
        user.save()
        print(f"Updated existing user '{USERNAME}' to admin with password '{PASSWORD}'.")
    else:
        print(f"Admin user '{USERNAME}' already exists. No changes made.")

print('Done.')
