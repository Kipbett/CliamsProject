from django.contrib import admin
from .models import CustUser, Claims, ClaimsPayment, ClaimsApproval
# Register your models here.

admin.site.register(CustUser)
admin.site.register(Claims)
admin.site.register(ClaimsPayment)
admin.site.register(ClaimsApproval)