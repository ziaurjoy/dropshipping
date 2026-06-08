import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dropshipping_project_app.settings')
django.setup()

from users_app.models import User

email = 'admin@gmail.com'
password = '1234'

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password)
    print(f"✓ Superuser created with email: {email}")
else:
    print(f"✓ Superuser with email {email} already exists - skipping creation")
