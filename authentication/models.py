from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser


class AllianceUserManager(BaseUserManager):

    def create_user(self, username, email , password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not username:
            raise ValueError('Users must have a username')

        if not email:
            raise ValueError('Users must have an email address')

        user = AllianceUser()
        user.set_username(username)
        user.set_email(email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user_withapi(self, username, email, password, api_id, api_key):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        
        if not username:
            raise ValueError('Users must have a username')

        if not email:
            raise ValueError('Users must have an email address')

        user = AllianceUser()
        user.set_username(username)
        user.set_email(email)
        user.set_password(password)
        user.api_id = api_id
        user.api_key = api_key
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(username, email, password)
        user.is_admin = True
        user.is_moderator = True
        user.save(using=self._db)
        return user
    
    def update_user_main_character(self, character_id, user_id):
        user = AllianceUser.objects.get(id=user_id)
        user.main_char_id = character_id
        user.save(update_fields=['main_char_id'])
        
    def check_if_user_exist_by_id(self, user_id):
        return AllianceUser.objects.filter(id=user_id).exists()

    def check_if_user_exist_by_name(self, user_name):
        return AllianceUser.objects.filter(username=user_name).exists()

    def update_user_form_info(self, username, password, user_id):
        if AllianceUser.objects.filter(id=user_id).exists():
            user = AllianceUser.objects.get(id=user_id)
            user.forum_username = username
            user.forum_password = password
            user.save(update_fields=['forum_username', 'forum_password'])

    def update_user_jabber_info(self, username, password, user_id):
        if AllianceUser.objects.filter(id=user_id).exists():
            user = AllianceUser.objects.get(id=user_id)
            user.jabber_username = username
            user.jabber_password = password
            user.save(update_fields=['jabber_username', 'jabber_password'])

    def update_user_mumble_info(self, username, password, user_id):
        if AllianceUser.objects.filter(id=user_id).exists():
            user = AllianceUser.objects.get(id=user_id)
            user.mumble_username = username
            user.mumble_password = password
            user.save(update_fields=['mumble_username', 'mumble_password'])


class AllianceUser(AbstractBaseUser):
    username = models.CharField(max_length=40, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    api_id = models.CharField(max_length=254)
    api_key = models.CharField(max_length=254)
    main_char_id = models.IntegerField(default=0)

    # Login information stuff
    forum_username = models.CharField(max_length=64)
    forum_password = models.CharField(max_length=64)
    jabber_username = models.CharField(max_length=64)
    jabber_password = models.CharField(max_length=64)
    mumble_username = models.CharField(max_length=64)
    mumble_password = models.CharField(max_length=64)

    objects = AllianceUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def set_username(self,username):
        self.username = username

    def set_email(self, email):
        self.email = email

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.username

    # On Python 3: def __str__(self):
    def __unicode__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

