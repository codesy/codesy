from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^events$', views.StripeHookView.as_view(), name='events'),
    url(r'^terms$', views.AcceptTermsView.as_view(), name='terms'),
    url(r'^identity$', views.VerifyIdentityView.as_view(), name='identity'),
    url(r'^bank$', views.BankAccountView.as_view(), name='bank'),
    url(r'^card$', views.CreditCardView.as_view(), name='card'),
]
