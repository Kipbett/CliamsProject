from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('new-user/', views.add_user, name='add_user'),
    path('new-claim/', views.add_claim, name='add_claim'),
    path('list-claim/', views.list_claim, name='claims_list'),
    path('user-login/', views.user_login, name='user_login'),
    path('claim-payment/<int:id>/', views.claims_payment, name='new_payment'),
    path('payments/', views.payment_list, name='payments'),
    path('approved-claims/', views.approved_claims, name='approved_claims'),
    path('claim-update/<int:id>/', views.update_claim, name='claim_update'),
    path('end-claim/<int:id>/', views.end_claim, name='end_claim'),
    path('claim-dispute/<int:id>/', views.claim_dispute, name='claim_dispute'),
    path('dispute_list/', views.dispute_list, name='dispute_list'),
    path('inivgilation/', views.invigilations, name='invigilation'),
    path('end-inivgilation/<int:id>/', views.end_invigilation, name='end_invigilation'),
    path('upload-exam/', views.upload_exam, name='upload_exam'),
    path('upload-appointement/', views.upload_appointment, name='upload_appointment'),
    path('exam_list/', views.exam_list, name='exam_list'),
    path('approve-exam/<int:id>/', views.approve_exam, name='approve_exam'),
    path('pay-exam/<int:id>/', views.pay_exam, name='pay_exam'),
    path('approve-invigilation/<int:id>/', views.approve_invigilation, name='approve_invigilation'),
    path('new-invigilation/', views.add_invigilation, name='new_invigilation'),
    path('pay-invigilation/<int:id>/', views.pay_invigilation, name='pay_invigilation'),
    path('logout/', views.logout, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
