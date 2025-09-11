# tests.py
import os
import django
from django.test import TestCase

# 配置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Question_Answering_System.settings')
django.setup()

from sendEmail.views import testzjz
from views import testzjz

print(testzjz())
