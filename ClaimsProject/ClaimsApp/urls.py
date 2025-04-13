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
    path('claim-approval/', views.approve_claim, name='claim_approval'),
    path('claim-update/<int:id>/', views.update_claim, name='claim_update'),
    path('end-claim/<int:id>/', views.end_claim, name='end_claim'),
    path('logout/', views.logout, name='logout'),
]
