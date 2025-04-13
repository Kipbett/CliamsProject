from datetime import date, datetime
from django.utils import timezone
from ClaimsApp.models import Claims
from django.db.models import Sum
def pending_claims(user):
    now = timezone.now()
    current_month_start = date(now.year, now.month, 1)
    next_month_start = date(now.year, now.month + 1, 1) if now.month < 12 else date(now.year + 1, 1, 1)

    claims = Claims.objects.filter(
        lecturer=user
        # date_taught__gte = current_month_start,
        # date_taught__lt = next_month_start
    )

    pending_claims = Claims.objects.filter(status=Claims.StatusChoices.PENDING, lecturer=user).count()
    approved_claims = Claims.objects.filter(status=Claims.StatusChoices.APPROVED, lecturer=user).count()

    # total_hours = claims.aggregate(Sum('time_taught'))['time_taught__sum'] or 0
    # total_amount = claims.aggregate(Sum('claim_sub_total'))['claim_sub_total__sum'] or 0

    total_hours = 0
    total_amount = 0
    paid_amount = 0
    duration = []
    for claim in claims:
        hours = 0  # Initialize hours for each claim
        duration.append(int(claim.time_taught))
        # if claim.start_time and claim.end_time:
        #     start = claim.start_time
        #     end = claim.end_time

        #     start_datetime = timezone.make_aware(datetime(2000, 1, 1, start.hour, start.minute, start.second), timezone.get_current_timezone())
        #     end_datetime = timezone.make_aware(datetime(2000, 1, 1, end.hour, end.minute, end.second), timezone.get_current_timezone())
        #     duration = end_datetime - start_datetime
        #     hours = duration.total_seconds() / 3600

        # total_hours += hours
        # claim_sub_total = hours * 2000
        # total_amount += claim_sub_total

        # if claim.status == Claims.StatusChoices.PAID:
        #     paid_amount += claim_sub_total
    for time in duration:
        total_hours +=time
    # total_hours = sum(duration)

    total_amount = total_hours * 2000

    balance = total_amount - paid_amount


    # paid_amount = Claims.objects.filter(
    #     lecturer=user,
    #     date_taught__gte=current_month_start,
    #     date_taught__lt=next_month_start,
    #     status=Claims.StatusChoices.PAID,
    # ).aggregate(Sum('claim_sub_total'))['claim_sub_total__sum'] or 0

    # balance = total_amount - paid_amount

    return {
        'pending_claims': pending_claims,
        'approved_claims': approved_claims,
        'total_hours': total_hours,
        'total_amount': total_amount,
        'paid_amount': paid_amount,
        'balance': balance,
    }