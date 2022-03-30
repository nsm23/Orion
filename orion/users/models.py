from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), unique=True, max_length=64)
    email = models.EmailField(_('email'), unique=True)
    name = models.CharField(_('name'), max_length=128, blank=True)
    birth_year = models.DateField(_('birth date'), blank=True, null=True)
    bio = models.TextField(_('bio'), blank=True)
    avatar = models.ImageField(_('avatar icon'), default='avatars/no_avatar.png', upload_to='avatars')
    date_joined = models.DateTimeField(_('registered'), auto_now_add=True)
    is_active = models.BooleanField(_('is_active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_banned = models.BooleanField(
        verbose_name='Заблокирован',
        default=False,
    )
    rating = models.PositiveSmallIntegerField(
        verbose_name=_('Rating'),
        default=5,
        validators=[
            MinValueValidator(limit_value=1, message=_('The value must be between 1 and 10.')),
            MaxValueValidator(limit_value=10, message=_('The value must be between 1 and 10.')),
        ],
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', ]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return f'{self.username}'
