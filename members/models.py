from django.db      import models

from coupons.models import Coupon

class Member(models.Model):
    name         = models.CharField(max_length=200)
    email        = models.CharField(max_length=200, unique=True)
    password     = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=200, unique=True)
    address      = models.CharField(max_length=200, null=True)
    recommender  = models.ForeignKey("self", on_delete=models.SET_NULL, null=True)
    coupon       = models.ManyToManyField(Coupon, null=True)

    class Meta:
        db_table = 'members'