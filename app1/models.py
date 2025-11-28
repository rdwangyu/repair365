from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    user_type = models.IntegerField(choices=[(1, 'customer'), (2, 'master'), (3, 'admin')])
    def __str__(self):
        return self.name



