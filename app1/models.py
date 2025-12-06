from django.db import models
from django.utils import timezone

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('customer', '客户'),
        ('implementer', '实施'),
    ]
    
    openid = models.CharField(max_length=255, unique=True)  # OpenID，唯一
    name = models.CharField(max_length=100)  # 用户名称
    phone = models.CharField(max_length=15)  # 用户电话
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)  # 用户类型（客户或实施）

    def __str__(self):
        return f"{self.name} ({self.get_user_type_display()})"


class RepairForm(models.Model):
    ORDER_STATUS_CHOICES = [
        ('created', '新建'),
        ('cancelled', '取消'),
        ('completed', '完成'),
        ('dispatched', '已派单'),
        ('dispatching', '派单中'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cash', '现金'),
        ('epay', '电子支付'),
    ]

    sponsor = models.CharField('发起者', max_length=20)
    description = models.TextField('问题描述')
    address = models.TextField('操作地址', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    appointment_time = models.DateTimeField('预约时间', null=True, blank=True)
    actual_arrival_time = models.DateTimeField('实际到达时间', null=True, blank=True)
    receiver = models.CharField('接收者', max_length=20, null=True, blank=True)
    order_status = models.CharField(
        '订单状态',
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='created'
    )
    amount = models.DecimalField('维修金额', max_digits=10, decimal_places=2, null=True, blank=True)
    payment_method = models.CharField(
        '支付方式',
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True
    )
    rating = models.IntegerField('用户评分', null=True, blank=True, choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField('用户评价', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '报修订单'
        verbose_name_plural = '报修订单'

    def __str__(self):
        return self.sponsor


