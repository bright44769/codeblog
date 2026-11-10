from django.contrib import admin
from .models import Contact, Profile, SiteReview
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display=('name','email','created_at')
    search_fields=('name','email','content')
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=('user','location','updated_at')
    search_fields=('user__username','bio')

@admin.register(SiteReview)
class SiteReviewAdmin(admin.ModelAdmin):
    list_display=('user','created_at')
    search_fields=('user__username','experience','expectations')
    readonly_fields=('created_at',)
