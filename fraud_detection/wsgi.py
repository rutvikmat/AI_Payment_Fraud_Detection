"""
WSGI config for fraud_detection project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os

from django.core.wsgi import get_wsgi_application

# Point to the settings file
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fraud_detection.settings')

# This is the critical line missing in your current file
application = get_wsgi_application()