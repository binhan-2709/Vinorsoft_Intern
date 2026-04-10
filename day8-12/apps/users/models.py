"""
apps/users/models.py — Custom User model.

Day 8: Extend AbstractUser, thêm role và phone.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user với thêm trường role và phone."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        STAFF = "staff", "Nhân viên"
        CUSTOMER = "customer", "Khách hàng"

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"

    def __str__(self) -> str:
        return self.email

    @property
    def is_staff_member(self) -> bool:
        return self.role in (self.Role.ADMIN, self.Role.STAFF)