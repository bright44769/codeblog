from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
 dependencies=[('home','0002_contact_timestamp'),migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
 operations=[migrations.RenameField(model_name='contact',old_name='timeStamp',new_name='created_at'),migrations.CreateModel(name='Profile',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('avatar',models.ImageField(blank=True,null=True,upload_to='avatars/')),('bio',models.TextField(blank=True,max_length=500)),('website',models.URLField(blank=True)),('location',models.CharField(blank=True,max_length=100)),('updated_at',models.DateTimeField(auto_now=True)),('user',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='profile',to=settings.AUTH_USER_MODEL))])]
