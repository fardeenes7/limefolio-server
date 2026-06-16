from django.urls import path
from .views import (
    PlanListView, PolarWebhookView, CheckoutView, BkashCallbackView, 
    PromoValidateView, BalanceView, UpgradeSubscriptionView, 
    CancelSubscriptionView, ReactivateSubscriptionView, 
    BkashUpgradeView, SubscriptionDetailView, ClaimPromotionView,
    LatestPromotionView
)

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='plan-list'),
    path('promotions/latest/', LatestPromotionView.as_view(), name='latest-promotion'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('webhooks/polar/', PolarWebhookView.as_view(), name='polar-webhook'),
    path('bkash/callback/', BkashCallbackView.as_view(), name='bkash-callback'),
    path('promo/validate/', PromoValidateView.as_view(), name='promo-validate'),
    path('balance/', BalanceView.as_view(), name='balance'),
    path('subscription/', SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('subscription/upgrade/', UpgradeSubscriptionView.as_view(), name='subscription-upgrade'),
    path('subscription/cancel/', CancelSubscriptionView.as_view(), name='subscription-cancel'),
    path('subscription/reactivate/', ReactivateSubscriptionView.as_view(), name='subscription-reactivate'),
    path('subscription/bkash/upgrade/', BkashUpgradeView.as_view(), name='subscription-bkash-upgrade'),
    path('claim-promotion/', ClaimPromotionView.as_view(), name='claim-promotion'),
]
