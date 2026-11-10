from django.urls import path
from . import views
urlpatterns=[path('',views.home,name='home'),path('about/',views.about,name='about'),path('search/',views.search,name='search'),path('contact/',views.contact,name='contact'),path('review/',views.review,name='review'),path('register/',views.register,name='register'),path('profile/',views.profile,name='profile'),path('u/<str:username>/',views.profile,name='public_profile')]
