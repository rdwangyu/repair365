from django.db import models

# Create your models here.
class CommonModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserModel(models.Model):
    openid = models.CharField(max_length=32, unique=True)
    access_token = models.CharField(max_length=128)
    token_expired = models.DateTimeField()

    class Meta:
        abstract = True
    
class UserCustomerModel(CommonModel, UserModel):

    ACCOUNT_STATUS_CHOICES = {
        0: 'create',
        1: 'block',
        2: 'delete',
    }

    phone = models.CharField(max_length=11, blank=True, default='')
    nickname = models.CharField(max_length=64, blank=True, default='')
    sex = models.SmallIntegerField(blank=True, default=0)
    age = models.SmallIntegerField(blank=True, default=0)
    address = models.TextField(max_length=256, blank=True, default='')
    account_status = models.SmallIntegerField(choices=ACCOUNT_STATUS_CHOICES, blank=True, default=0)

    def __str__(self):
        return f'User({self.nickname})-Phone({self.phone})'

    class Meta:
        db_table = 'user_customer'
        verbose_name = 'customer'
        verbose_name_plural = verbose_name

class UserMasterModel(CommonModel, UserModel):
    def upload_image_file(instance, filename):
        ext = filename.split('.')[-1]
        return f'image/{instance.fullname}_{instance.phone}/uploads.{ext}'
    
    ACCOUNT_STATUS_CHOICES = {
        0: 'create',
        1: 'review',
        2: 'block',
        3: 'delete'
    }
    fullname = models.CharField(max_length=64)
    sex = models.SmallIntegerField()
    age = models.SmallIntegerField()
    avatar = models.ImageField(upload_to=upload_image_file)
    identity_card_0 = models.ImageField(upload_to=upload_image_file)
    identity_card_1 = models.ImageField(upload_to=upload_image_file)
    business_license = models.ImageField(upload_to=upload_image_file)
    phone = models.CharField(max_length=11)
    address = models.TextField(max_length=256)
    work_year = models.SmallIntegerField()
    #skill_tree =
    #active_region_range =
    #active_time_range
    level = models.SmallIntegerField(blank=True, default=0)
    user_grade = models.DecimalField(max_digits=2, decimal_places=1, blank=True, default=1.0)
    account_status = models.SmallIntegerField(choices=ACCOUNT_STATUS_CHOICES, blank=True, default=0)

    def __str__(self):
        return f'User({self.fullname})-Phone({self.phone})'
        
    class Meta:
        db_table = 'user_master'
        verbose_name = 'master'
        verbose_name_plural = verbose_name


class RepairOrderModel(CommonModel):
    REPAIR_CATEGORY_CHOICES = {
        0: '维修电动车'
    }
    TRANSACTION_TYPE_CHOICES = {
        0: '网络支付'
    }
    ORDER_STATUS_CHOICES = {
        0: 'create',
        1: 'cancel',
        2: 'delete',
    }
    
    order_number = models.CharField(max_length=36)
    sponsor = models.ForeignKey(UserCustomerModel, on_delete=models.DO_NOTHING)
    location = models.TextField(max_length=256)
    repair_category = models.SmallIntegerField(choices=REPAIR_CATEGORY_CHOICES)
    contact_phone = models.CharField(max_length=11)
    issue_description = models.TextField(max_length=4096)
    appointment_time = models.DateTimeField(blank=True, null=True)
    comment = models.TextField(max_length=1024, blank=True, default='')
    assignee = models.ForeignKey(UserMasterModel, blank=True, null=True, on_delete=models.DO_NOTHING)
    transaction_amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, default=0.0)
    transaction_type = models.SmallIntegerField(choices=TRANSACTION_TYPE_CHOICES, blank=True, default=0)
    order_status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, blank=True, default=0)


    def __str__(self):
        return f'{self.sponsor.nickname}->{self.assignee.fullname} {self.get_repair_category_display()} {self.transaction_amount}'

    class Meta:
        db_table = 'repair_order'
        verbose_name = 'order'
        verbose_name_plural = verbose_name
