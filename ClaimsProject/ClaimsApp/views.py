from datetime import datetime, time
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from Utils.utils import pending_claims
from .forms import UserForm, ClaimsForm, ClaimsPaymentForm, UserLoginForm, ClaimsApprovalForm
from .models import Claims, ClaimsApproval, ClaimsPayment
from django.contrib.auth import login, get_user_model, authenticate, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
# Create your views here.

User = get_user_model()

def add_user(request):
    title = "Add New User"
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            messages.success(request, "Registration Successful")
            return redirect('user_login')
    else:
        form = UserForm()

    return render(request, 'new-user.html', {'user_form': form, 'title': title})

@login_required(login_url='/user-login/')
def add_claim(request):
    title = "Add New Claim"
    if request.method == 'POST':
        claims_form = ClaimsForm(request.POST)
        if claims_form.is_valid():
            claims_form.save(commit=fasle)
            # return redirect('claims_list')
        claims = Claims.objects.last()
        claims_id = claims.id
        new_claim = ClaimsApproval(claim_id=claims_id)
        new_claim.save()
        messages.success(request, "Claim Approval Added")
        return redirect('claims_list')

    else:
        claims_form = ClaimsForm()

    return render(request, 'new-claim.html', {'claims_form': claims_form, 'title': title})

@login_required(login_url='/user-login/')
def list_claim(request):
    
    title = "Claims List"
    pending_claims = Claims.objects.filter(status='pending')
    approved_claims = Claims.objects.filter(status='approved')
    user = request.user
    user_id = request.user.id
    user_role = request.user.role
    pending_duration = []
    approved_duration = []
    roles = []
    for claim in pending_claims:
        pending_duration.append(int(claim.time_taught))

    for app_claim in approved_claims:
        approved_duration.append(int(app_claim.time_taught))

    for role in roles:
        roles.append(user_role)

    claim_approve = ClaimsApprovalForm(request.POST)
    if request.method == 'POST':
        
        if claim_approve.is_valid():
            status = claim_approve.cleaned_data['claim_status']
            claim_id = request.POST.get('claim_id')

            update = get_object_or_404(ClaimsApproval, claim_id=claim_id)

            if user_role == 'student_rep':
                if update.rep_approval == 'pending':
                    update.rep_approval = status
                else:
                    messages.error(request, "You have already approved this claim")
                    return redirect('claims_list')
            elif user_role == 'faculty_dean':
                if update.dean_approval == 'pending':
                    update.dean_approval = status
                else:
                    messages.error(request, "You have already approved this claim")
                    # return redirect('claims_list')
            elif user_role == 'accountant':
                if update.acc_approval == 'pending':
                    update.acc_approval = status
                else:
                    messages.error(request, "You have already approved this claim")
                    return redirect('claims_list')
            else:
                messages.error(request, "You are not authorized to update this claim.")
                return redirect('claims_list')
            
            update.save()
            return redirect('claims_list')
    pending_claims_data = zip(pending_claims, pending_duration)
    approved_claims_data = zip(approved_claims, approved_duration)
    context = {
        'pending_claims': pending_claims_data,
        'approved_claims': approved_claims_data,
        'title': title,
        'user': user,
        'user_id': user_id,
        'user_role': user_role,
    }
    return render(request, 'claims-list.html', context)

