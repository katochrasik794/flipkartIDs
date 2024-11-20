from django.db import models
import django.utils.timezone
from django.contrib.auth.models import User


class email_info(models.Model):
    email = models.EmailField(max_length=50)
    phone_number = models.CharField(max_length=15, default=None, null=True)
    order_id = models.CharField(max_length=15, default=None, null=True)
    created_at = models.DateField(null=False, default=django.utils.timezone.now)
    assigned = models.BooleanField(null=False, default=False)
    status = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.email


class assigned_emails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emails = models.ManyToManyField(email_info)
