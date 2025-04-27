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
            return int(duration.total_seconds()/3600)
        else:
            return 0
    
    @property
    def claim_sub_total(self):
        duration = self.time_taught
        return duration * 1350

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
    
class ClaimsDispute(models.Model):
    claim = models.ForeignKey(Claims, on_delete=models.CASCADE)
    dispute_reason = models.TextField()
    date_disputed = models.DateTimeField(auto_now_add=True)
    dispute_by = models.ForeignKey(CustUser, on_delete=models.CASCADE, related_name='dispute_by')
    status = models.CharField(max_length=10, choices=ClaimsApproval.StatusChoices.choices, default=ClaimsApproval.StatusChoices.PENDING)

    def __str__(self):
        return f"{self.claim.lecturer.username} {self.claim.course}"
    
class ClaimsCancel(models.Model):
    claim = models.ForeignKey(Claims, on_delete=models.CASCADE)
    cancel_reason = models.TextField()
    date_cancelled = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.claim.lecturer.username} {self.claim.course}"
    
class ExamInvigilation(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending'
        APPROVED = 'approved'
        DISPUTE = 'dispute'
        CANCELLED = 'cancelled'
        PAID = 'paid'
    lecturer = models.ForeignKey(CustUser, on_delete=models.CASCADE)
    course = models.CharField(max_length=100)
    no_students = models.PositiveIntegerField(null=True)
    exam_venue = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    start_time = models.TimeField(auto_now_add=True)
    end_time = models.TimeField(null=True)
    date_invigilated = models.DateField(auto_now_add=True)
    date_paid = models.DateTimeField(auto_now_add=True)
    amount_paid = models.PositiveIntegerField(default=0)

    @property
    def time_invigilated(self):

        if self.start_time and self.end_time:
            start = self.start_time
            end = self.end_time

            start_datetime = datetime(2000, 1, 1, start.hour, start.minute, start.second)
            end_datetime = datetime(2000, 1, 1, end.hour, end.minute, end.second)
            duration = end_datetime - start_datetime
            return int(duration.total_seconds()/3600)
        else:
            return 0
        
    @property
    def invigilate_sub_total(self):
        duration = self.time_invigilated
        if duration == 0:
            return 0
        elif duration >= 2 and duration < 4:
            return duration * 1350
        else:
            return 0
        
    def __str__(self):
        return f'{self.lecturer.first_name} - {self.course}'
        
class SetExam(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending'
        APPROVED = 'approved'
        DISPUTE = 'dispute'
        CANCELLED = 'cancelled'
        PAID = 'paid'
    lecturer = models.ForeignKey(CustUser, on_delete=models.CASCADE)
    course = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    date_set = models.DateField(auto_now_add=True)
    exam_paper = models.FileField(upload_to='uploads', null=True)

    @property
    def set_exam_sub_total(self):
        return 1000
    def __str__(self):
        return f'{self.lecturer.first_name} - {self.course}'

class ExamPayment(models.Model):
    lecturer = models.ForeignKey(CustUser, on_delete=models.CASCADE, related_name='paid_to')
    amount_paid = models.PositiveIntegerField()
    paid_by = models.ForeignKey(CustUser, on_delete=models.CASCADE, related_name='paid_by')
    date_paid = models.DateTimeField(auto_now_add=True)
    exam_paid = models.ForeignKey(SetExam, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.lecturer.first_name} {self.exam_paid.course}'
    
class Appointment(models.Model):
    lecturer = models.ForeignKey(CustUser, on_delete=models.CASCADE, related_name='appointment_lec')
    appointment_letter = models.FileField(upload_to='uploads')
    date_uploaded = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(CustUser, on_delete=models.CASCADE, related_name='appointing_auth')

    def __str__(self):
        return self.lecturer.first_name
    