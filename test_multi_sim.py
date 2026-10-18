#!/usr/bin/env python
import os, sys, django, json, time
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='test_camera_user')
client = Client()
client.force_login(user)

for i in range(10):
    resp = client.post('/activities/stream-predict/', {'image':'data:image/jpeg;base64,AAA'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    print(i, resp.status_code, resp.content)
    data = json.loads(resp.content)
    if data.get('status') == 'multi_saved':
        print('Multi-person simulated:', data)
        break
    time.sleep(0.2)
else:
    print('No multi-person generated in 10 attempts')
