from django.contrib import admin
from .models import Contact, Profile
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display=('name','email','created_at')
    search_fields=('name','email','content')
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=('user','location','updated_at')
    search_fields=('user__username','bio')
