from django.db import models

# Create your models here.
class CommonModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserModel(models.Model):
    SEX_CHOICES = [(0, 'unknown'), (1, 'male'), (2, 'female')]

    openid = models.CharField(max_length=32, unique=True)
    access_token = models.CharField(max_length=128)
    token_expired = models.DateTimeField()
    sex = models.SmallIntegerField(choices=SEX_CHOICES, blank=True, default=0)
    age = models.SmallIntegerField(blank=True, default=0)

    class Meta:
        abstract = True
    
class UserCustomerModel(CommonModel, UserModel):

    ACCOUNT_STATUS_CHOICES = {
        0: 'created',
        1: 'blocking',
        2: 'deleted',
    }

    phone = models.CharField(max_length=11)
    nickname = models.CharField(max_length=64, blank=True, default='')
    address = models.TextField(max_length=256, blank=True, default='')
    account_status = models.SmallIntegerField(choices=ACCOUNT_STATUS_CHOICES, blank=True, default=0)

    def __str__(self):
        return f"User({self.nickname})-Phone({self.phone})"

    class Meta:
        db_table = 'user_customer'
        verbose_name = 'customer'
        verbose_name_plural = verbose_name


class UserMasterModel(CommonModel):
    ACCOUNT_STATUS_CHOICES = {
        0: 'created',
        1: 'reviewing',
        2: 'reviewed',
        3: 'blocking',
        4: 'deleted'
    }
    fullname = models.CharField(max_length=64)
    avatar = models.ImageField()
    idcard_front = models.ImageField()
    idcard_back = models.ImageField()
    business_license = models.ImageField()
    phone = models.CharField(max_length=11)
    address = models.TextField(max_length=256)
    work_year = models.SmallIntegerField()
    #skill_tree =
    #active_region_range =
    #active_time_range
    level = models.SmallIntegerField(blank=True, default=0)
    user_grade = models.DecimalField(max_digits=2, decimal_places=1, blank=True, default=1.0)

    def __str__(self):
        return f"User({self.fullname})-Phone({self.phone})"
        
    class Meta:
        db_table = 'user_master'
        verbose_name = 'master'
        verbose_name_plural = verbose_name
