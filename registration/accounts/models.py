from hashlib import sha1

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser):
    username = models.CharField(unique=True, max_length=60)
    password = models.CharField(max_length=100)
    ip = models.GenericIPAddressField(blank=True, null=True)
    fail_count = models.IntegerField(default=0)
    login_attempt_time = models.DateTimeField(blank=True, null=True)
    is_banned = models.BooleanField(default=False)
    ip_banned = models.BooleanField(default=False)
    ban_time = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'users'

    @property
    def is_superuser(self):
        return True

    @property
    def is_staff(self):
        return True

    @staticmethod
    def hash_password(password):
        salt = settings.PASSWORD_SALT
        hashed_token = sha1((salt + password).encode()).hexdigest()
        return hashed_token

    def set_password(self, raw_password):
        self.password = User.hash_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        return User.hash_password(raw_password) == self.password

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
