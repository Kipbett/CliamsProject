from django import forms
from .models import CustUser, Claims, ClaimsPayment, ClaimsApproval
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

class ClaimsApprovalForm(forms.Form):
    class StatusChoices:
        PENDING = 'pending'
        APPROVED = 'approved'
        DISPUTE = 'dispute'
        CANCELLED = 'cancelled'
        PAID = 'paid'

        CHOICES = [
            (PENDING, 'pending'),
            (APPROVED, 'approved'),
            (DISPUTE, 'dispute'),
            (CANCELLED, 'cancelled'),
            (PAID, 'paid')
        ]

    claim_status = forms.ChoiceField(choices=StatusChoices.CHOICES)
    # class Meta:
    #     model = ClaimsApproval
    #     fields = (
    #         'status',
    #     )
