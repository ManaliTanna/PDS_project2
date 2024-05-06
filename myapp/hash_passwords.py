# Script to hash passwords and update the database
import os
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from myapp.models import Users  # Replace 'myapp' with your actual app name

class Command(BaseCommand):
    help = 'Hashes all plain text passwords in the database'
    print("asdsa")
    default_password = 'test@123'
    default_hashed_password = make_password(default_password)
    print(default_hashed_password)
    users = Users.objects.all()
    for user in users:
        user.password = default_hashed_password
        user.save()
        print(f'Successfully updated password for {user.user_name}')
    
    print('Password update process completed.')
