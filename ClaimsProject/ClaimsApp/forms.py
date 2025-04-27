from django import forms
from .models import Appointment, ClaimsCancel, ClaimsDispute, CustUser, Claims, ClaimsPayment, ClaimsApproval, ExamInvigilation, SetExam
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()


class UserForm(forms.ModelForm):
    class Meta:
        model = CustUser
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'password'
        )


class ClaimsForm(forms.ModelForm):
    class Meta:
        model = Claims
        fields = (
            'lecturer',
            'course'
        )

class ClaimsPaymentForm(forms.ModelForm):
    class Meta:
        model = ClaimsPayment
        fields = (
            'claims',
            'lecturer',
            'amount_paid'
        )

class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class ClaimsDisputeForm(forms.ModelForm):
    class Meta:
        model = ClaimsDispute
        fields = (
            'dispute_reason',
        )

class ClaimsCancelForm(forms.ModelForm):
    class Meta:
        model = ClaimsCancel
        fields = (
            'cancel_reason',
        )

class ExamInvigilationForm(forms.ModelForm):
    class Meta:
        model = ExamInvigilation
        fields = (
            'course',
            'no_students',
            'exam_venue'
        )

class SetExamForm(forms.ModelForm):
    class Meta:
        model = SetExam
        fields = (
            'course',
            'exam_paper'
        )

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = (
            'lecturer',
            'appointment_letter',
        )