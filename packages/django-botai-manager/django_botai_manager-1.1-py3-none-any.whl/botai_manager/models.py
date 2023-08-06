from django.db import models


class Company(models.Model):
    email_sale_notification = models.TextField(null=True)
    
    class Meta:
        db_table = 'company'
        managed = False
