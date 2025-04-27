from datetime import datetime, time
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from Utils.utils import pending_claims
from .forms import AppointmentForm, ClaimsDisputeForm, ExamInvigilationForm, SetExamForm, UserForm, ClaimsForm, ClaimsPaymentForm, UserLoginForm
from .models import Claims, ClaimsApproval, ClaimsDispute, ClaimsPayment, ExamInvigilation, ExamPayment, SetExam
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
            claims_form.save(commit=False)
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

    # claim_approve = ClaimsApprovalForm(request.POST)
    if request.method == 'POST':
        status = 'approved'
        # if claim_approve.is_valid():
        #     status = claim_approve.cleaned_data['claim_status']
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
    
# @login_required(login_url='/user-login/')
# def approve_claim(request):
#     title = "Approve Claim"
#     if request.method == 'POST':
#         approval_form = ClaimsApprovalForm(request.POST)
#         if approval_form.is_valid():
#             approval_form.save()
#             return redirect('claims_list')
#     else:
#         approval_form = ClaimsApprovalForm()

#     return render(request, 'claim-approval.html', {'approval_form': approval_form, 'title': title})

@login_required(login_url='/user-login/')
def payment_list(request):
    title = "Payment List"
    payments = ClaimsPayment.objects.all()
    return render(request, 'payment-list.html', {'payments': payments, 'title': title})

@login_required(login_url='/user-login/')
def update_claim(request, id):
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

@login_required(login_url='/user-login/')
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

@login_required(login_url='/user-login/')
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

@login_required(login_url='/user-login/')
def approved_claims(request):
    approved = Claims.objects.filter(status='approved')
    duration = []
    sum_amount = []
    for claim in approved:
        duration.append(claim.time_taught)

    for cliam in approved:
        sum_amount.append(claim.claim_sub_total)
    content = {
        'title': 'Approved Claims',
        'approved': approved
    }

    return render(request, 'approved-claims.html', content)

@login_required(login_url='/user-login/')
def claim_dispute(request, id):
    claim = Claims.objects.get(id=id)
    claim_approval = ClaimsApproval.objects.get(claim_id=id)
    user = request.user

    if claim.status == 'paid':
        messages.error(request, "Claim is already paid")
        return redirect('dispute_list')
    elif claim.status == 'dispute':
        messages.error(request, "Claim is already in dispute")
        return redirect('dispute_list')
    else:
        if request.method == 'POST':
            dispute_form = ClaimsDisputeForm(request.POST)
            if dispute_form.is_valid():
                reason = dispute_form.cleaned_data['dispute_reason']
                claim_dispute = ClaimsDispute(
                    claim=claim,
                    dispute_reason=reason,
                    dispute_by=user,
                )
                claim_dispute.save()
                if user.role == 'accountant':
                    claim_approval.acc_approval = 'dipsute'
                elif user.role == 'student_rep':
                    claim_approval.rep_approval = 'dispute'
                elif user.role == 'faculty_dean':
                    claim_approval.dean_approval = 'dispute'
                claim_approval.save()
                claim.status = 'dispute'
                claim.save()
                messages.success(request, "Claim Disputed")
                return redirect('dispute_list')
            else:
                messages.error(request, "Invalid Form Submission")
                return redirect('dispute_list')
        else:
            dispute_form = ClaimsDisputeForm()
    # return redirect('dispute_list')

@login_required(login_url='/user-login/')
def dispute_list(request):
    title = "Dispute List"
    disputes = Claims.objects.all()
    return render(request, 'claim-dispute.html', {'disputes': disputes, 'title': title})

@login_required(login_url='/user-login/')
def add_invigilation(request):
    user = request.user
    invigilation_form = ExamInvigilationForm(request.POST)
    if request.method == 'POST':
        if invigilation_form.is_valid():
            invigilate = invigilation_form.save(commit=False)
            invigilate.lecturer = user
            invigilate.save()
            messages.success(request, "Invigilation Added Successfully")
        return redirect('dashboard')
        
    else:
        invigilation_form = ExamInvigilationForm()

    return render(request, 'new-invigilation.html', {'invigilation_form': invigilation_form, 'user': user})

