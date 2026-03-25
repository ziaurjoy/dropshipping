from django.db import models
from django.contrib.auth.models import AbstractUser

USER_TYPE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('VENDOR', 'Vendor'),
        ('CUSTOMER', 'Customer'),
        ('STAFF', 'Staff'),
    )



class User(AbstractUser):
    email = models.EmailField(unique=True)

    # Optional: login via email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    is_verified = models.BooleanField(default=False)

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    # Override ManyToMany fields to avoid reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='users_app_user_groups',
        related_query_name='users_app_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='users_app_user_permissions',
        related_query_name='users_app_user',
    )

    def __str__(self):
        return self.email



class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')

    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Dropshipping-specific
    company_name = models.CharField(max_length=255, blank=True, null=True)
    store_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email}"