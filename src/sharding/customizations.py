
import uuid
from functools import reduce

from django.db import models
from django.utils import timezone
from django.conf import settings

from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)

from .querysetsequence import QuerySetSequence
from .models import Databases
from .utils import select_write_db
 
################# User model ############################
class  ShardedUserManager(BaseUserManager):

    def create_user(self, username, email, password=None, is_staff =False, is_superuser = False):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        # get prefix    
        try:
            db = select_write_db(model_name=self.model._meta.model_name)
            prefix = db.get_prefix 
        except:
            uuid3  = uuid.uuid3(uuid.NAMESPACE_DNS,settings.USER_INIT_DATABASE)
            prefix =  str(uuid3)[:8]
 
        # create uuidn
        uuidn =  prefix + "-" + str(uuid.uuid4())[9:]    

        user = self.model(
            username = username, 
            email = self.normalize_email(email),
            nid   = str(uuidn),
        )

        user.set_password(password)
        user.staff = is_staff
        user.admin = is_superuser

        if settings.SHARDING_USER_MODEL:
            user.save(using=str(db.get_name))
            db.count = db.count + 1
            db.save()
        else:
            user.save(using=self._db)
        return user

    def create_staffuser(self, username, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        return self.create_user(username, email, password, is_staff = True)
    
    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        return self.create_user(username, email, password, is_staff = True, is_superuser= True) 

    def get_queryset(self):
        if settings.SHARDING_USER_MODEL:
            db_list = Databases.objects.all().filter(model_name=self.model._meta.model_name).exclude(count=0)
            if db_list.count() != 0:       
                return reduce(QuerySetSequence, [super(ShardedUserManager, self).get_queryset().using(db.get_name) for db in db_list])          
            return super(ShardedUserManager, self).get_queryset().none()
        else:
            return super(ShardedUserManager, self).get_queryset()
    
    def raw_queryset(self, using = None):
        if using:
            return super(ShardedUserManager, self).get_queryset().using(using)
        else:
            return super(ShardedUserManager, self).get_queryset()


class ShardedUser(AbstractBaseUser):
    nid      = models.CharField(db_index=True, editable=False, max_length=36, unique=True, primary_key=True)
    username = models.CharField(verbose_name='Username', max_length=120,db_index=True, unique=True)
    email    = models.EmailField(verbose_name='email address', max_length=255, db_index=True, unique=True)
    active   = models.BooleanField(default=True)
    staff    = models.BooleanField(default=False) # a admin user; non super-user
    admin    = models.BooleanField(default=False) # a superuser
    date_joined = models.DateTimeField(editable=False, default=timezone.now)
    first_name  = models.CharField(verbose_name='First name', max_length=225)
    last_name   = models.CharField(verbose_name='First name', max_length=225)
    birth_date  = models.DateTimeField(default=timezone.now)
    # notice the absence of a "Password field", that is built in.

    objects = ShardedUserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ["username"] # Email & Password are required by default.

    if settings.SHARDING_USER_MODEL:
        SHAREDED_MODEL  = True
    else:
        SHAREDED_MODEL  = False
    
    def get_full_name(self):
        # The user is identified by their email address
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __unicode__(self):  # on Python 2
        return self.email

    def __str__(self):             
        return self.email

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
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        "Is the user active?"
        return self.active

    # for user multidatabase table save 
    def save(self, *args, **kwargs):
        if settings.SHARDING_USER_MODEL:
            # select database name
            db = select_write_db(model_name=self._meta.model_name)
            if self.nid:
                # get prefix
                prefix = str(self.nid)[:8]
                # get database name
                db_name = Databases.objects.get_data_by_prefix(prefix)
                # save
                if "using" in kwargs:
                    super(ShardedUser, self).save(*args, **kwargs)
                else:
                    super(ShardedUser, self).save(*args, **kwargs, using=str(db_name))
            else:
                # get prefix
                prefix = db.get_prefix
                # create nid
                self.nid = str(prefix)+ "-" + str(uuid.uuid4())[9:]
                # write to selected database 
                if kwargs["using"]:
                    super(ShardedUser, self).save(*args, **kwargs)
                else:
                    super(ShardedUser, self).save(*args, **kwargs, using=db.get_name)
                # update count
                db.count = db.count + 1
                db.save()
        else:
            super(ShardedUser, self).save(*args, **kwargs)


################# All Models ############################
class ShardedModelManager(models.Manager):

    def raw_queryset(self, using = None):
        if using:
            return super(ShardedModelManager, self).get_queryset().using(using)
        else:
            return super(ShardedModelManager, self).get_queryset()

    def get_queryset(self):
        db_list = Databases.objects.all().filter(model_name=self.model._meta.model_name).exclude(count=0)
        if db_list.count() != 0:           
            return reduce(QuerySetSequence, [super(ShardedModelManager, self).get_queryset().using(db.get_name) for db in db_list])           
        return super(ShardedModelManager, self).get_queryset().none()


class ShardedModel(models.Model):

    nid   = models.CharField(db_index=True, editable=False, max_length=36, unique=True, primary_key=True)

    objects = ShardedModelManager()

    SHAREDED_MODEL  = True

    class Meta:
        ordering = ['nid']

    def save(self, *args, **kwargs):
        #print("in save: ", self.__class__.objects._db)
        #print("in save: ", self._state.db)
        # select database name
        db = select_write_db(model_name=self._meta.model_name)
        # get prefix
        prefix = db.get_prefix
        if self.nid:
            # get prefix
            prefix = str(self.nid)[:8]
            # get database name
            db_name = Databases.objects.get_data_by_prefix(prefix)
            # save
            #Product
            super(ShardedModel, self).save(*args, **kwargs, using=str(db_name))
        else:
            # create nid
            self.nid = str(prefix)+ "-" + str(uuid.uuid4())[9:]
            # write to selected database 
            super(ShardedModel, self).save(*args, **kwargs, using=db.get_name)
            # update count
            db.count = db.count + 1
            db.save()
