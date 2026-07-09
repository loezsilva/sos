import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager

from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django_lifecycle import LifecycleModelMixin
from django.contrib.auth.models import PermissionsMixin

import logging

logger = logging.getLogger("")


def avatar_upload_to(instance, filename):
    return f"avatar/{instance}-{filename}"


class User(LifecycleModelMixin, AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)

    avatar = models.ImageField(
        "Imagem", upload_to=avatar_upload_to, blank=True, null=True, max_length=5000
    )

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=("150 caracteres ou menos. Letras, números e @/./+/-/_ apenas."),
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    first_name = models.CharField(_("first name"), max_length=255, blank=True)

    name = models.CharField("Nome completo", max_length=255, blank=True)

    last_name = models.CharField(_("last name"), max_length=150, blank=True)

    email = models.EmailField(_("email address"), unique=True)

    phone = models.CharField("Telefone", max_length=30, blank=True, null=True)

    document = models.CharField(
        "CPF", max_length=30, unique=True, blank=True, null=True
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    date_of_birth = models.DateField("Data de nascimento", blank=True, null=True)

    accepted_the_terms_of_use = models.BooleanField(
        "Aceitou os termos de uso", blank=True, default=False
    )

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["date_joined"]

    def __str__(self):
        if self.name:
            return f"{self.name}"
        return f"{self.username}"
