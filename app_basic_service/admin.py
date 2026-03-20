from django.contrib import admin
from .models import UserCustomerModel, UserMasterModel, RepairOrderModel

# Register your models here.
admin.site.register(UserCustomerModel)
admin.site.register(UserMasterModel)
admin.site.register(RepairOrderModel)
