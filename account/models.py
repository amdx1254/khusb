from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self,userid,  email, username, password=None):
        if not email:
            raise ValueError(_('Users must have an email address'))
        if not userid:
            raise ValueError(_('Users must have an ID'))
        if not username:
            raise ValueError(_('Users must have an username'))
        user = self.model(userid=userid, username=username, email=self.normalize_email(email))

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, userid, email, username, password):
        user = self.create_user(userid=userid, email=email, username=username, password=password)
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255,unique=True)
    userid = models.CharField(max_length=30, unique=True)
    username = models.CharField(max_length=30)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'userid'
    REQUIRED_FIELDS = ['username', 'email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('-date_joined',)

    def __str__(self):
        return self.userid

    def get_full_name(self):
        return self.userid

    def get_short_name(self):
        return self.userid

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All superusers are staff
        return self.is_superuser

    get_full_name.short_description = _('Full name')