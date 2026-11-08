from django.urls import path
from . import views
app_name='blog'
urlpatterns=[
 path('',views.bloghome,name='home'), path('write/',views.create_post,name='create'), path('mine/',views.my_posts,name='my_posts'),
 path('<slug:slug>/edit/',views.edit_post,name='edit'), path('<slug:slug>/delete/',views.delete_post,name='delete'),
 path('<slug:slug>/like/',views.toggle_like,name='like'), path('<slug:slug>/bookmark/',views.toggle_bookmark,name='bookmark'), path('<slug:slug>/',views.blogpost,name='post'),
]
