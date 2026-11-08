from django.urls import path
from . import views
urlpatterns=[path('',views.home,name='home'),path('about/',views.about,name='about'),path('search/',views.search,name='search'),path('contact/',views.contact,name='contact'),path('register/',views.register,name='register'),path('mfa/verify/',views.mfa_verify,name='mfa_verify'),path('mfa/resend/',views.resend_mfa_code,name='mfa_resend'),path('profile/',views.profile,name='profile'),path('u/<str:username>/',views.profile,name='public_profile')]
