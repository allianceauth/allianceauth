"""
WSGI config for alliance_auth project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alliance_auth.settings")

# virtualenv wrapper, uncomment below to activate
# activate_env=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'env/bin/activate_this.py')
# execfile(activate_env, dict(__file__=activate_env))


application = get_wsgi_application()
