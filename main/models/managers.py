from django.contrib.auth.base_user import BaseUserManager
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from main.choices import (
    Role,
)


class UserManager(BaseUserManager):
    """
    Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User` for free.
    All we have to do is override the `create_user` function which we will use
    to create `User` objects.
    """

    def create_user(self, phone, password, **extra_fields):
        """Create and return a `User` with a username and password."""

        if phone is None:
            raise TypeError(_('Users must have a username'))

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, phone, password, **extra_fields):
        """
        Create and return a `User` with superuser powers.
        Superuser powers means that this use is an admin that can do anything
        they want.
        """

        if password is None:
            raise TypeError('Superusers must have a password')
        extra_fields['role'] = Role.OWNER
        user = self.create_user(phone, password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class StudentManager(Manager):
    def get_queryset(self):
        return super(StudentManager, self).get_queryset().filter(blacklist=False)


class GroupManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(archived=False)
