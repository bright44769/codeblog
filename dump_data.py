import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codeblog.settings')
django.setup()
from django.core.management import call_command

with open('data.json', 'w', encoding='utf-8') as f:
    call_command(
        'dumpdata',
        natural_foreign=True,
        natural_primary=True,
        exclude=['contenttypes', 'auth.permission', 'admin.logentry', 'sessions'],
        stdout=f,
  )