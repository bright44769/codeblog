from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[('blog','0002_post_remove_contact_author_remove_contact_slug_and_more'),migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
      migrations.DeleteModel(name='Post'),
      migrations.CreateModel(name='Post',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('title',models.CharField(max_length=255)),('slug',models.SlugField(blank=True,max_length=280,unique=True)),('excerpt',models.CharField(blank=True,max_length=300)),('content',models.TextField()),('cover_image',models.ImageField(blank=True,null=True,upload_to='post_covers/')),('category',models.CharField(blank=True,max_length=80)),('tags',models.CharField(blank=True,max_length=250,help_text='Comma-separated tags')),('is_published',models.BooleanField(default=True)),('views',models.PositiveIntegerField(default=0)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('author',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='posts',to=settings.AUTH_USER_MODEL))],options={'ordering':['-created_at']}),
      migrations.CreateModel(name='Comment',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('body',models.TextField(max_length=2000)),('created_at',models.DateTimeField(auto_now_add=True)),('author',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),('post',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='comments',to='blog.post'))],options={'ordering':['created_at']}),
      migrations.CreateModel(name='Like',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),('post',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='likes',to='blog.post')),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL))]),
      migrations.CreateModel(name='Bookmark',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),('post',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='bookmarks',to='blog.post')),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL))]),
      migrations.AddConstraint(model_name='like',constraint=models.UniqueConstraint(fields=('post','user'),name='unique_post_like')),
      migrations.AddConstraint(model_name='bookmark',constraint=models.UniqueConstraint(fields=('post','user'),name='unique_post_bookmark')),
    ]
