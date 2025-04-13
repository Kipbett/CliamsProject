from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class CustUser(AbstractUser):
    class RoleChoices(models.TextChoices):
        ADMIN = 'admin'
        REP = 'student_rep'
        LECTURER = 'lecturer'
        ACCOUNTANT = 'accountant'
        DEAN = 'faculty_dean'
    

    phone_number = models.IntegerField(null= True, blank=True)
    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.ADMIN)

    def __str__(self):
        return f"{self.username} {self.last_name}"
    
class Claims(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING = 'pending'
        APPROVED = 'approved'
        DISPUTE = 'dispute'
        CANCELLED = 'cancelled'
        PAID = 'paid'

    lecturer = models.ForeignKey(CustUser, on_delete=models.CASCADE)
    course = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    start_time = models.TimeField(auto_now_add=True)
    end_time = models.TimeField(null=True)
    date_taught = models.DateField(auto_now_add=True)

    @property
    def time_taught(self):

        if self.start_time and self.end_time:
            start = self.start_time
            end = self.end_time

            start_datetime = datetime(2000, 1, 1, start.hour, start.minute, start.second)
            end_datetime = datetime(2000, 1, 1, end.hour, end.minute, end.second)
            duration = end_datetime - start_datetime
            return duration.total_seconds()/3600
        else:
            return 0
    
    @property
    def claim_sub_total(self):
        duration = self.time_taught
        return duration * 2000

    def __str__(self):
        return f'{self.lecturer.first_name} {self.date_taught}'
    
class ClaimsPayment(models.Model):
    claims = models.ManyToManyField(Claims, related_name='claims')
    lecturer = models.ForeignKey(CustUser, on_delete=models.CASCADE)
    date_paid = models.DateTimeField(auto_now_add=True)
    amount_paid = models.PositiveIntegerField()
    balance = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.lecturer.first_name
    
class ClaimsApproval(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending'
        APPROVED = 'approved'
        DISPUTE = 'dispute'
        CANCELLED = 'cancelled'
        PAID = 'paid'
    claim = models.ForeignKey(Claims, on_delete=models.CASCADE)
    rep_approval = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    dean_approval = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    acc_approval = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)

    def __str__(self):
        return f"{self.claim.lecturer.username} {self.claim.course}"
