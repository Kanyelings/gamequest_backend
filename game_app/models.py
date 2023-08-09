from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models import Q


# Create your models here.

class GameUsersManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        try:
            user = GameUsers.objects.get(username=username)
        except GameUsers.DoesNotExist:
            user = self.model(username=username, **extra_fields)
            user.set_password(password)
            user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)


GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)


class GameUsers(AbstractBaseUser):
    username = models.CharField(
        max_length=250,
        unique=True
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = GameUsersManager()

    USERNAME_FIELD = 'username'

    class Meta:
        db_table = 'gamequest_users'
        verbose_name = "GameUsers"
        verbose_name_plural = "GameUsers"


User = settings.AUTH_USER_MODEL


class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(first_person=user) | Q(second_person=user)
        return self.get_queryset().filter(lookup).distinct()


class Thread(models.Model):
    first_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='thread_first_person')
    second_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='thread_second_person')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    class Meta:
        unique_together = ['first_person', 'second_person']


class chatMessage(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    sender = models.ForeignKey(GameUsers, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
