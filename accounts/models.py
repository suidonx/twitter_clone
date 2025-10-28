from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        validators=[RegexValidator(r"\d{10,15}", "10~15桁の数字を入力してください")],
    )
    birth_of_date = models.DateField(null=True, blank=True)
    icon_image = models.ImageField(
        upload_to="icon/",
        null=True,
        blank=True,
    )
    header_image = models.ImageField(
        upload_to="header/",
        null=True,
        blank=True,
    )
    self_introduction = models.TextField(null=True, blank=True)
    place = models.CharField(null=True, blank=True)
    website = models.CharField(null=True, blank=True)

    REQUIRED_FIELDS = ["email", "phone_number", "birth_of_date"]