def user_login(request):
    title = "User Login"
    if request.method == 'POST':
        login_form = UserLoginForm(request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.get(email=email)
                authenticated_user = authenticate(request, username=user.username, password=password)
                if authenticated_user is not None:
                    login(request, authenticated_user)
                    messages.success(request, "Login Successful")
                    return redirect('dashboard')
                    # return render(request, "dashboard.html")
                
                else:
                    messages.error(request, "Invalid Email or Password ")
            except User.DoesNotExist:
                messages.error(request, "User Does Not Exist") 
    else:
        login_form = UserLoginForm()

    return render(request, 'user-login.html', {'login_form': login_form, 'title': title})

@login_required(login_url='/user-login/')
def claims_payment(request, id):
    claims = Claims.objects.get(id=id)
    
    if claims.status == 'approved':
        claims.status = 'paid'
        claims.save()
        messages.success(request, "Claim Successfully Paid")
        claim_payment = ClaimsPayment(
            amount_paid= claims.claim_sub_total,
            lecturer_id= claims.lecturer.id
        )

        claim_payment.save()
        return redirect('approved_claims')
            
    else:
        messages.warning(request, "Claim Already Approved")
        return redirect('approved_claims')
    
@login_required(login_url='/user-login/')
def approve_claim(request):
    title = "Approve Claim"
    if request.method == 'POST':
        approval_form = ClaimsApprovalForm(request.POST)
        if approval_form.is_valid():
            approval_form.save()
            return redirect('claims_list')
    else:
        approval_form = ClaimsApprovalForm()

    return render(request, 'claim-approval.html', {'approval_form': approval_form, 'title': title})

@login_required(login_url='/user-login/')
def payment_list(request):
    title = "Payment List"
    payments = ClaimsPayment.objects.all()
    return render(request, 'payment-list.html', {'payments': payments, 'title': title})

@login_required(login_url='/user-login/')
def update_claim(request, id):
    # claim_update = get_object_or_404(ClaimsApproval, id=id)
    # update = ClaimsApproval.objects.filter(id=claim_id)
    claims = get_object_or_404(Claims, id=id)
    status = 'approved'
    user = request.user
    user_role = request.user.role

    if user_role == 'student_rep':
        update = ClaimsApproval.objects.get(claim_id=id)
        if update.rep_approval == 'pending':
            update.rep_approval = status
            update.save()
            messages.success(request, "Claim Successfuly Approved")
        else:
            messages.warning(request, "Claim Is already Approved")
        return redirect('claims_list')
    
    elif user_role == 'faculty_dean':
        update = ClaimsApproval.objects.get(claim_id=id)
        if update.dean_approval == 'pending':
            update.dean_approval = status
            update.save()
            messages.success(request, "Claim Successfully Approved")
        else:
            messages.warning(request, "Claim Is already Approved")
        return redirect('claims_list')
    
    elif user_role == 'accountant':
        update = ClaimsApproval.objects.get(claim_id=id)
        if update.acc_approval == 'pending':
            update.acc_approval = status
            update.save()
            messages.success(request, "Claim Successfully Approved")
        else:
            messages.warning(request, "Claim Is already Approved")

        if update.acc_approval == status and update.dean_approval == status and update.rep_approval == status:
            claims.status = status
            claims.save()
            messages.success(request, "Claim Fully approved. \n You can now pay the claim")
        return redirect('claims_list')
    
    else:
        messages.error(request, f"User not allowed. { user_role }")
        return redirect('claims_list')

def approive_claim(request, id):
    update = ClaimsApproval.objects.get(id=id)
    claims = Claims.objects.get(id=id)
    if claims.status == 'pending' and update.dean_approval == 'pending' and update.acc_approval == 'pending' and update.rep_approval == 'pending':
        claims.status = 'approved'
        claims.save()
        return redirect('claims_list')

    

@login_required(login_url='/user-login/')   
def dashboard(request):
    user = request.user
    user_id = request.user.id
    user_role = request.user.role
    claim_stats = pending_claims(user_id)
    stats = {
        'user': user,
        'user_id': user_id,
        'user_role': user_role,
        'pending_claims': claim_stats['pending_claims'],
        'approved_claims': claim_stats['approved_claims'],
        'total_hours': claim_stats['total_hours'],
        'total_amount': claim_stats['total_amount'],
        'paid_amount': claim_stats['paid_amount'],
        'balance': claim_stats['balance'],
    }
    return render(request, 'dashboard.html', {'stats': stats})

def end_claim(request, id):
    end_time = datetime.now().time()
    claims = Claims.objects.filter(id=id, end_time=None)
    if claims:
        for claim in claims:
            claim.end_time = end_time
            claim.save()
            messages.success(request, "Claim Successfully Ended")
        return redirect('claims_list')
    else:
        messages.error(request, "Could not end claim")
        return redirect('dashboard')

def approved_claims(request):
    approved = Claims.objects.filter(status='approved')
    duration = []
    sum_amount = []
    for claim in approved:
        duration.append(claim.time_taught)

    for cliam in approved:
        sum_amount.append(claim.claim_sub_total)
    
    # claims_data = zip(duration, approved, sum_amount)
    content = {
        'title': 'Approved Claims',
        'approved': approved
    }

    return render(request, 'approved-claims.html', content)

def logout(request):
    auth_logout(request)
    return redirect('user_login')