@login_required(login_url='/user-login/')
def invigilations(request):
    user = request.user
    invigilations = ExamInvigilation.objects.all()
    duration = []
    amount_to_pay = []
    for invigilation in invigilations:
        duration.append(invigilation.time_invigilated)
        amount_to_pay.append(invigilation.invigilate_sub_total)
    invigilation_details = zip(invigilations, duration, amount_to_pay)
    return render(request, 'invigilation.html', {'invigilations': invigilation_details, 'user': user})
    

@login_required(login_url='/user-login/')
def end_invigilation(request, id):
    invigilation = ExamInvigilation.objects.get(id=id)
    if invigilation and invigilation.end_time == None:
        invigilation.end_time = datetime.now().time()
        invigilation.save()
        messages.success(request, 'Invigilation Successfully Ended')
        return redirect('invigilation')
    else:
        messages.warning(request, 'Invigilation Already Ended')
        return redirect('invigilation')
    
@login_required(login_url='/user-login/')
def upload_exam(request):
    user = request.user
    upload_form = SetExamForm(request.POST, request.FILES)
    if request.method =='POST':
        if upload_form.is_valid():
            upload = upload_form.save(commit=False)
            upload.lecturer = user 
            upload.save()
            messages.success(request, 'Exam Successfully Uploaded')
        return redirect('dashboard')
    else:
        upload_form = SetExamForm()
    return render(request, 'upload-exam.html', {'upload_form': upload_form})

@login_required(login_url='/user-login/')
def upload_appointment(request):
    user = request.user
    appointment_form = AppointmentForm(request.POST, request.FILES)
    if request.method == 'POST':
        if appointment_form.is_valid():
            appointment = appointment_form.save(commit=False)
            appointment.uploaded_by = user
            appointment.save()
            messages.success(request, 'Appointment Letter Successfully Uploaded')
        return redirect('dashboard')
    else:
        appointment_form = AppointmentForm()
    return render(request, 'upload-appointment.html', {'appointment_form': appointment_form})

@login_required(login_url='/user-login/')
def exam_list(request):
    user = request.user
    exams = SetExam.objects.all()
    return render(request, 'exam-list.html', {'exams': exams, 'user': user})

@login_required(login_url='/user-login/')
def approve_exam(request, id):
    exams = SetExam.objects.filter(id=id, status='pending')
    if exams:
        for exam in exams:
            exam.status = 'approved'
            exam.save()
            messages.success(request, 'Exam Successfully Approved')
        return redirect('exam_list')
    else:
        messages.warning(request, 'No Pending Exam')
        return redirect('exam_list')

@login_required(login_url='/user-login/')   
def pay_exam(request, id):
    user = request.user
    exam = SetExam.objects.get(id=id)
    if exam and exam.status == 'approved':
        exam.status = 'paid'
        exam.save()
        payment = ExamPayment(
            lecturer=exam.lecturer,
            paid_by=user,
            exam_paid=exam,
            amount_paid=exam.set_exam_sub_total
        )
        payment.save()            
        messages.success(request, 'Exam Successfully Updated and Paid')
        return redirect('exam_list')
    else:
        messages.warning(request, 'Exam Already Paid For.')
        return redirect('exam_list')

@login_required(login_url='/user-login/')
def approve_invigilation(request, id):
    invigilation = ExamInvigilation.objects.get(id=id)
    if invigilation and invigilation.status == 'pending':
        invigilation.status = 'approved'
        invigilation.save()
        messages.success(request, 'Invigilation Successfully Approved')
        return redirect('invigilation')
    else:
        messages.warning(request, 'Invigilation Already Approved.')
        return redirect('invigilation')
    
@login_required(login_url='/user-login/')
def pay_invigilation(request, id):
    invigilation = ExamInvigilation.objects.get(id=id)
    if invigilation and invigilation.status == 'approved':
        invigilation.status = 'paid'
        invigilation.date_paid = datetime.now().date()
        invigilation.amount_paid = invigilation.invigilate_sub_total
        invigilation.save()
        messages.success(request, "Invigilation Successfully Paid")
        return redirect('invigilation')
    else:
        messages.warning(request, 'Failed to pay invigilation')
        return redirect('invigilation')

def logout(request):
    auth_logout(request)
    return redirect('user_login')